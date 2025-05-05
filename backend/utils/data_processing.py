import json
import datetime
from collections import defaultdict

class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder for datetime objects"""
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        return super().default(obj)

def parse_software_string(software_str):
    """Parse semicolon-separated software string into a list of software"""
    if not software_str:
        return []
    
    return [s.strip() for s in software_str.split(';') if s.strip()]

def calculate_risk_metrics(threats):
    """Calculate risk metrics from a list of threats"""
    if not threats:
        return {
            'overall_risk_score': 0,
            'critical_count': 0,
            'high_count': 0,
            'medium_count': 0,
            'low_count': 0,
            'total_count': 0
        }
    
    # Count threats by severity
    critical_count = sum(1 for t in threats if t.get('risk_score', 0) >= 8.0)
    high_count = sum(1 for t in threats if 6.0 <= t.get('risk_score', 0) < 8.0)
    medium_count = sum(1 for t in threats if 4.0 <= t.get('risk_score', 0) < 6.0)
    low_count = sum(1 for t in threats if t.get('risk_score', 0) < 4.0)
    
    # Calculate weighted average risk score
    weighted_sum = 0
    weight_total = 0
    
    for threat in threats:
        score = threat.get('risk_score', 5.0)
        # Weight critical threats more heavily
        weight = 3 if score >= 8.0 else (2 if score >= 6.0 else 1)
        weighted_sum += score * weight
        weight_total += weight
    
    overall_score = weighted_sum / weight_total if weight_total > 0 else 0
    
    return {
        'overall_risk_score': round(overall_score, 1),
        'critical_count': critical_count,
        'high_count': high_count,
        'medium_count': medium_count,
        'low_count': low_count,
        'total_count': len(threats)
    }

def generate_timeline_data(threats, interval='day'):
    """Generate timeline data for visualization"""
    timeline = defaultdict(lambda: {'total': 0, 'critical': 0, 'high': 0, 'medium': 0, 'low': 0})
    
    for threat in threats:
        date_str = None
        discovered_date = threat.get('discovered_date')
        
        if not discovered_date:
            continue
            
        # Handle both string and datetime objects
        if isinstance(discovered_date, str):
            date_str = discovered_date.split('T')[0]
        elif isinstance(discovered_date, datetime.date):
            date_str = discovered_date.isoformat()
        else:
            continue
            
        if interval == 'month':
            # Group by month (YYYY-MM)
            date_str = date_str[:7]
        
        timeline[date_str]['total'] += 1
        
        score = threat.get('risk_score', 5.0)
        if score >= 8.0:
            timeline[date_str]['critical'] += 1
        elif score >= 6.0:
            timeline[date_str]['high'] += 1
        elif score >= 4.0:
            timeline[date_str]['medium'] += 1
        else:
            timeline[date_str]['low'] += 1
    
    # Convert to list format for API response
    sorted_timeline = [{'date': date, **counts} for date, counts in sorted(timeline.items())]
    
    return sorted_timeline

def analyze_vulnerability_trends(threats, time_period='month'):
    """Analyze vulnerability trends over time"""
    if not threats:
        return {
            'trend': 'stable',
            'percent_change': 0,
            'current_period_count': 0,
            'previous_period_count': 0
        }
    
    # Sort threats by discovery date
    sorted_threats = sorted(
        [t for t in threats if t.get('discovered_date')], 
        key=lambda t: t.get('discovered_date')
    )
    
    if not sorted_threats:
        return {
            'trend': 'stable',
            'percent_change': 0,
            'current_period_count': 0,
            'previous_period_count': 0
        }
    
    # Determine the current and previous time periods
    now = datetime.datetime.now()
    
    if time_period == 'month':
        current_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(days=30)
        previous_start = current_start - datetime.timedelta(days=30)
    elif time_period == 'week':
        current_start = now - datetime.timedelta(days=7)
        previous_start = current_start - datetime.timedelta(days=7)
    else:  # day
        current_start = now - datetime.timedelta(days=1)
        previous_start = current_start - datetime.timedelta(days=1)
    
    # Count threats in each period
    current_period_count = sum(
        1 for t in sorted_threats 
        if isinstance(t.get('discovered_date'), str) and t.get('discovered_date', '') >= current_start.isoformat()
    )
    
    previous_period_count = sum(
        1 for t in sorted_threats 
        if (isinstance(t.get('discovered_date'), str) and 
            previous_start.isoformat() <= t.get('discovered_date', '') < current_start.isoformat())
    )
    
    # Calculate percent change
    if previous_period_count > 0:
        percent_change = ((current_period_count - previous_period_count) / previous_period_count) * 100
    else:
        percent_change = 100 if current_period_count > 0 else 0
    
    # Determine trend
    if percent_change > 10:
        trend = 'increasing'
    elif percent_change < -10:
        trend = 'decreasing'
    else:
        trend = 'stable'
    
    return {
        'trend': trend,
        'percent_change': round(percent_change, 1),
        'current_period_count': current_period_count,
        'previous_period_count': previous_period_count
    }

def generate_asset_risk_report(asset, threats):
    """Generate a comprehensive risk report for an asset"""
    risk_metrics = calculate_risk_metrics(threats)
    timeline_data = generate_timeline_data(threats, interval='month')
    trend_analysis = analyze_vulnerability_trends(threats)
    
    # Group threats by category
    categories = defaultdict(list)
    for threat in threats:
        if threat.get('risk_score', 0) >= 8.0:
            severity = 'critical'
        elif threat.get('risk_score', 0) >= 6.0:
            severity = 'high'
        elif threat.get('risk_score', 0) >= 4.0:
            severity = 'medium'
        else:
            severity = 'low'
            
        categories[severity].append(threat)
    
    # Calculate risk factors
    risk_factors = []
    
    if risk_metrics['critical_count'] > 0:
        risk_factors.append({
            'factor': 'Critical Vulnerabilities',
            'impact': 'High',
            'description': f"{risk_metrics['critical_count']} critical vulnerabilities detected"
        })
    
    if asset.get('criticality') == 'Critical':
        risk_factors.append({
            'factor': 'Critical Asset',
            'impact': 'High',
            'description': 'This is a critical asset for the organization'
        })
    
    if asset.get('data_classification') in ['Confidential', 'Restricted']:
        risk_factors.append({
            'factor': 'Sensitive Data',
            'impact': 'High',
            'description': f"Asset contains {asset.get('data_classification').lower()} data"
        })
    
    # Check for outdated software/OS
    os_version = asset.get('os_version', '')
    if any(v in os_version.lower() for v in ['xp', 'vista', '7', '2003', '2008']):
        risk_factors.append({
            'factor': 'Outdated Operating System',
            'impact': 'High',
            'description': f"Using {asset.get('operating_system', '')} {os_version}"
        })
    
    return {
        'asset_id': asset.get('asset_id'),
        'asset_name': asset.get('name'),
        'department': asset.get('department'),
        'criticality': asset.get('criticality'),
        'overall_risk_score': risk_metrics['overall_risk_score'],
        'risk_level': get_risk_level(risk_metrics['overall_risk_score']),
        'threat_counts': {
            'total': risk_metrics['total_count'],
            'critical': risk_metrics['critical_count'],
            'high': risk_metrics['high_count'],
            'medium': risk_metrics['medium_count'],
            'low': risk_metrics['low_count']
        },
        'trend': trend_analysis,
        'risk_factors': risk_factors,
        'timeline': timeline_data,
        'last_scan_date': asset.get('vulnerabilities_last_scan_date'),
        'top_threats': {
            'critical': categories['critical'][:3],
            'high': categories['high'][:3],
            'medium': categories['medium'][:3]
        }
    }

def get_risk_level(score):
    """Convert a numerical risk score to a risk level string"""
    if score >= 8.0:
        return 'Critical'
    elif score >= 6.0:
        return 'High'
    elif score >= 4.0:
        return 'Medium'
    else:
        return 'Low'