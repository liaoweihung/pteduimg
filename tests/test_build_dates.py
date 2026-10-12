import datetime
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build


SEO = {
    "canonical": build.abs_url("cards/example.html"),
    "meta_description": "Example description",
    "og_image": build.abs_url("img/example.webp"),
    "keywords": "example, education",
}
PERSON = {
    "@type": "Person",
    "@id": build.abs_url("author.html#person"),
    "name": "Example author",
    "url": build.abs_url("author.html"),
}
NS = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}


class ArticleDatesTest(unittest.TestCase):
    def setUp(self):
        author = patch.object(build, "read_page_json_ld", return_value={"mainEntity": PERSON})
        author.start()
        self.addCleanup(author.stop)

    def article(self, content=None):
        return json.loads(build.render_json_ld(SEO, "Example", content))

    def test_updated_at_has_priority(self):
        self.assertEqual(self.article({"updatedAt": "2026-09-27", "imageUpdatedAt": "2026-09-28"})["dateModified"], "2026-09-27")

    def test_substantive_image_revision_only(self):
        self.assertEqual(self.article({"imageUpdatedAt": "2024-02-29"})["dateModified"], "2024-02-29")

    def test_missing_dates_are_omitted(self):
        for content in (None, {}, {"updatedAt": "", "imageUpdatedAt": None}):
            with self.subTest(content=content):
                self.assertNotIn("dateModified", self.article(content))

    def test_source_check_is_not_content_revision(self):
        self.assertNotIn("dateModified", self.article({"sourceCheckedAt": "2026-10-13"}))

    def test_invalid_dates_warn_and_are_omitted(self):
        for field in ("updatedAt", "imageUpdatedAt"):
            for value in ("2026-02-29", "2026-13-01", "0000-01-01", "2026-1-01", "20261013", " 2026-10-13", "2026-10-13T00:00:00Z", 20261013, False, []):
                with self.subTest(field=field, value=value):
                    with self.assertWarnsRegex(UserWarning, field) as warning:
                        self.assertNotIn("dateModified", self.article({field: value}))
                    self.assertIn(SEO["canonical"], str(warning.warning))

    def test_invalid_primary_can_use_valid_image_date(self):
        with self.assertWarnsRegex(UserWarning, "updatedAt"):
            self.assertEqual(self.article({"updatedAt": "bad", "imageUpdatedAt": "2026-09-28"})["dateModified"], "2026-09-28")

    def test_invalid_secondary_warns_without_replacing_primary(self):
        with self.assertWarnsRegex(UserWarning, "imageUpdatedAt"):
            self.assertEqual(self.article({"updatedAt": "2026-09-27", "imageUpdatedAt": "bad"})["dateModified"], "2026-09-27")

    def test_author_and_other_fields_preserved(self):
        data = self.article()
        self.assertEqual(data, {
            "@context": "https://schema.org", "@type": "Article",
            "headline": "Example", "description": SEO["meta_description"],
            "image": SEO["og_image"], "url": SEO["canonical"],
            "mainEntityOfPage": {"@type": "WebPage", "@id": SEO["canonical"]},
            "inLanguage": "zh-TW",
            "isPartOf": {"@type": "WebSite", "name": build.SITE_TITLE, "url": build.BASE_URL},
            "keywords": SEO["keywords"], "author": PERSON,
        })

    def test_other_author_is_not_overridden(self):
        self.assertNotIn("author", self.article({"author": "Another author"}))

    def test_article_does_not_use_clock(self):
        with patch.object(build.datetime, "datetime") as clock:
            clock.now.side_effect = AssertionError("Build time is not a revision date")
            self.assertNotIn("dateModified", self.article())
            self.assertEqual(self.article({"updatedAt": "2026-09-27"})["dateModified"], "2026-09-27")

    def test_article_stable_across_days(self):
        outputs = []
        for day in (datetime.datetime(2026, 10, 13), datetime.datetime(2027, 1, 1)):
            with patch.object(build.datetime, "datetime") as clock:
                clock.now.return_value = day
                outputs.append([self.article(), self.article({"updatedAt": "2026-09-27"})])
        self.assertEqual(outputs[0], outputs[1])


class SitemapDatesTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        root_patch = patch.object(build, "ROOT", self.root)
        root_patch.start()
        self.addCleanup(root_patch.stop)
        self.content = {
            "img/dated.webp": {"updatedAt": "2026-09-27", "imageUpdatedAt": "2026-09-28"},
            "img/image.webp": {"imageUpdatedAt": "2026-09-28"},
            "img/checked.webp": {"sourceCheckedAt": "2026-10-13"},
            "img/not_generated.webp": {"updatedAt": "2026-09-27"},
        }
        self.pages = ["cards/dated.html", "cards/image.html", "cards/checked.html", "cards/missing.html"]

    def generate(self):
        build.update_sitemap(self.pages, self.content)
        return (self.root / "sitemap.xml").read_bytes()

    def test_only_trusted_dates_and_original_url_rules(self):
        xml = self.generate()
        self.assertEqual(xml, (self.root / "sitemap-main.xml").read_bytes())
        rows = {row.findtext("s:loc", namespaces=NS): row for row in ET.fromstring(xml)}
        self.assertEqual(len(rows), 16 + len(self.pages))
        self.assertNotIn(build.abs_url("cards/not_generated.html"), rows)
        for page, expected in (("cards/dated.html", "2026-09-27"), ("cards/image.html", "2026-09-28"), ("cards/checked.html", None), ("cards/missing.html", None), ("", None), ("about.html", None)):
            with self.subTest(page=page):
                self.assertEqual(rows[build.abs_url(page)].findtext("s:lastmod", namespaces=NS), expected)
        for url, row in rows.items():
            if url not in {build.abs_url(page) for page in self.pages}:
                self.assertIsNone(row.find("s:lastmod", NS))

    def test_sitemap_invalid_date_warns(self):
        self.content["img/dated.webp"] = {"updatedAt": "2026-02-30"}
        with self.assertWarnsRegex(UserWarning, "cards/dated.html"):
            xml = self.generate()
        dated = ET.fromstring(xml).find("s:url[s:loc='" + build.abs_url("cards/dated.html") + "']", NS)
        self.assertIsNone(dated.find("s:lastmod", NS))

    def test_sitemap_does_not_use_clock_or_old_artifacts(self):
        (self.root / "sitemap.xml").write_text("old build date: 2026-10-13", encoding="utf-8")
        with patch.object(build.datetime, "datetime") as clock:
            clock.now.side_effect = AssertionError("Build time is not a revision date")
            first = self.generate()
            self.assertEqual(first, self.generate())

    def test_sitemap_stable_across_days(self):
        outputs = []
        for day in (datetime.datetime(2026, 10, 13), datetime.datetime(2027, 1, 1)):
            with patch.object(build.datetime, "datetime") as clock:
                clock.now.return_value = day
                outputs.append(self.generate())
        self.assertEqual(outputs[0], outputs[1])


class ExistingPagesTest(unittest.TestCase):
    def test_three_articles_keep_every_non_date_field(self):
        content = build.read_card_content()
        seo = json.loads(build.SEO_JSON.read_text(encoding="utf-8"))
        person = build.read_page_json_ld(build.ROOT / "author.html")["mainEntity"]
        for stem in ("comedo", "acne_topicals_02_retinoids", "acne_patch_how_to_use"):
            with self.subTest(page=stem):
                old = build.read_page_json_ld(build.CARDS_DIR / (stem + ".html"))
                record = content.get("img/" + stem + ".webp")
                new = json.loads(build.render_json_ld(seo["cards/" + stem + ".html"], old["headline"], record))
                self.assertEqual(new["author"]["@id"], person["@id"])
                old.pop("dateModified", None)
                new.pop("dateModified", None)
                self.assertEqual(new, old)

    def test_existing_sitemap_urls_priorities_and_frequencies_unchanged(self):
        old = ET.parse(build.ROOT / "sitemap.xml").getroot()
        pages = [row.findtext("s:loc", namespaces=NS).removeprefix(build.BASE_URL) for row in old
                 if row.findtext("s:loc", namespaces=NS).startswith(build.BASE_URL + "cards/")]
        content = build.read_card_content()
        with tempfile.TemporaryDirectory() as temp, patch.object(build, "ROOT", Path(temp)):
            build.update_sitemap(pages, content)
            new = ET.parse(Path(temp) / "sitemap.xml").getroot()
        def without_dates(root):
            return [[(child.tag, child.text) for child in row if child.tag != "{" + NS["s"] + "}lastmod"] for row in root]
        self.assertEqual(without_dates(old), without_dates(new))


if __name__ == "__main__":
    unittest.main()
