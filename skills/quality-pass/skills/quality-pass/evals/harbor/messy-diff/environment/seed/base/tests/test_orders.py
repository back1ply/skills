from orders import line_total


def test_line_total():
    assert line_total({"price": 2.5, "qty": 4}) == 10.0
