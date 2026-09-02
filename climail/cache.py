import sqlite3
from platformdirs import user_config_path
import typer
from rich import print
from rich.panel import Panel
from typing import Annotated

app = typer.Typer()
PRJ_DIR = user_config_path() / "CLIMAIL"
CACHE_FILE = PRJ_DIR / "climail.db"

@app.callback()
def connect_db(ctx: typer.Context):
    conn = sqlite3.connect(CACHE_FILE)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS email_sent(
        ID INTEGER PRIMARY KEY,
        Date_sent TEXT NOT NULL,
        Recipient TEXT NOT NULL,
        Sender TEXT NOT NULL,
        Subject TEXT,
        Body TEXT
    );
    """)

    cursor = conn.execute("""
    SELECT EXISTS (
        SELECT 1 FROM email_sent LIMIT 1
    ); 

    """)
    result = bool(cursor.fetchone()[0])
    ctx.ensure_object(dict)
    ctx.obj["db"] = conn
    ctx.obj["result"] = result    

@app.command("subject")
def get_subjects(ctx: typer.Context):
    result = ctx.obj["result"]
    conn = ctx.obj["db"]
    if not result:
        conn.close()
        typer.echo("No emails has been sent yet")
        raise typer.Exit()

    cursor = conn.execute("""
    SELECT ID, Subject FROM email_sent;
    """)

    data = cursor.fetchall()
    for row in data:
        id = row[0]
        subject = row[1]
        typer.echo(f"ID: {id} | Subject: {subject}\n")

    conn.close()

@app.command("read")
def see_mail(ctx :typer.Context, id: int = None):
    result = ctx.obj["result"]
    conn = ctx.obj["db"]
    if not result:
        conn.close()
        typer.echo("No emails has been sent yet")
        raise typer.Exit()

    if id is None:
        id = typer.prompt("Enter email ID", default=int)
    
    cursor = conn.execute("SELECT Subject, Date_sent, Recipient, Sender, Body FROM email_sent WHERE ID = ?",
    (id,)
    )
    data = cursor.fetchone()
    if data is None:
        conn.close()
        typer.echo("No email message of that ID found")
        raise typer.Exit()

    subject = data[0]
    date_sent = data[1]
    recipient = data[2]
    sender = data[3]
    body = data[4]
    content = Panel(
        f"[bold]From:[/bold] {sender}\n"
        f"[bold]To:[/bold] {recipient}\n"
        f"[bold]Date:[/bold] {date_sent}\n\n"
        f"{body}",
        title=f"[bold]{subject}[/bold]"
    )
    print(content)

    conn.close()
    
@app.command()
def delete_row(ctx: typer.Context, delete_all: Annotated[bool, typer.Option("--something", help="Delete all the email sent records")] = False):
    result = ctx.obj["result"]
    conn = ctx.obj["db"]
    if not result:
        conn.close()
        typer.echo("No email message to delete")
        raise typer.Exit()

    if delete_all:
        conn.execute("DELETE FROM email_sent;")
        conn.commit()
        conn.close()
        typer.echo("All records deleted")
        raise typer.Exit()
    
    id = typer.prompt("Enter email ID", default=int)
    conn.execute("DELETE FROM email_sent WHERE ID = ?", (id,))
    conn.commit()
    conn.close()
    typer.echo("Email message record successfully deleted")

def store_data(date_sent, recipient, sender, subject, body):
    conn = sqlite3.connect(CACHE_FILE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS email_sent(
            ID INTEGER PRIMARY KEY,
            Date_sent TEXT NOT NULL,
            Recipient TEXT NOT NULL,
            Sender TEXT NOT NULL,
            Subject TEXT,
            Body TEXT
        );
        """)

    try:
        conn.execute("""
        INSERT INTO email_sent (Date_sent, Recipient, Sender, Subject, Body)
        VALUES (?, ?, ?, ?, ?);
        """, (date_sent, recipient, sender, subject, body))
        conn.commit()
    except sqlite3.Error as e:
        print("Error adding email message to db", e)
    finally:
        conn.close()
