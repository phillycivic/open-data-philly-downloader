import pytest

from odp_downloader.client import CartoClient, CartoError


class Response:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class Session:
    def __init__(self, payloads):
        self.payloads = iter(payloads)
        self.queries = []

    def mount(self, *_):
        return None

    def post(self, _url, *, data, timeout):
        self.queries.append((data["q"], timeout))
        return Response(next(self.payloads))


def test_query_returns_rows():
    session = Session([{"rows": [{"a": 1}], "fields": {"a": {"type": "number"}}}])
    assert CartoClient(session=session).query("SELECT 1")["rows"] == [{"a": 1}]


def test_query_raises_for_carto_error():
    session = Session([{"error": ["relation does not exist"]}])
    with pytest.raises(CartoError, match="Carto rejected query"):
        CartoClient(session=session).query("SELECT * FROM missing")


def test_iter_query_paginates_until_short_page():
    session = Session(
        [
            {"rows": [{"id": 1}, {"id": 2}]},
            {"rows": [{"id": 3}]},
        ]
    )
    pages = list(CartoClient(session=session).iter_query("SELECT * FROM example", page_size=2))
    assert pages == [[{"id": 1}, {"id": 2}], [{"id": 3}]]
    assert session.queries[0][0].endswith("LIMIT 2 OFFSET 0")
    assert session.queries[1][0].endswith("LIMIT 2 OFFSET 2")
