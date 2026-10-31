import json
from html.parser import HTMLParser
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import urlsplit

from build import LANGUAGES, ROUTES, ROOT, PRODUCTS, checked_downloads, checked_store, checked_url, load_locales, main, product_cards, route


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

    def test_windows_offers_suite_store_first_and_preserves_direct_pdf_link(self):
        urls = {"suite": "https://apps.microsoft.com/detail/9P5P5QD5GDK1",
                "pdf": "https://apps.microsoft.com/detail/9PBWKBZRBJNR",
                "cad": "https://apps.microsoft.com/detail/9P5CZZSKKG1Q",
                "video": "https://apps.microsoft.com/detail/9NRKLM46BCDG"}
        for product, url in urls.items():
            self.assertEqual(checked_store(url, product), url)
            for bad in [url.replace("https:", "http:"), url + "?redirect=elsewhere",
                        url.rsplit("/", 1)[0] + "/OTHER", url.replace("apps.microsoft.com", "apps.microsoft.com.evil"),
                        urls["pdf" if product == "suite" else "suite"]]:
                with self.assertRaises(ValueError):
                    checked_store(bad, product)
        for language, strings in load_locales().items():
            content = (ROOT / "dist" / route(language, "home").lstrip("/") / "index.html").read_text()
            parser = Links()
            parser.feed(content)
            card = next(attrs for _, attrs in parser.elements if attrs.get("id") == "download-windows")
            self.assertEqual(card["data-download-label"], strings["SUITE_STORE_PRIMARY"])
            windows = Links()
            windows.feed(content.split('id="download-windows"', 1)[1].split('</article>', 1)[0])
            self.assertEqual(windows.links, [urls["suite"], urls["pdf"], urls["cad"], urls["video"]])
            self.assertIn(strings["SUITE_STORE_DOWNLOAD"], content)
            self.assertIn(strings["PDF_STORE_DOWNLOAD"], content)

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
        for platform, releases in checked_downloads(config["downloads"]).items():
            checksums = ""
            for release in releases:
                filename = urlsplit(release["url"]).path.rsplit("/", 1)[-1]
                self.assertTrue(filename.startswith("plervo-suite-"))
                checksums += release["sha256"] + "  " + filename + "\n"
            self.assertEqual((ROOT / "dist" / f"plervo-suite-{platform}.sha256").read_text(), checksums)
        for language, strings in load_locales().items():
            parser = Links()
            parser.feed((ROOT / "dist" / route(language, "home").lstrip("/") / "index.html").read_text())
            self.assertCountEqual([link for link in parser.links if "/releases/download/" in link],
                                  [release["url"] for release in config["downloads"]])
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

    def test_linux_formats_are_each_validated_and_cannot_hide_a_bad_alternative(self):
        def linux(format):
            return {"platform": "linux", "version": "0.1.0-alpha.3", "validated": True,
                    "sha256": "a" * 64,
                    "url": "https://github.com/alportblu/plervo-pdf/releases/download/v0.1.0-alpha.3/"
                           f"plervo-suite-0.1.0-alpha.3-linux-x86_64.{format}"}
        deb, rpm = linux("deb"), linux("rpm")
        self.assertEqual(checked_downloads([deb, rpm])["linux"], [deb, rpm])
        for invalid in (dict(rpm, validated=False), dict(rpm, sha256=""),
                        dict(rpm, url=rpm["url"].replace("x86_64", "aarch64")),
                        dict(rpm, version="0.1.0-alpha.4", url=rpm["url"].replace("alpha.3", "alpha.4")),
                        linux("deb"), linux("exe")):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                checked_downloads([deb, invalid])

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

    def test_catalogue_availability_follows_the_qualified_platform_packages(self):
        release = json.loads((ROOT / "config.json").read_text())["downloads"][0]
        values = load_locales()["en"]
        icons = {product: f"/assets/products/{product}.svg" for product in PRODUCTS}
        pending = product_cards(checked_downloads([dict(release, products=["pdf"])]), values, icons)
        self.assertEqual(pending.count(values["PRODUCT_TESTING"]), len(PRODUCTS))
        self.assertNotIn('href="#downloads"', pending)
        available = product_cards(checked_downloads([dict(release, products=["pdf", "photo"])]), values, icons)
        self.assertEqual(available.count('href="#downloads"'), 1)
        self.assertIn(values["PRODUCT_ALPHA"] + " · macOS", available)
        self.assertEqual(available.count(values["PRODUCT_TESTING"]), len(PRODUCTS) - 1)
        for products in ([], "photo", ["pdf", "unknown"], ["pdf", "pdf"], [{}]):
            with self.subTest(products=products), self.assertRaises(ValueError):
                checked_downloads([dict(release, products=products)])

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
