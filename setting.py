def value_web3_checker():
    '''
    Нужно раскомментировать, токен для проверки
    '''

    datas = {
        # 'bsc': [
        #    '', # BNB
        #        ],
        # 'arbitrum': [
        #     '', # ETH
            # '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9', # USDT
            #     ],
        # 'optimism': [
        #      '', # ETH
            # '0x7f5c764cbc14f9669b88837ca1490cca17c31607', # USDC
        #         ],
        # 'polygon': [
        #     '',  # MATIC
        # ],
        # 'avalanche': [
        #    '', # AVAX
        #        ],
        # 'fantom': [
        #        '', # FTM
        #         ],
        # 'zksync': [
        #    '', # ETH
        #        ],
        # 'nova': [
        #     '', # ETH
        #     ],
        # 'ethereum': [
        #     '', # ETH
        #        ],
        # 'polygon_zkevm': [
        #     '', # ETH
        #     ],
        # 'celo': [
        #     '', # CELO
        #     ],
        # 'gnosis': [
        #     '', # xDAI
        #     ],
        # 'harmony': [
        #     '', # ONE
        #     ],
        # 'core': [
        #     '', # CORE
        #     ],
        # 'linea': [
        #     '', # ETH
        #     ],
        'base': [
            '',  # ETH
        ],
        'zora': [
            '',  # ETH
        ],
        #     ],
    }

    min_balance = {
        'chain': 'zksync',
        'coin': 'ETH',
        'amount': 0  # если баланс меньше этого числа, кошелек будет выделен
    }

    file_name = 'web3_balances'  # Создается сам

    return datas, min_balance, file_name
