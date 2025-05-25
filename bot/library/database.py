import traceback
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

    @staticmethod
    def modernize():
        """
        Modernizes the PostgreSQL database schema to match the current table definition.
        """
        table_dict = {
            'bug_reports': {
                'report_id': 'SERIAL PRIMARY KEY',
                'reporter_id': 'BIGINT NOT NULL',
                'stated_bug': 'TEXT NOT NULL',
                'reproduction': 'TEXT NOT NULL',
                'extra_info': 'TEXT',
                'exception': 'TEXT',
                'resolved': 'BOOLEAN DEFAULT FALSE',
                'date': 'TIMESTAMP DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE \'localtime\')'
            }
        }

        try:
            conn = dbman.connect()
            conn.autocommit = True
            cur = conn.cursor()

            for table_name, columns in table_dict.items():
                # Check if the table exists
                cur.execute("""
                            SELECT EXISTS (
                                SELECT FROM information_schema.tables
                                WHERE table_name = %s
                            );
                            """, (table_name,))
                table_exists = cur.fetchone()[0]

                if table_exists:
                    # Get existing columns
                    cur.execute("""
                                SELECT column_name
                                FROM information_schema.columns
                                WHERE table_name = %s;
                                """, (table_name,))
                    existing_columns = {row[0] for row in cur.fetchall()}

                    for column_name, column_type in columns.items():
                        if column_name not in existing_columns:
                            try:
                                cur.execute(f'ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type};')
                            except Exception as e:
                                logging.error(f"Error adding column {column_name} to {table_name}: {e}")
                else:
                    # Create table
                    columns_str = ', '.join(f'{col} {dtype}' for col, dtype in columns.items())
                    try:
                        cur.execute(f'CREATE TABLE {table_name} ({columns_str});')
                    except Exception as err:
                        logging.error(f"Error creating table {table_name} with columns {columns_str}: {err}")
                        exit(1)

            cur.close()
            conn.close()
        except psycopg2.Error as e:
            logging.error(f"Database connection failed: {e}")
            exit(1)

class database:
    @staticmethod
    def add_bug_report(reporter_id, stated_bug, bug_reproduction, extra_info=None, exception:Exception=None, return_ticket:bool=False):
        # Formats the exception traceback into a string before saving it.
        if exception:
            exception_traceback = traceback.format_exc()
            exception = str(exception) + "\n" + exception_traceback
        else:
            exception = "No Traceback Saved"

        if extra_info is None:
            extra_info = "No Extra Info"

        conn = dbman.connect()
        try:
            cur = conn.cursor()
            cur.execute(
                """INSERT INTO bug_reports (reporter_id, stated_bug, reproduction, extra_info, exception)
                   VALUES (%s, %s, %s, %s, %s)""",
                (reporter_id, stated_bug, bug_reproduction, extra_info, exception)
            )
            conn.commit()
            cur.close()
            if return_ticket:
                ticket_id = cur.lastrowid
                return ticket_id
            return True
        except (psycopg2.errors.OperationalError, psycopg2.errors.ProgrammingError) as err:
            logging.error(f"There was a database error in file {inspect.stack()[0][1]}, line {inspect.stack()[0][2]}: {err}", exc_info=err)
            conn.rollback()
            return False

    @staticmethod
    def get_bug_report(report_id:int):
        conn = dbman.connect()
        try:
            cur = conn.cursor()
            cur.execute(
                """SELECT * FROM bug_reports WHERE report_id = %s""",
                (report_id,)
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
            return None