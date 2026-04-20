package httpx

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"regexp"
	"strings"
)

type YouTubePostData struct {
	Text   string
	Images []string
}

var ytInitialDataRegex = regexp.MustCompile(`var ytInitialData = ({.*?});`)

func GetYouTubePost(url string) (*YouTubePostData, error) {
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	match := ytInitialDataRegex.FindSubmatch(body)
	if len(match) < 2 {
		return nil, fmt.Errorf("could not find ytInitialData")
	}

	var data map[string]interface{}
	if err := json.Unmarshal(match[1], &data); err != nil {
		return nil, err
	}

	return parseYouTubePost(data)
}

func parseYouTubePost(data map[string]interface{}) (*YouTubePostData, error) {
	renderer := findBackstagePostRenderer(data)
	if renderer == nil {
		return nil, fmt.Errorf("backstagePostRenderer not found")
	}

	postData := &YouTubePostData{}
	if contentText, ok := renderer["contentText"].(map[string]interface{}); ok {
		if runs, ok := contentText["runs"].([]interface{}); ok {
			var sb strings.Builder
			for _, run := range runs {
				if r, ok := run.(map[string]interface{}); ok {
					if text, ok := r["text"].(string); ok {
						sb.WriteString(text)
					}
				}
			}
			postData.Text = sb.String()
		}
	}

	if attachment, ok := renderer["backstageAttachment"].(map[string]interface{}); ok {
		if imgRenderer, ok := attachment["backstageImageRenderer"].(map[string]interface{}); ok {
			if url := getBestThumbnail(imgRenderer); url != "" {
				postData.Images = append(postData.Images, url)
			}
		}

		if multiImgRenderer, ok := attachment["postMultiImageRenderer"].(map[string]interface{}); ok {
			if images, ok := multiImgRenderer["images"].([]interface{}); ok {
				for _, img := range images {
					if imgMap, ok := img.(map[string]interface{}); ok {
						if imgRenderer, ok := imgMap["backstageImageRenderer"].(map[string]interface{}); ok {
							if url := getBestThumbnail(imgRenderer); url != "" {
								postData.Images = append(postData.Images, url)
							}
						}
					}
				}
			}
		}
	}

	return postData, nil
}

func findBackstagePostRenderer(data interface{}) map[string]interface{} {
	switch v := data.(type) {
	case map[string]interface{}:
		if r, ok := v["backstagePostRenderer"].(map[string]interface{}); ok {
			return r
		}
		for _, val := range v {
			if found := findBackstagePostRenderer(val); found != nil {
				return found
			}
		}
	case []interface{}:
		for _, val := range v {
			if found := findBackstagePostRenderer(val); found != nil {
				return found
			}
		}
	}
	return nil
}

func getBestThumbnail(imgRenderer map[string]interface{}) string {
	if image, ok := imgRenderer["image"].(map[string]interface{}); ok {
		if thumbnails, ok := image["thumbnails"].([]interface{}); ok && len(thumbnails) > 0 {
			last := thumbnails[len(thumbnails)-1]
			if thumbMap, ok := last.(map[string]interface{}); ok {
				if url, ok := thumbMap["url"].(string); ok {
					return url
				}
			}
		}
	}
	return ""
}
