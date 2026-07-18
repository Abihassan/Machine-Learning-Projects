import requests
import streamlit as st

class AlpacaPaperTrader:
    def __init__(self):
        self.key = st.secrets["ALPACA_API_KEY"]
        self.secret = st.secrets["ALPACA_SECRET_KEY"]
        self.headers = {"APCA-API-KEY-ID": self.key, "APCA-API-SECRET-KEY": self.secret}
        self.base_url = "https://paper-api.alpaca.markets/v2"

    def execute_trade(self, ticker, is_bullish, amount=1000):
        if is_bullish:
            data = {"symbol": ticker, "notional": amount, "side": "buy", "type": "market", "time_in_force": "day"}
            return requests.post(f"{self.base_url}/orders", json=data, headers=self.headers).json()
        return "Bearish signal: No buy executed."