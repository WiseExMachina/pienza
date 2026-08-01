---
name: pdf-export-canon
description: "Reusable Playwright recipe for converting self-bundled HTML resumes/CVs (dc-root style) to clean, 1-page PDFs — background, justify, margin/scale fitting"
metadata: 
  node_type: memory
  type: project
  originSessionId: e1616b04-98d3-4e90-a4e2-fd2a853bf60e
  modified: 2026-07-24T02:10:56.635Z
---

Worked out 2026-07-22 converting `assets_ignored/Resume_Takeda_standalone.html` to PDF. Same recipe applies to any future "Bundled Page" HTML export (look for `<title>Bundled Page</title>`, a `#dc-root` div, and `<script type="__bundler/...">` tags — this is the format Claude Design / similar tools export as a standalone HTML file).

## The gotchas, in order of how they bite

1. **Must serve over real HTTP, not `file://`.** These bundled pages reconstruct their content at runtime via `fetch()` calls, which Chromium blocks under `file://` (CORS/file-access restriction). Rendering under `file://` silently produces an almost-empty page — no error, just missing content. Fix: `python3 -m http.server 8123 --bind 127.0.0.1` from the file's directory, then `page.goto("http://127.0.0.1:8123/whatever.html")`.

2. **`page.pdf()` defaults to print-media CSS emulation.** These pages have no print stylesheet, so Chromium's print-layout algorithm collapses the content to near-nothing (a ~1.3KB PDF with real-looking body text but a blank visual page). Fix: call `page.emulate_media(media="screen")` before `page.pdf()`.

3. **The content is a fixed-width design with zero internal padding.** The root container (`<doc-page>` in the observed case) is sized to exactly Letter width (816px = 8.5in) with `padding: 0; margin: 0`. It was built assuming it fills an entire physical page — so any `page.pdf(margin=...)` you add is *extra*, on top of a page already sized full-bleed. Keep PDF margins small (`0` to `0.15in`) rather than assuming normal document margins (`0.5in`+) are needed.

4. **`zoom` and `font-size: X%` on a wrapper do NOT reliably shrink content.** This bundler format sets explicit pixel `font-size` on individual elements (`style="font-size: 10.66px"` etc.), not relative units — so a parent's `font-size: 75%` or `zoom: 75%` doesn't cascade the way you'd expect for a normal page. The one thing that reliably works is Playwright's own **`page.pdf(scale=...)`** parameter (native Chromium print scaling, range 0.1-2), which uniformly shrinks the whole rendered layout including all descendant fixed-px content.

5. **Negative margins are hard-rejected.** `page.pdf(margin={"left": "-0.1in", ...})` throws `Protocol error (Page.printToPDF): left margin is negative`. Not usable at all — don't try to "just use less than zero" for extra tightness.

6. **`scale` shrinks width AND height together — this creates artificial gutters.** If you only need to reduce vertical overflow (fit more content per page), shrinking `scale` also shrinks the content narrower than the page, leaving empty left/right whitespace that looks like "too much margin" even when the PDF margin itself is `0`. There is no clean fix for this without editing the source content's own spacing (line-height, `margin-top`/`margin-bottom` on list items, spacing between sections) — that requires finding every spacing rule via `page.add_style_tag()` overrides, which is real per-file work, not a one-liner.

## Finding the exact 1-page-fit scale — do this empirically, not by calculation

CSS pixel math on the container width does **not** reliably predict how Chromium's print layout will paginate the content (confirmed by testing — the arithmetic prediction and the real fitting scale did not match). Instead:

```python
from playwright.sync_api import sync_playwright
from pypdf import PdfReader

def try_it(scale, margin_in):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1200, "height": 1600})
        page.goto("http://127.0.0.1:8123/file.html", wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(1000)
        page.add_style_tag(content="body { background: #fff !important; }")
        page.emulate_media(media="screen")
        page.pdf(path="out.pdf", format="Letter", print_background=True, scale=scale,
                  margin={"top": f"{margin_in}in", "bottom": f"{margin_in}in", "left": f"{margin_in}in", "right": f"{margin_in}in"})
        browser.close()
    return len(PdfReader("out.pdf").pages)

# binary-search-ish sweep, e.g. for margin=0:
for s in [0.9, 0.85, 0.8, 0.78, 0.77, 0.76]:
    print(s, try_it(s, 0))
```

Pick the **largest** scale that still returns 1 page — don't shrink further than necessary (readability). In the observed case: `margin=0.3in` needed `scale=0.73`; tightening margin to `0.15in` only moved it to `scale=0.75`; margin `0` (as tight as possible) only reached `scale=0.77`. Diminishing returns — margin reduction alone won't get you to `scale=1.0`; only trimming the content's own internal spacing would.

## Other recipes that worked

- **White background**: `page.add_style_tag(content="body { background: #fff !important; } #dc-root { background: #fff !important; }")` — target both `body` and the bundler's root div, the observed page had the background color on `body`, not on a nested element.
- **Justify body text**: target the actual tags used, not blindly `p` — this bundler format used **no `<p>` tags at all**, just `<li>` (for both real bullets and bold section-sub-headers) and `<span>`/`<strong>`. `li, span, strong { text-align: justify !important; }` worked; verify actual tag usage per new file via `document.querySelectorAll('#dc-root *')` tag-count inspection first, don't assume.
- **The Summary paragraph is NOT covered by that selector.** It lives in a bare `<div>` with no class (found via `Array.from(document.querySelectorAll('#dc-root *')).find(e => e.textContent.trim().startsWith('Summary:'))`), and `text-align` only takes effect on a block-level container — `<span>`/`<strong>` are inline, so justifying them does nothing for a paragraph's line-wrapping. A blanket `div { text-align: justify }` CSS rule is risky (could hit the centered header or flex title/date rows), so fix it with a targeted JS `page.evaluate()` call that finds that one specific div and sets `.style.textAlign = 'justify'` on it directly, rather than a CSS selector. Do this every time justify is requested — it's needed in addition to the `li, span, strong` rule, not instead of it.
- **Reordering sections** (e.g. Skills before Experience): sections are flat sibling `<div>`s under one wrapper with no semantic classnames — inspect via `page.evaluate()` printing each child's `tagName`/`textContent.slice(0,40)` to find the right indices, then `wrapper.insertBefore(nodeToMove, targetNode)` via another `page.evaluate()` call before generating the PDF. The source `.html` file itself is never touched — the reorder only exists in that one render, so regenerating without the reorder script naturally reverts to the original order.
- **Verify results properly, every time**: page count via `pypdf.PdfReader`, and render the actual output PDF to a PNG (`pdftoppm -png -r 150 out.pdf preview`) and visually inspect it — do not trust "the script ran without error" as proof the PDF looks right. The print-media bug (gotcha #2) produced a valid, error-free, but nearly-blank PDF; only an actual visual check caught it.

**Why this file exists:** so a future session (this one or another AI) picking up a new CV/resume HTML export doesn't have to rediscover the `file://`+fetch() trap, the print-media-emulation trap, and the scale-vs-zoom distinction from scratch — all three cost real iteration time to find here.
**How to apply:** when asked to convert a new "Bundled Page"-style HTML file to PDF, follow this recipe directly rather than starting from `page.pdf()` defaults.
