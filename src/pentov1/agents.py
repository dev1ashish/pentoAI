from langchain.agents import Tool
import os
from crewai import Agent
from langchain_mistralai import ChatMistralAI
from pentov1.tools import (
    discover_endpoints,
    scan_vulnerability,
    test_authentication,
    test_jwt_vulnerabilities,
    safely_exploit_vulnerability,
    generate_security_report
)

api_key = os.getenv("MISTRAL_API_KEY")
if not api_key:
    raise ValueError("MISTRAL_API_KEY environment variable is not set")

print(f"API Key: {api_key[:5]}...{api_key[-5:]}")  # Print first and last 5 characters

mistral = ChatMistralAI(
    model="mistral-medium",
    mistral_api_key=api_key,
    temperature=0.1
)

# Initialize tools

discover_endpoints_tool = Tool(
    name="Discover Endpoints",
    func=discover_endpoints,
    description="Discovers API endpoints for a given base URL"
)
scan_vulnerability_tool = Tool(
    name="Scan Vulnerability",
    func=scan_vulnerability,
    description="Scans for vulnerabilities in a given endpoint"
)
test_authentication_tool = Tool(
    name="Test Authentication",
    func=test_authentication,
    description="Tests authentication for a given endpoint and auth type"
)
test_jwt_vulnerabilities_tool = Tool(
    name="Test JWT Vulnerabilities",
    func=test_jwt_vulnerabilities,
    description="Tests for JWT-specific vulnerabilities"
)
safely_exploit_vulnerability_tool = Tool(
    name="Safely Exploit Vulnerability",
    func=safely_exploit_vulnerability,
    description="Safely attempts to exploit a given vulnerability"
)
generate_security_report_tool = Tool(
    name="Generate Security Report",
    func=generate_security_report,
    description="Generates a comprehensive security report"
)


recon_agent = Agent(
    role="API Reconnaissance Specialist",
    goal="Discover all API endpoints and understand the API structure",
    backstory="""You are an expert in API reconnaissance with deep knowledge
    of API security best practices. You use advanced techniques to map out
    API structures and identify potential security weaknesses.""",
    tools=[discover_endpoints_tool],
    llm=mistral,
    verbose=True
)

vuln_agent = Agent(
    role="Vulnerability Assessor",
    goal="Identify and analyze security vulnerabilities in API endpoints",
    backstory="""You are a skilled security analyst who specializes in 
    identifying API vulnerabilities. You understand complex API security
    issues and can explain them clearly.""",
    tools=[
        test_authentication_tool,
        scan_vulnerability_tool,
        test_jwt_vulnerabilities_tool
    ],
    llm=mistral,
    verbose=True
)

exploit_agent = Agent(
    role="Ethical Exploitation Specialist",
    goal="Safely verify identified vulnerabilities",
    backstory="""You are an ethical hacker who specializes in safely 
    exploiting vulnerabilities to prove their existence. You always
    ensure that your exploitation attempts are controlled and safe.""",
    tools=[safely_exploit_vulnerability_tool],
    llm=mistral,
    verbose=True
)

report_agent = Agent(
    role="Security Report Specialist",
    goal="Create comprehensive, actionable security reports",
    backstory="""You are an expert in creating detailed, actionable 
    security reports. You can explain complex vulnerabilities in a
    way that both technical and non-technical stakeholders can understand.""",
    tools=[generate_security_report_tool],
    llm=mistral,
    verbose=True
)