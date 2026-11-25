from server import app

def run_in_memory_tests():
    client = app.test_client()

    # 1. Index route test
    r = client.get("/")
    print(f"GET / => Status: {r.status_code}, Length: {len(r.data)}")
    assert r.status_code == 200, f"Expected 200 but got {r.status_code}"
    assert (b"BharatSevai AI" in r.data or b"NammaSevai AI" in r.data), "Brand title missing in response"

    # 2. Health check API test
    r = client.get("/api/health")
    print(f"GET /api/health => Status: {r.status_code}, Response: {r.get_json()}")
    assert r.status_code == 200, "Health check failed"
    assert r.get_json().get("status") == "healthy"

    # 3. Schemes list API test
    r = client.get("/api/schemes")
    data = r.get_json()
    print(f"GET /api/schemes => Status: {r.status_code}, Schemes Count: {data.get('count')}")
    assert r.status_code == 200, "Schemes API failed"
    assert data.get("count") > 0, "No schemes returned"

    # 4. Schemes filter test (category)
    r = client.get("/api/schemes?category=education")
    edu_data = r.get_json()
    print(f"GET /api/schemes?category=education => Count: {edu_data.get('count')}")
    assert r.status_code == 200

    # 5. Asset serving test
    r = client.get("/assets/nammasevai_minimal.svg")
    print(f"GET /assets/nammasevai_minimal.svg => Status: {r.status_code}, Type: {r.content_type}")
    assert r.status_code == 200, "SVG logo asset failed to serve"

    # 6. Static CSS serving test
    r = client.get("/static/css/style.css")
    print(f"GET /static/css/style.css => Status: {r.status_code}, Length: {len(r.data)}")
    assert r.status_code == 200, "CSS failed to serve"
    assert b"--primary-navy" in r.data, "Design system variables missing"

    # 7. Static JS serving test
    r = client.get("/static/js/app.js")
    print(f"GET /static/js/app.js => Status: {r.status_code}, Length: {len(r.data)}")
    assert r.status_code == 200, "app.js failed to serve"

    # 8. Post new scheme API test
    new_scheme = {
        "name": "Test Citizen Scheme",
        "name_ta": "தேர்வு திட்டம்",
        "department": "Test Dept",
        "department_ta": "தேர்வு துறை",
        "category": "education",
        "benefit_amount": "₹500 / month",
        "benefit_summary": "Test monthly assistance",
        "benefit_summary_ta": "மாத உதவி",
        "official_portal": "https://tn.gov.in"
    }
    r = client.post("/api/schemes", json=new_scheme)
    print(f"POST /api/schemes => Status: {r.status_code}, New Scheme ID: {r.get_json().get('scheme', {}).get('id')}")
    assert r.status_code == 201

    print("\n==========================================")
    print("ALL IN-MEMORY FLASK & API TESTS PASSED!")
    print("==========================================")

if __name__ == "__main__":
    run_in_memory_tests()
