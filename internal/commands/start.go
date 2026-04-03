package commands

import "github.com/AshokShau/gotdbot"

func startHandler(c *gotdbot.Client, ctx *gotdbot.Context) error {
	text := `Welcome to <b>NoiNoi Bot</b>! 🚀

I can help you download media from various platforms. Just send me a link, and I'll do the rest!

<b>Cloning Feature:</b>
You can create your own copy of this bot! Click the "Create Bot" button below.

Join @FallenProjects for more cool bots and updates.`

	replyMarkup := &gotdbot.ReplyMarkupInlineKeyboard{
		Rows: [][]gotdbot.InlineKeyboardButton{
			{
				{Text: "➕ Create Bot", Type: &gotdbot.InlineKeyboardButtonTypeCallback{Data: []byte("clone_create")}},
				{Text: "🤖 My Bots", Type: &gotdbot.InlineKeyboardButtonTypeCallback{Data: []byte("clone_mybots")}},
			},
		},
	}

	_, err := ctx.EffectiveMessage.ReplyText(c, text, &gotdbot.SendTextMessageOpts{
		ParseMode:   "HTML",
		ReplyMarkup: replyMarkup,
	})
	return err
}

func helpHandler(c *gotdbot.Client, ctx *gotdbot.Context) error {
	return gotdbot.EndGroups
}
