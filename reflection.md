# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- The game was giving completely backwards hints.  If the secret was 100 and I guessed 50 it would tell me to go "LOWER" instead of "HIGHER", and vice‑versa.
- Once I either won or ran out of tries the "New Game" button stopped working; the session state never got cleared so I had to reload the page to play again.
- The attempt counter was lying.  The banner might say "Attempts left: 1" and the very next message would be "Out of attempts!" because the info line was using an old value of the counter.
- Difficulty didn’t actually change anything.  The sidebar correctly said 1–50 for Hard, but the top prompt still said 1–100 and new secrets were always drawn from 1–100 no matter what difficulty I picked.

---

## 2. How did you use AI as a teammate?

- **Tools used:** I relied mainly on GitHub Copilot in Agent mode to help refactor and suggest fixes, along with some ChatGPT-style ideas when reasoning about session state.  Copilot generated most of the helper functions and the form layout.

- **Correct suggestion example:** Copilot pointed out that the `submit` button and text input could be wrapped in an `st.form` so the user could press Enter to submit.  The generated code snippet included `with st.form(...)` and Copilot even added a comment about `st.form_submit_button`.  After inserting the suggested form and manually testing the app, the guess count decremented on the very first Enter press, confirming the fix worked exactly as described.

- **Incorrect/misleading suggestion example:** Early on the assistant generated logic for `check_guess` that treated a guess higher than the secret by returning "📈 Go HIGHER!" – essentially reversing the hint.  That copy‑paste came straight from the buggy starter code.  I caught the mistake while reading the generated function and by running the unit tests, which failed until I corrected the message directions.  This showed that AI output is not automatically correct and needs verification.

---

## 3. Debugging and testing your fixes

I treated a problem as fixed only after I could reproduce the original behaviour, apply a change, and then confirm the behaviour no longer occurred.  For logic issues I wrote small `pytest` functions that exercised the helpers directly.  For example, I wrote a regression test for `check_guess` asserting that guessing 60 against a secret of 50 returned the "Too High" outcome with a LOWER hint; the test failed before the fix and passed afterwards.  That gave me confidence the most obvious hint‑reversal bug was gone.

To verify the session‑state problems I used manual play; after each change I started a game, triggered a win/loss, clicked New Game, and observed that the secret number, attempt count, and score were correctly reset.  The form‑submission tweak was also checked by using the Enter key and watching the attempts decrement immediately.

AI helped indirectly by suggesting code structure that made testing easier (for instance refactoring routines into the `logic_utils` module so they could be imported from a plain test file).  It also suggested example inputs when I was writing assertions, but I still reviewed every generated test to ensure it matched the bug description.

---

## 4. What did you learn about Streamlit and state?

The secret number kept changing because Streamlit reruns the entire script from top to bottom whenever a user interacts with any widget.  The original code was regenerating the secret by calling `random.randint()` on every rerun instead of storing it safely in `st.session_state`.  So every time I clicked a button or typed a guess, the script would restart and execute `st.session_state.secret = random.randint(low, high)` again, giving me a new target.

I'd explain Streamlit reruns and session state like this: think of a Streamlit app as a recipe that gets re-cooked from the beginning every time someone flips a switch (clicks a button, types in a box, etc.). Without session state, ingredients reset each time you cook—so you'd never be able to keep track of anything between flips. Session state is like a notepad that survives the re-cooking; you can write your important values (like the secret number) on it, and they'll still be there the next time the recipe runs.

The breakthrough fix was wrapping the initial secret-number generation in an `if "secret" not in st.session_state:` guard, so the secret only gets created once on the very first load, then persists across reruns.  I also added a secondary check for when the user switched difficulties, explicitly clearing and regenerating the secret for the new range.  This two-part approach gave the game a genuinely stable secret that only changed when the player wanted it to (on "New Game" or difficulty change).

---

## 5. Looking ahead: your developer habits

One habit I'm keeping from this project is writing small, focused tests *while fixing*, not after.  Instead of trying to fix everything and then writing tests at the end, I'd write a test that captured the buggy behaviour, watch it fail, apply a fix, and confirm the test passed.  That immediate feedback loop kept me from going in circles and gave me proof each fix actually worked.  I'll do this in future labs by starting with a failing pytest case that documents the expected behaviour, then building the fix around it.

One thing I'd do differently: next time I work with AI I'll be more aggressive about asking for *reasoning* before accepting generated code.  A couple times Copilot suggested fixes that sounded right but were actually copies of the buggy starter code.  If I'd asked "why does this comparison work?" I might have caught the reversed logic sooner instead of finding it later in testing.  The AI can explain its thinking, and I should demand that before copy-pasting.

This project taught me that AI-generated code is a starting point, not a finish line.  The AI wrote functions that *looked* correct and had nice docstrings, but they still had bugs inherited from the source material.  I'm no longer worried about using AI to draft code quickly; I'm just much more skeptical of it, knowing I have to read it carefully, test it thoroughly, and push back when something doesn't make sense.  The AI was genuinely useful for refactoring and structure, but it wasn't a substitute for understanding the code myself.
