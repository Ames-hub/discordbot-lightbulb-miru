from library.orderapi import run_api
from library.database import dbman
from library.botapp import botapp
import multiprocessing
import psycopg2
import datetime
import logging
import hikari
import time
import sys
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename=f"logs/{datetime.date.today()}.log",
)

def wait_for_pg():
    password = os.environ.get("DB_PASSWORD")
    DEBUG = "debug" in sys.argv or os.environ.get("debug", 'false').lower() == "true"

    user = "postgres"
    port = 5432
    dbname = "appdb"
    db_password = os.environ.get("DB_PASSWORD")
    if not DEBUG:
        db_host = "postgres"
    else:
        db_host = "127.0.0.1"
        if db_password is None:
            print("You are in debug mode. For this, you must set your DB_PASSWORD environment variable. Else, we cannot start.")

    tries = 0
    while True:
        try:
            conn = psycopg2.connect(host=db_host, port=port, user=user, password=password, dbname=dbname)
            conn.close()
            logging.info("Connected to database successfully.")
            print("Connected to database successfully.")
            break
        except psycopg2.OperationalError as err:
            if tries > 15:
                print("Failed to connect to database 15 times in a row. Raising original exception.")
                logging.error("Failed to connect to database 15 times in a row. Raising original exception.", err)
                raise err
            tries += 1
            logging.warning(f"Waiting for database... ({tries}/15)")
            print("Waiting for database...")
            time.sleep(2)

wait_for_pg()

os.makedirs("logs", exist_ok=True)

botapp.d['BOT_NAME'] = os.environ.get('BOT_NAME', 'EnvVarKeyError')  # TODO: Make this configurable in WebUI
botapp.d['WEBUI_ENABLED'] = os.environ.get('WEBUI_ENABLED', 'false').lower() == "true"
botapp.d['orders'] = []

dbman.modernize()

botapp.load_extensions_from("cogs/bugs")

if __name__ == "__main__":
    try:
        api_proc = multiprocessing.Process(
            target=run_api,
            daemon=True,
        )
        api_proc.start()

        botapp.run(
            shard_count=1  # Default. TODO: Make this configurable in WebUI.
        )
    except hikari.UnauthorizedError as err:
        print(f"Unauthorized. Did you enter your token correctly? Error: {err}")
        print(f"Token Entered: {os.environ.get('BOT_TOKEN')} | type: {type(os.environ.get('BOT_TOKEN'))}")