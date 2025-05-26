import os.path
import subprocess
import json

def init_project():
    if not os.path.exists("configuration.json"):
        print("Configuration file not found. Please run the file \"bootstrap.py\" to create a configuration file,\n"
              "or drop a pre-existing valid config file in the root directory.")
        exit(0)
    with open("configuration.json", "r") as f:
        configuration:dict = json.load(f)

        PG_CONTAINER_NAME = configuration['container_names']['PG']
        WEBUI_CONTAINER_NAME = configuration['container_names']['WEBUI']
        BOT_CONTAINER_NAME = configuration['container_names']['BOT']
        WEBUI_ENABLED = configuration['webui_enabled']

    subprocess.run(["docker", "start", PG_CONTAINER_NAME], check=True)
    if WEBUI_ENABLED:
        subprocess.run(["docker", "start", WEBUI_CONTAINER_NAME], check=True)
    subprocess.run(["docker", "start", BOT_CONTAINER_NAME], check=True)

    print("All containers started successfully.")
    print("Press CTRL + C to close all programs, or send SIGINT code 2")
    try:
        while True:  # Keep the program running. Wait for Sigint 2
            pass
    except KeyboardInterrupt:
        # On Sigint 2, shutdown containers.
        print("Shutdown signal received.\n"
              "Closed containers:")
        subprocess.run(["docker", "stop", PG_CONTAINER_NAME], check=True)
        if WEBUI_ENABLED:
            subprocess.run(["docker", "stop", WEBUI_CONTAINER_NAME], check=True)
        subprocess.run(["docker", "stop", BOT_CONTAINER_NAME], check=True)
        print("All programs closed successfully.")
        exit(0)

init_project()