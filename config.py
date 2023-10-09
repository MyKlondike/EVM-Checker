import json, time
import random
from loguru import logger
from tqdm import tqdm
import asyncio, aiohttp

max_time_check_tx_status = 100  

outfile = ''

with open(f"{outfile}erc20.json", "r") as file:
    ERC20_ABI = json.load(file)

with open(f"{outfile}wallets.txt", "r") as f:
    WALLETS = [row.strip() for row in f]


def intToDecimal(qty, decimal):
    return int(qty * int("".join(["1"] + ["0"] * decimal)))


def decimalToInt(qty, decimal):
    return qty / int("".join((["1"] + ["0"] * decimal)))


def call_json(result, outfile):
    with open(f"{outfile}.json", "w") as file:
        json.dump(result, file, indent=4, ensure_ascii=False)


def sleeping(from_sleep, to_sleep) -> object:
    x = random.randint(from_sleep, to_sleep)
    for i in tqdm(range(x), desc='sleep ', bar_format='{desc}: {n_fmt}/{total_fmt}'):
        time.sleep(1)


def get_prices():
    prices = {
        'ETH': 0, 'BNB': 0, 'AVAX': 0, 'MATIC': 0, 'FTM': 0, 'xDAI': 0, 'CELO': 0, 'COREDAO': 0,
        'ONE': 0, 'MOVR': 0, 'GLMR': 0, 'klaytn': 0,
    }

    async def get_get(session, symbol):
        url = f'https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USDT'

        try:
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    resp_json = await resp.json(content_type=None)
                    try:
                        prices[symbol] = float(resp_json['USDT'])
                    except Exception as error:
                        logger.error(f'{error}. set price : 0')
                        prices[symbol] = 0
                else:
                    await asyncio.sleep(1)
                    return await get_get(session, symbol)
        except Exception as error:
            await asyncio.sleep(1)
            return await get_get(session, symbol)

    async def fetch_prices():
        async with aiohttp.ClientSession() as session:
            tasks = []
            for symbol in prices:
                task = asyncio.create_task(get_get(session, symbol))
                tasks.append(task)

            await asyncio.gather(*tasks)

    asyncio.run(fetch_prices())

    data = {
        'avalanche': prices['AVAX'],
        'polygon': prices['MATIC'],
        'ethereum': prices['ETH'],
        'bsc': prices['BNB'],
        'arbitrum': prices['ETH'],
        'optimism': prices['ETH'],
        'fantom': prices['FTM'],
        'zksync': prices['ETH'],
        'nova': prices['ETH'],
        'gnosis': prices['xDAI'],
        'celo': prices['CELO'],
        'polygon_zkevm': prices['ETH'],
        'core': prices['COREDAO'],
        'harmony': prices['ONE'],
        'moonbeam': prices['GLMR'],
        'moonriver': prices['MOVR'],
        'linea': prices['ETH'],
        'base': prices['ETH'],
        'klaytn': prices['klaytn'],
    }

    return data


PRICES_NATIVE = get_prices()
