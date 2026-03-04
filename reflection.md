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

- In your own words, explain why the secret number kept changing in the original app.
- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?
- What change did you make that finally gave the game a stable secret number?

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.
