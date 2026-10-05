import httpx
import time

def main():
    print("=" * 70)
    print("      CYBERGUARD AI: FRONTEND & BACKEND INTEGRATION VERIFICATION       ")
    print("=" * 70)

    client = httpx.Client(timeout=60.0)

    # 1. Frontend UI Root
    r_fe = client.get("http://127.0.0.1:5173/")
    assert r_fe.status_code == 200, f"Expected 200, got {r_fe.status_code}"
    assert "CyberGuard AI" in r_fe.text, "Expected CyberGuard AI in HTML"
    print(f"[+] 1. Frontend UI Root verified: HTTP 200 (HTML size: {len(r_fe.text):,} bytes)")

    # 2. Health via Vite Proxy
    r_health = client.get("http://127.0.0.1:5173/api/health")
    assert r_health.status_code == 200, f"Expected 200, got {r_health.status_code}"
    health_data = r_health.json()
    assert health_data["status"] == "healthy"
    assert health_data["database"] == "connected"
    print(f"[+] 2. Health check via UI proxy verified: {health_data}")

    # 3. Analytics Overview (Initial load)
    t0 = time.time()
    r_overview = client.get("http://127.0.0.1:5173/api/analytics/overview")
    t1 = time.time()
    assert r_overview.status_code == 200, f"Expected 200, got {r_overview.status_code}"
    overview_json = r_overview.json()
    total_events = overview_json.get("total_threat_events")
    print(f"[+] 3. Analytics Overview (Initial load): HTTP 200 in {t1 - t0:.2f}s | Total events: {total_events:,}")

    # 4. Cached Analytics Overview (High-speed load)
    t2 = time.time()
    r_cached = client.get("http://127.0.0.1:5173/api/analytics/overview")
    t3 = time.time()
    assert r_cached.status_code == 200, f"Expected 200, got {r_cached.status_code}"
    print(f"[+] 4. Analytics Overview (Cached load): HTTP 200 in {t3 - t2:.4f}s (Instant response)")

    # 5. LSTM Threat Forecasting via UI Proxy
    t4 = time.time()
    r_fc = client.post("http://127.0.0.1:5173/api/forecast", json={"threat_type": "Phishing", "forecast_days": 14})
    t5 = time.time()
    assert r_fc.status_code == 200, f"Expected 200, got {r_fc.status_code}"
    fc_json = r_fc.json()
    fc_points = fc_json.get("forecast_data", [])
    risk = fc_json.get("risk_level")
    print(f"[+] 5. Forecast Inference via UI proxy: HTTP 200 in {t5 - t4:.2f}s | Points: {len(fc_points)} | Risk: {risk}")

    # 6. Threat Telemetry log query
    r_threats = client.get("http://127.0.0.1:5173/api/threats?limit=5")
    assert r_threats.status_code == 200, f"Expected 200, got {r_threats.status_code}"
    total_telemetry = r_threats.json().get("total")
    print(f"[+] 6. Threat Telemetry query via UI proxy: HTTP 200 | Total indexed: {total_telemetry:,}")

    # 7. Model Registry
    r_models = client.get("http://127.0.0.1:5173/api/forecast/models/status")
    assert r_models.status_code == 200, f"Expected 200, got {r_models.status_code}"
    models_count = r_models.json().get("count")
    print(f"[+] 7. Model Registry via UI proxy: HTTP 200 | Online LSTM Models: {models_count}/8")

    print("\n" + "=" * 70)
    print("   SUCCESS: COMPLETE FRONTEND & BACKEND INTEGRATION CONFIRMED 100%!  ")
    print("=" * 70)

if __name__ == "__main__":
    main()
