import typer

from bakasur.constants import console
from bakasur.helpers import Login, store_orders
from bakasur.utils import token_file_exists, db_file_exists
from bakasur.database import BakasurDB
from bakasur.dashboard import display

app = typer.Typer()


@app.callback(invoke_without_command=True)
def run():
    console.rule("[bold red] Welcome to Bakasur!")
    console.print(
        'Bakasur is your friendly demon :ogre: who helps you track your Thuisbezorgd order history and visualise it.',
        style="bold white", justify="left", crop=True)
    console.rule("[bold red] ***")

    if not token_file_exists():
        user = typer.prompt("Please enter your email id", type=str)
        password = typer.prompt("Please enter your password", type=str, hide_input=True)

        loginObj = Login(username=user, password=password)
        result = loginObj.attempt_login()
        if result == 'LOGIN PENDING':
            # console.log(result)
            vcode = typer.prompt("Please enter the verification code", type=str)
            loginObj.attempt_login(vcode=vcode)
        else:
            console.print(":warning: [red]Login attempt failed. Please check your credentials.")
            return

    if db_file_exists():
        db = BakasurDB()
        db.init_db()
        store_orders(db, store_recent=True)
    else:
        db = BakasurDB()
        db.init_db()
        db.create_db()
        store_orders(db, store_recent=False)

    orders_df, order_details_df = db.export_to_df()
    display(orders_df, order_details_df)


@app.command()
def reset():
    """
    This command deletes the DB, token files to start a new session
    """
    pass


if __name__ == "__main__":
    app()
