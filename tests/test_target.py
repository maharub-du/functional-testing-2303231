"""Comprehensive functional tests for target.py — all 16 functions.

Strategy:
  - Valid cases: typical inputs, standard boundaries
  - Boundary cases: edge values at decision thresholds
  - Invalid inputs: wrong types, negative values, empty containers
  - Exception checks: exact exception class & exact message matching with pytest.raises(match=...)
  - Result type checks: isinstance assertions where return type matters
  - Float precision: pytest.approx only where truly needed
"""

import pytest
from target import (
    is_adult,
    celsius_to_fahrenheit,
    count_vowels,
    invert,
    greet,
    find_max,
    get_price,
    swap,
    common_items,
    is_leap_year,
    to_int,
    divide,
    power,
    square_root,
    factorial,
    average,
)


# ---------------------------------------------------------------------------
# 1. is_adult(age)
# ---------------------------------------------------------------------------
class TestIsAdult:
    """age >= 18 returns True; age < 0 raises ValueError."""

    @pytest.mark.parametrize(
        "age, expected",
        [
            (18, True),
            (19, True),
            (100, True),
            (0, False),
            (1, False),
            (17, False),
        ],
    )
    def test_valid_ages(self, age, expected):
        assert is_adult(age) is expected

    def test_boundary_floats(self):
        assert is_adult(17.99) is False
        assert is_adult(18.0) is True

    def test_negative_age_raises(self):
        with pytest.raises(ValueError, match="age cannot be negative"):
            is_adult(-1)

    def test_negative_large_raises(self):
        with pytest.raises(ValueError, match="age cannot be negative"):
            is_adult(-100)

    def test_boolean_treated_as_int(self):
        """Bug/quirk: True == 1, False == 0 — both pass the < 0 check."""
        assert is_adult(True) is False   # True == 1, 1 < 18
        assert is_adult(False) is False  # False == 0, 0 < 18

    @pytest.mark.parametrize("bad_age", ["18", None, [18], {"age": 18}])
    def test_wrong_type_raises(self, bad_age):
        with pytest.raises(TypeError):
            is_adult(bad_age)

    def test_return_type_is_bool(self):
        assert isinstance(is_adult(18), bool)
        assert isinstance(is_adult(10), bool)


# ---------------------------------------------------------------------------
# 2. celsius_to_fahrenheit(celsius)
# ---------------------------------------------------------------------------
class TestCelsiusToFahrenheit:
    """Formula: round(celsius * 9/5 + 32, 2)."""

    @pytest.mark.parametrize(
        "celsius, expected",
        [
            (0, 32.0),
            (100, 212.0),
            (-40, -40.0),
            (37, 98.6),
        ],
    )
    def test_standard_conversions(self, celsius, expected):
        assert celsius_to_fahrenheit(celsius) == pytest.approx(expected)

    def test_return_type_is_float(self):
        result = celsius_to_fahrenheit(0)
        assert isinstance(result, float)

    def test_negative_temperature(self):
        assert celsius_to_fahrenheit(-273.15) == pytest.approx(-459.67)

    def test_decimal_rounding(self):
        # 35.555 * 9 / 5 + 32 = 95.999 -> rounded to 96.0
        assert celsius_to_fahrenheit(35.555) == pytest.approx(96.0)

    @pytest.mark.parametrize("bad_temp", ["100", None, [0], {"temp": 0}])
    def test_wrong_type_raises(self, bad_temp):
        with pytest.raises(TypeError):
            celsius_to_fahrenheit(bad_temp)


# ---------------------------------------------------------------------------
# 3. count_vowels(text)
# ---------------------------------------------------------------------------
class TestCountVowels:
    """Count a/e/i/o/u case-insensitively. Non-string raises TypeError."""

    @pytest.mark.parametrize(
        "text, expected",
        [
            ("", 0),
            ("aeiouAEIOU", 10),
            ("bcdfg", 0),
            ("Hello World", 3),
            ("AEIOU", 5),
            ("123 !@# \t\n", 0),
            (" a e i o u ", 5),
        ],
    )
    def test_valid_strings(self, text, expected):
        assert count_vowels(text) == expected

    @pytest.mark.parametrize("bad_input", [123, None, ["a", "e"], True, False, 3.14])
    def test_non_string_raises(self, bad_input):
        with pytest.raises(TypeError, match="text must be a string"):
            count_vowels(bad_input)

    def test_return_type_is_int(self):
        assert isinstance(count_vowels("hello"), int)


# ---------------------------------------------------------------------------
# 4. invert(flag)
# ---------------------------------------------------------------------------
class TestInvert:
    """Return not flag. Non-bool raises TypeError."""

    def test_true_returns_false(self):
        assert invert(True) is False

    def test_false_returns_true(self):
        assert invert(False) is True

    @pytest.mark.parametrize("bad_input", [0, 1, "True", "False", None, [], {}, 1.0, 0.0])
    def test_non_bool_raises(self, bad_input):
        with pytest.raises(TypeError, match="flag must be True or False"):
            invert(bad_input)

    def test_return_type_is_bool(self):
        assert isinstance(invert(True), bool)
        assert isinstance(invert(False), bool)


# ---------------------------------------------------------------------------
# 5. greet(name)
# ---------------------------------------------------------------------------
class TestGreet:
    """Greet by name; None/empty/whitespace -> 'Hello, Guest!'."""

    @pytest.mark.parametrize(
        "name, expected",
        [
            (None, "Hello, Guest!"),
            ("", "Hello, Guest!"),
            ("   ", "Hello, Guest!"),
            ("\t\n  ", "Hello, Guest!"),
            ("Alice", "Hello, Alice!"),
            ("  Bob ", "Hello, Bob!"),
        ],
    )
    def test_greeting(self, name, expected):
        assert greet(name) == expected

    def test_default_parameter(self):
        assert greet() == "Hello, Guest!"

    @pytest.mark.parametrize("bad_name", [123, True, [], {"name": "Bob"}, 4.56])
    def test_non_string_raises_attribute_error(self, bad_name):
        """Bug/quirk: non-strings lack .strip() -> raises AttributeError."""
        with pytest.raises(AttributeError):
            greet(bad_name)

    def test_return_type_is_str(self):
        assert isinstance(greet("Alice"), str)
        assert isinstance(greet(None), str)


# ---------------------------------------------------------------------------
# 6. find_max(numbers)
# ---------------------------------------------------------------------------
class TestFindMax:
    """Return the largest number. Empty list raises ValueError."""

    @pytest.mark.parametrize(
        "numbers, expected",
        [
            ([1, 5, 3], 5),
            ([-10, -5, -20], -5),
            ([42], 42),
            ([3, 3, 3], 3),
            ([1.5, 2.5, 0.5], 2.5),
            ((10, 20, 15), 20),
        ],
    )
    def test_valid_lists(self, numbers, expected):
        assert find_max(numbers) == expected

    def test_empty_list_raises(self):
        with pytest.raises(ValueError, match="list is empty"):
            find_max([])

    def test_empty_tuple_raises(self):
        with pytest.raises(ValueError, match="list is empty"):
            find_max(())

    def test_wrong_type_raises(self):
        with pytest.raises(TypeError):
            find_max(123)

    def test_unorderable_elements_raises(self):
        with pytest.raises(TypeError):
            find_max([1, "a"])


# ---------------------------------------------------------------------------
# 7. get_price(prices, item)
# ---------------------------------------------------------------------------
class TestGetPrice:
    """Return price of item. Missing item raises KeyError."""

    def test_existing_item(self):
        prices = {"apple": 1.5, "banana": 0.75}
        assert get_price(prices, "apple") == 1.5

    def test_another_existing_item(self):
        prices = {"apple": 1.5, "banana": 0.75}
        assert get_price(prices, "banana") == 0.75

    def test_missing_item_raises(self):
        prices = {"apple": 1.5}
        with pytest.raises(KeyError, match="cherry not found"):
            get_price(prices, "cherry")

    def test_empty_dict_raises(self):
        with pytest.raises(KeyError, match="apple not found"):
            get_price({}, "apple")

    def test_integer_price(self):
        prices = {"widget": 10}
        assert get_price(prices, "widget") == 10

    def test_zero_price(self):
        prices = {"free_item": 0}
        assert get_price(prices, "free_item") == 0

    def test_wrong_type_raises(self):
        with pytest.raises(TypeError):
            get_price(None, "item")


# ---------------------------------------------------------------------------
# 8. swap(pair)
# ---------------------------------------------------------------------------
class TestSwap:
    """Swap two values. Not exactly 2 values raises ValueError."""

    def test_tuple_swap(self):
        assert swap((1, 2)) == (2, 1)

    def test_list_swap(self):
        result = swap(["a", "b"])
        assert result == ("b", "a")

    def test_heterogeneous_elements(self):
        assert swap((1, "two")) == ("two", 1)

    def test_string_pair_swap(self):
        assert swap("ab") == ("b", "a")

    def test_return_type_is_tuple(self):
        result = swap([10, 20])
        assert isinstance(result, tuple)

    def test_single_element_raises(self):
        with pytest.raises(ValueError, match="pair must have exactly 2 values"):
            swap((1,))

    def test_three_elements_raises(self):
        with pytest.raises(ValueError, match="pair must have exactly 2 values"):
            swap((1, 2, 3))

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="pair must have exactly 2 values"):
            swap(())

    def test_wrong_type_raises(self):
        with pytest.raises(TypeError):
            swap(123)


# ---------------------------------------------------------------------------
# 9. common_items(set_a, set_b)
# ---------------------------------------------------------------------------
class TestCommonItems:
    """Return the intersection of two sets."""

    def test_partial_overlap(self):
        assert common_items({1, 2, 3}, {2, 3, 4}) == {2, 3}

    def test_no_overlap(self):
        assert common_items({1, 2}, {3, 4}) == set()

    def test_identical_sets(self):
        assert common_items({1, 2, 3}, {1, 2, 3}) == {1, 2, 3}

    def test_one_empty(self):
        assert common_items(set(), {1, 2}) == set()

    def test_both_empty(self):
        assert common_items(set(), set()) == set()

    def test_mixed_types_in_sets(self):
        assert common_items({"apple", 42}, {42, "banana"}) == {42}

    def test_return_type_is_set(self):
        result = common_items({1}, {1})
        assert isinstance(result, set)

    def test_wrong_type_raises(self):
        with pytest.raises(TypeError):
            common_items({1, 2}, [2, 3])


# ---------------------------------------------------------------------------
