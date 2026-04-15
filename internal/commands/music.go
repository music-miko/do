package commands

import (
	"fmt"
	"html"
	"noinoi/internal/database"
	"noinoi/internal/httpx"
	"os"
	"strings"

	"github.com/AshokShau/gotdbot"
)

func musicHandler(c *gotdbot.Client, ctx *gotdbot.Context) error {
	m := ctx.EffectiveMessage
	targetUrl := getUrl(m)
	if targetUrl == "" {
		return nil
	}

	botId := c.Me.Id

	reply, err := m.ReplyText(c, "⏳ Processing Music...", nil)
	if err != nil {
		return err
	}

	musicInfo, err := httpx.GetMusicInfo(targetUrl)
	if err != nil {
		database.IncrementDownloads(botId, false)
		_, _ = reply.EditText(c, fmt.Sprintf("Error: %v", err), nil)
		return nil
	}

	if len(musicInfo.Results) == 0 {
		_, _ = reply.EditText(c, "No tracks found for this URL.", nil)
		return nil
	}

	track := musicInfo.Results[0]
	trackDetails, err := httpx.GetTrack(track.URL)
	if err != nil {
		database.IncrementDownloads(botId, false)
		_, _ = reply.EditText(c, fmt.Sprintf("Error fetching track details: %v", err), nil)
		return nil
	}

	escapedTitle := html.EscapeString(track.Title)
	caption := fmt.Sprintf("<b>%s</b>\n\nJoin @FallenProjects", escapedTitle)

	var thumbInput *gotdbot.InputThumbnail
	if track.Thumbnail != "" {
		thumbInput = &gotdbot.InputThumbnail{Thumbnail: &gotdbot.InputFileRemote{Id: track.Thumbnail}}
	}

	if strings.ToLower(trackDetails.Platform) == "mxplayer" {
		localPath, dlErr := httpx.DownloadFile(trackDetails.CdnURL)
		if dlErr != nil {
			_, _ = reply.EditText(c, fmt.Sprintf("Failed to download for local upload: %v", dlErr), nil)
			return nil
		}

		localInput := &gotdbot.InputFileLocal{Path: localPath}
		_, err = m.ReplyVideo(c, localInput, &gotdbot.SendVideoOpts{
			Caption:   caption,
			ParseMode: "HTML",
			Duration:  int32(track.Duration),
			Thumbnail: thumbInput,
		})
		if err != nil {
			_, _ = reply.EditText(c, fmt.Sprintf("Error downloading video: %v", err), nil)
			return gotdbot.EndGroups
		}

		_ = reply.Delete(c, true)
		return gotdbot.EndGroups
	}

	input := &gotdbot.InputFileRemote{Id: trackDetails.CdnURL}
	_, err = m.ReplyAudio(c, input, &gotdbot.SendAudioOpts{
		Caption:             caption,
		ParseMode:           "HTML",
		Title:               track.Title,
		Performer:           track.Channel,
		Duration:            int32(track.Duration),
		AlbumCoverThumbnail: thumbInput,
	})

	if err != nil && (strings.Contains(err.Error(), "WEBPAGE_CURL_FAILED") || strings.Contains(err.Error(), "WEBPAGE_MEDIA_EMPTY")) {
		localPath, dlErr := httpx.DownloadFile(trackDetails.CdnURL)
		if dlErr == nil {
			defer os.Remove(localPath)
			localInput := &gotdbot.InputFileLocal{Path: localPath}
			_, err = m.ReplyAudio(c, localInput, &gotdbot.SendAudioOpts{
				Caption:             caption,
				ParseMode:           "HTML",
				Title:               track.Title,
				Performer:           track.Channel,
				Duration:            int32(track.Duration),
				AlbumCoverThumbnail: thumbInput,
			})
		} else {
			err = fmt.Errorf("failed to download for local upload: %v", dlErr)
		}
	}

	if err != nil {
		database.IncrementDownloads(botId, false)
		_, _ = reply.EditText(c, fmt.Sprintf("Failed to send audio: %v", err), nil)
	} else {
		database.IncrementDownloads(botId, true)
		_ = reply.Delete(c, true)
	}

	return gotdbot.EndGroups
}
