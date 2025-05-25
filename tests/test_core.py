import splice

from unittest.mock import MagicMock


def test_put_get():
    splice.put("anything", 42)

    res = splice.get("anything")
    assert isinstance(res, list)
    assert len(res) == 1
    assert res[0].key_expr == "anything"
    assert res[0].value == 42

    for ix in range(10):
        splice.put(f"anything/{ix}", 42+ ix)

    res = splice.get("anything")
    assert len(res) == 1

    res = splice.get("anything/*")
    assert len(res) == 10

    res = splice.get("anything/**")
    assert len(res) == 11


def test_put_subscribe():

    mock = MagicMock()
    mock_s = MagicMock()
    mock_ss = MagicMock()

    splice.subscribe("anything")(mock)
    splice.subscribe("anything/*")(mock_s)
    splice.subscribe("anything/**")(mock_ss)

    splice.put("anything", 42)

    mock.assert_called_once()
    assert len(mock.call_args.args) == 1
    assert len(mock.call_args.kwargs) == 0
    assert isinstance(mock.call_args.args[0], splice.Sample)
    assert mock.call_args.args[0].key_expr == "anything"
    assert mock.call_args.args[0].value == 42

    mock_s.assert_not_called()

    mock_ss.assert_called_once()

def test_put_subscribe_and_get():

    call_args_list = []

    @splice.subscribe("anything")
    def callback(sample: splice.Sample):
        call_args_list.append(sample)

        assert splice.get("another/thing")


    splice.put("another/thing", 43)

    assert len(call_args_list) == 0

    splice.put("anything", 42)

    assert len(call_args_list) == 1



