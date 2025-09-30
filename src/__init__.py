import logging
from datetime import datetime

from pytdbot import Client, types

from src import config
from src.utils import HttpClient, db

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(filename)s:%(lineno)d - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[logging.StreamHandler()],
)

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("pymongo").setLevel(logging.WARNING)

LOGGER = logging.getLogger("Bot")

StartTime = datetime.now()


class Telegram(Client):
    def __init__(self) -> None:
        self._check_config()
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self._save_cookies())
        except Exception as e:
            LOGGER.error(f"Failed to save cookies: {e}")
        
        super().__init__(
            token=config.TOKEN,
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            default_parse_mode="html",
            td_verbosity=2,
            td_log=types.LogStreamEmpty(),
            plugins=types.plugins.Plugins(folder="src/modules"),
            files_directory="",
            database_encryption_key="",
            options={"ignore_background_updates": True},
        )

        self._http_client = HttpClient()

    async def start(self) -> None:
        await self._http_client.get_client()
        # await self._save_cookies()
        await super().start()
        self.logger.info(f"Bot started in {datetime.now() - StartTime} seconds.")
        await db.connect()

    async def stop(self) -> None:
        await self._http_client.close_client()
        await db.close()
        await super().stop()

    @staticmethod
    def _check_config() -> None:
        required_keys = [
            "TOKEN",
            "API_ID",
            "API_HASH",
            "API_KEY",
            "API_URL",
            "MONGO_URI",
            "LOGGER_ID",
        ]

        if missing := [
            key for key in required_keys if not getattr(config, key, None)
        ]:
            raise RuntimeError(
                f"Missing required config values in .env: {', '.join(missing)}"
            )


    async def _save_cookies(self) -> None:
        from pathlib import Path
        from urllib.parse import urlparse
        from typing import Optional, Tuple
        
        async def _download_cookies(url: str) -> Optional[str]:
            try:
                parsed = urlparse(url)
                if parsed.netloc != 'batbin.me':
                    LOGGER.error(f"Invalid domain in URL: {url}")
                    return None
                    
                paste_id = parsed.path.strip('/').split('/')[-1]
                if not paste_id:
                    LOGGER.error(f"Could not extract paste ID from URL: {url}")
                    return None
                    
                raw_url = f"https://batbin.me/raw/{paste_id}"
                http_client = await HttpClient.get_client()
                resp = await http_client.get(raw_url)
                if resp.status_code != 200:
                    LOGGER.error(f"Failed to download cookies from {url}: HTTP {resp.status_code}")
                    return None
                return resp.text
            except Exception as exc:
                LOGGER.error(f"Error downloading cookies: {str(exc)}")
                return None

        db_dir = Path("database")
        db_dir.mkdir(exist_ok=True)
        if config.AM_COOKIES:
            if content := await _download_cookies(config.AM_COOKIES):
                filename = "am_cookies.txt"
                try:
                    (db_dir / filename).write_text(content)
                    LOGGER.info(f"Successfully saved {filename}")
                except Exception as e:
                    LOGGER.error(f"Failed to save cookies to file: {str(e)}")

        if config.YT_COOKIES:
            if content := await _download_cookies(config.YT_COOKIES):
                filename = "yt_cookies.txt"
                try:
                    (db_dir / filename).write_text(content)
                    LOGGER.info(f"Successfully saved {filename}")
                except Exception as e:
                    LOGGER.error(f"Failed to save cookies to file: {str(e)}")
        return None


client: Telegram = Telegram()
