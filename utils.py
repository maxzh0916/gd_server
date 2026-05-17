import logging
import time
import os

import steam

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
_steam_cookies_available = False


def is_steam_cookies_available() -> bool:
    return _steam_cookies_available


def set_steam_cookies_available(value: bool):
    global _steam_cookies_available
    _steam_cookies_available = value


def verify_cookies_available():
    verify_cookies_interval = 120 if not os.environ.get("VERIFY_COOKIES_INTERVAL") else int(
        os.environ.get("VERIFY_COOKIES_INTERVAL"))
    while True:
        logger.info(f"[验证cookies有效性]开始验证cookies有效性")
        try:
            if steam.get_market_listings():
                set_steam_cookies_available(True)
        except steam.SteamAPIError as e:
            if e.msg == "Cookies无效":
                set_steam_cookies_available(False)
            else:
                logger.error(f"[验证cookies有效性]{e.msg}")
        time.sleep(verify_cookies_interval)
