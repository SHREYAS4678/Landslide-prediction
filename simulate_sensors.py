"""
Sensor simulator — posts live readings to /sensors/data every few seconds.
Usage: python scripts/simulate_sensors.py --url http://localhost:8000 --interval 5
"""
import argparse, random, time, requests, datetime

REGIONS = ["munnar","darjeeling","shimla","ooty","coorg","wayanad"]

REGION_PROFILES = {
    "munnar":     dict(rf=65, sm=88, tp=22, vb=3.8, sl=38),
    "darjeeling": dict(rf=40, sm=72, tp=18, vb=2.0, sl=35),
    "shimla":     dict(rf=25, sm=52, tp=12, vb=0.7, sl=28),
    "ooty":       dict(rf=48, sm=80, tp=16, vb=2.8, sl=33),
    "coorg":      dict(rf=35, sm=65, tp=24, vb=1.2, sl=30),
    "wayanad":    dict(rf=55, sm=78, tp=26, vb=2.5, sl=36),
}

def noisy(base, spread):
    return round(max(0, base + random.uniform(-spread, spread)), 2)

def send(url, region):
    p = REGION_PROFILES[region]
    payload = {
        "region":        region,
        "rainfall":      noisy(p["rf"], 8),
        "soil_moisture": min(100, noisy(p["sm"], 5)),
        "temperature":   noisy(p["tp"], 2),
        "vibration":     noisy(p["vb"], 0.5),
        "slope_angle":   noisy(p["sl"], 1),
    }
    try:
        r = requests.post(f"{url}/sensors/data", json=payload, timeout=5)
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{ts}] {region:12s} RF={payload['rainfall']:5.1f}  SM={payload['soil_moisture']:5.1f}  → {r.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url",      default="http://localhost:8000")
    parser.add_argument("--interval", type=float, default=5)
    args = parser.parse_args()
    print(f"Simulating sensors → {args.url}  (interval {args.interval}s)")
    while True:
        for region in REGIONS:
            send(args.url, region)
        time.sleep(args.interval)
