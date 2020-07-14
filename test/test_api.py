import requests

url = "https://bn95qvy10m.execute-api.us-east-2.amazonaws.com/prod"
input_data = {}
r = requests.post(url, json=input_data)
