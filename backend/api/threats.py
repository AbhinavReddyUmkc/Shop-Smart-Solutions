from flask import Blueprint, jsonify, request
from services.database import get_db_connection, get_db_cursor

bp = Blueprint('threats', __name__, url_prefix='/api/threats/')

@bp.route('/', strict_slashes=False, methods=['GET'])
def get_all_threats():

    """Get all threats with optional filtering"""
    severity = request.args.get('severity')
    cve_id = request.args.get('cve_id')
    
    with get_db_cursor() as cursor:
        query = "SELECT * FROM threats WHERE 1=1"
        params = []
        
        if severity:
            query += " AND cvss_severity = %s"
            params.append(severity)
        
        if cve_id:
            query += " AND cve_id LIKE %s"
            params.append(f"%{cve_id}%")
        
        query += " ORDER BY cvss_score DESC"
        
        cursor.execute(query, params)
        threats = cursor.fetchall()
        
        # Convert date objects to strings
        for threat in threats:
            if threat.get('published_date'):
                threat['published_date'] = threat['published_date'].isoformat()
            if threat.get('last_modified_date'):
                threat['last_modified_date'] = threat['last_modified_date'].isoformat()
        
        return jsonify(threats)

@bp.route('/<int:threat_id>', methods=['GET'])
def get_threat(threat_id):
    """Get detailed information for a specific threat"""
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM threats WHERE threat_id = %s", (threat_id,))
        threat = cursor.fetchone()
        
        if not threat:
            return jsonify({"error": "Threat not found"}), 404
        
        # Convert date objects to strings
        if threat.get('published_date'):
            threat['published_date'] = threat['published_date'].isoformat()
        if threat.get('last_modified_date'):
            threat['last_modified_date'] = threat['last_modified_date'].isoformat()
        
        # Get affected assets
        cursor.execute("""
            SELECT a.asset_id, a.name, a.type, a.department, a.criticality, 
                   at.risk_score, at.mitigation_status
            FROM asset_threats at
            JOIN assets a ON at.asset_id = a.asset_id
            WHERE at.threat_id = %s
        """, (threat_id,))
        affected_assets = cursor.fetchall()
        
        threat['affected_assets'] = affected_assets
        
        return jsonify(threat)

@bp.route('/stats', methods=['GET'])
def get_threat_stats():
    """Get statistics about threats for dashboard"""
    with get_db_cursor() as cursor:
        # Total threat count
        cursor.execute("SELECT COUNT(*) as total FROM threats")
        total_count = cursor.fetchone()['total']
        
        # Count by severity
        cursor.execute("""
            SELECT cvss_severity, COUNT(*) as count FROM threats 
            GROUP BY cvss_severity 
            ORDER BY CASE cvss_severity 
                WHEN 'CRITICAL' THEN 1 
                WHEN 'HIGH' THEN 2 
                WHEN 'MEDIUM' THEN 3 
                WHEN 'LOW' THEN 4 
                ELSE 5 END
        """)
        severity = cursor.fetchall()
        
        # Count by source
        cursor.execute("SELECT source, COUNT(*) as count FROM threats GROUP BY source ORDER BY count DESC")
        sources = cursor.fetchall()
        
        # Count published by month (last 6 months)
        cursor.execute("""
            SELECT TO_CHAR(published_date, 'YYYY-MM') as month, COUNT(*) as count 
            FROM threats 
            WHERE published_date > CURRENT_DATE - INTERVAL '6 months'
            GROUP BY month 
            ORDER BY month
        """)
        by_month = cursor.fetchall()
        
        return jsonify({
            "total_threats": total_count,
            "by_severity": severity,
            "by_source": sources,
            "by_month": by_month
        })

@bp.route('/search', methods=['GET'])
def search_threats():
    """Search for threats by keyword"""
    keyword = request.args.get('q', '')
    
    if not keyword or len(keyword) < 3:
        return jsonify({"error": "Search query must be at least 3 characters"}), 400
    
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT * FROM threats 
            WHERE cve_id LIKE %s 
               OR name LIKE %s 
               OR description LIKE %s
            ORDER BY cvss_score DESC
            LIMIT 100
        """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
        
        threats = cursor.fetchall()
        
        # Convert date objects to strings
        for threat in threats:
            if threat.get('published_date'):
                threat['published_date'] = threat['published_date'].isoformat()
            if threat.get('last_modified_date'):
                threat['last_modified_date'] = threat['last_modified_date'].isoformat()
        
        return jsonify(threats)