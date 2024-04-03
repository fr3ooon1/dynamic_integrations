import json
import requests



data = {
					"staff_ID": 116 ,
					"elemVal" :9000 ,
					"actionUser": "4",
					"cmp_code": 1,
					"br_code": 1,
					"openMonth_ser": 1

				}
body = [data]
token = "c2D2xk95U8QwPdvqH7ktA0JK2Zcxi-4XYz5ZyhbYG0RjZkRYMZZCThZ1-DkWYfUgiM3_fft9EXCzBFSYGu54lUwwia5U1mNyf6tZyR9B2pplpU3nVy16lfU9UB7AgDAv1L5n_TS7qKp9BKIDBhmN5TAyhTn9GwDfEsKjyNG8PoT6Ct1NWefDO8DhU3DrskEqCbPZq8I3rsiC4MDE42BRpM7BKDu9oTEMV94AEhv89Qo6ZvKhEG6NYMD5NCmi4x7dBMzF7rREPImpBdm7_bWk_DBk93bcUEntEOqxYcgg3LbcagGuRoKJzmq8rOrf-W5A8G8c2S5iJ3grhRtx0xVenaQVvc3BKxtCqomF5uB6C6PQ_n2uyfH45P5VN5rZ-ZyZfAeJHQZfbux04l1iB-6YQb2yDWgNHT5MDM0dN65WlJeP5jJ647hsOfVs8_9pROT5d1q9SzbGmhTpCtckx8tk5GAQ0CjVrHZkpbFhndR5RCn_vFY3iEm7FmpPZA3i29PE"
url = "http://92.205.106.50:65/"
end_point = url+ "api/ERPAddPayval"
header = {
			"Authorization" : f"Bearer {token}" ,
			"Content-Type" : "application/json"
		}


req = requests.post(end_point, headers=header ,data=json.dumps(body))
print("OKKKKKKKKK")
print(req.json())
print(req.status_code)