# from json5.loader import RoundTripLoader, loads
# from json5.dumper import dumps, RoundTripDumper
#
#
# def test_load_string():
#     json_string = """{"foo":"bar"}"""
#     data = loads(json_string, loader=RoundTripLoader())
#     assert data['foo'] == 'bar'
#
#
# def test_load_change_dump_string():
#     json_string = """{"foo": "bar"}"""
#     data = loads(json_string, loader=RoundTripLoader())
#     data['foo'] = 'baz'
#     new_json_string = dumps(data, dumper=RoundTripDumper())
#     assert 'baz' in new_json_string
#     assert new_json_string == """{"foo": "baz"}"""
#
#
# def test_load_change_whitespace_dump_string():
#     json_string = """["foo" ]"""
#     data = loads(json_string, loader=RoundTripLoader())
#     elem = data[0]
#     elem.wsc_after = []
#     new_json_string = dumps(data, dumper=RoundTripDumper())
#     assert new_json_string == """["foo"]"""
