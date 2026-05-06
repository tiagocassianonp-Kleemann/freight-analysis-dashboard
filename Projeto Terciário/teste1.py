import requests

API_KEY = "SUA_API_KEY"
url = f"https://api.tradingeconomics.com/markets/commodities?c={API_KEY}"

r = requests.get(url)

print(r.status_code)
print(r.text[:500])