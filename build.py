"""Build three static languages; English is the default, with no redirects by device."""
import html
import hashlib
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
        if platform not in PLATFORMS:
            raise ValueError("Unknown platform")
        checked_url(release["url"], "github.com")
        path = urlsplit(release["url"]).path
        if not re.fullmatch(r"/alportblu/plervo-pdf/releases/download/[\w.-]+/[\w.-]+", path):
            raise ValueError("Installer must come from the Plervo release repository")
        version = release["version"]
        if not re.fullmatch(r"\d+\.\d+\.\d+(?:-[A-Za-z0-9]+(?:\.[A-Za-z0-9]+)*)?", version):
            raise ValueError("Installer version must be explicit")
        suffixes = {"macos": r"macos-(?:aarch64|x86_64|universal)\.dmg",
                    "windows": r"windows-(?:x86_64|aarch64)\.(?:msi|exe)",
                    "linux": r"linux-x86_64\.(?:deb|rpm)"}
        expected = (r"/alportblu/plervo-pdf/releases/download/v" + re.escape(version)
                    + r"/plervo-suite-" + re.escape(version) + "-" + suffixes[platform])
        if not re.fullmatch(expected, path):
            raise ValueError("The primary download must be Suite, with matching version and platform")
        if not re.fullmatch(r"[a-f0-9]{64}", release["sha256"]):
            raise ValueError("Installer SHA-256 is required")
        if release.get("validated") is not True:
            raise ValueError("Do not publish an unvalidated installer")
        if platform in ("macos", "windows") and release.get("signed") is not True:
            raise ValueError("A public Mac or Windows installer must be signed")
        if platform == "macos" and release.get("notarized") is not True:
            raise ValueError("A public Mac installer must be notarized")
        group = downloads.setdefault(platform, [])
        if group and (platform != "linux" or version != group[0]["version"]
                      or any(Path(item["url"]).suffix == Path(path).suffix for item in group)):
            raise ValueError("Duplicate package format or inconsistent platform version")
        group.append(release)
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


def versioned_asset(dest, filename):
    """A new URL prevents cached assets from styling a different release's HTML."""
    source = dest / "assets" / filename
    digest = hashlib.sha256(source.read_bytes()).hexdigest()[:12]
    target = source.with_name(f"{source.stem}.{digest}{source.suffix}")
    shutil.copyfile(source, target)
    return "/assets/" + target.name


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
    assets = {key: versioned_asset(dest, filename) for key, filename in {
        "STYLE_URL": "style.css", "SCRIPT_URL": "downloads.mjs",
        "MARK_URL": "plervo-mark.svg", "PREVIEW_URL": "plervo-suite.png",
    }.items()}
    templates = {name: (ROOT / "templates" / f"{name}.html").read_text() for name in ("layout", "index", "page")}
    for platform, releases in downloads.items():
        checksums = "".join(release["sha256"] + "  " + urlsplit(release["url"]).path.rsplit("/", 1)[-1] + "\n"
                            for release in releases)
        (dest / f"plervo-suite-{platform}.sha256").write_text(checksums)
    for language, strings in locales.items():
        values = {key: value if key.endswith("_HTML") else html.escape(value, quote=True) for key, value in strings.items()}
        values.update({key.upper() + "_URL": route(language, key) for key in ROUTES[language]})
        values.update(DONATION_URL=donation, SOURCE_URL=source, RELEASE_URL=release_url)
        values.update(assets)
        cards = []
        for platform, label in PLATFORMS.items():
            action = f'<span class="pending">{values[platform.upper() + "_PENDING"]}</span>'
            if platform in downloads:
                action = ""
                for release in downloads[platform]:
                    package = Path(release["url"]).suffix[1:].upper() if platform == "linux" else release["version"]
                    action += (f'<a class="button" href="{html.escape(release["url"], quote=True)}">'
                               f'{values["DOWNLOAD"]} {html.escape(package)} ↗</a>')
                action += f'<a class="hash" href="/plervo-suite-{platform}.sha256">{values["CHECKSUM"]}</a>'
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
            page_values["SCRIPTS"] = f'<script type="module" src="{assets["SCRIPT_URL"]}"></script>' if page == "home" else ""
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
