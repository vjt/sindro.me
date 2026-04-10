#!/usr/bin/env python3
"""Generate resume.pdf directly from the resume markdown files.

Reads content/resume/_index.{en,it}.md, renders markdown to HTML,
wraps in a print stylesheet, and generates PDF via WeasyPrint.
"""

import re
import sys
from datetime import date
from pathlib import Path

import markdown

from weasyprint import HTML

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"

PRINT_CSS = """
@page {
    size: A4;
    margin: 12mm 15mm;
}
body {
    font-family: "Fira Sans", "Helvetica Neue", Helvetica, sans-serif;
    font-weight: 300;
    font-size: 10.5pt;
    line-height: 1.5;
    color: #222;
    max-width: 180mm;
    margin: 0 auto;
}
h1:first-of-type {
    font-size: 22pt;
    margin-top: 0;
    margin-bottom: 0.2rem;
}
h1 { font-size: 12pt; border-bottom: 2px solid #268bd2; padding-bottom: 3pt; }
h2 { color: #268bd2; font-size: 10.5pt; margin-bottom: 2pt; }
h2 + p em { color: #555; font-size: 9pt; }
hr { border: none; border-top: 1px solid #ddd; margin: 0.8rem 0; }
a { color: #268bd2; text-decoration: none; }
ul { padding-left: 1.2rem; margin: 0.3rem 0; }
li { margin-bottom: 2pt; }
p { margin: 0.3rem 0; }
.photo {
    width: 80px; height: 80px;
    border-radius: 50%;
    border: 2px solid #268bd2;
    object-fit: cover;
    float: right;
    margin-left: 1rem;
}
.nebula {
    width: 100%;
    max-width: 300px;
    display: block;
    margin: 1rem auto 0.3rem;
    border-radius: 6px;
}
.footer-img {
    text-align: center;
    margin-top: 1.5rem;
    font-size: 8pt;
    color: #555;
}
.footer-img em { font-size: 9pt; }
.footer {
    text-align: center;
    margin-top: 1rem;
    font-size: 8pt;
    color: #666;
}
"""


def parse_md(path):
    """Read a Hugo markdown file, strip front matter, return body."""
    text = path.read_text()
    # Strip YAML front matter
    text = re.sub(r'^---\n.*?\n---\n', '', text, flags=re.DOTALL)
    return text.strip()


def resolve_shortcodes(text):
    """Resolve {{< years-since "DATE" >}} and {{< age "DATE" >}} shortcodes."""
    today = date.today()

    def years_since(match):
        d = date.fromisoformat(match.group(1))
        years = (today - d).days // 365
        return str(years)

    def age(match):
        d = date.fromisoformat(match.group(1))
        months = (today.year - d.year) * 12 + (today.month - d.month)
        if months < 24:
            if months == 1:
                return "1 month"  # will be patched for IT below
            return f"{months} months"
        return str(months // 12)

    text = re.sub(r'\{\{<\s*years-since\s+"([^"]+)"\s*>\}\}', years_since, text)
    text = re.sub(r'\{\{<\s*age\s+"([^"]+)"\s*>\}\}', age, text)
    return text


def resolve_shortcodes_it(text):
    """Italian-specific post-processing for age shortcodes."""
    text = text.replace(" months", " mesi").replace("1 mesi", "1 mese")
    return text


def build_pdf(lang, output_name):
    md_path = ROOT / "content" / "resume" / f"_index.{lang}.md"
    if not md_path.exists():
        print(f"WARNING: {md_path} not found, skipping", file=sys.stderr)
        return

    body = parse_md(md_path)
    body = resolve_shortcodes(body)
    if lang == "it":
        body = resolve_shortcodes_it(body)

    html_body = markdown.markdown(body)

    static = ROOT / "static"
    photo = f'<img src="file://{static}/vjt.jpg" class="photo" alt="">'
    nebula = f'<img src="file://{static}/m27-nebula.jpg" class="nebula" alt="M27 Dumbbell Nebula">'
    nebula_caption = "Foto mia" if lang == "it" else "Photo by me"
    sysadmin_quote = (
        'Il vero sistemista — e le sue auto sono i server.'
        if lang == "it"
        else 'The real sysadmin — and his cars are servers.'
    )
    sysadmin_url = f'https://sindro.me/{"it/" if lang == "it" else ""}posts/2014-02-28-il-vero-sistemista/'

    full_html = f"""<!DOCTYPE html>
<html lang="{lang}">
<head><meta charset="utf-8"><style>{PRINT_CSS}</style></head>
<body>
{photo}
{html_body}
<div class="footer-img">{nebula}<p>M27 (Dumbbell) Planetary Nebula · {nebula_caption}</p></div>
<div class="footer"><a href="{sysadmin_url}"><em>{sysadmin_quote}</em></a></div>
<div class="footer">sindro.me · {today_str(lang)}</div>
</body>
</html>"""

    output = PUBLIC / output_name
    HTML(string=full_html).write_pdf(str(output))
    print(f"  {output_name} ({output.stat().st_size // 1024}KB)")


def today_str(lang):
    d = date.today()
    if lang == "it":
        months_it = ["", "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio",
                      "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre",
                      "Novembre", "Dicembre"]
        return f"{months_it[d.month]} {d.year}"
    return d.strftime("%B %Y")


if __name__ == "__main__":
    build_pdf("en", "resume.pdf")
    build_pdf("it", "resume-it.pdf")
    print("Done.")
