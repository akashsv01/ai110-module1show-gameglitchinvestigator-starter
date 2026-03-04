# FIX: refactored from app.py with AI assistance in Copilot Agent mode
# This helper centralises difficulty ranges and allowed the app logic to
# query them without duplicating the mapping.
def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty.

    The game uses the following mappings:
      * Easy   -> 1..20
      * Normal -> 1..100
      * Hard   -> 1..50
    Any other string defaults to the "Normal" range.
    """
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 50
    # defensively handle unexpected values
    return 1, 100


# FIX: moved from app.py and cleaned up parsing logic with AI suggestions
# Accept floats and surface errors; Copilot Agent helped structure return tuple
def parse_guess(raw: str):
    """
    Convert a raw text input into an integer guess.

    Returns a tuple of (ok: bool, guess_int: int | None, error_message: str | None).
    If the input is blank or None we ask the user to enter a guess.
    If the value cannot be converted to an integer we return an error message.
    Floats are accepted by casting to int (truncating the fractional part).
    """
    if raw is None or raw == "":
        return False, None, "Enter a guess."

    try:
        # allow floats such as "3.0" or "4.7"
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except Exception:
        return False, None, "That is not a number."

    return True, value, None


# FIX: logic corrected; high/low messages were reversed in original
# Copilot assisted with integer coercion and robust fallback behavior
def check_guess(guess, secret):
    """
    Compare ``guess`` to ``secret`` and return a tuple ``(outcome, message)``.

    ``outcome`` is one of "Win", "Too High", or "Too Low".  The accompanying
    message is a user‑friendly hint describing what the player should do next.

    The original implementation in ``app.py`` had the hint text reversed when
    the guess was above the secret; this routine fixes that bug and also makes
    sure comparisons are done on integers whenever possible.
    """
    # try to coerce both values to integers so comparisons behave predictably
    try:
        g = int(guess)
        s = int(secret)
    except Exception:
        # fall back to string comparison if conversion fails; this mirrors the
        # previous implementation but should rarely be hit in normal game flow
        if guess == secret:
            return "Win", "🎉 Correct!"
        if guess > secret:
            return "Too High", "📉 Go LOWER!"
        return "Too Low", "📈 Go HIGHER!"

    if g == s:
        return "Win", "🎉 Correct!"
    elif g > s:
        return "Too High", "📉 Go LOWER!"
    else:
        return "Too Low", "📈 Go HIGHER!"


# FIX: extracted scoring logic from app; Copilot suggested docstring
# and preserved original weird even/odd rules during refactor.
def update_score(current_score: int, outcome: str, attempt_number: int):
    """Return a new score based on the outcome of the latest guess.

    The scoring rules are unchanged from the original application:

      * A win gives between 10 and 100 points depending on how many attempts
        the player used (fewer attempts yields more points).
      * A "Too High" hint grants or deducts points alternating on even/odd
        attempts.
      * A "Too Low" hint always deducts 5 points.
      * Unknown outcomes leave the score unchanged.
    """
    if outcome == "Win":
        points = 100 - 10 * (attempt_number + 1)
        if points < 10:
            points = 10
        return current_score + points

    if outcome == "Too High":
        if attempt_number % 2 == 0:
            return current_score + 5
        return current_score - 5

    if outcome == "Too Low":
        return current_score - 5

    return current_score
