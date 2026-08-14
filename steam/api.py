import httpx
import json
import os

from steam.exception import SteamAPIError

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "zh-CN,zh;q=0.9"
}
_E_TIME_OUT = os.environ.get("TIME_OUT")
_TIME_OUT = 3 if not _E_TIME_OUT else _E_TIME_OUT
client = httpx.Client(base_url="https://steamcommunity.com/market", headers=_HEADERS, timeout=_TIME_OUT)


def get_market_listings():
    try:
        response = client.get(url="/mylistings")
        status_code = response.status_code
        match status_code:
            case 200:
                response = response.json()
                if response["success"]:
                    return response
                else:
                    raise SteamAPIError(f"未知错误，{status_code} - {response.text}")
            case 400:
                raise SteamAPIError("Cookies无效")
            case 429:
                raise SteamAPIError("请求次数太多")
            case 502:
                raise SteamAPIError("网关错误")
            case 503:
                raise SteamAPIError("服务不可用")
            case _:
                raise SteamAPIError(f"状态码错误，{status_code} - {response.text}")
    except httpx.TimeoutException:
        raise SteamAPIError("连接超时")
    except httpx.TransportError:
        raise SteamAPIError("连接错误")


def get_orderbook(app_id: int, hash_name: str):
    params = {
        "q": "Load",
        "qp": json.dumps([app_id, hash_name]),
    }
    try:
        response = client.get("/orderbook", params=params)
        status_code = response.status_code
        match status_code:
            case 200:
                response = response.json()
                if response["data"]["success"]:
                    return response
                else:
                    raise SteamAPIError(f"未知错误，{status_code} - {response.text}")
            case 400:
                raise SteamAPIError("Cookies无效")
            case 429:
                raise SteamAPIError("请求次数太多")
            case 502:
                raise SteamAPIError("网关错误")
            case 503:
                raise SteamAPIError("服务不可用")
            case _:
                raise SteamAPIError(msg=f"状态码错误，{status_code} - {response.text}")
    except httpx.TimeoutException:
        raise SteamAPIError("连接超时")
    except httpx.TransportError:
        raise SteamAPIError("连接错误")


def get_price_history(app_id: int, hash_name: str):
    params = {
        "appid": app_id,
        "market_hash_name": hash_name
    }
    try:
        response = client.get("/pricehistory", params=params)
        status_code = response.status_code
        match status_code:
            case 200:
                response = response.json()
                if response["success"]:
                    return response
                else:
                    raise SteamAPIError(f"未知错误，{status_code} - {response.text}")
            case 400:
                raise SteamAPIError("Cookies无效")
            case 429:
                raise SteamAPIError("请求次数太多")
            case 502:
                raise SteamAPIError("网关错误")
            case 503:
                raise SteamAPIError("服务不可用")
            case _:
                raise SteamAPIError(msg=f"状态码错误，{status_code} - {response.text}")
    except httpx.TimeoutException:
        raise SteamAPIError("服务端连接超时")
    except httpx.TransportError:
        raise SteamAPIError("服务端连接错误")
