import os
import logging
import time
from my_database import Database
from fastapi import FastAPI


BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(
    filename=os.path.join(BASE_FOLDER, "error.log"),
    level=logging.ERROR,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()
db = Database()


@app.on_event("startup")
async def startup():
    try:
        await db.connect()
        await db.create_table()
    except Exception as e:
        logger.error(f"Failed to connect to database: {str(e)}")
        time.sleep(3)
        startup()


@app.on_event("shutdown")
async def shutdown():
    await db.close()


@app.get("/")
def read_root():
    return {"Hello, tresspassser"}


@app.get("/get-computers")
async def get_computers():
    try:
        computers = await db.get_computers()
        return computers
    except Exception as e:
        logger.error(f"Failed to get computers: {str(e)}")
        return {"error": "Failed to get computers"}


@app.post("/add-computer")
async def add_computer(name: str, update_status: bool, reboot_required: bool):
    try:
        await db.insert_computer(name, update_status, reboot_required)
        return {"message": "Computer added successfully"}
    except Exception as e:
        logger.error(str(e))
        return {"error": "An error occurred while adding the computer"}


@app.get("/clear-computers")
async def clear_computers():
    # This is a dangerous operation, so we should add some
    # kind of authentication
    try:
        await db.conn.execute("DELETE FROM computers")
        return {"message": "Computers cleared successfully"}
    except Exception as e:
        logger.error(f"Failed to clear computers: {str(e)}")
        return {"error": "An error occurred while clearing computers"}

if __name__ == "__main__":
    try:
        if __name__ == "__main__":
            os.system("uvicorn server:app --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"An error occurred: {e}")
