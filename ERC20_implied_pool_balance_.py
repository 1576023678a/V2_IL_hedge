from web3 import Web3
import ccxt

# Alchemy API endpoint
ALCHEMY_API_KEY = ''
alchemy_url = f'https://eth-mainnet.alchemyapi.io/v2/{ALCHEMY_API_KEY}'

uniswap_v2_pool_address = '0x3c8AD34155B83ddB7f43119A19503d34Ed2B5c7a'
user_address = '0x34fda56b5c9aa52df9fa51b01666683b7b1434d6'

mvl_token_address = '0xA849EaaE994fb86Afa73382e9Bd88c2B6b18Dc71'
weth_token_address = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'

uniswap_v2_pool_abi = [
    {
        "inputs": [],
        "name": "getReserves",
        "outputs": [
            {"internalType": "uint112", "name": "_reserve0", "type": "uint112"},
            {"internalType": "uint112", "name": "_reserve1", "type": "uint112"},
            {"internalType": "uint32", "name": "_blockTimestampLast", "type": "uint32"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

erc20_abi = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
]


def get_user_lp_balance(address):
    # Connect to Ethereum node via Alchemy API
    web3 = Web3(Web3.HTTPProvider(alchemy_url))

    # Convert address to checksum address
    checksum_address = web3.to_checksum_address(address)

    # Instantiate Uniswap V2 pool contract
    uniswap_v2_pool_contract = web3.eth.contract(address=uniswap_v2_pool_address, abi=uniswap_v2_pool_abi)

    # Call balanceOf() function of the contract
    balance = uniswap_v2_pool_contract.functions.balanceOf(checksum_address).call()

    return balance


def get_total_lp_supply():
    # Connect to Ethereum node via Alchemy API
    web3 = Web3(Web3.HTTPProvider(alchemy_url))

    # Instantiate Uniswap V2 pool contract
    uniswap_v2_pool_contract = web3.eth.contract(address=uniswap_v2_pool_address, abi=uniswap_v2_pool_abi)

    # Call totalSupply() function of the contract
    total_supply = uniswap_v2_pool_contract.functions.totalSupply().call()

    return total_supply


def get_pool_reserves():
    # Connect to Ethereum node via Alchemy API
    web3 = Web3(Web3.HTTPProvider(alchemy_url))

    # Instantiate Uniswap V2 pool contract
    uniswap_v2_pool_contract = web3.eth.contract(address=uniswap_v2_pool_address, abi=uniswap_v2_pool_abi)

    # Call getReserves() function of the contract
    reserves = uniswap_v2_pool_contract.functions.getReserves().call()

    return reserves


def get_mid_price(symbol):
    # Initialize Upbit exchange
    upbit = ccxt.upbit()

    # Fetch order book for the symbol
    order_book = upbit.fetch_order_book(symbol)

    # Calculate mid price
    bids = order_book['bids'][0][0] if len(order_book['bids']) > 0 else None
    asks = order_book['asks'][0][0] if len(order_book['asks']) > 0 else None

    if bids and asks:
        mid_price = (bids + asks) / 2
        return mid_price
    else:
        return None


def get_token_balance(token_address, pool_address):
    # Connect to Ethereum node via Alchemy API
    web3 = Web3(Web3.HTTPProvider(alchemy_url))

    # Instantiate token contract
    token_contract = web3.eth.contract(address=token_address, abi=erc20_abi)

    # Get balance of the pool address
    balance = token_contract.functions.balanceOf(pool_address).call()

    return balance


if __name__ == "__main__":
    user_lp_balance = get_user_lp_balance(user_address)
    total_lp_supply = get_total_lp_supply()
    reserves = get_pool_reserves()

    # Assuming both tokens have 18 decimals
    mvl_reserve = reserves[0] / (10 ** 18)
    weth_reserve = reserves[1] / (10 ** 18)

    user_share = user_lp_balance / total_lp_supply

    user_mvl = mvl_reserve * user_share
    user_weth = weth_reserve * user_share

    # Get total MVL and WETH balance in the pool
    total_mvl_balance = get_token_balance(mvl_token_address, uniswap_v2_pool_address) / (10 ** 18)
    total_weth_balance = get_token_balance(weth_token_address, uniswap_v2_pool_address) / (10 ** 18)

    # Calculate L value
    L_value = (total_mvl_balance * total_weth_balance) ** 0.5

    print(f"Total MVL Balance in Pool: {total_mvl_balance}")
    print(f"Total WETH Balance in Pool: {total_weth_balance}")

    print(f"User's LP Balance: {user_lp_balance / (10 ** 18)}")
    print(f"Total LP Supply: {total_lp_supply / (10 ** 18)}")
    print(f"User's MVL: {user_mvl}")
    print(f"User's WETH: {user_weth}")

    # Symbol for ETH/KRW pair
    eth_krw_symbol = 'ETH/KRW'
    # Symbol for MVL/KRW pair
    mvl_krw_symbol = 'MVL/KRW'

    # Get mid prices for ETH/KRW and MVL/KRW pairs
    eth_krw_mid_price = get_mid_price(eth_krw_symbol)
    mvl_krw_mid_price = get_mid_price(mvl_krw_symbol)

    print(f"Mid Price for {eth_krw_symbol}: {eth_krw_mid_price}")
    print(f"Mid Price for {mvl_krw_symbol}: {mvl_krw_mid_price}")

    # Calculate p value
    p_value = (eth_krw_mid_price / mvl_krw_mid_price) ** 0.5
    print(f"Calculated p value: {p_value}")

    print(f"Calculated L value: {L_value}")

    # Calculate implied pool balances
    mvl_implied_pool_balance = p_value * L_value
    eth_implied_pool_balance = L_value / p_value

    print(f"MVL Implied Pool Balance: {mvl_implied_pool_balance}")
    print(f"ETH Implied Pool Balance: {eth_implied_pool_balance}")

    # Calculate user's implied balances
    user_mvl_implied_balance = mvl_implied_pool_balance * user_share
    user_eth_implied_balance = eth_implied_pool_balance * user_share

    print(f"User's MVL Implied Balance: {user_mvl_implied_balance}")
    print(f"User's ETH Implied Balance: {user_eth_implied_balance}")
