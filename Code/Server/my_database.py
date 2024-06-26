import logging
import asyncpg
import os
import asyncio


BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(
    filename=os.path.join(BASE_FOLDER, "database.log"),
    level=logging.ERROR,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)
logger = logging.getLogger(__name__)


class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        while self.pool is None:
            try:
                self.pool = await asyncpg.create_pool(
                    database='postgres',
                    user='postgres',
                    password='mysecretpassword',
                    host='db'
                )
            except Exception as e:
                logger.error(f"Failed to connect to database: {str(e)}")
                self.pool = None
                await asyncio.sleep(5)

    async def close(self):
        if self.pool is not None:
            await self.pool.close()

    async def create_table(self):
        if self.pool is None:
            logger.error("Cannot create table: No database connection")
            return
        try:
            await self.pool.execute("""
                CREATE TABLE IF NOT EXISTS computers (
                    id SERIAL PRIMARY KEY,
                    comp_uuid UUID,
                    name VARCHAR(255),
                    update_status BOOLEAN,
                    reboot_required BOOLEAN,
                    update_count INTEGER DEFAULT 0
                )
            """)
            logger.info("Successfully created the 'computers' table.")
        except Exception as e:
            logger.error(f"Failed to create table: {str(e)}")

    async def insert_computer(self,
                              comp_uuid,
                              name,
                              update_status,
                              reboot_required):
        try:
            # Try to update the record
            result = await self.pool.execute(
                """
                UPDATE computers
                SET
                    name = $2,
                    update_status = $3,
                    reboot_required = $4,
                    update_count = computers.update_count + 1
                WHERE comp_uuid = $1
                """,
                comp_uuid, name, update_status, reboot_required
            )

            # If no record was updated, insert a new one
            if result == 'UPDATE 0':
                await self.pool.execute(
                    """
                    INSERT INTO computers
                        (
                            comp_uuid,
                            name,
                            update_status,
                            reboot_required,
                            update_count
                        )
                    VALUES
                        ($1, $2, $3, $4, 1)
                    """,
                    comp_uuid, name, update_status, reboot_required
                )
        except Exception as e:
            error_message = f"Failed to insert or update computer: {str(e)}"
            logger.error(error_message)

    async def get_computers(self):
        try:
            result = await self.pool.fetch('SELECT * FROM computers')
            return result
        except Exception as e:
            logger.error(f"Failed to get computers: {str(e)}")
            return None
