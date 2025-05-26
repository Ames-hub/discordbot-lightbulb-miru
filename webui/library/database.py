"""
The two files in /bot/library/database and /webui/library/database are more or less the same.
This is because they both use the same database and access the same data, and would be in containers in production.
"""
import psycopg2
import logging
import inspect
import sys
import os

DEBUG = "debug" in sys.argv or os.environ.get("debug", 'false').lower() == "true"

if DEBUG:
    print("Running in debug mode.")
else:
    print("Running in production mode.")

db_user = "postgres"
db_port = 5432
db_name = "appdb"
db_password = os.environ.get("DB_PASSWORD")
if not DEBUG:
    db_host = "postgres"
else:
    db_host = "127.0.0.1"
    if db_password is None:
        print("You are in debug mode. For this, you must set your DB_PASSWORD environment variable. Else, we cannot start.")

class dbman:
    @staticmethod
    def connect():
        return psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name,
        )

class database:
    @staticmethod
    def list_bans():
        conn = dbman.connect()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT case_id, banned_username, banned_id, reason, timestamp FROM ban_list ORDER BY timestamp DESC; -- Timestamp DESC to get newest first.
                """
            )
            bans = cur.fetchall()
            cur.close()

            # Formats to dict
            formatted_bans = {}
            for ban in bans:
                formatted_bans[ban[0]] = {
                    "case_id": ban[0],
                    "banned_username": ban[1],
                    "banned_id": ban[2],
                    "reason": ban[3],
                    "timestamp": ban[4]
                }

            return formatted_bans

        except (psycopg2.errors.OperationalError, psycopg2.errors.ProgrammingError) as err:
            logging.error(f"There was a database error in file {inspect.stack()[0][1]}, line {inspect.stack()[0][2]}: {err}", exc_info=err)
            conn.close()
            return None

    @staticmethod
    def ban_user(user_uuid, ban_reason):
        conn = dbman.connect()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO ban_list (banned_id, reason) VALUES (%s, %s);
                """,
                (user_uuid, ban_reason)
            )
            conn.commit()
            cur.close()
            conn.close()
            return True
        except (psycopg2.errors.OperationalError, psycopg2.errors.ProgrammingError) as err:
            logging.error(f"There was a database error in file {inspect.stack()[0][1]}, line {inspect.stack()[0][2]}: {err}", exc_info=err)
            conn.rollback()
            conn.close()
            return False

    @staticmethod
    def get_bug_report(bug_report_id):
        conn = dbman.connect()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT reporter_id, report_id, stated_bug, reproduction, extra_info, exception, resolved, date
                FROM bug_reports WHERE report_id = %s;
                """,
                (bug_report_id,)
            )
            report = cur.fetchone()
            cur.close()
            return {
                "reporter_id": report[0],
                "report_id": report[1],
                "stated_bug": report[2],
                "reproduction": report[3],
                "extra_info": report[4],
                "exception": report[5],
                "resolved": report[6],
                "date": report[7]
            }
        except (psycopg2.errors.OperationalError, psycopg2.errors.ProgrammingError) as err:
            logging.error(f"There was a database error in file {inspect.stack()[0][1]}, line {inspect.stack()[0][2]}: {err}", exc_info=err)
            conn.close()
            return None

    @staticmethod
    def list_unresolved_bug_reports():
        conn = dbman.connect()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT reporter_id, report_id, stated_bug, reproduction, extra_info, exception, resolved, date
                FROM bug_reports WHERE resolved = FALSE;
                """
            )
            raw_reports = cur.fetchall()
            cur.close()

            reports = {}
            for report in raw_reports:
                reports[report[1]] = {
                    "reporter_id": report[0],
                    "report_id": report[1],
                    "stated_bug": report[2],
                    "reproduction": report[3],
                    "extra_info": report[4],
                    "exception": report[5],
                    "resolved": report[6],
                    "date": report[7]
                }

            return reports
        except (psycopg2.errors.OperationalError, psycopg2.errors.ProgrammingError) as err:
            logging.error(f"There was a database error in file {inspect.stack()[0][1]}, line {inspect.stack()[0][2]}: {err}", exc_info=err)
            conn.close()
            return None

    @staticmethod
    def mark_report_solved(report_id:int):
        conn = dbman.connect()
        try:
            cur = conn.cursor()
            cur.execute(
                """UPDATE bug_reports SET resolved = TRUE WHERE report_id = %s;""",
                (int(report_id),)
            )
            conn.commit()
            cur.close()
            conn.close()
            return True
        except (psycopg2.errors.OperationalError, psycopg2.errors.ProgrammingError) as err:
            logging.error(f"There was a database error in file {inspect.stack()[0][1]}, line {inspect.stack()[0][2]}: {err}", exc_info=err)
            conn.rollback()
            conn.close()
            return False