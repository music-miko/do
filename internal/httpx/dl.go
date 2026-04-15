package httpx

import (
	"fmt"
	"log/slog"
	"net/url"
	"os/exec"
	"strings"
	"time"
)

// isM3U8 returns true when the URL looks like an HLS stream.
func isM3U8(rawURL string) bool {
	lower := strings.ToLower(rawURL)
	if strings.Contains(lower, ".m3u8") {
		return true
	}
	if u, err := url.Parse(rawURL); err == nil {
		return strings.Contains(strings.ToLower(u.Path), ".m3u8")
	}
	return false
}

func DownloadFile(rawURL string) (string, error) {
	if strings.TrimSpace(rawURL) == "" {
		return "", fmt.Errorf("httpx: empty URL provided")
	}

	template := fmt.Sprintf("%%(id)s_%d.%%(ext)s", time.Now().Unix())

	args := []string{
		"--no-warnings",
		"--no-playlist",
		"-o", template,
		"--print", "after_move:filepath",
		"--retries", "1",
		"--merge-output-format", "mp4",
	}

	if isM3U8(rawURL) {
		args = append(args,
			"--hls-prefer-native",
			"--format", "bestvideo+bestaudio/best",
			"--downloader", "ffmpeg",
			"--downloader-args", "ffmpeg:-c copy",
		)
	} else {
		args = append(args, "--format", "bestvideo+bestaudio/best")
	}

	args = append(args, rawURL)

	slog.Info("downloading file", "url", rawURL, "m3u8", isM3U8(rawURL))

	cmd := exec.Command("yt-dlp", args...)
	out, err := cmd.CombinedOutput()
	output := strings.TrimSpace(string(out))
	if err != nil {
		slog.Warn("yt-dlp failed", "url", rawURL, "err", err, "output", output)
		return "", fmt.Errorf("httpx: yt-dlp failed: %w\noutput: %s", err, output)
	}

	path, err := extractFilePath(output)
	if err != nil {
		slog.Warn("downloading file failed", "url", rawURL, "err", err)
		return "", fmt.Errorf("httpx: %w\nraw output: %s", err, output)
	}

	slog.Info("download complete", "path", path)
	return path, nil
}

// extractFilePath pulls the last non-empty line from yt-dlp output.
func extractFilePath(output string) (string, error) {
	lines := strings.Split(output, "\n")
	for i := len(lines) - 1; i >= 0; i-- {
		if line := strings.TrimSpace(lines[i]); line != "" {
			return line, nil
		}
	}
	return "", fmt.Errorf("could not extract file path from yt-dlp output")
}
