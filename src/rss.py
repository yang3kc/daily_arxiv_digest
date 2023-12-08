from bs4 import BeautifulSoup
import feedparser


class ArxivRSS:
    def __init__(self, url):
        self.url = url
        self.papers = dict()

    def fetch_paper_list(self):
        feed = self._fetch_n_parse_rss()

        for rss_entry in feed["entries"]:
            paper_information = self._extract_paper_information(rss_entry)
            self.papers[paper_information["id"]] = paper_information
        return self.papers

    def _fetch_n_parse_rss(self):
        feed = feedparser.parse(self.url)
        return feed

    def _parse_html_element(self, raw_string):
        soup = BeautifulSoup(raw_string, "html.parser")
        return soup.text

    def _extract_paper_information(self, rss_entry):
        paper_id = rss_entry["id"]
        paper_title = rss_entry["title"]
        paper_abstract = self._parse_html_element(rss_entry["summary"])
        paper_url = rss_entry["link"]
        paper_authors = []
        for author_info in rss_entry["authors"]:
            author_name = self._parse_html_element(author_info["name"])
            paper_authors.append(author_name)
        return {
            "id": paper_id,
            "title": paper_title,
            "abstract": paper_abstract,
            "url": paper_url,
            "authors": paper_authors,
        }
