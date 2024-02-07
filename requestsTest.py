import requests 

x = requests.get("http://20.1.0.96:80/photoResistor")

print(x.json()["status"])