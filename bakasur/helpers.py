import sys
import json
import requests
from collections import namedtuple

from bakasur.exceptions import ThuisbezorgdApiError, ThuisbezorgdAuthError
from bakasur.constants import (THUISBEZORGD_LOGIN_URL,
                               THUISBEZORGD_ORDER_URL,
                               THUISBEZORGD_REFRESH_TOKEN,
                               THUISBEZORGD_TOKEN_FILE,
                               DB_FILEPATH,
                               HEADERS,
                               console)


class Login:
    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password
        self.access_token = None
        self.refresh_token = None
        self.headers = HEADERS

    def save_token_file(self):
        data = {
            'authToken': self.access_token,
            'refreshToken': self.refresh_token,
            'headers': self.headers,
        }
        with open(THUISBEZORGD_TOKEN_FILE, 'w') as token_file:
            json.dump(data, token_file)

    def attempt_login(self, vcode: str = None):
        status = 'LOGIN FAILED'

        if vcode is None:
            json_data = {
                'username': self.username,
                'password': self.password,
            }
        else:
            json_data = {
                'username': self.username,
                'password': self.password,
                'twoFactorAuthenticationCode': vcode,
            }

        try:
            resp = requests.post(THUISBEZORGD_LOGIN_URL, headers=self.headers, json=json_data)
            if resp.status_code == 201:
                console.print("Login initiated, you will now receive a verification code via mail")
                status = 'LOGIN PENDING'
            elif resp.status_code == 200:
                console.print("Login successful!")
                data = resp.json()
                self.access_token = data.get('authToken', None)
                self.refresh_token = data.get('refreshToken', None)
                self.save_token_file()
                status = 'DONE'
        except ThuisbezorgdAuthError:
            sys.exit("Login attempt failed. Please check your credentials.")
        return status


class Orders:
    def __init__(self, db) -> None:
        self.db = db


def check_token_file_exists():
    pass


def get_refresh_tokens():
    pass


def update_headers():
    pass


def process_orders():
    response = open('/home/kdcore/git_projects/bakasur/bakasur/data/order_data.json')
    data = json.load(response)

    order_details = []
    OrderDetails = namedtuple(
        'OrderDetails', ['order_id', 'order_val', 'order_date', 'order_time', 'restaurant_name'])
    orders = data.get('orders', None)

    if orders is None:
        sys.exit("You don't have any orders placed with Thuisbezorgd.")

    for order in orders:
        order_id = order.get('id')
        divisor = order['currency']['denominator']
        order_val = order.get('value') / divisor
        order_date = order.get('date')  # TODO: make a date parser
        order_time = order.get('time')
        restaurant_name = order['restaurant']['name']
        order_details.append(OrderDetails(order_id=order_id,
                                          order_val=order_val,
                                          order_date=order_date,
                                          order_time=order_time,
                                          restaurant_name=restaurant_name))

    # TODO: Get item details of every order
