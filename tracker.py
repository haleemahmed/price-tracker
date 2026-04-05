import requests
from bs4 import BeautifulSoup
import os

# ========================
# CONFIG
# ========================
URL = "https://www.flipkart.com/emma-germany-black-orthopaedic-roll-pack-6-inch-queen-high-resilience-hr-foam-mattress/p/itm7c912b40797bf?pid=BEMH7JHJYZRUH4JP&lid=LSTBEMH7JHJYZRUH4JPJYYGK7&marketplace=FLIPKART&pageUID=1775356044004"  # replace with your product link
NTFY_TOPIC = "price-alerts-123"  # same as your mobile subscription

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Accept-Language": "en-IN,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

# ========================
# GET PRICE
# ========================
import time

def get_price():
    for attempt in range(3):  # retry 3 times
        try:
            print(f"Attempt {attempt + 1}...")

            response = requests.get(URL, headers=HEADERS, timeout=10)
            print("Status Code:", response.status_code)

            soup = BeautifulSoup(response.content, "html.parser")

            price = soup.select_one("div._30jeq3._16Jk6d")

            if price:
                price_text = price.text.replace("₹", "").replace(",", "").strip()
                return int(price_text)

            print("Price not found")

        except Exception as e:
            print("Error:", e)
            time.sleep(5)  # wait before retry

    return None


# ========================
# FILE STORAGE
# ========================
def get_old_price():
    if os.path.exists("price.txt"):
        with open("price.txt", "r") as f:
            return int(f.read())
    return None


def save_price(price):
    with open("price.txt", "w") as f:
        f.write(str(price))


# ========================
# NOTIFICATION
# ========================
def send_notification(message):
    url = f"https://ntfy.sh/{NTFY_TOPIC}"
    requests.post(url, data=message.encode("utf-8"))


# ========================
# MAIN LOGIC
# ========================
def main():
    current_price = get_price()

    if current_price is None:
        print("Skipping this run due to error")
        return

    old_price = get_old_price()

    print(f"Current Price: ₹{current_price}")
    print(f"Old Price: {old_price}")

    # First run
    if old_price is None:
        send_notification(f"Tracking started. Current price: ₹{current_price}")
    elif current_price < old_price:
        send_notification(f"🔥 Price Dropped!\nNow: ₹{current_price}\nBefore: ₹{old_price}\n{URL}")
    else:
        print("No price drop")

    save_price(current_price)


if __name__ == "__main__":
    main()
