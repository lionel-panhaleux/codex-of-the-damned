import html.parser
import pytest
import requests

from codex_of_the_damned import navigation

VISITED = set()


class PageParser(html.parser.HTMLParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.urls = set()

    def handle_starttag(self, tag, attrs):
        if tag not in ["a", "img"]:
            return
        url = dict(attrs).get("href", "") or dict(attrs).get("src", "")
        # ignore internal hyperlinks
        if url[:4] != "http" or url in VISITED:
            return
        self.urls.add(url)


@pytest.mark.parametrize("page", [p["self"].url for p in navigation.HELPER.values()])
def test(client, page):
    response = client.get(page, follow_redirects=True)
    assert response.status_code == 200
    parser = PageParser()
    parser.feed(response.text)
    for url in parser.urls:
        # pass some urls - too much anti-scrapping stuff there
        if url.startswith("https://www.ebay.com"):
            continue
        if url.startswith("https://www.kickstarter.com"):
            continue
        try:
            try:
                requests.request(
                    "HEAD", url, timeout=10, headers={"User-Agent": "python"}
                ).raise_for_status()
            except requests.exceptions.HTTPError:
                requests.get(
                    url,
                    timeout=10,
                    headers={
                        "User-Agent": "Mozilla/5.0 (compatible; python/3.9)",
                    },
                ).raise_for_status()
        except Exception:
            assert False, url
        VISITED.add(url)


@pytest.mark.parametrize("page", [p["self"].url for p in navigation.HELPER.values()])
def test_fr(client, page):
    response = client.get("/fr" + page, follow_redirects=True)
    assert response.status_code == 200


def test_sitemap(client):
    response = client.get("/sitemap.xml", follow_redirects=True)
    assert response.status_code == 200
    assert response.content_type == "application/xml"
