import asyncio
from decimal import Decimal
from typing import Dict

import httpx
from multicall import Call, Multicall

from backend.settings import POLIGON_KEY


def build_url(contract_address, start_block, end_block):
    base_url = 'https://api.polygonscan.com/api'
    params = {
        'module': 'account',
        'action': 'tokentx',
        'contractaddress': contract_address,
        'startblock': start_block,
        'endblock': end_block,
        'sort': 'asc',
        'apikey': POLIGON_KEY
    }
    query_string = '&'.join(f'{key}={value}' for key, value in params.items())
    return f'{base_url}?{query_string}'


def from_wei(value, decimals):
    return Decimal(value) / Decimal(10**decimals)


def get_balances_multicall(token_address,
                           addresses,
                           web3) -> Dict:
    # Настройка chain_id для Polygon
    Multicall.chain_id = 137

    # Получение количества знаков после запятой
    decimals_call = Call(token_address,
                         ['decimals()(uint8)'],
                         [['decimals', None]])
    multicall_decimals = Multicall([decimals_call], _w3=web3)
    decimals_result = multicall_decimals()

    # Извлечение значения decimals из результатов вызова
    decimals = decimals_result['decimals']

    # Создание вызовов для получения балансов
    calls = [Call(token_address,
                  ['balanceOf(address)(uint256)', address],
                  [[address, None]]) for address in addresses]
    multicall = Multicall(calls, _w3=web3)
    results = multicall()

    # Преобразование результатов
    balances = {address: from_wei(results[address],
                                  decimals) for address in addresses}
    return balances


async def get_transactions(contract_address, start_block, end_block):
    url = build_url(contract_address, start_block, end_block)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            return data.get('result', [])
        except httpx.HTTPStatusError as e:
            print(f'Ошибка при запросе: {e.response.text}')
            return []


async def create_address_database(contract_address, web3):
    start_block = 0
    end_block = await get_current_block_number(web3)

    transactions = await get_transactions(contract_address,
                                          start_block,
                                          end_block)

    if transactions:
        addresses = set()
        for tx in transactions:
            from_address = tx['from']
            to_address = tx['to']
            if from_address:
                addresses.add(from_address)
            if to_address:
                addresses.add(to_address)

        return addresses
    else:
        print('Транзакции не найдены.')
        return set()


async def create_address_database_with_transactions(contract_address,
                                                    web3):
    start_block = 0
    end_block = await get_current_block_number(web3)

    transactions = await get_transactions(contract_address,
                                          start_block,
                                          end_block)

    address_last_tx_map = {}
    for tx in transactions:
        from_address = tx['from']
        to_address = tx['to']
        timestamp = tx['timeStamp']
        if from_address:
            address_last_tx_map[from_address] = timestamp
        if to_address:
            address_last_tx_map[to_address] = timestamp

    adresses = set(address_last_tx_map.keys())
    return adresses, address_last_tx_map


async def get_current_block_number(web3):
    return await asyncio.to_thread(web3.eth.get_block_number)
