import requests
import csv
from mnemonic import Mnemonic
from Crypto.Hash import SHA3_256

# Function to generate a valid BIP-39 mnemonic seed phrase
def generate_bip39_seed_phrase():
    mnemo = Mnemonic("english")
    return mnemo.generate(strength=128)  # 128 bits = 12 words

# Function to derive wallet address (Using SUI-specific address generation)
def derive_wallet_address(seed_phrase):
    """Derives a SUI wallet address from the seed phrase."""
    # Simulating the generation of the address using SHA3_256 from pycryptodome
    keccak_hash = SHA3_256.new()
    keccak_hash.update(seed_phrase.encode('utf-8'))
    return "0x" + keccak_hash.hexdigest()[:40]  # Fake SUI address for simulation

# Function to check wallet balance using the Sui RPC
def check_wallet_balance(address, rpc_url="https://fullnode.devnet.sui.io/"):
    """Checks the balance of a SUI wallet using the RPC."""
    try:
        response = requests.post(
            rpc_url,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "sui_getBalance",
                "params": {"owner": address},
            },
        )
        response.raise_for_status()
        result = response.json().get("result", {})
        # Return the balance in SUI (no decimal places, just the total)
        return result.get("totalBalance", 0) / 10**9  # Assume response balance is in MIST
    except Exception as e:
        print(f"Error checking balance for {address}: {e}")
        return 0

# Function to export wallet details with balance > 0 to a CSV file
def export_wallets_to_file(wallets, filename="wallets_with_balance.csv"):
    """Exports wallets with a balance greater than 0 to a CSV file."""
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Seed Phrase", "Wallet Address", "Balance (SUI)"])
        writer.writerows(wallets)
    print(f"Exported wallets to {filename}")

# Main execution function
def main():
    print("Welcome to the SUI Wallet Balance Checker!")
    
    num_wallets = int(input("Enter the number of wallets to generate and check: ").strip())
    
    wallets_with_balance = []
    
    for i in range(num_wallets):
        print(f"\nProcessing wallet {i + 1} of {num_wallets}...")
        
        # Generate a valid BIP-39 seed phrase
        seed_phrase = generate_bip39_seed_phrase()
        print(f"Generated Seed Phrase: {seed_phrase}")
        
        # Derive wallet address
        wallet_address = derive_wallet_address(seed_phrase)
        print(f"Derived Wallet Address: {wallet_address}")
        
        # Check balance
        balance = check_wallet_balance(wallet_address)
        print(f"Wallet Balance: {balance} SUI")
        
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