from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas_ta as ta

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/signals")
def get_signals():
    tickers = ["AAPL", "MSFT", "TSLA", "AMZN", "NVDA", "SOFI", "LYFT", "META", "GOOGL", "NFLX"]
    signals = []

    for ticker in tickers:
        try:
            data = yf.download(ticker, period="10d", interval="1d", progress=False)
            data.dropna(inplace=True)
            if len(data) < 5:
                continue

            data["RSI"] = ta.rsi(data["Close"], length=14)
            recent_vol = data["Volume"][-5:]
            volume_peak = recent_vol.max()
            current_volume = recent_vol[-1]
            volume_drop = (volume_peak - current_volume) / volume_peak
            last_rsi = data["RSI"].iloc[-1]

            if last_rsi < 30 and volume_drop > 0.4:
                signals.append({
                    "symbol": ticker,
                    "rsi": round(last_rsi, 2),
                    "volumeDrop": round(volume_drop * 100, 1),
                    "price": round(data["Close"].iloc[-1], 2)
                })

        except Exception as e:
            continue

    return {"signals": signals}
