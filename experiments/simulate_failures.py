import random
import requests

URL = "http://127.0.0.1:8000/api/predict"

for _ in range(50):
    features = [random.random() for _ in range(5)]
    r = requests.post(URL, json={"features": features})

    if r.status_code != 200:
        print("ERROR:", r.status_code, r.text)
        continue

    try:
        print(r.json())
    except Exception:
        print("Invalid JSON:", r.text)
