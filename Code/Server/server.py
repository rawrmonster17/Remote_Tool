import os
import psycopg2
import logging
import asyncpg
from fastapi import FastAPI


BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(filename=os.path.join(BASE_FOLDER, "error.log"), level=logging.ERROR, 
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.conn = None

    async def connect(self):
        try:
            self.conn = await asyncpg.connect(
                database='postgres',
                user='postgres',
                password='mysecretpassword',
                host='172.18.0.2'
            )
        except Exception as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            self.conn = None

    async def close(self):
        if self.conn is not None:
            await self.conn.close()

    async def create_table(self):
        try:
            await self.conn.execute("""
                CREATE TABLE IF NOT EXISTS computers (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255),
                    update_status BOOLEAN,
                    reboot_required BOOLEAN,
                    update_count INTEGER DEFAULT 0
                )
            """)
            logger.info("Successfully created the 'computers' table.")
        except Exception as e:
            logger.error(f"Failed to create table: {str(e)}")

    async def insert_computer(self, name, update_status, reboot_required):
        try:
            # Check if the computer already exists
            computer = await self.conn.fetchrow('SELECT * FROM computers WHERE name = $1', name)
            if computer is None:
                # If the computer doesn't exist, insert a new record
                await self.conn.execute("""
                    INSERT INTO computers (name, update_status, reboot_required, update_count)
                    VALUES ($1, $2, $3, 1)
                """, name, update_status, reboot_required)
            else:
                # If the computer exists, update the record and increment the update count
                await self.conn.execute("""
                    UPDATE computers
                    SET update_status = $2, reboot_required = $3, update_count = update_count + 1
                    WHERE name = $1
                """, name, update_status, reboot_required)
        except Exception as e:
            logger.error(f"Failed to insert or update computer: {str(e)}")
    
    async def get_computers(self):
        try:
            result = await self.conn.fetch('SELECT * FROM computers')
            return result
        except Exception as e:
            logger.error(f"Failed to get computers: {str(e)}")
            return None

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello, tresspassser"}

@app.get("/get-computers")
async def get_computers():
    try:
        db = Database()
        await db.connect()
        await db.create_table()  # Create the table if it doesn't exist
        computers = await db.get_computers()
        await db.close()
        return computers
    except Exception as e:
        logger.error(f"Failed to get computers: {str(e)}")
        return {"error": "Failed to get computers"}

@app.post("/add-computer")
async def add_computer(name: str, update_status: bool, reboot_required: bool):
    try:
        db = Database()
        await db.connect()
        await db.create_table()  # Create the table if it doesn't exist
        await db.insert_computer(name, update_status, reboot_required)
        await db.close()
        return {"message": "Computer added successfully"}
    except Exception as e:
        logger.error(str(e))
        return {"error": "An error occurred while adding the computer"}

@app.get("/clear-computers")
async def clear_computers():
    try:
        db = Database()
        await db.connect()
        await db.create_table()  # Create the table if it doesn't exist
        await db.conn.execute("DELETE FROM computers")
        await db.close()
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