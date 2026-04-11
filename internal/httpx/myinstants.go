package httpx

import (
	"fmt"
	"io"
	"net/http"
	"net/url"
	"regexp"
)

type Instant struct {
	Name string
	URL  string
}

const (
	myInstantsBaseURL = "https://www.myinstants.com"
	searchURL         = "https://www.myinstants.com/en/search/?name=%s"
	trendingURL       = "https://www.myinstants.com/en/index/in/"
	userAgent         = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
)

var (
	instantRegex = regexp.MustCompile(`onclick="play\('([^']*)',[^)]*\)" title="Play (.*?) sound"`)
)

func GetInstants(query string) ([]Instant, error) {
	var targetURL string
	if query == "" {
		targetURL = trendingURL
	} else {
		targetURL = fmt.Sprintf(searchURL, url.QueryEscape(query))
	}

	req, err := http.NewRequest("GET", targetURL, nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("User-Agent", userAgent)

	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("myinstants returned status: %d", resp.StatusCode)
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	matches := instantRegex.FindAllStringSubmatch(string(body), -1)
	var instants []Instant
	for _, match := range matches {
		if len(match) < 3 {
			continue
		}
		instants = append(instants, Instant{
			URL:  myInstantsBaseURL + match[1],
			Name: match[2],
		})
		if len(instants) >= 20 {
			break
		}
	}

	return instants, nil
}
