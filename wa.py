import random
import requests
import csv

def load_word_list(file_path_or_url):
    """Loads a word list from a local file or GitHub raw URL."""
    if file_path_or_url.startswith("http"):  # If it's a URL
        try:
            print("Fetching word list from URL...")
            response = requests.get(file_path_or_url)
            response.raise_for_status()  # Check for HTTP errors
            words = response.text.splitlines()
            if len(words) < 2048:
                print("Warning: Word list contains fewer than 2048 words.")
            return words
        except requests.exceptions.RequestException as e:
            print(f"Error fetching word list from URL: {e}")
            return []
    else:  # If it's a local file
        try:
            with open(file_path_or_url, "r") as file:
                words = [line.strip() for line in file.readlines()]
            if len(words) < 2048:
                print("Warning: Word list contains fewer than 2048 words.")
            return words
        except FileNotFoundError:
            print(f"Error: File '{file_path_or_url}' not found.")
            return []
        except Exception as e:
            print(f"Error reading file: {e}")
            return []

def generate_seed_phrase(word_list):
    """Generates a random 12-word seed phrase from the provided word list."""
    if not word_list:
        raise ValueError("Word list is empty. Cannot generate seed phrase.")
    return " ".join(random.choices(word_list, k=12))

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

def export_wallets_to_file(wallets, filename="wallets_with_balance.csv"):
    """Exports wallets with a balance greater than 0 to a CSV file."""
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Seed Phrase", "Wallet Address", "Balance (ETH)"])
        writer.writerows(wallets)
    print(f"Exported wallets to {filename}")

def main():
    print("Welcome to the Wallet Balance Checker with GitHub Word List Support!")
    
    # GitHub raw URL for the word list
    word_list_url = "https://raw.githubusercontent.com/talhasahir9/tk/main/english.txt"
    word_list = load_word_list(word_list_url)
    
    if not word_list:
        print("No valid word list loaded. Exiting.")
        return

    api_key = input("Enter your Etherscan API key: ").strip()
    num_wallets = int(input("Enter the number of wallets to generate and check: ").strip())
    
    wallets_with_balance = []
    
    for i in range(num_wallets):
        print(f"\nProcessing wallet {i + 1} of {num_wallets}...")
        
        # Generate a random seed phrase
        seed_phrase = generate_seed_phrase(word_list)
        print(f"Generated Seed Phrase: {seed_phrase}")
        
        # Derive wallet address (replace with actual derivation in production)
        wallet_address = derive_wallet_address(seed_phrase)
        print(f"Derived Wallet Address: {wallet_address}")
        
        # Check balance
        balance = check_wallet_balance(wallet_address, api_key)
        print(f"Wallet Balance: {balance} ETH")
        
        # Store wallets with balance > 0
        if balance > 0:
            wallets_with_balance.append((seed_phrase, wallet_address, balance))
            print("Wallet has balance. Added to the export list.")
        else:
            print("Wallet has no balance.")
    
    # Export results to a file
    if wallets_with_balance:
        export_wallets_to_file(wallets_with_balance)
    else:
        print("No wallets with balance greater than 0 were found.")

if __name__ == "__main__":
    main()