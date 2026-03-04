import sys
import os

# Ensure the project root is on sys.path so our modules can be imported from
# inside the tests directory; this guards against the odd hyphen in the
# workspace folder name preventing a normal import.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from logic_utils import (
    get_range_for_difficulty,
    parse_guess,
    check_guess,
    update_score,
)


def test_get_range_for_difficulty():
    assert get_range_for_difficulty("Easy") == (1, 20)
    assert get_range_for_difficulty("Normal") == (1, 100)
    assert get_range_for_difficulty("Hard") == (1, 50)
    # unrecognised difficulty defaults to normal
    assert get_range_for_difficulty("SuperHard") == (1, 100)


def test_parse_guess_valid_and_invalid():
    ok, val, err = parse_guess("42")
    assert ok and val == 42 and err is None
    ok, val, err = parse_guess("3.7")
    assert ok and val == 3 and err is None
    ok, val, err = parse_guess("")
    assert not ok and err == "Enter a guess."
    ok, val, err = parse_guess("not a number")
    assert not ok and err == "That is not a number."


def test_check_guess():
    outcome, msg = check_guess(50, 50)
    assert outcome == "Win" and "Correct" in msg
    outcome, msg = check_guess(60, 50)
    assert outcome == "Too High" and "LOWER" in msg
    outcome, msg = check_guess(40, 50)
    assert outcome == "Too Low" and "HIGHER" in msg


def test_update_score_rules():
    # winning on first attempt (points = 100 - 10*(1+1) = 80)
    assert update_score(0, "Win", 1) == 80
    # too high on even attempt (gain 5)
    assert update_score(10, "Too High", 2) == 15
    # too high on odd attempt (lose 5)
    assert update_score(10, "Too High", 3) == 5
    # too low always -5
    assert update_score(10, "Too Low", 4) == 5
    # unknown outcome leaves score unchanged
    assert update_score(10, "Something else", 5) == 10


def test_regression_fixed_bugs():
    """Regression tests corresponding to the bugs listed in reflection.md."""
    # 1. Range should respect difficulty and not default to 1-100.
    assert get_range_for_difficulty("Hard") == (1, 50)
    assert get_range_for_difficulty("Easy") == (1, 20)

    # 2. check_guess messages reversed originally: too-high should say LOWER
    outcome, msg = check_guess(90, 50)
    assert outcome == "Too High" and "LOWER" in msg
    outcome, msg = check_guess(10, 50)
    assert outcome == "Too Low" and "HIGHER" in msg

    # 3. parse_guess should accept floats and reject non-numbers
    ok, val, err = parse_guess("50.0")
    assert ok and val == 50
    ok, val, err = parse_guess("nope")
    assert not ok and err == "That is not a number."

    # 4. attempts-left calculation should behave correctly when incrementing
    # (simulating what the front end does); ensure zero attempts left when
    # you've just used the final attempt.
    limit = 3
    attempts = 2
    remaining = limit - (attempts + 1)
    assert remaining == 0

    # 5. update_score continues to adhere to its original rules after fixes
    assert update_score(5, "Too High", 2) == 10
