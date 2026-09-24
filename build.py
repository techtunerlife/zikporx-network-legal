#!/usr/bin/env python3
"""Builds the GitHub Pages site from PRIVACY.md and TERMS.md.

Run `python3 build.py` after editing either document, then commit the generated HTML.
Supports the Markdown the documents use: headings, paragraphs, lists, tables, bold, links.
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).parent

PAGES = [
    ("PRIVACY.md", "privacy/index.html", "Privacy Policy"),
    ("TERMS.md", "terms/index.html", "Terms of Use"),
]

CSS = """
:root {
  --sky-top: #E0E7F8; --sky-bottom: #E5ECFA; --card: #FFFFFF;
  --ink: #0B1330; --muted: #5B6480; --line: #E3E8F4;
  --blue: #2F7BFF; --purple: #8B45FF; --cyan: #2EE6FF;
}
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body {
  margin: 0; min-height: 100vh; color: var(--ink);
  font: 17px/1.6 -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  background: linear-gradient(180deg, var(--sky-top), var(--sky-bottom)) fixed;
}
.wrap { max-width: 820px; margin: 0 auto; padding: 32px 16px 56px; }
header.brand { display: flex; align-items: center; gap: 14px; margin-bottom: 22px; }
header.brand img { width: 56px; height: 56px; border-radius: 13px; box-shadow: 0 6px 18px rgba(47,123,255,.25); }
header.brand .name { font-weight: 800; font-size: 20px; letter-spacing: -.01em; }
header.brand .by { color: var(--muted); font-size: 14px; }
header.brand a { color: inherit; text-decoration: none; display: flex; align-items: center; gap: 14px; }
.card {
  background: var(--card); border-radius: 24px; padding: 28px 28px 20px;
  box-shadow: 0 8px 28px rgba(47,123,255,.14);
}
h1 { font-size: 34px; line-height: 1.15; margin: 0 0 8px; letter-spacing: -.02em; }
h1 .accent { background: linear-gradient(90deg, var(--cyan), var(--blue), var(--purple)); -webkit-background-clip: text; background-clip: text; color: transparent; }
h2 { font-size: 21px; margin: 32px 0 10px; letter-spacing: -.01em; }
p, li { color: #1D2440; }
.meta { color: var(--muted); font-size: 15px; margin: 0 0 18px; }
.meta p { margin: 2px 0; color: var(--muted); }
a { color: var(--blue); }
ul, ol { padding-left: 22px; }
li { margin: 6px 0; }
.table { overflow-x: auto; margin: 14px 0; border: 1px solid var(--line); border-radius: 14px; }
table { border-collapse: collapse; width: 100%; font-size: 15px; }
th, td { text-align: left; vertical-align: top; padding: 10px 12px; border-bottom: 1px solid var(--line); }
th { background: #F4F7FE; font-weight: 600; }
tr:last-child td { border-bottom: none; }
.upper { text-transform: none; }
.links { display: grid; gap: 14px; margin-top: 8px; }
.links a {
  display: flex; align-items: center; justify-content: space-between; gap: 12px;
  background: var(--card); border-radius: 20px; padding: 20px 22px; text-decoration: none; color: var(--ink);
  box-shadow: 0 8px 28px rgba(47,123,255,.14); font-weight: 600; font-size: 18px;
}
.links a span { color: var(--muted); font-weight: 400; font-size: 15px; display: block; }
.links a::after { content: "›"; color: var(--muted); font-size: 26px; }
footer { color: var(--muted); font-size: 14px; text-align: center; margin-top: 28px; }
footer a { color: var(--muted); }
@media (max-width: 600px) {
  .table { border: none; overflow: visible; }
  table, tbody, tr, td { display: block; width: 100%; }
  thead { display: none; }
  tr { border: 1px solid var(--line); border-radius: 14px; padding: 6px 12px; margin-bottom: 10px; }
  td { border: none; padding: 5px 0; }
  td::before { content: attr(data-label); display: block; font-size: 12px; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; }
}
@media (max-width: 520px) {
  .card { padding: 22px 18px 14px; border-radius: 20px; }
  h1 { font-size: 28px; }
  body { font-size: 16px; }
}
"""


def inline(text: str) -> str:
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', text)
    return text


def markdown_to_html(md: str) -> tuple[str, str, str]:
    """Returns (title, meta block, body) for a document."""
    lines = md.splitlines()
    title = lines[0].lstrip("# ").strip()
    out, meta = [], []
    i = 1
    # Metadata lines ("**Effective date:** …") directly under the title.
    while i < len(lines) and (not lines[i].strip() or lines[i].startswith("**")):
        if lines[i].strip():
            meta.append(f"<p>{inline(lines[i].strip())}</p>")
        i += 1
    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if not s:
            i += 1
        elif s.startswith("## "):
            out.append(f"<h2>{inline(s[3:])}</h2>")
            i += 1
        elif s.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            head, body = rows[0], [r for r in rows[2:]]
            t = ["<div class='table'><table><thead><tr>"] + [f"<th>{inline(c)}</th>" for c in head] + ["</tr></thead><tbody>"]
            for r in body:
                # data-label lets narrow screens show each row as a stacked, labeled block.
                t.append("<tr>" + "".join(f"<td data-label='{html.escape(h, quote=True)}'>{inline(c)}</td>" for h, c in zip(head, r)) + "</tr>")
            t.append("</tbody></table></div>")
            out.append("".join(t))
        elif re.match(r"^(- |\d+\. )", s):
            ordered = bool(re.match(r"^\d+\. ", s))
            items = []
            while i < len(lines) and re.match(r"^(- |\d+\. )", lines[i].strip()):
                items.append(re.sub(r"^(- |\d+\. )", "", lines[i].strip()))
                i += 1
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>")
        else:
            para = []
            while i < len(lines) and lines[i].strip() and not re.match(r"^(## |\||- |\d+\. )", lines[i].strip()):
                para.append(lines[i].strip())
                i += 1
            out.append(f"<p>{inline(' '.join(para))}</p>")
    return title, "".join(meta), "\n".join(out)


def page(title: str, body: str, depth: int, description: str) -> str:
    up = "../" * depth
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description)}">
<link rel="icon" href="{up}assets/favicon.png">
<link rel="apple-touch-icon" href="{up}assets/icon.png">
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<header class="brand"><a href="{up}"><img src="{up}assets/icon.png" alt="Zikporx Network app icon">
<div><div class="name">Zikporx Network</div><div class="by">by TechTunerLife LLC</div></div></a></header>
{body}
<footer>© 2026 TechTunerLife LLC · <a href="{up}privacy/">Privacy Policy</a> · <a href="{up}terms/">Terms of Use</a> · <a href="mailto:support@techtunerlife.com">support@techtunerlife.com</a></footer>
</div>
</body>
</html>
"""


def main() -> None:
    for src, dest, short in PAGES:
        title, meta, body = markdown_to_html((ROOT / src).read_text())
        heading = title.split("—")[-1].strip()
        content = f"<main class='card'><h1><span class='accent'>{html.escape(heading)}</span></h1><div class='meta'>{meta}</div>{body}</main>"
        out = ROOT / dest
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(title, content, 1, f"Zikporx Network {short}"))
        print("wrote", dest)

    index = """<main>
<h1 style="margin-bottom:6px"><span class="accent">Legal</span></h1>
<p class="meta">Legal documents for the Zikporx Network app for iPhone and iPad.</p>
<div class="links">
<a href="privacy/"><div>Privacy Policy<span>What the app stores and which services it contacts</span></div></a>
<a href="terms/"><div>Terms of Use<span>Rules for using the app and its network tools</span></div></a>
<a href="mailto:support@techtunerlife.com"><div>Contact Support<span>support@techtunerlife.com</span></div></a>
</div>
</main>"""
    (ROOT / "index.html").write_text(page("Zikporx Network — Legal", index, 0, "Zikporx Network legal documents"))
    print("wrote index.html")


if __name__ == "__main__":
    main()
