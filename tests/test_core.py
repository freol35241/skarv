import time
import skarv
import threading

import pytest
from unittest.mock import MagicMock


def test_put_get():
    skarv.put("anything", 42)

    res = skarv.get("anything")
    assert isinstance(res, list)
    assert len(res) == 1
    assert res[0].key_expr == "anything"
    assert res[0].value == 42

    for ix in range(10):
        skarv.put(f"anything/{ix}", 42 + ix)

    res = skarv.get("anything")
    assert len(res) == 1

    res = skarv.get("anything/*")
    assert len(res) == 10

    res = skarv.get("anything/**")
    assert len(res) == 11


def test_put_subscribe():

    mock = MagicMock()
    mock_s = MagicMock()
    mock_ss = MagicMock()

    skarv.subscribe("anything")(mock)
    skarv.subscribe("anything/*")(mock_s)
    skarv.subscribe("anything/**")(mock_ss)

    skarv.put("anything", 42)

    mock.assert_called_once()
    assert len(mock.call_args.args) == 1
    assert len(mock.call_args.kwargs) == 0
    assert isinstance(mock.call_args.args[0], skarv.Sample)
    assert mock.call_args.args[0].key_expr == "anything"
    assert mock.call_args.args[0].value == 42

    mock_s.assert_not_called()

    mock_ss.assert_called_once()


def test_put_subscribe_and_get():

    call_args_list = []

    @skarv.subscribe("anything")
    def callback(sample: skarv.Sample):
        call_args_list.append(sample)

        assert skarv.get("another/thing")

    skarv.put("another/thing", 43)

    assert len(call_args_list) == 0

    skarv.put("anything", 42)

    assert len(call_args_list) == 1


def test_recursive_loop():

    @skarv.subscribe("ping")
    def callback(sample: skarv.Sample):
        skarv.put("ping", 42)

    with pytest.raises(RecursionError):
        skarv.put("ping", 42)
