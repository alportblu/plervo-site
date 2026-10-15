"""Build three static languages; English is the default, with no redirects by device."""
import html
import json
from pathlib import Path
import re
import shutil
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
LANGUAGES = {"en": "English", "pt": "Português", "es": "Español"}
ROUTES = {
    "en": {"home": "", "support": "support", "security": "security", "privacy": "privacy", "about": "about"},
    "pt": {"home": "", "support": "apoiar", "security": "seguranca", "privacy": "privacidade", "about": "sobre"},
    "es": {"home": "", "support": "apoyar", "security": "seguridad", "privacy": "privacidad", "about": "acerca"},
}
PLATFORMS = {"macos": "macOS", "windows": "Windows", "linux": "Linux"}


def route(language, page):
    prefix = "" if language == "en" else language + "/"
    if page == "404":
        return "/" + prefix + "404.html"
    slug = ROUTES[language][page]
    return "/" + prefix + (slug + "/" if slug else "")


def checked_url(value, host):
    parsed = urlsplit(value)
    if (parsed.scheme != "https" or parsed.netloc != host
            or parsed.query or parsed.fragment or not parsed.path.strip("/")
            or re.search(r"[\s<>\\]", value)):
        raise ValueError(f"Expected a public HTTPS URL on {host}")
    return html.escape(value, quote=True)


def checked_downloads(releases):
    downloads = {}
    for release in releases:
        platform = release["platform"]
        if platform not in PLATFORMS or platform in downloads:
            raise ValueError("Unknown or duplicate platform")
        checked_url(release["url"], "github.com")
        path = urlsplit(release["url"]).path
        if not re.fullmatch(r"/alportblu/plervo-pdf/releases/download/[\w.-]+/[\w.-]+", path):
            raise ValueError("Installer must come from the Plervo release repository")
        if not re.fullmatch(r"[a-f0-9]{64}", release["sha256"]):
            raise ValueError("Installer SHA-256 is required")
        if release.get("validated") is not True:
            raise ValueError("Do not publish an unvalidated installer")
        if platform in ("macos", "windows") and release.get("signed") is not True:
            raise ValueError("A public Mac or Windows installer must be signed")
        if platform == "macos" and release.get("notarized") is not True:
            raise ValueError("A public Mac installer must be notarized")
        downloads[platform] = release
    return downloads


def render(template, values):
    def replace(match):
        key = match.group(1)
        if key not in values:
            raise ValueError(f"Unfilled template: {key}")
        return values[key]
    return re.sub(r"\{\{([A-Z_]+)\}\}", replace, template)


def load_locales():
    locales = {language: json.loads((ROOT / "locales" / f"{language}.json").read_text()) for language in LANGUAGES}
    keys = locales["en"].keys()
    for language, strings in locales.items():
        if strings.keys() != keys or any(not isinstance(value, str) or not value for value in strings.values()):
            raise ValueError(f"Incomplete translation: {language}")
    return locales


def main():
    config = json.loads((ROOT / "config.json").read_text())
    if config["site_url"] != "https://plervo.com":
        raise ValueError("Unexpected production domain")
    donation = checked_url(config["buy_me_a_coffee_url"], "buymeacoffee.com")
    source = checked_url(config["source_url"], "github.com")
    release_url = checked_url(config["release_url"], "github.com")
    downloads = checked_downloads(config["downloads"])
    locales = load_locales()
    dest = ROOT / "dist"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(ROOT / "public", dest)
    templates = {name: (ROOT / "templates" / f"{name}.html").read_text() for name in ("layout", "index", "page")}
    for platform, release in downloads.items():
        filename = urlsplit(release["url"]).path.rsplit("/", 1)[-1]
        (dest / f"plervo-pdf-{platform}.sha256").write_text(release["sha256"] + "  " + filename + "\n")
    for language, strings in locales.items():
        values = {key: value if key.endswith("_HTML") else html.escape(value, quote=True) for key, value in strings.items()}
        values.update({key.upper() + "_URL": route(language, key) for key in ROUTES[language]})
        values.update(DONATION_URL=donation, SOURCE_URL=source, RELEASE_URL=release_url)
        cards = []
        for platform, label in PLATFORMS.items():
            action = f'<span class="pending">{values[platform.upper() + "_PENDING"]}</span>'
            if platform in downloads:
                release = downloads[platform]
                action = (f'<a class="button" href="{html.escape(release["url"], quote=True)}">'
                          f'{values["DOWNLOAD"]} {html.escape(release["version"])} ↗</a>'
                          f'<a class="hash" href="/plervo-pdf-{platform}.sha256">{values["CHECKSUM"]}</a>')
            cards.append(f'<article class="download" id="download-{platform}" data-platform="{platform}">'
                         f'<h3>{label}</h3><p>{values[platform.upper() + "_DETAIL"]}</p>{action}</article>')
        values["DOWNLOADS"] = "".join(cards)
        for page in (*ROUTES[language], "404"):
            path = route(language, page)
            page_values = dict(values)
            page_values["LANGUAGE_LINKS"] = "".join(
                f'<a href="{route(other, page)}" lang="{locales[other]["LANG"]}" hreflang="{locales[other]["LANG"]}"'
                + (' aria-current="page"' if other == language else '') + f'>{name}</a>'
                for other, name in LANGUAGES.items())
            page_values["ALTERNATES"] = "".join(
                f'<link rel="alternate" hreflang="{locales[other]["LANG"]}" href="https://plervo.com{route(other, page)}">'
                for other in LANGUAGES) + f'<link rel="alternate" hreflang="x-default" href="https://plervo.com{route("en", page)}">'
            page_values["CANONICAL"] = "https://plervo.com" + path
            page_values["ROBOTS"] = '<meta name="robots" content="noindex">' if page == "404" else ""
            page_values["TITLE"] = values[page.upper() + "_TITLE"]
            page_values["DESCRIPTION"] = values[page.upper() + "_DESCRIPTION"]
            page_values["META_TITLE"] = page_values["TITLE"] + ("" if page == "home" else " — Plervo")
            page_values["SCRIPTS"] = '<script type="module" src="/assets/downloads.mjs"></script>' if page == "home" else ""
            if page == "home":
                page_values["MAIN"] = render(templates["index"], page_values)
            else:
                page_values["CONTENT"] = render(values[page.upper() + "_HTML"], page_values)
                page_values["MAIN"] = render(templates["page"], page_values)
            target = dest / path.lstrip("/")
            if page != "404":
                target /= "index.html"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(render(templates["layout"], page_values))
    paths = [route(language, page) for language in LANGUAGES for page in ROUTES[language]]
    (dest / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + ''.join(f'<url><loc>https://plervo.com{path}</loc></url>' for path in paths) + '</urlset>\n')
    # Preserve links shared before English became the default.
    (dest / "_redirects").write_text("".join(f'/{slug} /pt/{slug}/ 301\n/{slug}/ /pt/{slug}/ 301\n' for slug in ROUTES["pt"].values() if slug))
    print(f"Site built: {dest} (3 languages, 18 pages)")


if __name__ == "__main__":
    main()
