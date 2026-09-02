import typer
from .email_receive import app as email_receive
from .auth import app as account_app
from .email_send import app as email_send
from .cache import app as store

app = typer.Typer()
app.add_typer(account_app, name = "acc")
app.add_typer(email_receive, name = "receive")
app.add_typer(email_send, name = "send")
app.add_typer(store, name="store")

if __name__ == "__main__":
    app()


    
