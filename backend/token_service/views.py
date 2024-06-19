import asyncio

from adrf.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from web3 import Web3
from eth_typing import ChecksumAddress

from .decorators import (check_web3_initialization,
                         check_web3_initialization_sync,
                         check_request_param,
                         check_request_param_sync)
from .utils import (create_address_database,
                    create_address_database_with_transactions,
                    get_balances_multicall)
from backend.settings import CONTRACT_ADDRESS, N_DEFAULT
from .web3_setup import web3, contract
from data.abi import erc20_abi_info


@api_view(['GET'])
@check_web3_initialization
@check_request_param('address')
async def get_balance_view(request):
    """
    Получает баланс выбранного адреса.

    Parameters:
        /get_balance?address=

    Returns:
        Response: JSON-ответ с балансом в виде строки.
    """
    address = request.GET.get('address', '')
    if not address:
        return Response(
            {'error': 'Адрес не указан'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        checksum_address = Web3.toChecksumAddress(address)
        balance = contract.functions.balanceOf(checksum_address).call()
        decimals = contract.functions.decimals().call()
        human_readable_balance = balance / (10 ** decimals)
        response_data = {'balance': str(human_readable_balance)}
        return Response(response_data)
    except Exception:
        return Response(
            {'error': 'Ошибка при получении баланса адреса'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@check_web3_initialization
async def get_balance_batch_view(request):
    """
    Получает балансы нескольких адресов.

    Parameters:
        /get_balance_batch
            body:
                {
                    "addresses": ["", "",...]
                }

    Returns:
        Response: JSON-ответ с балансами.
    """
    addresses = request.data.get('addresses', [])
    if not addresses:
        return Response(
            {'error': f'Список адресов пуст {addresses}'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        balances = []
        for address in addresses:
            checksum_address = Web3.toChecksumAddress(address)
            balance = contract.functions.balanceOf(checksum_address).call()
            decimals = contract.functions.decimals().call()
            human_readable_balance = balance / (10 ** decimals)
            balances.append(human_readable_balance)
        return Response({'balances': balances})
    except Exception:
        return Response(
            {'error': 'Ошибка при получении баланса адресов'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@check_web3_initialization
async def get_top_view(request):
    """
    Получает топ N адресов по балансам токена.

    Parameters:
        /get_top?N=

    Returns:
        Response: JSON-ответ с топ N адресов и их балансами.
    """
    n = request.GET.get('N', N_DEFAULT)
    try:
        n = int(n)
    except ValueError:
        return Response(
            {'error': 'Неверное значение параметра N'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        addresses = await create_address_database(CONTRACT_ADDRESS, web3)
        if not addresses:
            return Response(
                {'error': 'Не удалось получить адреса'},
                status=status.HTTP_400_BAD_REQUEST
            )

        checksum_addresses: ChecksumAddress = [
            web3.toChecksumAddress(address) for address in addresses]

        loop = asyncio.get_running_loop()
        balances = await loop.run_in_executor(None,
                                              get_balances_multicall,
                                              CONTRACT_ADDRESS,
                                              checksum_addresses,
                                              web3)

        top_balances = sorted(balances.items(),
                              key=lambda x: x[1],
                              reverse=True)[:n]
        return Response({'top_balances': top_balances})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@check_web3_initialization
async def get_top_with_transactions_view(request):
    """
    Возвращает топ N адресов по балансам токена, с информацией
        по датам последних транзакций.

    Parameters:
        /get_top_with_transactions?N=

    Returns:
        Response: JSON-ответ с топ N адресов, их балансами и
            датами последних транзакций в формате timestamp.
    """
    n = request.GET.get('N', N_DEFAULT)
    try:
        n = int(n)
    except ValueError:
        return Response(
            {'error': 'Неверное значение параметра N'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        adresses, address_last_tx_map = \
            await create_address_database_with_transactions(
                CONTRACT_ADDRESS, web3)

        if not adresses:
            return Response(
                {'error': 'Не удалось получить адреса'},
                status=status.HTTP_400_BAD_REQUEST
            )

        loop = asyncio.get_running_loop()
        balances = await loop.run_in_executor(None,
                                              get_balances_multicall,
                                              CONTRACT_ADDRESS,
                                              adresses,
                                              web3)

        top_balances = sorted(balances.items(),
                              key=lambda x: x[1],
                              reverse=True)[:n]

        address_info = []
        for address, balance in top_balances:
            address_info.append((address,
                                 balance,
                                 address_last_tx_map[address]))

        return Response({'top_with_transactions': address_info})
    except Exception:
        return Response({'error': "Произошла не предвиденная ошибка"},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@check_web3_initialization_sync
@check_request_param_sync('address')
def get_token_info_view(request):
    """
    Получает информацию о токене по его адресу.

    Parameters:
        /get_token_info?address=

    Returns:
        Response: JSON-ответ с информацией о токене.
    """
    token_address = request.GET.get('address', '')
    try:
        checksum_address = Web3.toChecksumAddress(token_address)
        token_contract = web3.eth.contract(address=checksum_address,
                                           abi=erc20_abi_info)

        symbol = token_contract.functions.symbol().call()
        name = token_contract.functions.name().call()
        total_supply = token_contract.functions.totalSupply().call()

        token_info = {
            'symbol': symbol,
            'name': name,
            'totalSupply': total_supply
        }

        return Response(token_info)
    except Exception:
        return Response({'error': "Скорее всего вы ввели неверный адрес"},
                        status=status.HTTP_400_BAD_REQUEST)
