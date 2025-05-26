from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from library.database import database
from fastapi import FastAPI, Request
app = FastAPI()

# Mount a static directory to serve CSS/JS/images
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

class pages:
    @staticmethod
    @app.get("/", response_class=HTMLResponse)
    async def homepage(request: Request):
        return templates.TemplateResponse("home.html", {"request": request})

    @staticmethod
    @app.get("/bot", response_class=HTMLResponse)
    async def bot_page(request: Request):
        return templates.TemplateResponse("bot.html", {"request": request})

    @staticmethod
    @app.get("/webui", response_class=HTMLResponse)
    async def bot_page(request: Request):
        return templates.TemplateResponse("webui.html", {"request": request})

    @staticmethod
    @app.get("/bug/{bug_id}", response_class=HTMLResponse)
    async def view_bug(bug_id: int, request: Request):
        bug = database.get_bug_report(bug_id)

        date = bug['date'].strftime("%d/%m/%Y %I:%M:%S %p")

        bug_data = {
            "ticket_id": bug_id,
            "stated_bug": bug['stated_bug'],
            "reproduce": bug['reproduction'],
            "resolved": bug['resolved'],
            "extra_info": bug['extra_info'],
            "exception": bug['exception'],
            "reporter": bug['reporter_id'],
            "date_reported": date
        }
        return templates.TemplateResponse("bugticket.html", {"request": request, "bug": bug_data})

# noinspection PyUnusedLocal
class bugs_api:
    @staticmethod
    @app.get("/api/")
    async def root(request: Request):
        return {"message": "Hello World! This is the root API End point."}

    @staticmethod
    @app.get("/api/buglist")
    async def buglist(request: Request):
        # Returns a list of all the unresolved bugs in the database.
        data = database.list_unresolved_bug_reports()
        return data

    @staticmethod
    @app.post("/api/bug/set_resolved")
    async def set_resolved(request: Request):
        data = await request.json()
        bug_id = data.get("bug_id")

        if bug_id is None:
            return {"success": False, "message": "Missing ticket_id in request body."}

        success = database.mark_report_solved(bug_id)

        if success:
            return {"success": True, "message": f"Bug report {bug_id} has been marked as resolved."}
        else:
            return {"success": False, "message": f"Error while marking report {bug_id} as resolved."}

class ban_api:
    @staticmethod
    @app.get("/api/bans/list")
    async def list_all():
        bans = database.list_bans()
        return JSONResponse(bans, 200)

    @staticmethod
    @app.post("/api/bans/add")
    async def ban(request: Request):
        data = await request.json()
        user_id = data.get("user_id")
        ban_reason = data.get("ban_reason")

        success = database.ban_user(user_id, ban_reason)
        if success:
            return JSONResponse({"success": True}, 200)
        else:
            return JSONResponse({"success": False}, 400)

bot_order_queue = []
class BotOrders:
    valid_bug_resolutions = [
        "resolved",
        "intended",
        "duplicate",
        "no-reproduce",
        "wont_fix"
    ]

    @staticmethod
    @app.post("/api/bot/order/queue")
    async def queue_order(request: Request):
        data = await request.json()

        bug_id = data.get("bug_id")
        resolution = data.get("resolution")
        order = data.get("order")

        bug_info = database.get_bug_report(bug_id)
        reporter_id = bug_info['reporter_id']

        bot_order_queue.append({
            "order": order,
            "info": {
                "reporting_user_id": reporter_id,
                "report_id": bug_id,
                "resolution": resolution,
            }
        })
        return {"success": True}

    @staticmethod
    @app.get("/api/bot/pending_orders")
    async def get_orders():
        global bot_order_queue
        orders = bot_order_queue.copy()
        bot_order_queue.clear()
        return orders