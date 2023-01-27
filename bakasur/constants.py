import os
from rich.console import Console
from fake_useragent import UserAgent

ua = UserAgent()

THUISBEZORGD_URL = "https://cw-api.takeaway.com"
THUISBEZORGD_USER_URL = THUISBEZORGD_URL + "/api/v31/user"
THUISBEZORGD_LOGIN_URL = THUISBEZORGD_URL + "/api/v31/user/login" #POST 
THUISBEZORGD_ORDER_URL = THUISBEZORGD_URL + "/api/v31/user/orders" #GET
THUISBEZORGD_ORDER_DETAILS_URL = THUISBEZORGD_URL + "/api/v31/order/details"
THUISBEZORGD_REFRESH_TOKEN = THUISBEZORGD_URL + "/api/v31/user/jwt_refresh" #POST

DB_FILEPATH = os.path.join(str(os.getcwd()), 'thuisbezorgd.db')

# Credentials file
THUISBEZORGD_TOKEN_FILE = os.path.join(str(os.getcwd()), 'thuisbezorgd_token.json')

REPORT_PATH = os.path.join(str(os.getcwd()), 'report.html')

console = Console()

HEADERS = {
            'authority': 'cw-api.takeaway.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en',
            'content-type': 'application/json;charset=UTF-8',
            'origin': 'https://www.thuisbezorgd.nl',
            'referer': 'https://www.thuisbezorgd.nl/',
            'user-agent': ua.random,
            'x-country-code': 'nl',
            'x-language-code': 'en',
            'x-requested-with': 'XMLHttpRequest',
        }
