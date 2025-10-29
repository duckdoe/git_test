import requests
import json
import pprint

# payload = {
#     "username": "ducker",
#     "email": "fortune@mail.com",
#     "password": "fortune14",
#     "role": "",
# }

payload = {"username": "ducker", "password": "fortune@14"}

headers = {
    "Content-Type": "application/json",
    "Session-Id": "f55d2561-d78f-4aa8-b904-245156edc413|user",
}

# res = requests.post(
#     "http://127.0.0.1:5000/login", data=json.dumps(payload), headers=headers
# )
# res = requests.get("http://127.0.0.1:5000/ducker/dashboard", headers=headers)

res = requests.put(
    "http://127.0.0.1:5000/update/password", data=json.dumps(payload), headers=headers
)
pprint.pprint(res.json())
