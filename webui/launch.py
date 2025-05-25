from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from library.database import database
from fastapi import FastAPI, Request
import requests

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
class api:
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

class BotOrders:
    valid_bug_resolutions = [
        "resolved",
        "intended",
        "duplicate",
        "no-reproduce",
        "wont_fix"
    ]

    class bug_reports:
        @staticmethod
        @app.post("/api/bot/order/alert_user")
        def alert_user(report_id: int, resolution: str):
            if resolution not in BotOrders.valid_bug_resolutions:
                return False

            reporter_id = database.get_bug_report(report_id)['reporter_id']

            # noinspection HttpUrlsUsage
            requests.post(
                url=f"http://bot:8000/api/order/",
                json={
                    "order": "ALERT_USER_BUG_REPORT",
                    "info": {
                        "user_id": reporter_id,
                        "report_id": report_id,
                        "resolution": resolution
                    }
                }
            )

            return True