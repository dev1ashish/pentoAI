from typing import List, Dict
from zapv2 import ZAPv2
import requests
import json
import os
import jwt
from datetime import datetime, timedelta

zap = ZAPv2(apikey=os.getenv("ZAP_API_KEY"))

def discover_endpoints(base_url: str) -> Dict:
    try:
        scan_id = zap.spider.scan(base_url)
        endpoints = zap.spider.results(scan_id)
        return {"endpoints": [{"endpoint": endpoint, "method": "GET"} for endpoint in endpoints]}
    except Exception as e:
        return {"error": str(e)}

def scan_vulnerability(endpoint: str, method: str) -> Dict:
    try:
        scan_id = zap.ascan.scan(endpoint)
        alerts = zap.ascan.alerts()
        vulnerabilities = [
            {
                "name": alert.get('name'),
                "severity": alert.get('risk'),
                "description": alert.get('description')
            }
            for alert in alerts
        ]
        return {"vulnerabilities": vulnerabilities}
    except Exception as e:
        return {"error": str(e)}

def test_authentication(auth_endpoint: str, auth_type: str) -> Dict:
    vulnerabilities = []
    if auth_type == "JWT":
        vulnerabilities.extend(test_jwt_vulnerabilities(auth_endpoint))
    elif auth_type == "OAuth":
        vulnerabilities.extend(_test_oauth_vulnerabilities(auth_endpoint))
    elif auth_type == "Basic":
        vulnerabilities.extend(_test_basic_auth_vulnerabilities(auth_endpoint))
    return {"auth_vulnerabilities": vulnerabilities}

def test_jwt_vulnerabilities(auth_endpoint: str) -> List[Dict]:
    vulnerabilities = []
    
    none_token = create_none_algorithm_token()
    if test_token(auth_endpoint, none_token):
        vulnerabilities.append({
            "type": "JWT None Algorithm",
            "description": "API accepts JWT tokens signed with 'none' algorithm",
            "severity": "High"
        })
    
    weak_token = create_weak_signature_token()
    if test_token(auth_endpoint, weak_token):
        vulnerabilities.append({
            "type": "Weak JWT Signature",
            "description": "API accepts JWT tokens with weak signatures",
            "severity": "High"
        })
    
    return vulnerabilities

def create_none_algorithm_token():
    payload = {
        'sub': '1234567890',
        'name': 'Test User',
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, None, algorithm='none')

def create_weak_signature_token():
    payload = {
        'sub': '1234567890',
        'name': 'Test User',
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(hours=1)
    }
    weak_secret = '1234'  # Weak secret for demonstration purposes
    return jwt.encode(payload, weak_secret, algorithm='HS256')

def test_token(endpoint: str, token: str):
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(endpoint, headers=headers)
        return response.status_code == 200
    except Exception:
        return False

def _test_oauth_vulnerabilities(endpoint: str) -> List[Dict]:
    vulnerabilities = []
    
    insecure_redirect = f"{endpoint}?response_type=token&client_id=test&redirect_uri=http://attacker.com"
    response = requests.get(insecure_redirect)
    if response.status_code == 302:
        vulnerabilities.append({
            "type": "Insecure redirect_uri",
            "description": "OAuth endpoint allows arbitrary redirect URIs",
            "severity": "High"
        })
    
    if "csrf" not in response.text.lower():
        vulnerabilities.append({
            "type": "Missing CSRF token",
            "description": "OAuth flow does not include CSRF protection",
            "severity": "Medium"
        })
    
    return vulnerabilities

def _test_basic_auth_vulnerabilities(endpoint: str) -> List[Dict]:
    vulnerabilities = []
    
    if not endpoint.startswith("https://"):
        vulnerabilities.append({
            "type": "Insecure transport",
            "description": "Basic Auth used over non-HTTPS connection",
            "severity": "High"
        })
    
    weak_creds = [("admin", "admin"), ("user", "password"), ("test", "test")]
    for username, password in weak_creds:
        response = requests.get(endpoint, auth=(username, password))
        if response.status_code == 200:
            vulnerabilities.append({
                "type": "Weak credentials",
                "description": f"Successfully authenticated with weak credentials: {username}:{password}",
                "severity": "High"
            })
            break
    
    return vulnerabilities

def safely_exploit_vulnerability(vulnerability: Dict, endpoint: str) -> Dict:
    result = {
        "vulnerability": vulnerability,
        "exploitation_successful": False,
        "details": "",
        "evidence": None
    }
    
    if vulnerability["type"] == "JWT None Algorithm":
        none_token = create_none_algorithm_token()
        if test_token(endpoint, none_token):
            result["exploitation_successful"] = True
            result["details"] = "Successfully authenticated using a JWT token with 'none' algorithm"
            result["evidence"] = none_token
    
    elif vulnerability["type"] == "Weak JWT Signature":
        weak_token = create_weak_signature_token()
        if test_token(endpoint, weak_token):
            result["exploitation_successful"] = True
            result["details"] = "Successfully authenticated using a JWT token with weak signature"
            result["evidence"] = weak_token
    
    elif vulnerability["type"] == "Insecure redirect_uri":
        insecure_redirect = f"{endpoint}?response_type=token&client_id=test&redirect_uri=http://attacker.com"
        response = requests.get(insecure_redirect, allow_redirects=False)
        if response.status_code == 302 and "http://attacker.com" in response.headers.get('Location', ''):
            result["exploitation_successful"] = True
            result["details"] = "Successfully redirected to arbitrary URI"
            result["evidence"] = response.headers.get('Location')
    
    elif vulnerability["type"] == "Weak credentials":
        username, password = vulnerability["description"].split(": ")[1].split(":")
        response = requests.get(endpoint, auth=(username, password))
        if response.status_code == 200:
            result["exploitation_successful"] = True
            result["details"] = f"Successfully authenticated with weak credentials: {username}:{password}"
            result["evidence"] = response.text[:100]  # First 100 characters of the response
    
    return result

def generate_security_report(vulnerabilities: List[Dict], exploitation_results: List[Dict]) -> str:
    try:
        report = "Security Assessment Report\n"
        report += "==========================\n\n"
        
        report += "1. Executive Summary\n"
        report += "--------------------\n"
        total_vulns = len(vulnerabilities)
        exploited_vulns = sum(1 for result in exploitation_results if result["exploitation_successful"])
        report += f"Total vulnerabilities found: {total_vulns}\n"
        report += f"Successfully exploited: {exploited_vulns}\n\n"
        
        report += "2. Detailed Findings\n"
        report += "--------------------\n"
        for vuln, exploit_result in zip(vulnerabilities, exploitation_results):
            report += f"Vulnerability: {vuln['type']}\n"
            report += f"Severity: {vuln['severity']}\n"
            report += f"Description: {vuln['description']}\n"
            report += f"Exploitation: {'Successful' if exploit_result['exploitation_successful'] else 'Unsuccessful'}\n"
            if exploit_result['exploitation_successful']:
                report += f"Exploitation Details: {exploit_result['details']}\n"
            report += "\n"
        
        report += "3. Recommendations\n"
        report += "-------------------\n"
        for vuln in vulnerabilities:
            report += f"- {vuln['type']}: "
            if vuln['type'] == "JWT None Algorithm":
                report += "Ensure that the 'none' algorithm is not accepted for JWT validation.\n"
            elif vuln['type'] == "Weak JWT Signature":
                report += "Use a strong, unique secret key for JWT signing. Consider using asymmetric algorithms like RS256.\n"
            elif vuln['type'] == "Insecure redirect_uri":
                report += "Implement a whitelist of allowed redirect URIs and validate all redirect attempts against this list.\n"
            elif vuln['type'] == "Weak credentials":
                report += "Implement strong password policies and consider using multi-factor authentication.\n"
        
        return report
    except Exception as e:
        print(f"Error generating security report: {str(e)}")
        return "Error generating security report"