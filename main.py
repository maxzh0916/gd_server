import uvicorn
import threading
from fastapi import FastAPI
from datetime import datetime, timedelta
from collections import defaultdict
import os

import buff
import steam
import model
import utils

app = FastAPI(docs_url=None, redoc_url=None)
API_KEY = os.environ.get("API_KEY")


@app.get("/cookies/update_steam_market_cookies")
def update_steam_market_cookies(api_key: str, session_id: str, steam_login_secure: str):
    if api_key != API_KEY:
        return model.Response(success=False, msg="api_key错误")
    steam.client.cookies.update({"sessionid": session_id, "steamLoginSecure": steam_login_secure})
    try:
        if steam.get_market_listings():
            utils.set_steam_cookies_available(True)
            return model.Response(success=True)
    except steam.SteamAPIError as e:
        utils.set_steam_cookies_available(False)
        return model.Response(success=False, msg=e.msg)


@app.get("/steam/order_list")
def steam_order_list(api_key: str, app_id: int, hash_name: str):
    if api_key != API_KEY:
        return model.Response(success=False, msg="api_key错误")
    if not utils.is_steam_cookies_available():
        return model.Response(success=False, msg="Cookies无效")
    try:
        response = steam.get_orderbook(app_id, hash_name)
    except steam.SteamAPIError as e:
        return model.Response(success=False, msg=e.msg)
    sell_order_original = response["data"]["data"]["rgCompactSellOrders"][:20]
    buy_order_original = response["data"]["data"]["rgCompactBuyOrders"][:20]
    results = {
        "sell_order_list": [[sell_order_original[i] / 100, sell_order_original[i + 1]] for i in
                            range(0, len(sell_order_original), 2)],
        "buy_order_list": [[buy_order_original[i] / 100, buy_order_original[i + 1]] for i in
                           range(0, len(buy_order_original), 2)]
    }
    return model.Response(success=True, data=results)


@app.get("/steam/price_history")
def steam_price_history(api_key: str, app_id: int, hash_name: str):
    if api_key != API_KEY:
        return model.Response(success=False, msg="api_key错误")
    if not utils.is_steam_cookies_available():
        return model.Response(success=False, msg="Cookies无效")
    try:
        response = steam.get_price_history(app_id, hash_name)
    except steam.SteamAPIError as e:
        return model.Response(success=False, msg=e.msg)
    cleaned_data = []
    volume_24h = 0
    _volume_10d = defaultdict(int)
    volume_10d = []
    last_dt = datetime.strptime(response["prices"][-1][0].replace(": +0", ":00 +0800"), "%b %d %Y %H:%M %z")
    start_dt = last_dt.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=9)
    # 清洗数据
    for i in response["prices"]:
        dt_obj = datetime.strptime(i[0].replace(": +0", ":00 +0800"), "%b %d %Y %H:%M %z")
        if dt_obj >= start_dt:
            cleaned_data.append([dt_obj, int(i[2])])
    # 计算销量
    for i in cleaned_data[::-1]:
        if last_dt - i[0] < timedelta(hours=24):
            volume_24h += i[1]
        day_key = i[0].strftime("%m-%d")
        _volume_10d[day_key] += i[1]
    for key, value in _volume_10d.items():
        volume_10d.append([key, value])
    result = {"volume_24h": volume_24h, "volume_10d": volume_10d}
    return model.Response(success=True, data=result)


@app.get("/buff/price_data")
def buff_price_data(api_key: str, game: str, goods_id: str):
    if api_key != API_KEY:
        return model.Response(success=False, msg="api_key错误")
    try:
        response = buff.get_sell_order(game, goods_id)
    except buff.BuffAPIError as e:
        return model.Response(success=False, msg=e.msg)
    result = []
    for i in response["data"]["items"]:
        result.append(float(i["price"]))
    return model.Response(success=True, data=result)


if __name__ == "__main__":
    if not API_KEY:
        utils.logger.error("未设置api_key，程序已退出")
        exit()
    validate_steam_cookies_thread = threading.Thread(target=utils.verify_cookies_available)
    validate_steam_cookies_thread.daemon = True
    validate_steam_cookies_thread.start()
    uvicorn.run(app, host="0.0.0.0", port=8800, access_log=False)
