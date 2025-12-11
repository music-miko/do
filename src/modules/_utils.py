import asyncio

from pytdbot import types, Client


async def has_audio_stream(url: str) -> bool:
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'a',
        '-show_entries', 'stream=index',
        '-of', 'csv=p=0',
        '-user_agent', 'Mozilla/5.0',
        url
    ]

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=10)

        return bool(stdout.strip())
    except Exception as e:
        print(f"Error checking audio stream: {e}")
        return False


StartMessage = (
        "<b>🎧 Welcome to {bot_name}!</b>\n"
        "Your quick and easy tool to download music & media from top platforms.\n\n"
        "📩 Just send a song name, link, or media URL.\n"
        "🔎 Search inline: <code>@{bot_username} your search</code>\n\n"
        "🔐 Privacy policy: /privacy\n"
        "📺 Download videos: /yt <code>url</code>\n"
        "🎵 Get Spotify playlists: /playlist <code>url</code>"
    )

async def handle_help_callback(_: Client, message: types.UpdateNewCallbackQuery):
    data = message.payload.data.decode()
    platform = data.replace("help_", "")

    examples = {
        "spotify": (
            "💡<b>Spotify Downloader</b>\n\n"
            "🔹 Download songs, albums, and playlists in 320kbps quality\n"
            "🔹 Supports both public and private links\n\n"
            "Example formats:\n"
            "👉 <code>https://open.spotify.com/track/*</code> (Single song)\n"
            "👉 <code>https://open.spotify.com/album/*</code> (Full album)\n"
            "👉 <code>https://open.spotify.com/playlist/*</code> (Playlist)\n"
            "👉 <code>https://open.spotify.com/artist/*</code> (Artist's top tracks)"
        ),
        "youtube": (
            "💡<b>YouTube Downloader</b>\n\n"
            "🔹 Download videos or extract audio\n"
            "🔹 Supports both YouTube and YouTube Music links\n\n"
            "Example formats:\n"
            "👉 <code>https://youtu.be/*</code> (Short URL)\n"
            "👉 <code>https://www.youtube.com/watch?v=*</code> (Full URL)\n"
            "👉 <code>https://music.youtube.com/watch?v=*</code> (YouTube Music)"
        ),
        "soundcloud": (
            "💡<b>SoundCloud Downloader</b>\n\n"
            "🔹 Download tracks in high-quality\n"
            "🔹 Supports both public and private tracks\n\n"
            "Example formats:\n"
            "👉 <code>https://soundcloud.com/user/track-name</code>\n"
            "👉 <code>https://soundcloud.com/user/track-name?utm_source=*</code> (With tracking params)"
        ),
        "apple": (
            "💡<b>Apple Music Downloader</b>\n\n"
            "🔹 Lossless music downloads\n"
            "🔹 Supports songs, albums, and artists\n\n"
            "Example formats:\n"
            "👉 <code>https://music.apple.com/*</code>\n"
            "👉 <code>https://music.apple.com/us/song/*</code>\n"
            "👉 <code>https://music.apple.com/us/album/*</code>\n"
            "👉 <code>https://music.apple.com/us/artist/*</code>"
        ),
        "instagram": (
            "💡<b>Instagram Media Downloader</b>\n\n"
            "🔹 Download Instagram posts, reels, and stories\n"
            "🔹 Supports both public and private accounts\n\n"
            "Example formats:\n"
            "👉 <code>https://www.instagram.com/p/*</code> (Posts)\n"
            "👉 <code>https://www.instagram.com/reel/*</code> (Reels)\n"
            "👉 <code>https://www.instagram.com/stories/*</code> (Stories\n)"
           "Download Reels, Stories, and Posts:\n\n"
            "👉 <code>https://www.instagram.com/reel/Cxyz123/</code>"
        ),
        "pinterest": (
            "💡<b>Pinterest Downloader</b>\n\n"
            "Photos and videos are available to download:\n\n"
            "👉 <code>https://www.pinterest.com/pin/1085649053904273177/</code>"
        ),
        "facebook": (
            "💡<b>Facebook Downloader</b>\n\n"
            "Works with videos from public pages:\n\n"
            "👉 <code>https://www.facebook.com/watch/?v=123456789</code>"
        ),
        "twitter": (
            "💡<b>Twitter Downloader</b>\n\n"
            "Download videos or Photos from posts:\n\n"
            "👉 <code>https://x.com/i/status/1951310276814578086</code>\n"
            "👉 <code>https://twitter.com/i/status/1951310276814578086</code>\n"
            "👉 <code>https://x.com/luismbat/status/1951307858764607604/photo/1</code>"
        ),
        "tiktok": (
            "💡<b>TikTok Downloader</b>\n\n"
            "Supports watermark-free download:\n\n"
            "👉 <code>https://vt.tiktok.com/ZSB3BovQp/</code>\n"
            "👉 <code>https://vt.tiktok.com/ZSSe7NprD/</code>"
        ),
        "threads": (
            "💡<b>Threads Downloader</b>\n\n"
            "Download media from Threads:\n\n"
            "👉 <code>https://www.threads.com/@camycavero/post/DM0FquaM2At?xmt=AQF0u_6ebeMHEjWCw0cm0Li4i8fI3INIU7YeSMffM9DmDw</code>\n"
        ),
        "reddit": (
            "💡<b>Reddit Downloader</b>\n\n"
            "Download media from Reddit:\n\n"
            "👉 <code>https://www.reddit.com/r/tollywood/comments/1mld609/what_is_your_honest_unfiltered_opinion_on_mahesh/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button</code>\n"
            "👉 <code>https://www.reddit.com/r/Damnthatsinteresting/comments/1mlfgzv/when_cat_meets_cat/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button</code>\n"
            "👉 <code>https://www.reddit.com/r/Indian_flex/comments/1mlez7j/tough_life/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button</code>\n"
        ),
        "twitch": (
            "💡<b>Twitch Clip Downloader</b>\n\n"
            "Download media from Twitch:\n\n"
            "👉 <code>https://www.twitch.tv/tarik/clip/CheerfulHonorableBibimbapHumbleLife-cdCV_zL45i1p2Kh6</code>\n"
        ),
    }

    reply_text = examples.get(platform, "<b>No help available for this platform.</b>")
    await message.answer(text=f"{platform} Help Menu")
    await message.edit_message_text(
        text=reply_text,
        parse_mode="html",
        disable_web_page_preview=True,
        reply_markup=types.ReplyMarkupInlineKeyboard([
            [
                types.InlineKeyboardButton(
                    text="⬅️ Back",
                    type=types.InlineKeyboardButtonTypeCallback("back_menu".encode())
                )
            ]
        ])
    )
