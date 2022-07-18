import sqlite3
import pandas as pd

from bakasur.constants import DB_FILEPATH
from bakasur.exceptions import ThuisbezorgdCliDBError

create_order_table = """
CREATE TABLE IF NOT EXISTS orders(
id INTEGER PRIMARY KEY AUTOINCREMENT,
order_id INT UNIQUE,
order_val FLOAT,
order_datetime DATETIME,
restaurant_name VARCHAR)
"""

create_order_details_table = """
CREATE TABLE IF NOT EXISTS items(
id INTEGER PRIMARY KEY AUTOINCREMENT,
order_id INT,
restaurant_name VARCHAR,
order_name VARCHAR,
FOREIGN KEY(order_id) REFERENCES orders(order_id))
"""

latest_datetime_from_orders = """
SELECT order_datetime FROM orders ORDER BY order_datetime desc LIMIT 1
"""

insert_orders_query = """
INSERT INTO orders(order_id, order_val, order_datetime, restaurant_name) VALUES (?,?,?,?)
"""

insert_order_details_query = """
INSERT INTO items(order_id, restaurant_name, order_name) VALUES (?,?,?)
"""


def get_latest_datetime_from_orders(db):
    return db.fetch_result(query=latest_datetime_from_orders)[0][0]


class BakasurDB:
    def init_db(self):
        try:
            print("Connecting to {}".format(DB_FILEPATH))
            self.conn = sqlite3.connect(DB_FILEPATH)
        except Exception:
            raise ThuisbezorgdCliDBError("Unable to connect to database")

    def create_db(self):
        cur = self.conn.cursor()
        cur.execute(create_order_table)
        cur.execute(create_order_details_table)
        self.conn.commit()

    def insert_orders(self, orders):
        cur = self.conn.cursor()
        try:
            cur.executemany(insert_orders_query, orders)
            self.conn.commit()
        except sqlite3.Error as e:
            if "UNIQUE" in "{}".format(e):
                pass
            else:
                raise ThuisbezorgdCliDBError("Error while inserting orders: {}".format(e))

    def insert_order_details(self, order_details):
        cur = self.conn.cursor()
        try:
            cur.executemany(insert_order_details_query, order_details)
            self.conn.commit()
        except sqlite3.Error as e:
            if "UNIQUE" in "{}".format(e):
                pass
            else:
                raise ThuisbezorgdCliDBError("Error while inserting order details: {}".format(e))

    def fetch_result(self, query):
        cur = self.conn.cursor()
        try:
            response = cur.execute(query).fetchall()
            self.conn.commit()
        except sqlite3.Error as e:
            raise ThuisbezorgdCliDBError("Error while fetching items: {}".format(e))
        except Exception as e:
            raise ThuisbezorgdCliDBError("Error while executing query: {}".format(e))
        return response

    def export_to_df(self):
        # cur = self.conn.cursor()
        try:
            orders = self.conn.execute("SELECT * FROM orders")
            order_details = self.conn.execute("SELECT * FROM items")

            orders_cols = [column[0] for column in orders.description]
            order_detail_cols = [column[0] for column in order_details.description]

            orders_df = pd.DataFrame.from_records(data=orders.fetchall(), columns=orders_cols)
            order_details_df = pd.DataFrame.from_records(data=order_details.fetchall(), columns=order_detail_cols)
        except Exception as e:
            raise ThuisbezorgdCliDBError("Error while executing query: {}".format(e))

        return orders_df, order_details_df
