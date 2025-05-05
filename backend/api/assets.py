from flask import Blueprint, jsonify, request, abort
from services.database import get_db_cursor
from datetime import date, datetime
import logging

logger = logging.getLogger(__name__)
bp = Blueprint('assets', __name__, url_prefix='/api/assets')

@bp.route('/', methods=['GET'])
def get_all_assets():
    department = request.args.get('department')
    asset_type = request.args.get('type')
    criticality = request.args.get('criticality')

    with get_db_cursor() as cursor:
        query = "SELECT * FROM assets WHERE 1=1"
        params = []

        if department:
            query += " AND department = %s"
            params.append(department)

        if asset_type:
            query += " AND type = %s"
            params.append(asset_type)

        if criticality:
            query += " AND criticality = %s"
            params.append(criticality)

        query += """
          ORDER BY
            CASE criticality
              WHEN 'Critical' THEN 1
              WHEN 'High' THEN 2
              WHEN 'Medium' THEN 3
              WHEN 'Low' THEN 4
              ELSE 5
            END,
            name ASC
        """

        cursor.execute(query, params)
        assets = cursor.fetchall()

        for a in assets:
            for date_key in ('purchase_date', 'vulnerabilities_last_scan_date'):
                val = a.get(date_key)
                if isinstance(val, (date, datetime)):
                    a[date_key] = val.isoformat()

        return jsonify(assets), 200

@bp.route('/<string:asset_id>', methods=['GET'])
def get_asset(asset_id):
    numeric = ''.join(filter(str.isdigit, asset_id))
    if not numeric.isdigit():
        return jsonify({"error": "Invalid asset ID format"}), 400

    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM assets WHERE asset_id = %s", (numeric,))
        asset = cursor.fetchone()
        if not asset:
            abort(404)

        for date_key in ('purchase_date', 'vulnerabilities_last_scan_date'):
            val = asset.get(date_key)
            if isinstance(val, (date, datetime)):
                asset[date_key] = val.isoformat()

        return jsonify(asset), 200

@bp.route('/stats', methods=['GET'])
def get_asset_stats():
    """GET /api/assets/stats → Dashboard asset statistics"""

    with get_db_cursor() as cursor:
        try:
            cursor.execute("BEGIN")

            cursor.execute("SELECT COUNT(*) AS total FROM assets")
            total = cursor.fetchone()['total']

            cursor.execute("SELECT COUNT(*) AS critical FROM assets WHERE criticality = 'Critical'")
            critical = cursor.fetchone()['critical']

            cursor.execute("SELECT COUNT(*) AS high FROM assets WHERE criticality = 'High'")
            high = cursor.fetchone()['high']

            cursor.execute("SELECT COUNT(*) AS medium FROM assets WHERE criticality = 'Medium'")
            medium = cursor.fetchone()['medium']

            cursor.execute("SELECT COUNT(*) AS low FROM assets WHERE criticality = 'Low'")
            low = cursor.fetchone()['low']

            cursor.execute("COMMIT")
        except Exception as e:
            cursor.execute("ROLLBACK")
            logger.error(f"Database error: {e}")
            return jsonify({"error": "Database error"}), 500

    return jsonify({
        "total": total,
        "critical": critical,
        "high": high,
        "medium": medium,
        "low": low
    }), 200

@bp.route('/filter-options', methods=['GET'])
def get_filter_options():
    with get_db_cursor() as cursor:
        cursor.execute("SELECT DISTINCT department FROM assets ORDER BY department")
        departments = [r['department'] for r in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT type FROM assets ORDER BY type")
        types = [r['type'] for r in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT location FROM assets ORDER BY location")
        locations = [r['location'] for r in cursor.fetchall()]

        cursor.execute("""
            SELECT DISTINCT criticality FROM assets
            ORDER BY
              CASE criticality
                WHEN 'Critical' THEN 1
                WHEN 'High' THEN 2
                WHEN 'Medium' THEN 3
                WHEN 'Low' THEN 4
                ELSE 5
              END
        """)
        criticalities = [r['criticality'] for r in cursor.fetchall()]

    return jsonify({
        "departments": departments,
        "types": types,
        "locations": locations,
        "criticalities": criticalities
    }), 200
