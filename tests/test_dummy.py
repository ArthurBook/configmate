import pytest


def add(a, b):
    return a + b


@pytest.mark.parametrize(
    "input_a, input_b, expected",
    [
        (1, 2, 3),  # Test case 1
        (0, 0, 0),  # Test case 2
        (-1, 1, 0),  # Test case 3
        (3, 2, 5),  # Test case 4
    ],
)
def test_add(input_a, input_b, expected):
    result = add(input_a, input_b)
    assert result == expected
