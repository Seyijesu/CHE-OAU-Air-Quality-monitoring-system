import requests

url = "http://localhost:5000/predict_api"
r = requests.post(url, json={"PM25": 10, "PM10": 15, "NO": 2, "NO2": 3, "NOx": 3.5, "SO2": 8, "CO": 6, "ozone": 9, "benzen": 3, "toulene":5, "temparature": 30, "humidity": 15 })

print(r.json())