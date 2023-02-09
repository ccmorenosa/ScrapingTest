"""."""
import scrapy
from pathlib import Path
import re
from scrapy.linkextractors import LinkExtractor
from deep_translator import GoogleTranslator


class MainSpider(scrapy.Spider):
    name = "main"
    user_agent = (
        "Mozilla/5.0 (Windows NT 6.1; WOW64) "
        "AppleWebKit/537.1 (KHTML, like Gecko) "
        "Chrome/22.0.1207.1 "
        "Safari/537.1"
    )
    allowed_domains = ["www.classcentral.com"]
    start_urls = [
        "https://www.classcentral.com/"
    ]

    url_matcher = re.compile(r"^(https://www.classcentral.com)?/(.*)/?")

    output_path = Path("../docs").resolve()

    translator = GoogleTranslator(source='en', target='hi')

    def translate(self, text):
        return self.translator.translate(text)

    def parse(self, response):
        content = response.text
        translated = response.text

        page = re.match(
            r"(https://www.classcentral.com)?/(.*)/?",
            response.url
        )
        orig_filename = self.output_path / "original" / page[2]
        orig_filename.mkdir(parents=True, exist_ok=True)

        hindi_filename = self.output_path / "hindi" / page[2]
        hindi_filename.mkdir(parents=True, exist_ok=True)

        text_fields = {
            'span': response.css('span::text').getall(),
            'h1': response.css('h1::text').getall(),
            'h2': response.css('h2::text').getall(),
            'h3': response.css('h3::text').getall(),
            'h4': response.css('h4::text').getall(),
            'h5': response.css('h5::text').getall(),
            'p': response.css('p::text').getall(),
            'a': response.css('a::text').getall(),
            'strong': response.css('strong::text').getall(),
            'button': response.css('button::text').getall(),
        }

        for key, item in text_fields.items():
            for text in item:
                if text:
                    trans_text = self.translate(text)
                    translated = re.sub(
                        f"> *\n? *{text} *\n? *<", f">{trans_text}<", translated
                    )

        if not page[2]:
            link_extractor = LinkExtractor(allow=self.url_matcher)

            for link in link_extractor.extract_links(response):
                yield response.follow(link.url, callback=self.parse)
                content = content.replace(
                    link.url, f"./{self.url_matcher.match(link.url)[2]}"
                )
                translated = translated.replace(
                    link.url, f"./{self.url_matcher.match(link.url)[2]}"
                )

        with open(orig_filename/"index.html", "w") as index:
            index.write(content)

        with open(hindi_filename/"index.html", "w") as index:
            index.write(translated)
