import html.parser
import pytest
import requests

from codex_of_the_damned import navigation


class PageParser(html.parser.HTMLParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.urls = set()

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        url = dict(attrs).get("href", "")
        if url[:4] != "http":
            return
        self.urls.add(url)


@pytest.mark.parametrize("page", [p["self"].url for p in navigation.HELPER.values()])
def test(client, page):
    response = client.get(page, follow_redirects=True)
    assert response.status_code == 200
    parser = PageParser()
    parser.feed(response.data.decode(response.charset))
    for url in parser.urls:
        requests.request("HEAD", url).raise_for_status()


@pytest.mark.parametrize("page", [p["self"].url for p in navigation.HELPER.values()])
def test_fr(client, page):
    response = client.get("/fr" + page, follow_redirects=True)
    assert response.status_code == 200
