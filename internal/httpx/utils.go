package httpx

import (
	"context"
	"os/exec"
	"strings"
	"time"
)

// HasAudioStream checks if a video URL has an audio stream using ffprobe.
func HasAudioStream(url string) (bool, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	cmd := exec.CommandContext(ctx, "ffprobe",
		"-v", "error",
		"-select_streams", "a",
		"-show_entries", "stream=index",
		"-of", "csv=p=0",
		"-user_agent", "Mozilla/5.0",
		url,
	)

	output, err := cmd.Output()
	if err != nil {
		return false, err
	}

	return len(strings.TrimSpace(string(output))) > 0, nil
}
