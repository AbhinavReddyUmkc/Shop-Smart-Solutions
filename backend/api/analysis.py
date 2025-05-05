from flask import Blueprint, jsonify, request
from services.database import get_db_cursor
from services.llm_service import generate_risk_score
from services.mitre_service import get_mitre_threats
from services.nvd_service import get_vulnerabilities
from services.otx_service import get_otx_threats
from services.virustotal_service import get_virustotal_report
import datetime
import logging
import os

logger = logging.getLogger(__name__)
bp = Blueprint('analysis', __name__, url_prefix='/api/analysis')

@bp.route('/asset/<string:asset_id>', methods=['GET'])
def get_asset_analysis(asset_id):
    """Get analysis data for an asset"""
    try:
        numeric_id = ''.join(filter(str.isdigit, asset_id)) or asset_id

        if not numeric_id.isdigit():
            return jsonify({"error": "Invalid asset ID format"}), 400

        if not os.environ.get('ONST_API_KEY'):
            logger.error("ONST_API_KEY not configured")
            return jsonify({"error": "Configuration error", "message": "ONST API not configured"}), 500

        with get_db_cursor() as cursor:
            try:
                cursor.execute("BEGIN")

                cursor.execute("SELECT asset_id FROM assets WHERE asset_id = %s", (numeric_id,))
                if not cursor.fetchone():
                    cursor.execute("ROLLBACK")
                    return jsonify({"error": "Asset not found"}), 404

                vulnerability_query = """
                    SELECT v.* 
                    FROM vulnerabilities v
                    JOIN asset_vulnerabilities av ON v.id = av.vulnerability_id
                    WHERE av.asset_id = %s
                """
                cursor.execute(vulnerability_query, (numeric_id,))
                vulnerabilities = cursor.fetchall()

                threat_query = """
                    SELECT t.* 
                    FROM threats t
                    JOIN asset_threats at ON t.id = at.threat_id
                    WHERE at.asset_id = %s
                """
                cursor.execute(threat_query, (numeric_id,))
                threats = cursor.fetchall()

                cursor.execute("COMMIT")

                return jsonify({
                    'vulnerabilities': vulnerabilities,
                    'threats': threats,
                    'risk_score': calculate_risk_score(vulnerabilities, threats)
                })

            except Exception as e:
                cursor.execute("ROLLBACK")
                logger.error(f"Database error: {e}")
                return jsonify({"error": "Database error", "details": str(e)}), 500

    except Exception as e:
        logger.error(f"Connection error: {e}")
        return jsonify({"error": "Connection failed"}), 500

@bp.route('/scan', methods=['POST'])
def scan_asset():
    if not os.environ.get('ONST_API_KEY'):
        return jsonify({
            "error": "ONST API not configured",
            "message": "Please configure the ONST_API_KEY environment variable"
        }), 500

    data = request.get_json()
    asset_id = data.get('asset_id')

    if not asset_id:
        return jsonify({"error": "Asset ID is required"}), 400

    with get_db_cursor() as cursor:
        try:
            cursor.execute("BEGIN")

            cursor.execute("SELECT * FROM assets WHERE asset_id = %s", (asset_id,))
            asset = cursor.fetchone()

            if not asset:
                cursor.execute("ROLLBACK")
                return jsonify({"error": "Asset not found"}), 404

            cursor.execute("COMMIT")
        except Exception as e:
            cursor.execute("ROLLBACK")
            logger.error(f"Database error: {e}")
            return jsonify({"error": "Database error"}), 500

    try:
        threat_data = {
            "nvd": get_vulnerabilities(asset),
            "otx": get_otx_threats(asset),
            "virustotal": get_virustotal_report(asset)
        }

        risk_score = generate_risk_score(asset, threat_data)

        with get_db_cursor() as cursor:
            try:
                cursor.execute("BEGIN")

                cursor.execute("""
                    INSERT INTO asset_analysis (asset_id, risk_score, scan_date) 
                    VALUES (%s, %s, %s)
                    ON CONFLICT (asset_id) 
                    DO UPDATE SET risk_score = %s, scan_date = %s
                    RETURNING analysis_id
                """, (asset_id, risk_score, datetime.datetime.now(), risk_score, datetime.datetime.now()))

                analysis_id = cursor.fetchone()["analysis_id"]

                for source, vulnerabilities in threat_data.items():
                    for vuln in vulnerabilities:
                        cursor.execute("""
                            INSERT INTO vulnerabilities (
                                analysis_id, source, cve_id, name, 
                                description, severity, score
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (
                            analysis_id, source,
                            vuln.get("id"), vuln.get("name"),
                            vuln.get("description"),
                            vuln.get("severity"),
                            vuln.get("score")
                        ))

                cursor.execute("COMMIT")
            except Exception as e:
                cursor.execute("ROLLBACK")
                logger.error(f"Database error: {e}")
                return jsonify({"error": "Database error"}), 500

        return jsonify({
            "success": True,
            "asset_id": asset_id,
            "risk_score": risk_score,
            "threat_sources": list(threat_data.keys())
        })

    except Exception as e:
        logger.error(f"Scan failed: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    with get_db_cursor() as cursor:
        try:
            cursor.execute("BEGIN")

            cursor.execute("""
                SELECT 
                    scan_date::date, 
                    AVG(risk_score) as avg_risk_score,
                    COUNT(DISTINCT asset_id) as scanned_assets
                FROM asset_analysis
                GROUP BY scan_date::date
                ORDER BY scan_date::date DESC
                LIMIT 7
            """)
            trend_data = cursor.fetchall()

            cursor.execute("""
                SELECT 
                    a.type as type, 
                    COUNT(a.asset_id) as count,
                    AVG(aa.risk_score) as avg_risk
                FROM assets a
                JOIN asset_analysis aa ON a.asset_id = aa.asset_id
                GROUP BY a.type
                ORDER BY avg_risk DESC
                LIMIT 5
            """)
            top_risks = cursor.fetchall()

            cursor.execute("COMMIT")

            return jsonify({
                "risk_trend": trend_data,
                "top_risks": top_risks
            })
        except Exception as e:
            cursor.execute("ROLLBACK")
            logger.error(f"Database error: {e}")
            return jsonify({"error": "Database error"}), 500

@bp.route('/threats', methods=['GET'])
def get_threats():
    try:
        with get_db_cursor() as cursor:
            try:
                cursor.execute("BEGIN")

                vulnerability_query = """
                    SELECT v.* 
                    FROM vulnerabilities v
                    JOIN asset_vulnerabilities av ON v.id = av.vulnerability_id
                    WHERE av.asset_id = %s
                """
                threat_query = """
                    SELECT t.* 
                    FROM threats t
                    JOIN asset_threats at ON t.id = at.threat_id
                    WHERE at.asset_id = %s
                """

                asset_id = request.args.get('asset_id')
                try:
                    cursor.execute(vulnerability_query, (asset_id,))
                    vulnerabilities = cursor.fetchall()
                except Exception as e:
                    logger.warning(f"Vulnerability query failed: {e}")
                    vulnerabilities = []

                try:
                    cursor.execute(threat_query, (asset_id,))
                    threats = cursor.fetchall()
                except Exception as e:
                    logger.warning(f"Threat query failed: {e}")
                    threats = []

                cursor.execute("COMMIT")

                return jsonify({
                    'vulnerabilities': vulnerabilities,
                    'threats': threats
                })
            except Exception as e:
                cursor.execute("ROLLBACK")
                logger.error(f"Database error: {e}")
                return jsonify({'vulnerabilities': [], 'threats': []})
    except Exception as e:
        logger.error(f"Connection error: {e}")
        raise

@bp.route('/summary', methods=['GET'])
def get_dashboard_summary():
    """Get summary of total threats, vulnerabilities, critical assets"""
    with get_db_cursor() as cursor:
        try:
            cursor.execute("BEGIN")

            cursor.execute("SELECT COUNT(*) as total FROM threats")
            total_threats = cursor.fetchone()['total']

            cursor.execute("SELECT COUNT(*) as total FROM vulnerabilities")
            total_vulnerabilities = cursor.fetchone()['total']

            cursor.execute("SELECT COUNT(*) as total FROM assets WHERE criticality = 'Critical'")
            critical_assets = cursor.fetchone()['total']

            cursor.execute("COMMIT")

            return jsonify({
                "total_threats": total_threats,
                "total_vulnerabilities": total_vulnerabilities,
                "critical_assets": critical_assets
            })
        except Exception as e:
            cursor.execute("ROLLBACK")
            logger.error(f"Database error: {e}")
            return jsonify({"error": "Database error"}), 500
