import math
from requests import get
from web3 import Web3, HTTPProvider
from tabulate import tabulate
import csv
from termcolor import cprint
from time import sleep
from config import *
from data import *
from setting import *

RESULT = {}


def evm_wallet(key):
    retry = 0
    while True:
        try:
            web3 = Web3(HTTPProvider(DATA['ethereum']['rpc']))
            wallet = web3.eth.account.from_key(key).address
            return wallet
        except Exception as e:
            retry += 1
            if retry >= 2:
                return key


def round_to(num, digits=3):
    try:
        if num == 0:
            return 0
        scale = int(-math.floor(math.log10(abs(num - int(num))))) + digits - 1
        if scale < digits:
            scale = digits
        return round(num, scale)
    except Exception as e:
        return num


def get_prices(datas):
    prices = {}
    for data in datas.items():
        chain = data[0]
        coins = data[1]
        web3 = Web3(HTTPProvider(DATA[chain]['rpc']))
        for address_contract in coins:
            if address_contract == '':  # eth
                token_decimal = 18
                symbol = DATA[chain]['token']
            else:
                token_contract = web3.eth.contract(address=Web3.to_checksum_address(address_contract), abi=ERC20_ABI)
                symbol = token_contract.functions.symbol().call()
            prices.update({symbol: 0})
    for symbol in prices:
        url = f'https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USDT'
        response = get(url)
        try:
            result = [response.json()]
            price = result[0]['USDT']
            prices[symbol] = float(price)
        except Exception as error:
            print(f'{error}. set price : 0')
            prices[symbol] = 0
    return prices


def check_data_token(web3, token_address):
    try:
        token_contract = web3.eth.contract(address=Web3.to_checksum_address(token_address), abi=ERC20_ABI)
        decimals = token_contract.functions.decimals().call()
        symbol = token_contract.functions.symbol().call()
        return token_contract, decimals, symbol
    except Exception as error:
        print(f'{error}')
        sleep(2)
        return check_data_token(web3, token_address)


def check_balance(web3, wallet, chain, address_contract):
    try:
        try:
            wallet = web3.eth.account.from_key(wallet)
            wallet = wallet.address
        except Exception as error:
            wallet = wallet
        if address_contract == '':  # eth
            balance = web3.eth.get_balance(web3.to_checksum_address(wallet))
            token_decimal = 18
            symbol = DATA[chain]['token']
        else:
            token_contract, token_decimal, symbol = check_data_token(web3, address_contract)
            balance = token_contract.functions.balanceOf(web3.to_checksum_address(wallet)).call()
        human_readable = decimalToInt(balance, token_decimal)
        return human_readable, symbol
    except Exception as error:
        print(f'{error}')
        sleep(1)
        return check_balance(web3, wallet, chain, address_contract)


def main(datas, wallets):
    for wallet in wallets:
        worker(wallet, datas)


def worker(wallet, datas):
    for data in datas.items():
        chain = data[0]
        coins = data[1]
        while True:
            try:
                web3 = Web3(HTTPProvider(DATA[chain]['rpc']))
                break
            except Exception as error:
                print(error, 'red')
                sleep(1)
        for address_contract in coins:
            balance, symbol = check_balance(web3, wallet, chain, address_contract)
            RESULT[wallet][chain].update({symbol: balance})
            sleep(5)

def send_result(min_balance, file_name, prices):
    small_wallets = []

    balances = {}

    headers = [['number', 'wallet'], [], ['', ''], ['TOTAL_VALUE:']]

    number = 0
    for data in RESULT.items():
        number += 1

        wallet = data[0]
        chains = data[1]

        h_ = [number, wallet]

        for data in chains.items():

            chain = data[0]
            coins = data[1]

            for data in coins.items():

                coin = data[0]
                balance = round_to(data[1])

                head = f'{coin}-{chain.lower()}'

                if head not in headers[0]:
                    headers[0].append(head)
                h_.append(balance)

                if head not in balances:
                    balances.update({head: 0})
                balances[head] += balance

                if chain.lower() == min_balance['chain'].lower():
                    if coin.lower() == min_balance['coin'].lower():
                        if balance < min_balance['amount']:
                            small_wallets.append(wallet)

        headers[1].append(h_)

    # записываем в csv
    with open(f'{outfile}{file_name}.csv', 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_MINIMAL)

        spamwriter.writerow(headers[0])
        for header in headers[1]:
            spamwriter.writerow(header)

        send_table = []
        total_value = []

        for data in balances.items():

            coin = data[0]
            balance = round_to(data[1])

            symbol = coin.split('-')[0]
            price = prices[symbol]
            if symbol == 'USDT':
                price = 1

            # value = round_to(balance * price)
            value = int(balance * price)
            total_value.append(value)

            # cprint(f'{coin} : {balance} | value : {value} $', 'white')
            send_table.append([coin, balance, f'{value} $'])

            headers[2].append(balance)
            headers[3].append(f'{value} $')

        headers[3].insert(1, f'{int(sum(total_value))} $')

        spamwriter.writerow([])
        spamwriter.writerow(headers[2])
        spamwriter.writerow(headers[3])

        table_type = 'double_grid'
        head_table = ['token', 'amount', 'value']
        tokens_ = tabulate(send_table, head_table, tablefmt=table_type)

        small_text = f'{min_balance["coin"]} balance in {min_balance["chain"]} of these wallets < {min_balance["amount"]} :'
        cprint(small_text, 'blue')
        spamwriter.writerow([])
        spamwriter.writerow([small_text])
        for wallet in small_wallets:
            cprint(wallet, 'white')
            spamwriter.writerow([wallet])

        cprint(f'\nall balances :\n', 'blue')
        cprint(tokens_, 'white')
        cprint(f'\nTOTAL_VALUE : {int(sum(total_value))} $\n', 'blue')
        cprint(f'\nРезультаты записаны в файл : {outfile}{file_name}.csv\n', 'blue')


def run_web3_check():
    datas, min_balance, file_name = value_web3_checker()
    wallets = []
    for key in WALLETS:
        wallet = evm_wallet(key)
        wallets.append(wallet)
        RESULT.update({wallet: {}})
        for data in datas.items():
            chain = data[0]
            RESULT[wallet].update({chain: {}})
    prices = get_prices(datas)
    main(datas, wallets)
    send_result(min_balance, file_name, prices)


def web3_check():
    print('\nSTART WEB3 CHECKER\n')
    run_web3_check()


if __name__ == "__main__":
    web3_check()
