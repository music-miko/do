import os
import re
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from gamdl import AppleMusicApi, ItunesApi, Downloader, DownloaderSong
from gamdl.models import DownloadInfo
from pytdbot import Client, types

from src import LOGGER
from src.modules._fsub import fsub
from src.utils import Filter

apple_music_api = AppleMusicApi.from_netscape_cookies(cookies_path=Path("database/am_cookies.txt"))
itunes_api = ItunesApi(storefront=apple_music_api.storefront, language=apple_music_api.language)

downloader = Downloader(
        apple_music_api=apple_music_api,
        itunes_api=itunes_api,
        output_path= Path("database"),
)
downloader.set_cdm()
downloader_song = DownloaderSong(downloader=downloader)

def extract_apple_music_id(url: str) -> str | None:
    """
    Extract the Apple Music media ID from song/album URLs.
    Handles:
      - Album links with ?i= parameter -> track ID
      - Direct song links -> last numeric segment
    """
    try:
        parsed = urlparse(url)
        if "music.apple.com" not in parsed.netloc:
            return None

        query_params = parse_qs(parsed.query)
        if "i" in query_params and query_params["i"]:
            return query_params["i"][0]

        if match := re.search(r"/(\d+)(?:$|/|\?)", parsed.path):
            return match[1]

    except Exception as e:
        LOGGER.error(f"Failed to parse Apple Music URL: {e}")

    return None


@Client.on_message(filters=Filter.command(["am", "apple", "apple_music"]))
@fsub
async def apple_music_cmd(c: Client, message: types.Message):
    parts = message.text.split(" ", 1)
    if len(parts) < 2:
        await message.reply_text("Please provide a search query or Apple Music URL.")
        return

    query = parts[1].strip()
    if not re.match(r"^https?://", query):
        await message.reply_text("Please provide a valid Apple Music URL.")
        return

    media_id = extract_apple_music_id(query)
    if not media_id:
        await message.reply_text("❌ Could not extract a valid media ID from the URL.")
        return

    reply = await message.reply_text("⬇️ Downloading song...")
    download_info: DownloadInfo | None = None
    downloaded_path: Path | None = None
    try:
        for download_info in downloader_song.download(media_id=media_id):
            downloaded_path = download_info.final_path

        if not downloaded_path or not downloaded_path.exists():
            await reply.edit_text("❌ Downloaded file not found.")
            return

        attributes = download_info.media_metadata.get("attributes", {})
        duration_ms = attributes.get("durationInMillis")
        duration_sec = int(duration_ms / 1000) if duration_ms else None
        artwork = download_info.media_metadata["attributes"].get("artwork", {})
        cover_url = artwork.get("url", "").replace("{w}", "500").replace("{h}", "500")
        previews = download_info.media_metadata["attributes"].get("previews", [])
        preview_url = previews[0]["url"] if previews else "https://t.me/FallenProjects"
        button = types.ReplyMarkupInlineKeyboard(
            [[types.InlineKeyboardButton(text="Preview",
                                         type=types.InlineKeyboardButtonTypeUrl(url=preview_url))]]
        )
        done = await message.reply_audio(
            audio=types.InputFileLocal(str(downloaded_path)),
            album_cover_thumbnail=types.InputThumbnail(thumbnail=types.InputFileRemote(cover_url)),
            title=download_info.tags.title,
            performer=download_info.tags.artist,
            duration=duration_sec,
            caption=f"<b>{download_info.tags.title}</b>\n<i>{download_info.tags.artist}</i>\n\n{download_info.tags.copyright}",
            reply_markup=button,
        )
        if isinstance(done, types.Error):
            await reply.edit_text(f"❌ Error: {done.message}")
        else:
            await reply.delete()

    except Exception as e:
        c.logger.error(f"Apple Music download error: {e}", exc_info=True)
        await reply.edit_text(f"❌ Download failed: {e}")

    finally:
        if downloaded_path:
            try:
                os.remove(downloaded_path)
            except Exception as e:
                LOGGER.error(f"Error deleting file {downloaded_path}: {e}")
