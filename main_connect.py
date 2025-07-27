from kiteconnect import KiteConnect
import google.generativeai as genai
import pandas as pd
import traceback
import os

# # === CONFIGURATION ===
# ZERODHA_API_KEY = os.getenv('ZERODHA_API_KEY', '')
# ZERODHA_ACCESS_TOKEN = os.getenv('ZERODHA_ACCESS_TOKEN', '')
# GEMINI_API_KEY =os.getenv('GEMINI_API_KEY', '')

# # === Initialize Kite ===
# kite = KiteConnect(api_key=ZERODHA_API_KEY)
# kite.set_access_token(ZERODHA_ACCESS_TOKEN)

# # === Initialize Gemini ===
# genai.configure(api_key=GEMINI_API_KEY)
# model = genai.GenerativeModel('gemini-1.5-flash')

# def fetch_portfolio():
#     try:
#         holdings = kite.holdings()
#         positions = kite.positions()['net']
#         print("✅ Portfolio data fetched successfully.")
#         return holdings, positions
#     except Exception as e:
#         print("❌ Failed to fetch Zerodha portfolio.")
#         print(traceback.format_exc())
#         return [], []

# def filter_data(data):
#     try:
#         df = pd.DataFrame(data)
#         if df.empty:
#             print("⚠️ Empty portfolio data.")
#             return df
#         df = df[['tradingsymbol', 'quantity', 'average_price', 'last_price', 'pnl']].copy()
#         df.dropna(inplace=True)
#         df = df[df['quantity'] > 0]  # filter out zero holdings
#         return df
#     except Exception as e:
#         print("❌ Error during filtering.")
#         print(traceback.format_exc())
#         return pd.DataFrame()

# def analyze_with_gemini(df, title="Zerodha Portfolio Analysis"):
#     try:
#         prompt = f"""
#         I have the following stock portfolio from Zerodha:

#         {df.to_markdown(index=False)}

#         Please give a summary analysis. Include:
#         - Performance overview
#         - Top 3 profitable stocks
#         - Top 3 loss-making stocks
#         - Any notable patterns or risks
#         """
#         response = model.generate_content(prompt)
#         print("✅ Gemini Flash Analysis:\n")
#         print(response.text)
#     except Exception as e:
#         print("❌ Gemini Flash analysis failed.")
#         print(traceback.format_exc())

# if __name__ == "__main__":
#     holdings, positions = fetch_portfolio()

#     if holdings:
#         df_holdings = filter_data(holdings)
#         if not df_holdings.empty:
#             analyze_with_gemini(df_holdings, "Holdings Analysis")

#     if positions:
#         df_positions = filter_data(positions)
#         if not df_positions.empty:
#             analyze_with_gemini(df_positions, "Positions Analysis")


import requests
import hashlib

api_key = "j0irwpqbp7psn0nw"
api_secret = "0rlo7yncj2vzp722yoj2r73widtee3lr"
request_token = "y7Q3vuIZlXGNfebqgdnTujX3pKYEIxtN"

# Generate checksum
checksum = hashlib.sha256((api_key + request_token + api_secret).encode()).hexdigest()

url = "https://api.kite.trade/session/token"
data = {
    "api_key": api_key,
    "request_token": request_token,
    "checksum": checksum
}

response = requests.post(url, data=data)
print(response.json())