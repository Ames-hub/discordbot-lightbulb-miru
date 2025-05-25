from .database import database
from .botapp import botapp
from aiohttp import web
import logging
import hikari

"""
This is meant to be a simple API for the bot to communicate with the frontend.
NOTHING more. No security, little validation, no nothing. DO NOT EXPOSE THIS API TO THE WORLD.
"""

valid_orders = {
    "ALERT_USER_BUG_REPORT"
}

valid_bug_resolutions = [
    "resolved",
    "intended",
    "duplicate",
    "no-reproduce",
    "wont_fix"
]

async def execute_order(request):
    try:
        data = await request.json()
    except Exception as err:
        logging.error(err)
        return web.Response(status=400, text="Invalid JSON.")

    order = data.get('order')
    order_info = data.get('info')

    if order not in valid_orders:
        return web.Response(status=400, text="Invalid order.")

    if order == "ALERT_USER_BUG_REPORT":
        resolution = order_info.get('resolution')
        if resolution not in valid_bug_resolutions:
            return web.Response(status=400, text="Invalid resolution.")

        user_id = order_info.get('user_id')
        report_id = order_info.get('report_id')

        if not all([user_id, report_id]):
            return web.Response(status=400, text="Missing user_id or report_id.")

        dmc = await botapp.rest.create_dm_channel(int(user_id))

        resolved_check = "✅" if resolution in ["resolved", 'intended'] else "❌"

        embed = (
            hikari.Embed(
                title=f"Report #{report_id}",
                description=f"Resolved status: {resolved_check}"
            )
        )

        bug_data = database.get_bug_report(report_id)
        if not bug_data:
            return web.Response(status=400, text="Bad report ID.")

        embed.add_field(
            name=f"Information about your report",
            value=f"Stated Bug: {bug_data['stated_bug']}\n"
                  f"How to cause it: {bug_data['reproduction']}\n"
                  f"Additional Info: {bug_data['extra_info']}"
        )

        resolution_messages = {
            "resolved": "This bug has been resolved, and the fix will be rolled out as soon as possible.\nThank you for reporting the bug!",
            "intended": "The reported bug is actually not a bug, and is an intended feature and will not be 'fixed'",
            "duplicate": "Thank you for reporting! We've been informed of this and are working to handle it.",
            "no-reproduce": "We couldn't reproduce this bug due to lack of info or luck-based reproduction. It can't be fixed as-is.",
            "wont_fix": "Thank you for reporting this bug. However, due to its nature, we have decided not to fix this bug."
        }

        embed.add_field(name="Resolution", value=resolution_messages[resolution])

        try:
            await dmc.send(embed)
        except hikari.ForbiddenError:
            return web.Response(status=403, text="Forbidden")

    return web.Response(status=200, text="All good")


app = web.Application()
app.router.add_post("/api/order", execute_order)

def run_api():
    print("API STARTUP INITIATED")
    web.run_app(app, port=8000)
