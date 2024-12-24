from flask import Blueprint, render_template, request, jsonify
from pentov1.main import run_security_assessment
import json
import os

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/run_assessment', methods=['POST'])
def run_assessment():
    target_site = request.form.get('target_site')
    if not target_site:
        return jsonify({"error": "No target site provided"}), 400

    try:
        results = run_security_assessment(target_site)
        return jsonify({"message": "Assessment completed", "results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route('/get_reports')
def get_reports():
    reports_dir = "security_assessment_results"
    reports = []
    for filename in os.listdir(reports_dir):
        if filename.endswith(".json"):
            with open(os.path.join(reports_dir, filename), 'r') as f:
                report = json.load(f)
                reports.append({
                    "filename": filename,
                    "target_site": report["target_site"],
                    "assessment_date": report["assessment_date"]
                })
    return jsonify(reports)

@main.route('/get_report/<filename>')
def get_report(filename):
    file_path = os.path.join("security_assessment_results", filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "Report not found"}), 404
    
    with open(file_path, 'r') as f:
        report = json.load(f)
    return jsonify(report)