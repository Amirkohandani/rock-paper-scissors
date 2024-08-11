import logging
import aiohttp
import re
import time
import asyncio
import aiosqlite


logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] %(message)s @ %(asctime)s')
logger = logging.getLogger("car_data_logger")

rate_limiter = asyncio.Semaphore(4)


def extract_vehicle_info(html):
    regex = r'"type":"ad".+?url":"(.+?)".+?title":"(.+?)".+?time":"(.+?)".+?year":"(.+?)".+?mileage":"(.+?)".+?location":"(.+?)".+?description":"(.+?)".+?"image":(.+?),"modified_date":"(.+?)".+?price":"(.+?)"'
    vehicles = re.findall(regex, html)
    return vehicles

async def get_data(session, url):
    async with rate_limiter:
        try:
            logger.debug(f"Starting data retrieval for {url}")
            start_time = time.monotonic()
            async with session.get(url, headers=None, ssl=False) as resp:
                logger.debug(f"Received status {resp.status} from {url}")

                if resp.status == 200:
                    html_content = await resp.text()
                    cars_data = extract_vehicle_info(html_content)
                    duration = time.monotonic() - start_time
                    logger.debug(f"Fetched {len(cars_data)} vehicles from {url} in {duration:.3f} seconds")
                    return url, cars_data
                else:
                    logger.warning(f"Non-200 status {resp.status} from {url}")
                    return url, []
        except aiohttp.ClientError as client_err:
            logger.error(f"Client error for {url}: {client_err}")
            return url, []
        except asyncio.TimeoutError as timeout_err:
            logger.error(f"Timeout for {url}: {timeout_err}")
            return url, []
        except Exception as generic_err:
            logger.error(f"Unexpected error for {url}: {generic_err}")
            return url, []

async def get_all_data(url_list):
    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(get_data(session, url)) for url in url_list]
        logger.debug("Launching all tasks")
        start_time = time.monotonic()
        try:
            all_results = await asyncio.gather(*tasks)
        except Exception as gather_err:
            logger.critical(f"Gathering tasks encountered an error: {gather_err}")
            all_results = []
        duration = time.monotonic() - start_time
        logger.debug(f"All tasks completed in {duration:.3f} seconds")
        return all_results

async def main_task():
    target_urls = [f'https://bama.ir/cad/api/search?pageIndex={idx}' for idx in range(20)]

    async with aiosqlite.connect('vehicles.db') as database:
        async with database.cursor() as db_cursor:
            try:
                await db_cursor.execute('''
                    CREATE TABLE IF NOT EXISTS vehicle_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        url TEXT,
                        title TEXT,
                        time TEXT,
                        year TEXT,
                        image TEXT,
                        mileage TEXT,
                        location TEXT,
                        description TEXT,
                        created_at TEXT,
                        price TEXT
                    );
                ''')
                await database.commit()
                logger.info("Database table initialized")

                results = await get_all_data(target_urls)

                async with database.cursor() as db_cursor:
                    inserted_count = 0
                    start_time = time.monotonic()
                    for url, vehicles in results:
                        if not vehicles:
                            logger.error(f"No data retrieved from {url}")
                            continue

                        for vehicle in vehicles:
                            await db_cursor.execute('''
                                INSERT INTO vehicle_data (url, title, time, year, mileage, location, description, image, created_at, price)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                            ''', vehicle)
                            inserted_count += 1

                    await database.commit()
                    logger.info(f"{inserted_count} records successfully added to the database in {time.monotonic() - start_time:.3f} seconds.")

            except aiosqlite.Error as db_error:
                logger.critical(f"Database error: {db_error}")

asyncio.run(main_task())
