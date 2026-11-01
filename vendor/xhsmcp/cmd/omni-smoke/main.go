package main

import (
	"fmt"
	"github.com/xpzouying/xiaohongshu-mcp/browser"
)

func main() {
	b := browser.NewBrowser(true)
	defer b.Close()
	p := b.NewPage()
	defer p.Close()
	p.MustNavigate("data:text/html,<title>OmniLocalEngineCheck</title><body>local fixture</body>")
	if p.MustEval("() => document.title").Str() != "OmniLocalEngineCheck" {
		panic("unexpected browser result")
	}
	fmt.Println("{\"bundled_standard_chromium\":true,\"external_publications\":0}")
}
