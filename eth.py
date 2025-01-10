import requests
import csv
import random  # Import random for generating wallet address placeholder
from mnemonic import Mnemonic  # Import the BIP-39 mnemonic generator

def load_word_list():
    """Fetches the word list from the provided GitHub raw URL."""
    url = "https://raw.githubusercontent.com/talhasahir9/tk/main/english.txt"
    try:
        print("Fetching word list from GitHub...")
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors
        words = response.text.splitlines()
        if len(words) < 2048:
            print("Warning: Word list contains fewer than 2048 words.")
        return words
    except requests.exceptions.RequestException as e:
        print(f"Error fetching word list from GitHub: {e}")
        return []

def generate_bip39_seed_phrase():
    """Generates a valid BIP-39 mnemonic seed phrase."""
    mnemo = Mnemonic("english")
    return mnemo.generate(strength=128)  # 128 bits = 12 words, 256 bits = 24 words

def derive_wallet_address(seed_phrase):
    """Derives wallet address from seed phrase.
    (Placeholder: Replace with an actual implementation using libraries like `bip_utils`.)
    """
    return f"0x{random.randint(10**39, 10**40 - 1):x}"

def check_wallet_balance(address, api_key):
    """Checks the balance of an Ethereum address using the Etherscan API."""
    url = f"https://api.etherscan.io/api"
    params = {
        "module": "account",
        "action": "balance",
        "address": address,
        "tag": "latest",
        "apikey": api_key
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if data["status"] == "1":
            balance_wei = int(data["result"])
            balance_eth = balance_wei / 10**18
            return balance_eth
        else:
            return 0
    except Exception as e:
        return 0

def get_token_balances(address, api_key):
    """Fetches token balances for an Ethereum address using Etherscan API."""
    url = f"https://api.etherscan.io/api"
    params = {
        "module": "account",
        "action": "tokentx",
        "address": address,
        "page": 1,
        "offset": 100,  # Retrieve 100 transactions per page
        "apikey": api_key
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if data["status"] == "1":
            tokens = {}
            for tx in data["result"]:
                token_symbol = tx["tokenSymbol"]
                token_value = float(tx["value"]) / (10 ** int(tx["tokenDecimal"]))  # Adjust for decimal places
                if token_symbol in tokens:
                    tokens[token_symbol] += token_value
                else:
                    tokens[token_symbol] = token_value
            return tokens
        else:
            return {}
    except Exception as e:
        print(f"Error fetching token balances: {e}")
        return {}

def export_wallets_to_file(wallets, filename="wallets_with_balance.csv"):
    """Exports wallets with a balance greater than 0 to a CSV file."""
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Seed Phrase", "Wallet Address", "Balance (ETH)", "Tokens"])
        writer.writerows(wallets)
    print(f"Exported wallets to {filename}")

def main():
    print("Welcome to the Wallet Balance Checker with GitHub Word List Support!")
    
    # Load word list from GitHub
    word_list = load_word_list()
    
    if not word_list:
        print("No valid word list loaded. Exiting.")
        return

    api_key = input("Enter your Etherscan API key: ").strip()
    num_wallets = int(input("Enter the number of wallets to generate and check: ").strip())
    
    wallets_with_balance = []
    
    for i in range(num_wallets):
        print(f"\nProcessing wallet {i + 1} of {num_wallets}...")
        
        # Generate a valid BIP-39 seed phrase
        seed_phrase = generate_bip39_seed_phrase()
        print(f"Generated Seed Phrase: {seed_phrase}")
        
        # Derive wallet address (replace with actual derivation in production)
        wallet_address = derive_wallet_address(seed_phrase)
        print(f"Derived Wallet Address: {wallet_address}")
        
        # Check balance
        balance = check_wallet_balance(wallet_address, api_key)
        print(f"Wallet Balance: {balance} ETH")
        
        # Fetch token balances
        token_balances = get_token_balances(wallet_address, api_key)
        print("Tokens in wallet:")
        if token_balances:
            for token, token_balance in token_balances.items():
                print(f"{token}: {token_balance} tokens")
        else:
            print("No tokens found.")
        
        # Store wallets with balance > 0
        if balance > 0 or token_balances:
            wallets_with_balance.append((seed_phrase, wallet_address, balance, token_balances))
            print("Wallet has balance or tokens. Added to the export list.")
        else:
            print("Wallet has no balance and no tokens.")
    
    # Export results to a file
    if wallets_with_balance:
        export_wallets_to_file(wallets_with_balance)
    else:
        print("No wallets with balance greater than 0 or tokens were found.")

if __name__ == "__main__":
    main()