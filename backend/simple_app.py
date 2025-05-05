# backend/simple_app.py
from dotenv import load_dotenv
load_dotenv()

import os, json, logging
from decimal import Decimal
from flask import Flask, jsonify, request
from flask_cors import CORS
from psycopg2.extras import RealDictCursor

from services.database           import get_db_connection
from services.nvd_service        import get_vulnerabilities
from services.otx_service        import get_otx_threats
from services.virustotal_service import get_virustotal_report
from services.llm_service        import generate_risk_score
from api.assets import bp as assets_bp


# ─── JSON DECIMAL SETUP ──────────────────────────────────────────────────────────
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super().default(o)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
app.json_encoder = DecimalEncoder

# ─── HEALTH ─────────────────────────────────────────────────────────────────────
@app.route("/", methods=["GET"])
@app.route("/health", methods=["GET"])
def health():
    return jsonify(status="healthy")

# ─── LIST ASSETS ─────────────────────────────────────────────────────────────────
@app.route("/api/assets", methods=["GET"])
def list_assets():
    with get_db_connection() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM assets;")
        rows = cur.fetchall()
    for r in rows:
        r["id"] = r["asset_id"]
    return jsonify(rows), 200

# ─── ASSET DETAILS ───────────────────────────────────────────────────────────────
@app.route("/api/assets/<int:asset_id>", methods=["GET"])
def asset_details(asset_id):
    with get_db_connection() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM assets WHERE asset_id=%s", (asset_id,))
        row = cur.fetchone()
    if not row:
        return jsonify(error="not found"), 404
    row["id"] = row["asset_id"]
    return jsonify(row), 200

# ─── GET EXISTING ANALYSIS ───────────────────────────────────────────────────────
@app.route("/api/analysis/asset/<int:asset_id>", methods=["GET"])
def get_asset_analysis(asset_id):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor(cursor_factory=RealDictCursor)

            cur.execute("""
                SELECT v.*
                  FROM vulnerabilities v
                  JOIN asset_vulnerabilities av
                    ON v.id = av.vulnerability_id
                 WHERE av.asset_id = %s
            """, (asset_id,))
            vuls = cur.fetchall() or []

            cur.execute("""
                SELECT t.*
                  FROM threats t
                  JOIN asset_threats at
                    ON t.threat_id = at.threat_id
                 WHERE at.asset_id = %s
            """, (asset_id,))
            thrs = cur.fetchall() or []

            cur.execute("SELECT risk_score FROM assets WHERE asset_id=%s", (asset_id,))
            row = cur.fetchone() or {}
            risk = row.get("risk_score") or 0.0

        return jsonify({
            "vulnerabilities": vuls,
            "threats": thrs,
            "risk_score": float(risk)
        }), 200

    except Exception:
        logger.exception("get_asset_analysis failed")
        return jsonify(vulnerabilities=[], threats=[], risk_score=0), 500

# ─── TRIGGER A NEW SCAN ──────────────────────────────────────────────────────────
@app.route('/api/analysis/scan', methods=['POST','OPTIONS'])
def scan_asset():
    if request.method == 'OPTIONS':
        return jsonify({'message':'CORS preflight'})

    payload = request.get_json(silent=True) or {}
    try:
        asset_id = int(payload.get('asset_id'))
    except (TypeError, ValueError):
        return jsonify({'error':'asset_id must be an integer'}), 400

    logger.info(f"Triggering scan for asset {asset_id}")
    try:
        with get_db_connection() as conn:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("SELECT * FROM assets WHERE asset_id=%s", (asset_id,))
            asset = cur.fetchone()
        if not asset:
            return jsonify({'error':'Asset not found'}), 404

        vulnerabilities = get_vulnerabilities(asset)
        otx_threats     = get_otx_threats(asset)
        vt_threats      = get_virustotal_report(asset)
        threats         = otx_threats + vt_threats

        risk_score = generate_risk_score(asset, {
            'vulnerabilities': vulnerabilities,
            'threats': threats
        })

        with get_db_connection() as conn:
            cur = conn.cursor()

            cur.execute("""
                UPDATE assets
                   SET risk_score = %s,
                       vulnerabilities_last_scan_date = NOW()
                 WHERE asset_id = %s
            """, (risk_score, asset_id))

            for v in vulnerabilities:
                severity = v.get('severity', 'LOW').upper()
                if severity not in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
                    severity = "LOW"

                cur.execute("""
                    INSERT INTO vulnerabilities (cve_id, description, cvss_score, cvss_severity)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (cve_id) DO NOTHING
                """, (
                    v['id'],
                    v.get('description',''),
                    v.get('score',0)/10.0,
                    severity
                ))
                cur.execute("""
                    INSERT INTO asset_vulnerabilities (asset_id,vulnerability_id,detected_date)
                    VALUES (%s,(SELECT id FROM vulnerabilities WHERE cve_id=%s),NOW())
                    ON CONFLICT DO NOTHING
                """, (asset_id, v['id']))

            for t in threats:
                severity = t.get('severity','LOW').upper()
                cur.execute("""
                    INSERT INTO threats (source, external_id, name, description, severity, confidence)
                    VALUES (%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (source,external_id) DO NOTHING
                """, (
                    t['source'],
                    t['id'],
                    t['name'],
                    t.get('description',''),
                    severity,
                    t.get('score',0)
                ))
                cur.execute("""
                    INSERT INTO asset_threats (asset_id, threat_id, detected_date)
                    VALUES (%s,(SELECT threat_id FROM threats WHERE source=%s AND external_id=%s),NOW())
                    ON CONFLICT DO NOTHING
                """, (asset_id, t['source'], t['id']))

            conn.commit()

        return jsonify({
            'asset_id': asset_id,
            'risk_score': risk_score,
            'vulnerabilities': vulnerabilities,
            'threats': threats
        }), 200

    except Exception as e:
        logger.error(f"Scan error for asset {asset_id}: {e}", exc_info=True)
        return jsonify({'error':'Server error'}), 500

# ─── BOOTSTRAP ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
