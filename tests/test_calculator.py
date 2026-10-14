from chatbot.calculator import CalculatorError, calculate, format_number


def raises(expression):
    try:
        calculate(expression)
    except CalculatorError:
        return True
    return False


def test_basic_math_and_precedence():
    assert calculate("2 + 3 * 4") == 14
    assert calculate("(2 + 3) * 4") == 20
    assert calculate("10 / 4") == 2.5
    assert calculate("10 % 3") == 1
    assert calculate("-5 + 2") == -3


def test_caret_means_power():
    assert calculate("2^10") == 1024


def test_division_by_zero_is_an_error():
    assert raises("1 / 0")
    assert raises("5 % 0")


def test_huge_exponents_are_refused():
    assert raises("9 ^ 9 ^ 9")
    assert raises("2 ** 101")


def test_only_math_is_allowed():
    assert raises("__import__('os').system('echo hi')")
    assert raises("open('file.txt')")
    assert raises("[1, 2, 3]")
    assert raises("True + 1")
    assert raises("'a' * 3")


def test_invalid_input():
    assert raises("")
    assert raises("2 +")
    assert raises("2 3")
    assert raises("1" * 300)


def test_complex_results_are_refused():
    assert raises("(-8) ** 0.5")


def test_format_number():
    assert format_number(2.0) == "2"
    assert format_number(0.1 + 0.2) == "0.3"
    assert format_number(2.5) == "2.5"
    assert format_number(7) == "7"
    assert format_number(1 / 3) == "0.333333"
