import re

from pytdbot import Client, types

from src.modules._fsub import fsub
from src.utils import Filter, ApiData, Download


@Client.on_message(filters=Filter.command(["yt", "youtube"]))
@fsub
async def youtube_cmd(c: Client, message: types.Message):
    parts = message.text.split(" ", 1)
    if len(parts) < 2:
        await message.reply_text("Please provide a search query.")
        return

    query = parts[1]
    if not re.match(r"^https?://", query):
        await message.reply_text("Please provide a valid URL.")
        return

    is_yt_url = "youtube.com" in query.lower() or "youtu.be" in query.lower()
    if not is_yt_url:
        await message.reply_text("Please provide a valid YouTube URL.")
        return

    reply = await message.reply_text("🔍 Preparing download...")
    api = ApiData(query)
    track = await api.get_track(video=True, quality="1080p")
    if isinstance(track, types.Error):
        await reply.edit_text(f"❌ Error: {track.message or 'No results found'}")
        return

    dl = Download(track)
    result = await dl.process()
    if isinstance(result, types.Error):
        await reply.edit_text(f"❌ Error: {result.message}")
        return

    file, _ = result
    sent = await message.reply_video(
        video=types.InputFileLocal(file),
        supports_streaming=True,
        caption=f"🎵 {track.name} by {track.artist}",
    )
    if isinstance(sent, types.Error):
        await reply.edit_text(f"❌ Error: {sent.message}")
    else:
        await reply.delete()
