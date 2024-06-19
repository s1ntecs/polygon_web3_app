from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from .web3_setup import initialization_error


def check_web3_initialization(view_func):
    @wraps(view_func)
    async def _wrapped_view(request, *args, **kwargs):
        if initialization_error:
            return Response(
                {'error': f'Ошибка инициализации: {initialization_error}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return await view_func(request, *args, **kwargs)
    return _wrapped_view


def check_web3_initialization_sync(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if initialization_error:
            return Response(
                {'error': f'Ошибка инициализации: {initialization_error}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def check_request_param(param_name):
    def decorator(func):
        @wraps(func)
        async def wrapper(request, *args, **kwargs):
            if param_name not in request.GET:
                return Response(
                    {'error': f'Параметр "{param_name}" не указан'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator


def check_request_param_sync(param_name):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if param_name not in request.GET:
                return Response(
                    { 'error': f'Параметр "{param_name}" не указан' },
                    status=status.HTTP_400_BAD_REQUEST
                )
            return func(request, *args, **kwargs)
        return wrapper
    return decorator

