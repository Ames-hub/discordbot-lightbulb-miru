import subprocess
import psycopg2
import platform
import secrets
import random
import socket
import time
import json
import os

def port_is_used(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def init_bootstrap():
    if platform.system() == "Darwin":
        print(
            "Warning: MacOS has not been tested.\n"
            "This could cause problems of any kind or description.\n"
            "Here be dragons."
        )

    while True:
        BOT_NAME = input("Enter the name of your bot: ")
        if " " in BOT_NAME:
            print("Bot name cannot contain spaces. Please enter a different name.")
            continue
        elif len(BOT_NAME) < 1:
            print("Bot name must be at least 1 character long. Please enter a different name.")
            continue
        else:
            break

    while True:
        print("You'll need to have obtained a Bot Token from Discord's developer panel.")
        BOT_TOKEN = input("Please enter your bot's token: ")
        VALID_TOKEN = len(BOT_TOKEN.split(".")) == 3
        if VALID_TOKEN:
            print("Bot token is valid.")
            break
        else:
            print("Invalid bot token. Please enter a valid token.")
            continue

    while True:
        try:
            DB_PORT = input(
                "Enter a port number to bind on your host machine for your database.\n"
                "Leave this field blank to let us decide: "
            )
            if DB_PORT == "" or DB_PORT.lower() == "blank":
                DB_PORT = random.randint(5432, 65535)
            DB_PORT = int(DB_PORT)

            if port_is_used(DB_PORT):
                print("Port is already in use. Please enter a different port number.")
                continue

            break
        except ValueError:
            print("Invalid input. Please enter a valid port number.")

    while True:
        WEBUI_ENABLED = input("Would you like to enable the web UI? (y/n): ")
        if WEBUI_ENABLED.lower() == "y":
            WEBUI_ENABLED = True
            break
        elif WEBUI_ENABLED.lower() == "n":
            WEBUI_ENABLED = False
            break
        else:
            print("Invalid input. Please enter 'y' or 'n'.")
            continue

    WEBUI_CONTAINER_NAME = f"{BOT_NAME.lower().replace(' ', '_')}-webui"
    if WEBUI_ENABLED:
        while True:
            try:
                WEBUI_PORT = input(
                    "Enter what port you use to access your webUI on your Devices.\n"
                    "Leave this field blank to let us decide: "
                )
                if WEBUI_PORT == "" or WEBUI_PORT.lower() == "blank":
                    WEBUI_PORT = random.randint(1024, 65535)
                WEBUI_PORT = int(WEBUI_PORT)

                if port_is_used(WEBUI_PORT):
                    print("Port is already in use. Please enter a different port number.")
                    continue

                break
            except ValueError:
                print("Invalid input. Please enter a valid port number.")
    else:
        WEBUI_PORT = None

    while True:
        PRIMARY_MAINTAINER_ID = input("Enter your Discord ID: ")
        if PRIMARY_MAINTAINER_ID.isdigit():
            break
        else:
            print("Invalid input. Please enter a valid Discord ID. This is seperate from your username. Numbers only, no spaces or anything.")
            continue

    DB_PASSWORD = secrets.token_urlsafe(32)
    PG_CONTAINER_NAME = f"{BOT_NAME.lower().replace(' ', '_')}-postgre"
    BOT_CONTAINER_NAME = f"{BOT_NAME.lower().replace(' ', '_')}-bot"

    docker_compose_content = f"""
services:
  postgres:
    image: postgres:15
    container_name: {PG_CONTAINER_NAME}
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: {DB_PASSWORD}
      POSTGRES_DB: postgre
    ports:
      - "{DB_PORT}:5432"
    networks:
      - botnet
    volumes:
      - pgdata:/var/lib/postgresql/data

  bot:
    build:
      context: ./bot
    container_name: {BOT_CONTAINER_NAME}
    environment:
      BOT_NAME: {BOT_NAME}
      BOT_TOKEN: {BOT_TOKEN}
      DB_PASSWORD: {DB_PASSWORD}
      DB_PORT: {DB_PORT}
      PRIMARY_MAINTAINER_ID: {PRIMARY_MAINTAINER_ID}
    depends_on:
      - postgres
    networks:
      - botnet
"""

    if WEBUI_ENABLED:
        docker_compose_content += f"""
  webui:
    build:
      context: ./webui
    container_name: {WEBUI_CONTAINER_NAME}
    environment:
      BOT_NAME: {BOT_NAME}
      WEBUI_ENABLED: {WEBUI_ENABLED}
      DB_PASSWORD: {DB_PASSWORD}
      DB_PORT: {DB_PORT}
    depends_on:
      - postgres
    ports:
      - "{WEBUI_PORT}:80"
    networks:
      - botnet
"""

    docker_compose_content += """
networks:
  botnet:

volumes:
  pgdata:
"""

    with open("docker-compose.yml", "w") as f:
        f.write(docker_compose_content.strip())

    print("Docker Compose file written successfully.")

    print("Setup complete!")
    # build with no cache
    subprocess.run(["docker-compose", "build", "--no-cache"], check=True)

    # start the containers
    subprocess.run(["docker-compose", "up", "-d"], check=True)
    print("All containers started successfully via Docker Compose.")

    # Waits until DB Is available, then creates db 'appdata'
    tries = 0
    while True:
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=DB_PORT,
                database="postgre",
                user="postgres",
                password=DB_PASSWORD
            )
            print("Connected to database successfully as user postgre.")
            conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
            cur = conn.cursor()
            cur.execute("CREATE DATABASE appdb;")
            conn.close()
            print("Database 'appdb' created successfully.")
            break
        except psycopg2.OperationalError as err:
            time.sleep(3)
            if tries >= 10:
                print("Failed to connect to database 10 times in a row. Exiting.")
                raise err
            print("Failed to connect to database. Trying again")

    with open("configuration.json", "w") as f:
        json.dump({
            "setup_complete": True,
            "PRIMARY_MAINTAINER_ID": PRIMARY_MAINTAINER_ID,
            "bot_name": BOT_NAME,
            "bot_token": BOT_TOKEN,
            "db_port": DB_PORT,
            "db_password": DB_PASSWORD,
            "webui_enabled": WEBUI_ENABLED,
            "container_names": {
                "PG": PG_CONTAINER_NAME,
                "WEBUI": WEBUI_CONTAINER_NAME,
                "BOT": BOT_CONTAINER_NAME
            }
        }, f)

    print(
        "Here is a summary of what we've done:\n"
        f"1. Generated PostgreSQL service config: \"{PG_CONTAINER_NAME}\"\n"
        f"{f'2. Generated FastAPI WebUI config: {WEBUI_CONTAINER_NAME}\n' if WEBUI_ENABLED else '2. Skipped WebUI setup.\n'}"
        f"3. Configured Discord bot container: {BOT_CONTAINER_NAME}\n"
        "4. Started all above services.\n"
        "5. Created database 'appdb' in PostgreSQL.\n"
        "6. Wrote configuration.json file.\n"
        "7. Wrote the docker-compose.yml file."
    )
    print("Setup complete. Please run initialize.py to start up the project containers in the future.")

if __name__ == "__main__":
    if os.path.exists("configuration.json"):
        with open("configuration.json", "r") as f:
            configuration = json.load(f)
            setup_complete = configuration.get("setup_complete", True)
            if setup_complete:
                print("Setup already seems to have been completed. If this is the case, please instead run the file \"initialize.py\" to start up the bot. Bootstrap.py is for setup only.")
                exit(1)
            else:
                init_bootstrap()
    else:
        init_bootstrap()
