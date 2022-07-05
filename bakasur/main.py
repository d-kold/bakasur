import typer

from bakasur.constants import console
from bakasur.helpers import Login

app = typer.Typer()


@app.callback(invoke_without_command=True)
def callback():
    """
    Bakasur
    """


@app.command()
def login():
    user = typer.prompt("Please enter your email id", type=str)
    password = typer.prompt("Please enter your password", type=str, hide_input=True)

    loginObj = Login(username=user, password=password)
    result = loginObj.attempt_login()
    if result == 'LOGIN PENDING':
        console.log(result)
        vcode = typer.prompt("Please enter the verification code", type=str)
        result = loginObj.attempt_login(vcode=vcode)

    console.log(result)


@app.command()
def fetch(
        save: bool = typer.Option(False, help="Save your orders to a sqlite db on your local filesystem")
):
    console.print("Fetching all your orders orders")


@app.command()
def info():
    with console.capture() as capture:
        console.rule("[bold red] Welcome to bezorg-analytics!")
        console.print('''
                  This tool helps you analyse your orders from Thuisbezorgd by fetching your order history.
                  Additionally, you can store your data in a database to visualise your orders and generate interesting insights.
                  ''', style="bold white", justify="center", crop=False)
        console.rule("[bold red] ***")

    print(capture.get())
