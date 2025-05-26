from .botapp import botapp, tasks
from .database import database
import logging
import hikari

# This must match what FastAPI sends
ORDER_API_URL = "http://webui:80/api/bot/pending_orders"

valid_orders = {
    "ALERT_USER_BUG_REPORT_RESOLUTION"
}

valid_bug_resolutions = [
    "resolved",
    "intended",
    "duplicate",
    "no-reproduce",
    "wont_fix"
]

async def execute_order(order: dict):
    """Direct execution of an order dict"""
    order_type = order.get("order")
    order_info = order.get("info")

    if order_type not in valid_orders:
        logging.warning(f"Invalid order type: {order_type}")
        return

    if order_type == "ALERT_USER_BUG_REPORT_RESOLUTION":
        resolution = order_info.get('resolution')
        if resolution not in valid_bug_resolutions:
            logging.warning(f"Invalid resolution: {resolution}")
            return

        user_id = order_info.get('reporting_user_id')
        report_id = order_info.get('report_id')

        if not all([user_id, report_id]):
            logging.warning("Missing user_id or report_id")
            return

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
            logging.warning("Invalid bug report ID")
            return

        embed.add_field(
            name="Information about your report",
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
            logging.warning("Forbidden: Cannot DM user.")