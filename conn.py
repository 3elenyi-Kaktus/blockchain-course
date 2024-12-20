

from web3 import Web3

# Initialize endpoint URL
node_url = "https://sepolia.infura.io/v3/de887b634e97405693e522e0dec6d999"

# Create the node connection
web3 = Web3(Web3.HTTPProvider(node_url))

if web3.is_connected():
    print("-" * 50)
    print("Connection Successful")
    print("-" * 50)
else:
    print("Connection Failed")

# Initialize the address calling the functions/signing transactions
caller = "YOUR_ADDRESS"
private_key = "PRIVATE_KEY"  # To sign the transaction

# Initialize address nonce
nonce = web3.eth.get_transaction_count(caller)

# Initialize contract ABI and address
abi = '[{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"balanceLeft","type":"uint256"}],"name":"balance","type":"event"},{"inputs":[{"internalType":"address payable","name":"recipient","type":"address"}],"name":"destroy","outputs":[],"stateMutability":"nonpayable","type":"function"}'

contract_address = "CONTRACT_ADDRESS"

# Create smart contract instance
contract = web3.eth.contract(address=contract_address, abi=abi)


# initialize the chain id, we need it to build the transaction for replay protection
Chain_id = web3.eth.chain_id

# Call your function
call_function = contract.functions.testFunc().buildTransaction({"chainId": Chain_id, "from": caller, "nonce": nonce})

# Sign transaction
signed_tx = web3.eth.account.sign_transaction(call_function, private_key=private_key)

# Send transaction
send_tx = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

# Wait for transaction receipt
tx_receipt = web3.eth.wait_for_transaction_receipt(send_tx)
# print(tx_receipt) # Optional
