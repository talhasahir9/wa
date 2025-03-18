import time
import logging
import requests
from playwright.sync_api import sync_playwright
from mnemonic import Mnemonic

# Configuration
SOLFLARE_URL = "https://solflare.com/onboard"
MAX_RETRIES = 3
CHECK_INTERVAL = 600  # 10 minutes

# Telegram Configuration
TELEGRAM_BOT_TOKEN = "7545425035:AAHK2NRv_U9WwN_UgCCFcEk2bTwELsYTTec"
TELEGRAM_CHAT_ID = "1073449470"

# Logging setup
logging.basicConfig(filename="minting_log.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

def send_telegram(message):
    """Send Telegram alerts."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload)
        print("✅ Telegram notification sent!")
    except Exception as e:
        print(f"❌ Telegram sending failed: {e}")

def generate_wallets(count=10):
    """Generate seed phrases and save them to a file."""
    mnemo = Mnemonic("english")
    with open("wallets.txt", "w") as wallet_file:
        for _ in range(count):
            seed_phrase = mnemo.generate(strength=256)
            wallet_file.write(f"{seed_phrase}\n")
    print(f"✅ {count} wallets generated and saved to wallets.txt")

def load_wallets(filename="wallets.txt"):
    """Load seed phrases from file."""
    with open(filename, "r") as file:
        return [line.strip() for line in file.readlines()]

def import_seed_and_mint(page, seed_phrase):
    """Automate seed import and minting on Solflare."""
    page.goto(SOLFLARE_URL)
    time.sleep(3)

    # Click "Import Wallet"
    page.locator("text=Import Wallet").click()
    time.sleep(2)

    # Enter seed phrase
    page.locator("textarea").fill(seed_phrase)
    time.sleep(2)

    # Click Continue
    page.locator("text=Continue").click()
    time.sleep(5)

    # Check if the minting button exists
    mint_button = page.locator("text=Mint")
    if mint_button.is_visible():
        mint_button.click()
        time.sleep(5)
        return True
    return False

def retry_minting(browser, seed_phrase):
    """Retry minting if it fails."""
    for attempt in range(MAX_RETRIES):
        logging.info(f"Attempt {attempt + 1} for seed phrase")
        
        page = browser.new_page()
        success = import_seed_and_mint(page, seed_phrase)
        page.close()

        if success:
            msg = f"✅ Minting successful\nSeed Phrase: {seed_phrase}"
            logging.info(msg)
            send_telegram(msg)
            print(msg)
            return True
        else:
            msg = f"⚠️ Minting failed, retrying..."
            logging.warning(msg)
            print(msg)
            time.sleep(10)

    msg = f"❌ Minting failed after {MAX_RETRIES} retries\nSeed Phrase: {seed_phrase}"
    logging.error(msg)
    send_telegram(msg)
    print(msg)
    return False

def main():
    """Run the automation continuously."""
    generate_wallets(10)  # Generate 10 wallets (Modify count as needed)
    wallets = load_wallets()

    while True:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)  # Runs in headless mode for UserLAnd

            for seed in wallets:
                logging.info(f"Importing seed and minting: {seed}")
                retry_minting(browser, seed)

            browser.close()

        logging.info("🔄 Sleeping before next minting attempt...")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()