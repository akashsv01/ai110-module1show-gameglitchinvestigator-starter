import random
import streamlit as st
import pandas as pd

# ENHANCEMENT: Helper to determine "hotness" for visual feedback
def get_hotness_emoji(guess, secret, low, high):
    """Return emoji and color based on how close the guess is to the secret."""
    distance = abs(guess - secret)
    range_size = high - low
    
    if distance == 0:
        return "🔥🔥🔥 BULL'S EYE!", "green"
    elif distance <= range_size * 0.1:
        return "🔥🔥 Scalding!", "orange"
    elif distance <= range_size * 0.25:
        return "🔥 Hot!", "red"
    elif distance <= range_size * 0.5:
        return "🌅 Warm", "blue"
    else:
        return "❄️ Cold", "light-blue"

# Import logic helpers
# FIX: Refactored logic into logic_utils.py using Copilot Agent mode
from logic_utils import (
    get_range_for_difficulty,
    parse_guess,
    check_guess,
    update_score,
)

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

# if the user has switched difficulties, clear the old secret and start anew
if "difficulty" not in st.session_state or st.session_state.difficulty != difficulty:
    st.session_state.difficulty = difficulty
    # recalc range based on new difficulty below when low/high is computed
    # FIX: ensure secret is regenerated on difficulty change (bug discovered in reflection)
    st.session_state.secret = random.randint(*get_range_for_difficulty(difficulty))
    st.session_state.attempts = 0
    st.session_state.score = 0
    st.session_state.status = "playing"
    st.session_state.history = []

attempt_limit_map = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

# initialize session state only once per user
if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)

# start with zero attempts so the "attempts left" math works correctly
if "attempts" not in st.session_state:
    st.session_state.attempts = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

st.subheader("Make a guess")

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

# wrap the input and submit button in a form so that pressing Enter
# will act as a submission event
# FIX: changed UI to form to allow Enter key submission, AI suggested this pattern
with st.form(key="guess_form"):
    raw_guess = st.text_input(
        "Enter your guess:",
        key=f"guess_input_{difficulty}"
    )
    submit = st.form_submit_button("Submit Guess 🚀")

# show info after we know whether a submission happened this run so the
# "Attempts left" count reflects the increment that will occur
attempts_left = attempt_limit - (st.session_state.attempts + (1 if submit else 0))
st.info(
    f"Guess a number between {low} and {high}. "
    f"Attempts left: {attempts_left}"
)

col1, col2 = st.columns(2)
with col1:
    new_game = st.button("New Game 🔁")
with col2:
    show_hint = st.checkbox("Show hint", value=True)

if new_game:
    # reset everything to starting values; respect the current difficulty range
    st.session_state.attempts = 0
    st.session_state.score = 0
    st.session_state.status = "playing"
    st.session_state.history = []
    st.session_state.secret = random.randint(low, high)
    st.success("New game started.")
    st.rerun()

if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")
    st.stop()

if submit:
    st.session_state.attempts += 1

    ok, guess_int, err = parse_guess(raw_guess)

    if not ok:
        st.session_state.history.append(raw_guess)
        st.error(err)
    else:
        st.session_state.history.append(guess_int)

        if st.session_state.attempts % 2 == 0:
            secret = str(st.session_state.secret)
        else:
            secret = st.session_state.secret

        outcome, message = check_guess(guess_int, secret)

        # ENHANCEMENT: Show hot/cold feedback
        hotness_emoji, hotness_color = get_hotness_emoji(guess_int, st.session_state.secret, low, high)
        st.markdown(f":{hotness_color}[**{hotness_emoji}**]")

        if show_hint:
            st.warning(message)

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        # ENHANCEMENT: Show attempts progress bar
        progress = st.session_state.attempts / attempt_limit
        st.progress(progress, text=f"Attempts: {st.session_state.attempts}/{attempt_limit}")

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            st.success(
                f"You won! The secret was {st.session_state.secret}. "
                f"Final score: {st.session_state.score}"
            )
        else:
            if st.session_state.attempts >= attempt_limit:
                st.session_state.status = "lost"
                st.error(
                    f"Out of attempts! "
                    f"The secret was {st.session_state.secret}. "
                    f"Score: {st.session_state.score}"
                )

# ENHANCEMENT: Display game session history as a table
if len(st.session_state.history) > 0:
    st.subheader("📊 Session History")
    history_data = []
    for i, guess in enumerate(st.session_state.history, 1):
        if isinstance(guess, int):
            distance = abs(guess - st.session_state.secret)
            direction = "🎯 Win" if distance == 0 else ("🔽 Too Low" if guess < st.session_state.secret else "🔼 Too High")
            history_data.append({"Attempt": i, "Guess": guess, "Outcome": direction})
        else:
            history_data.append({"Attempt": i, "Guess": guess, "Outcome": "❌ Invalid"})
    
    if history_data:
        df = pd.DataFrame(history_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
