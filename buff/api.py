import time
import httpx
import os

from buff.exception import BuffAPIError

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "zh-CN,zh;q=0.9"
}
_E_TIME_OUT = os.environ.get("TIME_OUT")
_E_BUFF_302_RETRY_COUNT = os.environ.get("BUFF_302_RETRY_COUNT")
_TIME_OUT = 3 if not _E_TIME_OUT else _E_TIME_OUT
_BUFF_302_RETRY_COUNT = 5 if not _E_BUFF_302_RETRY_COUNT else _E_BUFF_302_RETRY_COUNT
client = httpx.Client(base_url="https://buff.163.com", headers=_HEADERS, timeout=_TIME_OUT)

def get_user_info():
    params = {
        "meta_list": "is_premium",
        "_": str(int(time.time() * 1000))
    }
    try:
        response = client.get("/account/api/user/info/v2", params=params)
        status_code = response.status_code
        response = response.json()
        if response["code"] == "OK":
            return response
        elif response["code"] == "Login Required":
            raise BuffAPIError("Cookies无效")
        elif response["code"] == "System Error":
            raise BuffAPIError("请求次数太多")
        elif response["code"] == "Internal Server Timeout":
            raise BuffAPIError("内部服务器超时")
        else:
            raise BuffAPIError(f"状态码错误，{status_code} - {response}")
    except httpx.TimeoutException:
        raise BuffAPIError("连接超时")
    except httpx.TransportError:
        raise BuffAPIError("连接错误")


def get_sell_order(game, goods_id):
    params = {
        "game": game,
        "goods_id": goods_id,
        "page_num": 1,
        "sort_by": "default",
        "_": str(int(time.time() * 1000))
    }
    for _ in range(_BUFF_302_RETRY_COUNT):
        try:
            response = client.get(url=f"/api/market/goods/sell_order", params=params)
            status_code = response.status_code
            if status_code == 302:
                continue
            response = response.json()
            if response["code"] == "OK":
                return response
            elif response["code"] == "Login Required":
                raise BuffAPIError("Cookies无效")
            elif response["code"] == "System Error":
                raise BuffAPIError("请求次数太多")
            elif response["code"] == "Internal Server Timeout":
                raise BuffAPIError("网易Buff内部服务器超时")
            else:
                raise BuffAPIError(f"状态码错误，{status_code} - {response}")
        except httpx.TimeoutException:
            raise BuffAPIError("连接超时")
        except httpx.TransportError:
            raise BuffAPIError("连接错误")
    raise BuffAPIError("多次重定向后仍无法获取价格数据")
