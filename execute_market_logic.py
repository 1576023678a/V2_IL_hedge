from web3 import Web3
from decimal import Decimal, getcontext
import datetime
import pytz
from orderbook import OrderBook
from gas_estimate import GasEstimator

order_book = OrderBook()

getcontext().prec = 28  # 정밀도 설정

# Alchemy API endpoint 설정
ALCHEMY_API_KEY = ''
w3 = Web3(Web3.HTTPProvider(f'https://eth-mainnet.alchemyapi.io/v2/{ALCHEMY_API_KEY}'))

# ERC20 토큰의 ABI (일부만 표시)
ERC20_ABI = [{
    "constant": True,
    "inputs": [{
        "name": "_owner",
        "type": "address"
    }],
    "name": "balanceOf",
    "outputs": [{
        "name": "balance",
        "type": "uint256"
    }],
    "type": "function"
}]

# 첫 번째 코드 조각의 TOKEN_INFO 및 USER_ADDRESS
TOKEN_INFO_1 = {
    '0xA849EaaE994fb86Afa73382e9Bd88c2B6b18Dc71': ('MVL(mvl_weth_pool)', 18),
    '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2': ('WETH1(mvl_weth_pool)', 18)
}
USER_ADDRESS_1 = '0x3c8AD34155B83ddB7f43119A19503d34Ed2B5c7a'

# 두 번째 코드 조각의 TOKEN_INFO 및 USER_ADDRESS
TOKEN_INFO_2 = {
    '0xdAC17F958D2ee523a2206206994597C13D831ec7': ('USDT(usdt_weth_pool)', 6),
    '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2': ('WETH2(usdt_weth_pool)', 18)
}
USER_ADDRESS_2 = '0x0d4a11d5EEaaC28EC3F61d100daF4d40471f1852'

def calculate_and_print_balances(token_info, user_address):
    balances = {}
    for token_address, (token_name, decimals) in token_info.items():
        token_contract = w3.eth.contract(address=token_address, abi=ERC20_ABI)
        raw_balance = token_contract.functions.balanceOf(user_address).call(block_identifier=desired_block)
        balance = Decimal(raw_balance) / Decimal(10 ** decimals)
        balances[token_name] = balance
        print(f"Token balance for {token_name} ({token_address}) at block {desired_block} (KST Time: {kst_time}): {balance:.18f}")
    return balances
# 원하는 블록 번호 설정
#
# desired_block = 18930538

desired_block = 'latest'
# 블록 타임스탬프 얻기
block_timestamp = w3.eth.get_block(desired_block)['timestamp']
utc_time = datetime.datetime.utcfromtimestamp(block_timestamp)

kst_time = utc_time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Seoul'))
# 잔액 계산 및 출력 함수 정의

# 첫 번째 및 두 번째 코드 조각의 잔액 계산 및 출력
balances_1 = calculate_and_print_balances(TOKEN_INFO_1, USER_ADDRESS_1)
balances_2 = calculate_and_print_balances(TOKEN_INFO_2, USER_ADDRESS_2)

# 토큰 이름을 변수로 사용하고 밸런스 값을 할당
MVL_mvl_weth_pool = balances_1['MVL(mvl_weth_pool)']
WETH1_mvl_weth_pool = balances_1['WETH1(mvl_weth_pool)']
USDT_usdt_weth_pool = balances_2['USDT(usdt_weth_pool)']
WETH2_usdt_weth_pool = balances_2['WETH2(usdt_weth_pool)']

# 변수에 할당된 밸런스 값 출력
print(f"MVL(mvl_weth_pool): {MVL_mvl_weth_pool}")
print(f"WETH1(mvl_weth_pool): {WETH1_mvl_weth_pool}")
print(f"USDT(usdt_weth_pool): {USDT_usdt_weth_pool}")
print(f"WETH2(usdt_weth_pool): {WETH2_usdt_weth_pool}")
print()





print(f"MVL_mvl_weth_pool/WETH1_mvl_weth_pool: {MVL_mvl_weth_pool/WETH1_mvl_weth_pool}")
print(f"WETH1_mvl_weth_pool/MVL_mvl_weth_pool: {WETH1_mvl_weth_pool/MVL_mvl_weth_pool}")
usdt_ratio = Decimal(USDT_usdt_weth_pool) / Decimal(WETH2_usdt_weth_pool)

print(f"usdt_ratio: {usdt_ratio}")
print(f"WETH2_usdt_weth_pool/USDT_usdt_weth_pool : {WETH2_usdt_weth_pool/USDT_usdt_weth_pool}")
v2_pool_mvl = (WETH1_mvl_weth_pool/MVL_mvl_weth_pool)*(USDT_usdt_weth_pool/WETH2_usdt_weth_pool)



print(f"v2_pool_mvl: {v2_pool_mvl}")
print()











KRW_MVL_MID_PRICE = Decimal(order_book.KRW_MVL_MID_PRICE)
USDT_MID_PRICE = Decimal(order_book.USDT_MID_PRICE)

print(KRW_MVL_MID_PRICE)
print(USDT_MID_PRICE)

mvl_usdt_upbit = (KRW_MVL_MID_PRICE / USDT_MID_PRICE)
print(f"mvl_usdt_upbit: {mvl_usdt_upbit}")








# gasfee_estimation
submit_gasfee, submit_gasfee_eth = GasEstimator.calculate_and_return_fees()
if submit_gasfee is not None and submit_gasfee_eth is not None:
    print(f"Calculated average base fee: {submit_gasfee} Gwei")
    print(f"Calculated average base fee in ETH: {submit_gasfee_eth:.13f} ETH")
else:
    print("Error calculating fees")







def calculate_price(x, y):
    """
    Calculate the price of token y in terms of token x.
    :param x: Quantity of token x
    :param y: Quantity of token y
    :return: Price of token y in terms of token x
    """
    price = y / x
    return price

def simulate_trade(x, y, delta_x=None, delta_y=None):
    """
    Simulate a trade on the Uniswap V2 AMM model with a 0.3% trading fee.
    Either delta_x or delta_y should be provided.
    :param x: Current quantity of token x
    :param y: Current quantity of token y
    :param delta_x: Change in quantity of token x (amount of token x bought or sold)
    :param delta_y: Change in quantity of token y (amount of token y bought or sold)
    :return: New quantities of x and y, and price after trade
    """
    k = x * y  # 상수 곱셈
    trading_fee = 0.003  # 0.3% 거래 수수료

    if delta_x is not None:
        fee_paid = Decimal(delta_x) * Decimal(trading_fee)
        effective_delta_x = Decimal(delta_x) - fee_paid
        new_x = x + Decimal(delta_x)  # Use entire delta_x including fee_paid
        new_y = k / (x + effective_delta_x)  # Use actual trade amount excluding fee_paid
    elif delta_y is not None:
        fee_paid = Decimal(delta_y) * Decimal(trading_fee)
        effective_delta_y = Decimal(delta_y) - fee_paid
        new_y = y + Decimal(delta_y)  # Use entire delta_y including fee_paid
        new_x = k / (y + effective_delta_y)  # Use actual trade amount excluding fee_paid
    else:
        raise ValueError("delta_x 또는 delta_y 중 하나가 제공되어야 합니다.")

    new_price = calculate_price(new_x, new_y)
    return new_x, new_y, new_price, fee_paid


def adjust_delta_y_for_target_difference(x_initial, y_initial, target_difference, tolerance=0.0001, max_iterations=1000):
    trading_fee = Decimal("0.003")
    low = Decimal("0")
    high = Decimal(y_initial) / 2
    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        delta_y = (low + high) / 2
        fee_paid = delta_y * trading_fee
        effective_delta_y = delta_y - fee_paid

        new_x, new_y, new_price, _ = simulate_trade(x_initial, y_initial, delta_y=delta_y)

        current_price = new_price * Decimal(usdt_ratio)
        current_difference = abs(current_price - Decimal(UPBIT_MVL_USDT_PRICE)) / Decimal(UPBIT_MVL_USDT_PRICE) * 100

        print(f"Iteration {iteration}: delta_y = {delta_y}, current_difference = {current_difference}%")  # 디버깅 정보 추가

        if abs(current_difference - Decimal(target_difference)) <= Decimal(tolerance):
            return delta_y, new_x, new_y, new_price, current_difference

        if current_price > Decimal(UPBIT_MVL_USDT_PRICE):
            high = delta_y
        else:
            low = delta_y

    # 예외 처리: 최대 반복 횟수에 도달하면 마지막 계산 결과 반환
    return delta_y, new_x, new_y, new_price, current_difference



def adjust_delta_x_for_target_difference(x_initial, y_initial, target_difference, tolerance=0.0001, max_iterations=1000):
    trading_fee = Decimal("0.003")
    low = Decimal("0")
    high = Decimal(x_initial) / 2
    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        delta_x = (low + high) / 2
        fee_paid = delta_x * trading_fee
        effective_delta_x = delta_x - fee_paid

        new_x, new_y, new_price, _ = simulate_trade(x_initial, y_initial, delta_x=delta_x)

        current_price = new_price * Decimal(usdt_ratio)
        current_difference = abs(current_price - Decimal(UPBIT_MVL_USDT_PRICE)) / Decimal(UPBIT_MVL_USDT_PRICE) * 100

        print(f"Iteration {iteration}: delta_x = {delta_x}, current_difference = {current_difference}%")  # 디버깅 정보 추가

        if abs(current_difference - Decimal(target_difference)) <= Decimal(tolerance):
            return delta_x, new_x, new_y, new_price, current_difference

        if current_price > Decimal(UPBIT_MVL_USDT_PRICE):
            low = delta_x
        else:
            high = delta_x

    # 예외 처리: 최대 반복 횟수에 도달하면 마지막 계산 결과 반환
    return delta_x, new_x, new_y, new_price, current_difference







# Initial values
x_initial = MVL_mvl_weth_pool  # Initial quantity of token x
y_initial = WETH1_mvl_weth_pool   # Initial quantity of token y

print(f"Initial Quantity of Token X: {x_initial}")
print(f"Initial Quantity of Token Y: {y_initial}")



print(f"INit Pool ratio: {y_initial/ x_initial}")

init_pool_ratio_price = (y_initial / x_initial) * usdt_ratio
print(f"Init Pool ratio*price: {init_pool_ratio_price}")
# init_pool_ratio_price_조절 = (y_initial + 1)/ (x_initial - 0) * usdt_ratio

# print(f"Init Pool ratio*price_조절: {init_pool_ratio_price_조절}")
print("UPBIT_MVL_USDT_PRICE:", mvl_usdt_upbit)

# 퍼센트 차이 계산
percent_difference = abs(init_pool_ratio_price - mvl_usdt_upbit) / mvl_usdt_upbit * 100

# 가격 비교를 통해 부등호 결정
if init_pool_ratio_price > mvl_usdt_upbit:
    comparison_expression = f"-{percent_difference:.4f}% (init_pool_ratio_price > UPBIT_MVL_USDT_PRICE)"
else:
    comparison_expression = f"+{percent_difference:.4f}% (UPBIT_MVL_USDT_PRICE > init_pool_ratio_price)"

# 최종 결과 출력
print(f"percent_difference: {comparison_expression}")
print(comparison_expression)
difference_in_y_initial = percent_difference / y_initial
print("difference_in_y_initial:", difference_in_y_initial)
submit_gasfee_eth_times_three = submit_gasfee_eth * 100000
print("submit_gasfee_eth : {:.15f}".format(submit_gasfee_eth_times_three))
print()
print()





