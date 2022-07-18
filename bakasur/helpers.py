import os.path
import sys
import json
import time
import requests
from collections import namedtuple
from datetime import datetime

from rich.progress import track

from bakasur.exceptions import ThuisbezorgdApiError, ThuisbezorgdAuthError
from bakasur.utils import get_headers, get_tokens, update_token_file
from bakasur.database import get_latest_datetime_from_orders, BakasurDB
from bakasur.constants import (THUISBEZORGD_LOGIN_URL,
                               THUISBEZORGD_USER_URL,
                               THUISBEZORGD_ORDER_URL,
                               THUISBEZORGD_REFRESH_TOKEN,
                               THUISBEZORGD_TOKEN_FILE,
                               THUISBEZORGD_ORDER_DETAILS_URL,
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
                console.print(
                    ":stopwatch: [yellow] Login initiated, you will now receive a verification code via mail. Your code expires in 30min")
                status = 'LOGIN PENDING'
            elif resp.status_code == 200:
                console.print(":party_popper: [green]Login successful!")
                data = resp.json()
                self.access_token = data.get('authToken', None)
                self.refresh_token = data.get('refreshToken', None)
                self.save_token_file()
                status = 'DONE'
        except ThuisbezorgdAuthError:
            sys.exit("Login attempt failed. Please check your credentials.")
        return status


def is_authenticated(func):
    def wrapper(*args, **kwargs):
        max_retries = 0
        while max_retries < 3:
            try:
                # print("Authenticating...")
                headers = get_headers()
                r = requests.get(THUISBEZORGD_USER_URL, headers=headers)
                if r.status_code == 200:
                    response = func(*args, **kwargs)
                    return response
                else:
                    print("Refreshing tokens")
                    r = requests.post(THUISBEZORGD_REFRESH_TOKEN, headers=HEADERS, json=get_tokens())
                    resp = r.json()
                    attempt = 1
                    while 'error' in resp.keys() and attempt < 3:
                        r = requests.post(THUISBEZORGD_REFRESH_TOKEN, headers=HEADERS, json=get_tokens())
                        time.sleep(2)
                        if r.status_code == 200:
                            resp = r.json()
                            break
                        attempt += 1
                    new_tokens = resp
                    update_token_file(new_tokens)
                    max_retries += 1
            except Exception as e:
                raise ThuisbezorgdAuthError(e)

    return wrapper


@is_authenticated
def fetch_orders(page=1, limit=100):
    # Fetch order data
    print("Fetching orders...")
    params = {
        'page': page,
        'limit': limit,
    }
    req = requests.get(THUISBEZORGD_ORDER_URL, headers=get_headers(), params=params)
    order_data = req.json()
    return order_data


@is_authenticated
def fetch_order_details(order_id):
    params = {
        'orderId': order_id
    }
    req = requests.get(THUISBEZORGD_ORDER_DETAILS_URL, headers=get_headers(), params=params)
    order_detail_data = req.json()
    return order_detail_data


def process_and_store_orders(db, orders_data, store_recent=False):
    orders = []
    Orders = namedtuple(
        'Orders', ['order_id', 'order_val', 'order_datetime', 'restaurant_name'])

    for key, data in orders_data.items():
        order_data = data.get('orders')
        for order in order_data:
            order_id = order.get('id')
            divisor = order['currency']['denominator']
            order_val = order.get('value') / divisor
            order_datetime = datetime.fromtimestamp(order.get('date') / 1000)
            restaurant_name = order['restaurant']['name']
            orders.append(Orders(order_id=order_id,
                                 order_val=order_val,
                                 order_datetime=order_datetime,
                                 restaurant_name=restaurant_name))

    if store_recent:
        # get the recent timestamp from the order table
        # compare the max
        db_datetime = get_latest_datetime_from_orders(db)
        orders = [order for order in orders if
                  order.order_datetime > datetime.strptime(db_datetime, "%Y-%m-%d %H:%M:%S")]
        if len(orders) == 0:
            print("There are no recent orders in your history since the last time")
            return
        else:
            db.insert_orders(orders)
            print("Storing your recent orders")
    else:
        db.insert_orders(orders)

    order_ids = [ord.order_id for ord in orders]
    item_dict = {}
    for idx, ord_id in track(enumerate(order_ids), description="Fetching order details..."):
        data = fetch_order_details(ord_id)
        item_dict[idx] = data
        time.sleep(2)

    order_details = []
    OrderDetails = namedtuple('OrderDetails', ['order_id', 'restaurant_name', 'order_name'])
    print("Starting to process the order details")
    for key, val in item_dict.items():
        orderID = val.get('order').get('id')
        restaurant_name = val.get('restaurant').get('name')
        cart_items = val.get('order').get('cartItems')
        for item in cart_items:
            item_name = item.get('name')
            order_details.append(OrderDetails(order_id=orderID,
                                              restaurant_name=restaurant_name,
                                              order_name=item_name))
    db.insert_order_details(order_details)


def store_orders(db, store_recent):
    try:
        data = {}
        orders = fetch_orders()
        total_pages = orders.get('pagination').get('totalPages')
        data[0] = orders

        if total_pages > 1:
            for page in range(2, total_pages + 1):
                orders = fetch_orders(page=page)
                time.sleep(2)
                data[page - 1] = orders

        process_and_store_orders(db, data, store_recent)
    except Exception as e:
        raise ThuisbezorgdApiError(e)
