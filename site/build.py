#!/usr/bin/env python3
"""Builds the public legal site from the Markdown documents in the repository root.

The pages are generated rather than written by hand so the published text and the text
under review in Git cannot drift apart: there is exactly one source for each document.

Usage:
    pip install markdown
    python3 site/build.py            # writes site/_site/
    python3 site/build.py --serve    # writes, then serves on http://localhost:8000
"""

from __future__ import annotations

import argparse
import html
import re
import shutil
from datetime import date
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent / "_site"

SUPPORT_EMAIL = "anton.sherbakov.01@gmail.com"

# Each published page: source document, output name, tab label, the language it is in, and
# whether it belongs in the navigation. The translations are reached from the language
# switch on the corresponding Russian page rather than from the navigation.
PAGES = [
    ("PRIVACY_POLICY.md", "privacy.html", "Политика конфиденциальности", "ru", True),
    ("TERMS_OF_USE.md", "terms.html", "Лицензионное соглашение", "ru", True),
    ("DELETE_ACCOUNT.md", "delete-account.html", "Удаление аккаунта", "ru", True),
    ("THIRD_PARTY_NOTICES.md", "third-party.html", "Компоненты третьих лиц", "ru", True),
    ("docs/ANALYTICS_EVENTS.md", "analytics.html", "События счётчиков", "ru", True),
    ("LEGAL_REQUISITES.md", "requisites.html", "Реквизиты", "ru", True),
]

# The other language of the same document, so every page can offer the switch.
# YouLife publishes Russian texts only for now.
TRANSLATIONS: dict[str, tuple[str, str]] = {}

# The documents cross-reference each other by file name. On the site those references must
# lead to the generated pages, so a reader can follow them without cloning the repository.
# The keys are matched against the code spans exactly as they appear in the text, so a
# document that names a file which is not published here shows up as plain text — that is
# how a dangling reference is meant to be noticed.
DOC_LINKS = {
    "PRIVACY_POLICY.md": "privacy.html",
    "TERMS_OF_USE.md": "terms.html",
    "DELETE_ACCOUNT.md": "delete-account.html",
    "THIRD_PARTY_NOTICES.md": "third-party.html",
    "LEGAL_REQUISITES.md": "requisites.html",
    "docs/ANALYTICS_EVENTS.md": "analytics.html",
}

STYLE = """
:root {
  color-scheme: light dark;
  --bg: #fbfaf8;
  --surface: #ffffff;
  --text: #1b1a18;
  --muted: #5f5b55;
  --line: #e3ded6;
  --accent: #7a5b2e;
  --accent-soft: #f3ede2;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #16151a;
    --surface: #1e1d23;
    --text: #eceaf0;
    --muted: #a3a0aa;
    --line: #34323b;
    --accent: #d9b678;
    --accent-soft: #262430;
  }
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font: 16px/1.65 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  -webkit-text-size-adjust: 100%;
}
.wrap { max-width: 46rem; margin: 0 auto; padding: 2rem 1.25rem 5rem; }
header.site {
  border-bottom: 1px solid var(--line);
  background: var(--surface);
}
header.site .wrap { padding: 1.25rem 1.25rem; display: flex; flex-wrap: wrap; gap: .75rem 1.25rem; align-items: baseline; }
header.site a.brand { font-weight: 650; color: var(--text); text-decoration: none; font-size: 1.05rem; }
header.site nav { display: flex; flex-wrap: wrap; gap: 1rem; margin-inline-start: auto; }
header.site nav a { color: var(--muted); text-decoration: none; font-size: .92rem; }
header.site nav a:hover, header.site nav a[aria-current="page"] { color: var(--accent); }
h1 { font-size: 1.7rem; line-height: 1.25; margin: 2rem 0 .5rem; letter-spacing: -.01em; }
h2 { font-size: 1.22rem; margin: 2.4rem 0 .6rem; letter-spacing: -.005em; }
h3 { font-size: 1.03rem; margin: 1.8rem 0 .4rem; }
p, li { overflow-wrap: break-word; }
a { color: var(--accent); }
code {
  background: var(--accent-soft);
  padding: .1em .35em;
  border-radius: .25rem;
  font-size: .9em;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}
blockquote {
  margin: 1.2rem 0;
  padding: .75rem 1rem;
  border-inline-start: 3px solid var(--accent);
  background: var(--accent-soft);
  border-radius: 0 .35rem .35rem 0;
  color: var(--muted);
}
blockquote p { margin: .3rem 0; }
.table-scroll { overflow-x: auto; margin: 1.1rem 0; }
table { border-collapse: collapse; width: 100%; font-size: .93rem; }
th, td { text-align: start; vertical-align: top; padding: .5rem .7rem; border-bottom: 1px solid var(--line); }
th { font-weight: 600; color: var(--muted); }
hr { border: 0; border-top: 1px solid var(--line); margin: 2.5rem 0; }
.lang { display: inline-block; margin: .25rem 0 1.5rem; font-size: .92rem; }
footer.site {
  border-top: 1px solid var(--line);
  color: var(--muted);
  font-size: .88rem;
}
footer.site .wrap { padding: 1.5rem 1.25rem 3rem; }
.cards { display: grid; gap: .9rem; margin: 1.5rem 0; padding: 0; list-style: none; }
.cards a {
  display: block;
  padding: 1rem 1.1rem;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: .6rem;
  text-decoration: none;
  color: var(--text);
}
.cards a:hover { border-color: var(--accent); }
.cards strong { display: block; font-size: 1.02rem; }
.cards span { color: var(--muted); font-size: .9rem; }
"""

SHELL = """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<meta name="robots" content="index, follow">
<style>{style}</style>
</head>
<body>
<header class="site"><div class="wrap">
<a class="brand" href="./">YouLife</a>
<nav>{nav}</nav>
</div></header>
<main class="wrap">{body}</main>
<footer class="site"><div class="wrap">
<p>ИП Щербаков Антон Алексеевич · ОГРНИП 325710000062103 · ИНН 712807221159<br>
<a href="mailto:{email}">{email}</a></p>
<p>Обновлено {updated}.</p>
</div></footer>
</body>
</html>
"""


def nav_html(current: str) -> str:
    items = [("./", "Главная")] + [(name, label) for _, name, label, _, in_nav in PAGES if in_nav]
    out = []
    for href, label in items:
        mark = ' aria-current="page"' if href == current else ""
        out.append(f'<a href="{href}"{mark}>{html.escape(label)}</a>')
    return "".join(out)


def render(source: Path) -> tuple[str, str]:
    """Returns (html body, first paragraph as a description)."""
    text = source.read_text(encoding="utf-8")
    converted = markdown.markdown(text, extensions=["tables", "sane_lists", "attr_list"])
    # Wide tables must scroll inside their own box rather than pushing the page sideways.
    converted = converted.replace("<table>", '<div class="table-scroll"><table>')
    converted = converted.replace("</table>", "</table></div>")

    # A reference to a sibling document should open that document's page, not a raw file.
    # Longest key first, so `docs/ANALYTICS_EVENTS.md` is not matched by the bare name.
    for filename in sorted(DOC_LINKS, key=len, reverse=True):
        converted = converted.replace(
            f"<code>{filename}</code>",
            f'<a href="{DOC_LINKS[filename]}"><code>{filename}</code></a>',
        )

    plain = re.sub(r"<[^>]+>", " ", converted)
    plain = html.unescape(re.sub(r"\s+", " ", plain)).strip()
    return converted, plain[:180]


def build() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    updated = date.today().strftime("%d.%m.%Y")

    for filename, out_name, label, lang, _ in PAGES:
        body, description = render(ROOT / filename)
        translation = TRANSLATIONS.get(out_name)
        if translation:
            href, name = translation
            body = f'<p class="lang"><a href="{href}">{name}</a></p>' + body
        (OUT / out_name).write_text(
            SHELL.format(
                lang=lang,
                title=f"{label} — YouLife",
                description=html.escape(description, quote=True),
                style=STYLE,
                nav=nav_html(out_name),
                body=body,
                email=SUPPORT_EMAIL,
                updated=updated,
            ),
            encoding="utf-8",
        )

    index_body = """
<h1>YouLife</h1>
<p>Симулятор жизни в исторических эпохах: от рождения до старости, из поколения в поколение.
Игра работает без интернета; аккаунт необязателен и нужен только для покупок, обращений и
облачной копии партии.</p>
<p>Здесь опубликованы юридические документы игры.</p>
<ul class="cards">
<li><a href="privacy.html"><strong>Политика конфиденциальности</strong>
<span>Как обрабатываются персональные данные · 152-ФЗ</span></a></li>
<li><a href="terms.html"><strong>Лицензионное соглашение и оферта</strong>
<span>Условия использования и покупки «Летописца»</span></a></li>
<li><a href="delete-account.html"><strong>Удаление аккаунта</strong>
<span>Как удалить аккаунт и что при этом удаляется</span></a></li>
<li><a href="third-party.html"><strong>Компоненты третьих лиц</strong>
<span>Библиотеки, шрифты, данные карт и их лицензии</span></a></li>
<li><a href="analytics.html"><strong>События счётчиков</strong>
<span>Закрытый перечень того, что может быть отправлено</span></a></li>
<li><a href="requisites.html"><strong>Реквизиты правообладателя</strong>
<span>Сведения о продавце и сроки ответа на обращения</span></a></li>
</ul>
<h2>Коротко о данных</h2>
<p>Партии хранятся на устройстве. Сервер находится в России; рекламы нет; данные карт
игра не получает — оплату проводит магазин приложений. Отчёты об ошибках и счётчики не
содержат идентификаторов игрока и выключаются в настройках.</p>
<h2>Поддержка</h2>
<p>Вопросы, запросы по персональным данным, удаление аккаунта и претензии — на
<a href="mailto:{email}">{email}</a>.</p>
""".format(email=SUPPORT_EMAIL)

    (OUT / "index.html").write_text(
        SHELL.format(
            lang="ru",
            title="YouLife — документы",
            description="Политика конфиденциальности, лицензионное соглашение и удаление аккаунта игры YouLife.",
            style=STYLE,
            nav=nav_html("./"),
            body=index_body,
            email=SUPPORT_EMAIL,
            updated=updated,
        ),
        encoding="utf-8",
    )

    # Tells GitHub Pages not to run the files through Jekyll.
    (OUT / ".nojekyll").write_text("", encoding="utf-8")

    for path in sorted(OUT.iterdir()):
        print(f"  {path.name}  {path.stat().st_size:>6} bytes")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--serve", action="store_true", help="serve the result on :8000")
    arguments = parser.parse_args()

    build()

    if arguments.serve:
        import functools
        import http.server

        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(OUT))
        print("http://localhost:8000")
        http.server.HTTPServer(("", 8000), handler).serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
