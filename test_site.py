import json
from html.parser import HTMLParser
from pathlib import Path
import unittest
from urllib.parse import urlsplit

from build import ROOT, checked_url, main


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()
        self.scripts = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.scripts += tag == "script"
        if "id" in attrs:
            self.ids.add(attrs["id"])
        self.links.extend(attrs[k] for k in ("href", "src") if k in attrs)


class SiteTests(unittest.TestCase):
    def test_payment_links_reject_other_hosts_and_unsafe_urls(self):
        self.assertEqual(checked_url("https://buymeacoffee.com/alport", "buymeacoffee.com"), "https://buymeacoffee.com/alport")
        for url in ("http://buymeacoffee.com/alport", "https://buymeacoffee.com.evil/a", "https://evil@buymeacoffee.com/a", "https://buymeacoffee.com/a?next=evil", "javascript:alert(1)", "https://buymeacoffee.com/a\nb"):
            with self.assertRaises(ValueError):
                checked_url(url, "buymeacoffee.com")

    def test_generated_pages_have_no_broken_local_links_or_scripts(self):
        main()
        for page in (ROOT / "dist").rglob("*.html"):
            parser = Links()
            parser.feed(page.read_text())
            self.assertEqual(parser.scripts, 0, page)
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
        support = (ROOT / "dist/apoiar/index.html").read_text()
        if config["buy_me_a_coffee_url"]:
            self.assertIn(f'href="{config["buy_me_a_coffee_url"]}"', support)
            self.assertNotIn("Nosso café ainda está passando", support)
        else:
            self.assertNotIn('href="https://buymeacoffee.com/', support)


if __name__ == "__main__":
    unittest.main()
