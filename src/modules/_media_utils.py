import re
from typing import Tuple, Optional, Union, TYPE_CHECKING
from pytdbot import types, Client
from src.utils import ApiData, Download, shortener, db

if TYPE_CHECKING:
    from src.utils._dataclass import TrackInfo


async def process_track_media(
    c: Client,
    track:  'TrackInfo' ,
    chat_id: Optional[int] = None,
    message_id: Optional[int] = None,
    inline_message_id: Optional[str] = None
) -> Tuple[Optional[types.InputFile], Optional[str], str]:
    """
    Process media for a track, handling both regular and inline messages.

    Args:
        c: The Telegram client instance
        track: The track to process
        chat_id: Chat ID for regular messages (None for inline)
        message_id: Message ID for regular messages (None for inline)
        inline_message_id: Inline message ID for inline messages (None for regular)

    Returns:
        Tuple containing (audio_file, cover_path, status_text)
    """
    status_text = f"<b>🎵 {track.name}</b>\n👤 {track.artist} | 📀 {track.album}\n⏱️ {track.duration}s"
    parsed_status = await c.parseTextEntities(status_text, types.TextParseModeHTML())
    # Update status message
    if inline_message_id:
        await c.editInlineMessageText(
            inline_message_id=inline_message_id,
            input_message_content=types.InputMessageText(parsed_status)
        )
    elif chat_id and message_id:
        await c.editMessageText(
            chat_id=chat_id,
            message_id=message_id,
            input_message_content=types.InputMessageText(parsed_status)
        )

    audio_file, cover = None, None
    audio: Optional[Union[types.InputFileLocal, types.InputFileRemote]] = None

    # Spotify shortcut if file already cached
    if track.platform.lower() == "spotify" and track.tc:
        if file_id := await db.get_song_file_id(track.tc):
            audio = types.InputFileRemote(file_id)

    # Download if not found in DB
    if not audio:
        dl = Download(track)
        result = await dl.process()
        if isinstance(result, types.Error):
            error_msg = f"❌ Download failed.\n<b>{result.message}</b>"
            return None, None, error_msg

        audio_file, cover = result
        if not audio_file:
            return None, None, "❌ Failed to download song.\nPlease report this to @FallenProjects."

        if track.platform.lower() == "spotify":
            file_id = await db.upload_song_and_get_file_id(audio_file, cover, track)
            if isinstance(file_id, types.Error):
                return None, None, file_id.message or "❌ Failed to send song to database."
            audio = types.InputFileRemote(file_id)

        elif re.match(r"https?://t\.me/([^/]+)/(\d+)", audio_file):
            info = await c.getMessageLinkInfo(audio_file)
            if isinstance(info, types.Error) or not info.message:
                return None, None, f"❌ Failed to resolve link: {audio_file}"

            public_msg = await c.getMessage(info.chat_id, info.message.id)
            if isinstance(public_msg, types.Error):
                return None, None, f"❌ Failed to fetch message: {public_msg.message}"

            if isinstance(public_msg.content, types.MessageAudio):
                audio = types.InputFileRemote(public_msg.content.audio.audio.remote.id)
            elif isinstance(public_msg.content, types.MessageDocument):
                audio = types.InputFileRemote(public_msg.content.document.document.remote.id)
            elif isinstance(public_msg.content, types.MessageVideo):
                audio = types.InputFileRemote(public_msg.content.video.video.remote.id)
            else:
                return None, None, f"❌ No audio file in t.me link: {audio_file}"
        else:
            audio = types.InputFileLocal(audio_file)

    return audio, cover, status_text


def get_reply_markup(track_name: str, artist: str) -> types.ReplyMarkupInlineKeyboard:
    """Generate a reply markup with the track name and update button."""
    return types.ReplyMarkupInlineKeyboard(
        [
            [
                types.InlineKeyboardButton(
                    text="Update ",
                    type=types.InlineKeyboardButtonTypeUrl("https://t.me/FallenProjects"),
                ),
                types.InlineKeyboardButton(
                    text=track_name,
                    type=types.InlineKeyboardButtonTypeSwitchInline(
                        query=artist,
                        target_chat=types.TargetChatCurrent()
                    )
                ),
            ],
        ]
    )
