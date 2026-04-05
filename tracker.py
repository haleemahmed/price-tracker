import requests
from bs4 import BeautifulSoup
import os

# ========================
# CONFIG
# ========================
URL = "https://dl.flipkart.com/s/asDPw1uuuN"  # replace with your product link
NTFY_TOPIC = "price-alerts-123"  # same as your mobile subscription

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# ========================
# GET PRICE
# ========================
def get_price():
    response = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(response.content, "html.parser")

    # Amazon price selectors (multiple fallbacks)
    price = soup.select_one(".a-price-whole")

    if not price:
        print("Price not found!")
        return None

    price_text = price.text.replace(",", "").strip()
    return int(price_text)


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
