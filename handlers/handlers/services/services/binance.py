import requests

BASE_URL = "https://api.binance.com"


def get_price(symbol: str) -> str:
    """
    Отримати поточну ціну активу з Binance
    """

    try:
        url = f"{BASE_URL}/api/v3/ticker/price"

        response = requests.get(
            url,
            params={"symbol": symbol},
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        price = float(data["price"])

        return (
            f"📈 {symbol}\n\n"
            f"💰 Поточна ціна:\n"
            f"{price:,.2f} USDT"
        )

    except Exception as e:
        return (
            "❌ Не вдалося отримати дані з Binance.\n\n"
            f"Помилка:\n{e}"
        )
