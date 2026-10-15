import json
from html.parser import HTMLParser
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import urlsplit

from build import LANGUAGES, ROUTES, ROOT, checked_downloads, checked_url, load_locales, main, route


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()
        self.scripts = []
        self.elements = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.elements.append((tag, attrs))
        if tag == "script":
            self.scripts.append(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        self.links.extend(attrs[k] for k in ("href", "src") if k in attrs)


class SiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        main()

    def test_payment_links_reject_other_hosts_and_unsafe_urls(self):
        self.assertEqual(checked_url("https://buymeacoffee.com/alport", "buymeacoffee.com"), "https://buymeacoffee.com/alport")
        for url in ("http://buymeacoffee.com/alport", "https://buymeacoffee.com.evil/a", "https://evil@buymeacoffee.com/a", "https://buymeacoffee.com/a?next=evil", "javascript:alert(1)", "https://buymeacoffee.com/a\nb"):
            with self.assertRaises(ValueError):
                checked_url(url, "buymeacoffee.com")

    def test_generated_pages_have_no_broken_links_or_external_scripts(self):
        for page in (ROOT / "dist").rglob("*.html"):
            parser = Links()
            parser.feed(page.read_text())
            homes = {ROOT / "dist" / route(language, "home").lstrip("/") / "index.html" for language in LANGUAGES}
            if page in homes:
                self.assertEqual(len(parser.scripts), 1, page)
                self.assertEqual(parser.scripts[0]["type"], "module")
                self.assertRegex(parser.scripts[0]["src"], r"^/assets/downloads\.[a-f0-9]{12}\.mjs$")
            else:
                self.assertEqual(parser.scripts, [], page)
            for link in parser.links:
                parsed = urlsplit(link)
                if parsed.scheme or parsed.netloc:
                    self.assertEqual(parsed.scheme, "https", link)
                    continue
                target = ROOT / "dist" / parsed.path.lstrip("/") if parsed.path else page
                if target.is_dir():
                    target /= "index.html"
                self.assertTrue(target.is_file(), f"{page}: {link}")
                if parsed.fragment:
                    target_parser = Links()
                    target_parser.feed(target.read_text())
                    self.assertIn(parsed.fragment, target_parser.ids)
        config = json.loads((ROOT / "config.json").read_text())
        for language in LANGUAGES:
            support = (ROOT / "dist" / route(language, "support").lstrip("/") / "index.html").read_text()
            self.assertIn(f'href="{config["buy_me_a_coffee_url"]}"', support)

    def test_language_switch_preserves_page_and_navigation(self):
        locales = load_locales()
        self.assertEqual(len(list((ROOT / "dist").rglob("*.html"))), 18)
        self.assertEqual(route("en", "home"), "/")
        for language in LANGUAGES:
            for page in (*ROUTES[language], "404"):
                target = ROOT / "dist" / route(language, page).lstrip("/")
                if page != "404":
                    target /= "index.html"
                parser = Links()
                content = target.read_text()
                parser.feed(content)
                self.assertNotIn("{{", content)
                self.assertIn(("html", {"lang": locales[language]["LANG"]}), parser.elements)
                switches = [attrs for tag, attrs in parser.elements if tag == "a" and "hreflang" in attrs]
                self.assertEqual(len(switches), 3)
                self.assertEqual([link["href"] for link in switches], [route(other, page) for other in LANGUAGES])
                self.assertEqual([link["href"] for link in switches if link.get("aria-current") == "page"], [route(language, page)])
                self.assertIn(("link", {"rel": "canonical", "href": "https://plervo.com" + route(language, page)}), parser.elements)
                self.assertIn(("link", {"rel": "alternate", "hreflang": "x-default", "href": "https://plervo.com" + route("en", page)}), parser.elements)
                for target_page in ("home", "support", "privacy", "security", "about"):
                    self.assertIn(route(language, target_page), parser.links)

    def test_updated_styles_and_scripts_cannot_reuse_a_visitors_cached_url(self):
        def resource_urls(root):
            parser = Links()
            parser.feed((root / "dist/index.html").read_text())
            return {"style": next(attrs["href"] for tag, attrs in parser.elements
                                  if tag == "link" and attrs.get("rel") == "stylesheet"),
                    "script": parser.scripts[0]["src"]}

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("public", "templates", "locales"):
                shutil.copytree(ROOT / name, root / name)
            shutil.copyfile(ROOT / "config.json", root / "config.json")
            with patch("build.ROOT", root):
                main()
                original = resource_urls(root)
                main()
                self.assertEqual(resource_urls(root), original)
                for name in ("style.css", "downloads.mjs"):
                    with (root / "public/assets" / name).open("a") as stream:
                        stream.write("\n/* changed release asset */\n")
                main()
                updated = resource_urls(root)
                for kind in original:
                    self.assertNotEqual(original[kind], updated[kind], kind)
                    self.assertIn("changed release asset", (root / "dist" / updated[kind].lstrip("/")).read_text())

    def test_downloads_match_verified_package_in_each_language(self):
        config = json.loads((ROOT / "config.json").read_text())
        release = config["downloads"][0]
        self.assertEqual(release["platform"], "macos")
        filename = urlsplit(release["url"]).path.rsplit("/", 1)[-1]
        self.assertTrue(filename.startswith("plervo-suite-"))
        self.assertEqual((ROOT / "dist/plervo-suite-macos.sha256").read_text(), release["sha256"] + "  " + filename + "\n")
        for language, strings in load_locales().items():
            parser = Links()
            parser.feed((ROOT / "dist" / route(language, "home").lstrip("/") / "index.html").read_text())
            self.assertEqual([link for link in parser.links if "/releases/download/" in link], [release["url"]])
            device = next(attrs for _, attrs in parser.elements if attrs.get("id") == "device-note")
            self.assertEqual(device["data-desktop"], strings["DEVICE_DESKTOP"])
            self.assertEqual(device["data-mobile"], strings["DEVICE_MOBILE"])
            self.assertEqual(device["data-badge"], strings["DEVICE_BADGE"])

    def test_release_guard_rejects_untrusted_unvalidated_or_unsigned_packages(self):
        release = json.loads((ROOT / "config.json").read_text())["downloads"][0]
        self.assertIn("macos", checked_downloads([release]))
        for patch in (
            {"url": "https://github.com/other/project/releases/download/v1/app.dmg"},
            {"url": "https://github.com/alportblu/plervo-pdf/releases/download/v1/../../evil"},
            {"sha256": "unknown"}, {"validated": False}, {"validated": "true"},
            {"signed": False}, {"notarized": False}, {"platform": "android"},
            {"platform": "windows", "signed": False},
        ):
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                checked_downloads([dict(release, **patch)])
        with self.assertRaises(ValueError):
            checked_downloads([release, release])

    def test_primary_download_cannot_be_pdf_or_mismatch_version_or_platform(self):
        release = json.loads((ROOT / "config.json").read_text())["downloads"][0]
        for patch in (
            {"url": release["url"].replace("/plervo-suite-", "/plervo-pdf-")},
            {"version": "9.9.9"},
            {"platform": "linux"},
            {"url": release["url"].replace("/download/v", "/download/other-")},
        ):
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                checked_downloads([dict(release, **patch)])

    def test_legacy_portuguese_links_redirect_to_portuguese(self):
        redirects = (ROOT / "dist/_redirects").read_text().splitlines()
        for slug in ("apoiar", "seguranca", "privacidade", "sobre"):
            self.assertIn(f"/{slug}/ /pt/{slug}/ 301", redirects)
            self.assertIn(f"/{slug} /pt/{slug}/ 301", redirects)

    def test_sitemap_covers_all_public_language_routes(self):
        import xml.etree.ElementTree as ET
        sitemap = ET.parse(ROOT / "dist/sitemap.xml")
        urls = {item.text for item in sitemap.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")}
        expected = {"https://plervo.com" + route(language, page) for language in LANGUAGES for page in ROUTES[language]}
        self.assertEqual(urls, expected)


if __name__ == "__main__":
    unittest.main()
