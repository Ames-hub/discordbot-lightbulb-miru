# Bot Template
This repository hosts a template for a Hikari-based discord bot.

## Deployment
To set up the repository, you need to run the file 'bootstrap.py'
with the following terminal command:
```shell
cd (FULL PROJECT DIRECTORY LOCATION)
python3.12 -m venv venv
```
And after running that,
on Windows, run:
```
./venv/scripts/activate
```
But for Linux:
```shell
source venv\bin\activate
```
And then for either Operating system, run
```shell
pip install -r requirements.txt
python bootstrap.py
```

You will need to get from the discord developer portal a bot token.<br>

## Post-Deployment
After it has been successfully deployed, the intended way to run the project is
using only the file located in the root directory of the project,
"initialize.py"

## Environment Variables
Upon a successful bootstrapped deployment, we'll have set for you some environment
variables that you can make use of for your bot and webui.

### Bot Variables
- BOT_TOKEN
- BOT_NAME
- DB_PASSWORD
- DB_PORT (the port on your HOST machine, not the docker container)
- PRIMARY_MAINTAINER_ID (the discord ID you entered when bootstrapping the bot)

### WebUI Variables
- WEBUI_ENABLED
- DB_PASSWORD
- DB_PORT (again, host port.)
- BOT_NAME

## Dependencies
- Python3.12
- Docker start, stop, run and rm Permissions<br>
For the above, we will only manage our own PostgreSQL database.

## Docker problems?
Try running in the project working directory (where bootstrap.py is)
```shell
docker-compose down -v
```
It'll basically do a reset for the docker-compose. Might work if you've tried
this before.
Won't help if this is your first time running the bootstrapper.

## Technology

- Python3.12
- Hikari-Lightbulb
- Hikari-Miru Enabled
- Built-in PostgreSQL Database Manager
- Admin Web interface with FastAPI
- WebUI bug tracking
- WebUI User banning (prevent users from accessing bot)