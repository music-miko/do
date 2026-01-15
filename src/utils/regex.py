import re

# === URL Regex Patterns ===
URL_PATTERNS = {
    "youtube": re.compile(
        r'(?i)https?://(?:www\.|m\.)?'
        r'(?:youtube\.com/(?:watch\?v=[\w-]+|playlist\?list=[\w-]+|shorts/[\w-]+)'
        r'|youtu\.be/[\w-]+)'
    ),

    "youtube_music": re.compile(
        r'(?i)https?://music\.youtube\.com/.*'
    ),

    "soundcloud": re.compile(
        r'(?i)https?://(?:www\.|m\.)?soundcloud\.com/.*'
    ),

    "apple_music": re.compile(
        r'(?i)^https?://music\.apple\.com/[a-zA-Z-]+/'
        r'(?:'
        r'song/(?:[^/]+/)?\d+'
        r'|album/[^/]+/\d+(?:\?i=\d+)?'
        r'|playlist/[^/]+/pl\.[\w.-]+'
        r'|artist/[^/]+/\d+'
        r')'
        r'(?:\?.*)?$'
    ),

    "deezer": re.compile(
        r'(?i)https?://(?:www\.)?deezer\.com/(?:[a-z]{2}/)?'
        r'(track|album|playlist)/\d+'
    ),

    "jiosaavn": re.compile(
        r'(?i)https?://(?:www\.)?jiosaavn\.com/'
        r'(song|album|playlist|featured)/[^/]+/[A-Za-z0-9_]+'
    ),

    "spotify": re.compile(
        r'(?i)https?://(?:open\.|www\.)?spotify\.com/'
        r'(album|track|playlist|artist)/[A-Za-z0-9]+'
    ),

    "gaana": re.compile(
        r'(?i)https?://(?:www\.)?gaana\.com/'
        r'(song|album|playlist|artist)/[A-Za-z0-9-]+'
    ),

    "tidal": re.compile(
        r'(?i)https?://(?:listen\.)?tidal\.com/'
        r'(?:browse/)?(track|album|playlist)/[A-Za-z0-9-]+'
    ),
}

# === Save Snap Regex Patterns ===
SAVE_SNAP_PATTERNS = [
    # Instagram
    re.compile(
        r"(?i)https?://(?:www\.)?(?:instagram\.com|instagr\.am)/(?:p|reel|reels|tv|stories/(?:highlights/)?[\w._-]+)?/?[\w._-]*"
    ),

    # TikTok
    re.compile(
        r"(?i)https?://(?:www\.|m\.)?(?:"
        r"tiktok\.com/@[\w.-]+/(?:video|photo)/\d+|"
        r"tiktok\.com/(?:t|v)/\d+|"
        r"vm\.tiktok\.com/[\w-]+|"
        r"vt\.tiktok\.com/[\w-]+)"
    ),

    # Pinterest
    re.compile(
        r"(?i)https?://(?:www\.|[a-z]{2}\.)?(?:pinterest\.[a-z.]+/pin/\d+|pin\.it/[\w-]+)/?"
    ),

    # Twitter / X
    re.compile(
        r"(?i)https?://(?:www\.|m\.)?(?:twitter\.com|x\.com)/[\w._-]+/status/\d+"
    ),

    # Snapchat
    re.compile(
        r"(?i)https?://(?:www\.)?snapchat\.com/.*"
    ),

    # Facebook (fb.watch + videos/reels)
    re.compile(
        r"(?i)https?://(?:www\.|m\.|web\.)?(?:facebook\.com|fb\.watch|fb\.com)/.*"
    ),

    # LinkedIn
    re.compile(
        r"(?i)https?://(?:www\.)?linkedin\.com/.*"
    ),

    # Bilibili
    re.compile(
        r"(?i)https?://(?:www\.|m\.)?bilibili\.com/video/.*"
    ),

    # CapCut
    re.compile(
        r"(?i)https?://(?:www\.|m\.)?capcut\.com/.*"
    ),

    # IMDb video
    re.compile(
        r"(?i)https?://(?:www\.|m\.)?imdb\.com/video/.*"
    ),

    # ShareChat
    re.compile(
        r"(?i)https?://(?:www\.)?sharechat\.com/.*"
    ),

    # Streamable
    re.compile(
        r"(?i)https?://(?:www\.)?streamable\.com/.*"
    ),

    # TED Talks
    re.compile(
        r"(?i)https?://(?:www\.)?ted\.com/talks/.*"
    ),

    # Threads
    re.compile(
        r"(?i)https?://(?:www\.)?threads\.(?:net|com)/.*"
    ),

    # VK
    re.compile(
        r"(?i)https?://(?:www\.|m\.)?vk\.com/.*"
    ),

    # Twitch VOD
    re.compile(
        r"(?i)https?://(?:www\.|m\.)?twitch\.tv/(?:videos|[\w._-]+/video)/\d+"
    ),

    # Twitch Clips
    re.compile(
        r"(?i)https?://(?:www\.|m\.)?(?:"
        r"twitch\.tv/clip/[\w-]+|"
        r"clips\.twitch\.tv/[\w-]+|"
        r"twitch\.tv/[\w-]+/clip/[\w-]+"
        r")"
    ),

    # Tumblr
    re.compile(
        r"(?i)https?://(?:www\.|m\.)?tumblr\.com/.*"
    ),

    # Dailymotion
    re.compile(
        r"(?i)https?://(?:www\.)?dailymotion\.com/video/.*"
    ),

    # Douyin
    re.compile(
        r"(?i)https?://(?:www\.|v\.)?douyin\.com/.*"
    ),

    # 9GAG
    re.compile(
        r"(?i)https?://(?:www\.)?9gag\.com/gag/[\w-]+"
    ),

    # AkilliTV
    re.compile(
        r"(?i)https?://(?:www\.)?akillitv\.com/(?:video|embed)/[\w-]+"
    ),

    # Bandcamp
    re.compile(
        r"(?i)https?://(?:www\.|m\.)?[\w.-]+\.bandcamp\.com/(?:track|album|video)/[\w-]+"
    ),

    # BitChute
    re.compile(
        r"(?i)https?://(?:www\.)?bitchute\.com/video/[\w-]+"
    ),

    # Blogger
    re.compile(
        r"(?i)https?://(?:www\.)?blogger\.com/.*"
    ),

    # Rumble
    re.compile(
        r"(?i)https?://(?:www\.)?rumble\.com/.*"
    ),

    # ESPN
    re.compile(
        r"(?i)https?://(?:www\.)?espn\.com/video/.*"
    ),

    # BuzzFeed
    re.compile(
        r"(?i)https?://(?:www\.)?buzzfeed\.com/.*"
    ),

    # Mastodon
    re.compile(
        r"(?i)https?://(?:[\w.-]+\.)?mastodon\.social/@[\w.-]+/\d+"
    ),

    # Imgur
    re.compile(
        r"(?i)https?://(?:www\.)?imgur\.com/(?:gallery|a|t)?/?[\w-]+"
    ),

    # Reddit (full + short)
    re.compile(
        r"(?i)https?://(?:www\.|m\.)?reddit\.com/r/[\w-]+/comments/[\w-]+/.*"
    ),
    re.compile(
        r"(?i)https?://redd\.it/[\w-]+"
    ),

    # Vimeo
    re.compile(
        r"(?i)https?://(?:www\.)?vimeo\.com/\d+"
    ),

    # Sora AI
    re.compile(r'^https://sora\.chatgpt\.com/p/s_[0-9a-fA-F]{32}\?psh=[A-Za-z0-9\-_.]+$'),

    # Suno Music AI
    re.compile(r'^https://suno\.com/song/[0-9a-fA-F\-]{36}/?$')
]
