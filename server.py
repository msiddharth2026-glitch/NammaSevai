"""
NammaSevai AI - Full-Stack Application Server
Serves the responsive GovTech Web Application and provides REST API endpoints.
Ready for PostgreSQL and FastAPI deployment.
"""

import os
import json
from flask import Flask, send_from_directory, jsonify, request, render_template

app = Flask(__name__, static_folder='static', template_folder='templates')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEMES_FILE = os.path.join(BASE_DIR, 'data_schemes.json')

# Helper: load or initialize schemes database
def get_schemes():
    if os.path.exists(SCHEMES_FILE):
        try:
            with open(SCHEMES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading schemes file: {e}")
    
    # Load fallback from JS data or default list
    # We load initial schemes
    return [
        {
            "id": "pudhumai-penn",
            "name": "Moovalur Ramamirtham Ammaiyar Higher Education Assurance Scheme (Pudhumai Penn)",
            "name_ta": "மூவலூர் ராமாமிர்தம் அம்மையார் புதுமைப் பெண் திட்டம்",
            "department": "Social Welfare and Women Empowerment Department",
            "department_ta": "சமூக நலன் மற்றும் மகளிர் உரிமைத் துறை",
            "category": "education",
            "beneficiary_type": "Girl students joining undergraduate/diploma courses",
            "beneficiary_type_ta": "அரசுப் பள்ளியில் படித்து கல்லூரி சேரும் மாணவிகள்",
            "benefit_summary": "₹1,000 per month deposited directly into bank account until graduation",
            "benefit_summary_ta": "கல்லூரி படிப்பு முடியும் வரை மாதம் ₹1,000 நேரடி வங்கி வரவு",
            "benefit_amount": "₹1,000 / month",
            "description": "Financial assistance to encourage female students who studied from 6th to 12th standard in Tamil Nadu government schools to pursue higher education.",
            "description_ta": "தமிழ்நாடு அரசுப் பள்ளிகளில் 6 முதல் 12-ம் வகுப்பு வரை பயின்று உயர்கல்வியில் சேரும் மாணவிகளுக்கு மாதம் ₹1,000 உதவித்தொகை வழங்கும் திட்டம்.",
            "eligibility_criteria": [
                "Must have studied Classes 6 to 12 in Tamil Nadu Government schools",
                "Must be enrolled in recognized higher education (UG degree, diploma, ITI)",
                "Student must have a valid individual bank account seeded with Aadhaar"
            ],
            "required_documents": [
                { "name": "Aadhaar Card", "name_ta": "ஆதார் அட்டை", "mandatory": True },
                { "name": "10th & 12th Marksheet", "name_ta": "10 மற்றும் 12-ம் வகுப்பு மதிப்பெண் சான்றிதழ்", "mandatory": True },
                { "name": "Govt School Study Bonafide", "name_ta": "அரசுப் பள்ளி பயின்றதற்கான சான்றிதழ்", "mandatory": True },
                { "name": "Bank Passbook with IFSC", "name_ta": "வங்கி சேமிப்புக் கணக்கு புத்தகம்", "mandatory": True }
            ],
            "official_portal": "https://www.penkalvi.tn.gov.in",
            "official_source": "Tamil Nadu Social Welfare Dept (Sample Demo Entry)",
            "source_verification": "verified",
            "verified_date": "2026-10-20"
        },
        {
            "id": "kmut-magalir",
            "name": "Kalaignar Magalir Urimai Thittam (KMUT)",
            "name_ta": "கலைஞர் மகளிர் உரிமைத் திட்டம்",
            "department": "Special Programme Implementation & Revenue Department",
            "department_ta": "சிறப்புத் திட்டச் செயலாக்கம் மற்றும் வருவாய்த் துறை",
            "category": "women",
            "beneficiary_type": "Eligible female heads of family in Tamil Nadu",
            "beneficiary_type_ta": "குடும்பத் தலைவிகள் (பெண்கள்)",
            "benefit_summary": "₹1,000 monthly basic income guarantee directly credited to bank account",
            "benefit_summary_ta": "குடும்பத் தலைவிகளுக்கு மாதம் ₹1,000 உரிமைத் தொகை வங்கி வரவு",
            "benefit_amount": "₹1,000 / month",
            "description": "A universal basic income program providing economic independence to women heads of family across Tamil Nadu.",
            "description_ta": "குடும்பத் தலைவிகளின் பொருளாதார சுதந்திரத்திற்காக மாதம் ₹1,000 வழங்கும் திட்டம்.",
            "eligibility_criteria": [
                "Female head of family named in the Smart Family Ration Card",
                "Family annual income should be less than ₹2.5 Lakhs",
                "Applicant age should be 21 years or older"
            ],
            "required_documents": [
                { "name": "Smart Ration Card", "name_ta": "ஸ்மார்ட் குடும்ப அட்டை", "mandatory": True },
                { "name": "Aadhaar Card", "name_ta": "ஆதார் அட்டை", "mandatory": True },
                { "name": "Electricity Bill", "name_ta": "மின் நுகர்வோர் எண்", "mandatory": True },
                { "name": "Bank Passbook", "name_ta": "வங்கி புத்தகம்", "mandatory": True }
            ],
            "official_portal": "https://kmut.tn.gov.in",
            "official_source": "Tamil Nadu Revenue Department (Sample Demo Entry)",
            "source_verification": "verified",
            "verified_date": "2026-11-01"
        }
    ]

def save_schemes(schemes):
    with open(SCHEMES_FILE, 'w', encoding='utf-8') as f:
        json.dump(schemes, f, indent=2, ensure_ascii=False)

# Root route serves index.html
@app.route('/')
def index():
    return render_template('index.html')

# Static assets serving
@app.route('/assets/<path:filename>')
def serve_assets(filename):
    assets_dir = os.path.join(BASE_DIR, 'assets')
    return send_from_directory(assets_dir, filename)

# REST API Endpoints
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "NammaSevai AI Core API",
        "version": "1.0.0",
        "database": "Ready for PostgreSQL integration"
    })

@app.route('/api/schemes', methods=['GET'])
def list_schemes():
    schemes = get_schemes()
    category = request.args.get('category')
    search = request.args.get('search', '').lower()

    filtered = schemes
    if category and category != 'all':
        filtered = [s for s in filtered if s.get('category') == category]
    if search:
        filtered = [
            s for s in filtered
            if search in (s.get('name', '') + ' ' + s.get('name_ta', '') + ' ' + s.get('department', '')).lower()
        ]

    return jsonify({"schemes": filtered, "count": len(filtered)})

@app.route('/api/schemes/<scheme_id>', methods=['GET'])
def get_scheme(scheme_id):
    schemes = get_schemes()
    scheme = next((s for s in schemes if s.get('id') == scheme_id), None)
    if not scheme:
        return jsonify({"error": "Scheme not found"}), 404
    return jsonify(scheme)

@app.route('/api/schemes', methods=['POST'])
def create_scheme():
    data = request.get_json() or {}
    if not data.get('name'):
        return jsonify({"error": "Name is required"}), 400

    schemes = get_schemes()
    new_id = data.get('id') or f"scheme-{len(schemes) + 1}"
    data['id'] = new_id
    schemes.append(data)
    save_schemes(schemes)
    return jsonify({"message": "Scheme created successfully", "scheme": data}), 201

@app.route('/api/schemes/<scheme_id>', methods=['PUT'])
def update_scheme(scheme_id):
    data = request.get_json() or {}
    schemes = get_schemes()
    index = next((i for i, s in enumerate(schemes) if s.get('id') == scheme_id), None)
    if index is None:
        return jsonify({"error": "Scheme not found"}), 404

    schemes[index].update(data)
    save_schemes(schemes)
    return jsonify({"message": "Scheme updated", "scheme": schemes[index]})

@app.route('/api/schemes/<scheme_id>', methods=['DELETE'])
def delete_scheme(scheme_id):
    schemes = get_schemes()
    schemes = [s for s in schemes if s.get('id') != scheme_id]
    save_schemes(schemes)
    return jsonify({"message": "Scheme deleted successfully"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting NammaSevai AI server on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
