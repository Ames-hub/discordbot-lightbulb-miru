from library.orderapi import execute_order
from library.botapp import tasks
import lightbulb
import logging
import httpx
import sys
import os

DEBUG = "debug" in sys.argv or os.environ.get("debug", 'false').lower() == "true"
plugin = lightbulb.Plugin(__name__)

@tasks.task(s=10, wait_before_execution=True, auto_start=DEBUG is not True)
async def poll_orders():
    """Polls the FastAPI for any new orders"""
    while True:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://webui:80/api/bot/pending_orders")
                if response.status_code == 200:
                    orders = response.json()
                    for order in orders:
                        await execute_order(order)
        except Exception as err:
            logging.error(f"Error checking orders: {err}", exc_info=err)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)
