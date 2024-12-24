from crewai import Task
from pentov1.agents import (
    recon_agent, vuln_agent, exploit_agent, report_agent
)

def create_recon_task(target_site: str) -> Task:
    return Task(
        description=f"""
        1. Use the discover_endpoints tool to perform reconnaissance on {target_site}
        2. Identify all accessible API endpoints
        3. Document the API structure, including endpoint paths and methods
        4. Determine the authentication type (JWT, OAuth, or Basic) used by the API
        """,
        agent=recon_agent
    )

def create_vuln_assessment_task() -> Task:
    return Task(
        description=f"""
        1. Utilize the scan_vulnerability tool to analyze all discovered endpoints
        2. If JWT authentication is detected, use test_jwt_vulnerabilities for specific checks
        3. Employ test_authentication for comprehensive auth vulnerability assessment
        4. Prioritize and document all identified vulnerabilities based on severity
        """,
        agent=vuln_agent
    )

def create_exploitation_task() -> Task:
    return Task(
        description=f"""
        1. Based on the vulnerability assessment, attempt safe exploitation of identified issues
        2. Document the process and results of each exploitation attempt
        3. For successful exploits, collect and securely store evidence (e.g., token data, response headers)
        4. Ensure all exploitation attempts adhere to ethical hacking principles
        """,
        agent=exploit_agent
    )

def create_reporting_task() -> Task:
    return Task(
        description=f"""
        1. Compile a comprehensive security report including reconnaissance, vulnerability assessment, and exploitation results
        2. Provide clear, technical explanations of each vulnerability, referencing specific endpoints and auth mechanisms
        3. Include actionable remediation recommendations for each identified issue
        4. Prioritize fixes based on risk level and potential impact on the API's security posture
        """,
        agent=report_agent
    )