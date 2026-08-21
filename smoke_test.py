import os, json, logging
os.environ["JWT_SECRET_KEY"] = "dev-secret-key-change-in-production"
os.environ["API_USERNAME"] = "admin"
os.environ["API_PASSWORD"] = "admin123"
os.environ["WEBHOOK_URL"] = ""
logging.disable(logging.CRITICAL)

from app import create_app
app = create_app()

with app.test_client() as c:
    r = c.get("/health")
    d = json.loads(r.get_data())
    print(f"1.  HEALTH           {r.status_code}  status={d['status']}  coingecko={d['coingecko']['status']}")

    r = c.post("/auth/login", json={"username": "admin", "password": "admin123"})
    d = json.loads(r.get_data())
    token = d["access_token"]
    h = {"Authorization": "Bearer " + token}
    print(f"2.  LOGIN            {r.status_code}")

    r = c.get("/coins?per_page=3", headers=h)
    d = json.loads(r.get_data())
    print(f"3.  GET /coins       {r.status_code}  total={d['pagination']['total_items']}  first={d['data'][0]['coin_id']}")

    r = c.get("/categories?per_page=3", headers=h)
    d = json.loads(r.get_data())
    print(f"4.  GET /categories  {r.status_code}  total={d['pagination']['total_items']}  first={d['data'][0]['category_id']}")

    r = c.get("/market?coin_id=bitcoin&per_page=1", headers=h)
    d = json.loads(r.get_data())
    print(f"5.  GET /market      {r.status_code}  bitcoin_cad={d['data'][0]['current_price']}")

    r = c.get("/market", headers=h)
    d = json.loads(r.get_data())
    print(f"6.  MARKET no params {r.status_code}  error={d['error']}")

    r = c.get("/market?coin_id=fakecoin999xyz", headers=h)
    d = json.loads(r.get_data())
    print(f"7.  MARKET fake coin {r.status_code}  error={d['error']}")

    r = c.get("/coins")
    d = json.loads(r.get_data())
    print(f"8.  NO TOKEN         {r.status_code}  error={d['error']}")

    r = c.post("/auth/login", json={"username": "wrong", "password": "bad"})
    d = json.loads(r.get_data())
    print(f"9.  BAD CREDS        {r.status_code}  error={d['error']}")

    r = c.get("/apidocs/")
    print(f"10. SWAGGER          {r.status_code}  bytes={len(r.get_data())}")
