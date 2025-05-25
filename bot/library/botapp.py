from lightbulb.ext import tasks
import lightbulb
import miru
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "none")
if BOT_TOKEN == "none":
    raise Exception("BOT_TOKEN is not set in environment variables. Please set it.")

botapp = lightbulb.BotApp(token=BOT_TOKEN)

tasks.load(botapp)  # Tasks enabled
miru_client = miru.Client(botapp)  # Miru Enabled