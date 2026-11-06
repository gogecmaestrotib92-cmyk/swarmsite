# /checklist — The pre-launch checklist (30 checks + master prompt) — gbuilds.si

Structure: Part 1 · 22 customer checks (first screen 5, the button 5, sign-up 4, first value 4, paying 4). Part 2 · 8 safety checks (secrets, other users' data, webhooks, email consent, privacy policy, cookies, accessibility, tax).

## Master prompt (verbatim)
You are checking my app before I send it real visitors. Test it like a careful QA tester, and like a first-time customer who has never seen it.

AUDIT ONLY. Do not change any code, files, settings, content or data unless I ask you to in a later message. When you find a problem, describe it and suggest the fix. Don't apply it.

MY APP (replace every [...] before you start)
- URL: [...]
- Who it's for: [...]
- The one job it does: [...]
- Main traffic source and what it promises: [...]
- Countries I sell in: [...]
- TEST account you may use: [...]

HOW TO WORK
- Go through all 30 checks below, in order. Mark each PASS, FAIL, NOT TESTED or NEEDS CONFIRMATION, with evidence (what you did, what you saw, where).
- PASS only when you saw it work. Use a real browser at phone size (390×844), logged out, fresh private window; repeat at 1280 when it matters.
- Code is extra evidence; the browser is the test. Test accounts only. Don't buy anything, don't type card details.
- Checks 26–30 touch privacy/accessibility/tax law: report what you see, no legal verdict.

THE 30 CHECKS
Step 1 · The first screen: 1 stranger gets it in 5 s (plain headline, no slogans) · 2 repeats the promise of the traffic source · 3 shows the real product (screenshot/clip near top) · 4 loads fast on phone data (~2 s, no layout jumps) · 5 fits a phone (no sideways scroll, thumb-sized buttons)
Step 2 · The button: 6 one main button (same label/colour/destination everywhere) · 7 the button says what they get · 8 every button goes somewhere real (list final URLs) · 9 cost is clear before the tap (free/trial/price, card needed?) · 10 every bit of proof is real
Step 3 · Sign-up: 11 asks only what's needed · 12 confirmation email arrives in inbox (Gmail + Outlook) · 13 log back in + reset password work, errors say what to do · 14 first screen after sign-up has one next step
Step 4 · Value: 15 first win in about a minute · 16 works with messy input · 17 slow steps show progress, errors say what to do, keep input · 18 result easy to keep/find again
Step 5 · Paying: 19 price/currency/period/what unlocks visible before checkout · 20 one real purchase on a phone (owner does it) · 21 paid features unlock from the webhook, not the redirect · 22 receipts, cancel in-app, refund rule written
Part 2 · Safety: 23 secret keys stay on server (search sk_, secret, service_role, private_key, api_key; rotate if ever public) · 24 user B never sees user A's data (change IDs in URL/requests; RLS on) · 25 webhooks verified + idempotent (save event IDs) · 26 marketing emails only to opt-in, one-click unsubscribe, checkbox unticked by default · 27 privacy policy matches real services (hosting, analytics, AI, payments, email) + deletion · 28 cookies/analytics ask first in EU/UK, Reject as easy as Accept · 29 keyboard, labels, contrast, alt (Lighthouse) · 30 digital sales tax handled (VAT, MoR?)

WHAT TO GIVE ME
1. Table of all 30: #, check, status, evidence, fix (one line). 2. Top 5 fixes in order (what's wrong, why, smallest change). 3. Every NEEDS CONFIRMATION as a short question. Then stop.
