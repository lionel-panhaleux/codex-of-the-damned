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
    parser.feed(response.data.decode(response.charset))
    for url in parser.urls:
        requests.request("HEAD", url, timeout=10).raise_for_status()
        VISITED.add(url)


@pytest.mark.parametrize("page", [p["self"].url for p in navigation.HELPER.values()])
def test_fr(client, page):
    response = client.get("/fr" + page, follow_redirects=True)
    assert response.status_code == 200
