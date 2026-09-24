from odp_downloader.download import Downloader


def test_generic_query_quotes_table_and_has_stable_default_order():
    fields = {"cartodb_id": {"type": "number"}, "name": {"type": "string"}}
    query = Downloader._select_query("some_table", fields, where="name IS NOT NULL")
    assert query == (
        'SELECT * FROM "some_table" WHERE name IS NOT NULL '
        'ORDER BY "cartodb_id"'
    )


def test_generic_query_falls_back_to_objectid_order():
    fields = {"objectid": {"type": "number"}, "name": {"type": "string"}}
    query = Downloader._select_query("some_table", fields)
    assert query.endswith('ORDER BY "objectid"')


def test_geometry_columns_are_computed_only_when_present():
    fields = {
        "cartodb_id": {"type": "number"},
        "the_geom": {"type": "geometry"},
        "lng": {"type": "number"},
        "lat": {"type": "number"},
    }
    query = Downloader._select_query("places", fields)
    assert "st_x(the_geom) AS lng" in query
    assert "st_y(the_geom) AS lat" in query
