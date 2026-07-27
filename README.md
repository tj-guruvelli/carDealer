# carDealer

Version-controlled workspace for a used-car purchase. Every document, every candidate, every
number that goes into the decision lives here so the choice is reproducible and auditable.

Modeled on the three-layer approach from Sathish Jayapal's write-up (GitHub as source of truth,
a structured decision matrix, a queryable document knowledge base), plus the `used-car-finder`
Claude skill for listing triage.

## Layout

```
vehicles/<year>-<make>-<model>-<vin8>/   one folder per seriously-considered car
  listing.md                             URL, ask, mileage, seller, body text (paste verbatim)
  carfax.pdf | autocheck.pdf             history reports
  photos/                                trim ID, defect evidence, odometer
  verdict.md                             the skill's VERDICT block + your notes
tools/
  otd.py                                 out-the-door cost + weighted score from candidates.csv
  candidates.csv                         the decision matrix (your live working file)
  candidates.example.csv                 shape reference
research/                                market notes, model-specific known issues, price comps
SOURCES.md                               what's installed, where it came from, what it does not cover
```

## The three layers

**Layer 1 — Source of truth.** This repo. One folder per vehicle. Commit per research session,
so "what did that 2019 Pilot's service history show?" is a `git log` away.

**Layer 2 — Decision matrix.** `tools/otd.py`. Listed price is not the price. The script folds in
dealer fees, sales tax, title and registration to produce the out-the-door number, then scores
candidates on weighted criteria. A $27,990 car with a $998 doc fee is a different car than a
$28,400 one with a $500 fee.

**Layer 3 — Document Q&A.** Dump the CARFAX and dealer PDFs into a queryable knowledge base and
ask across all of them at once ("across the CVT cars, what is the transmission fluid interval
variance?"). Google NotebookLM is the low-friction option. Locally, this vault already has
`server/` vault-recall (FTS5 + fastembed) if you want it offline. Verify every synthesized claim
against the source PDF — NotebookLM hallucinates details.

## Skills installed for this

- `used-car-finder` — private-party Facebook Marketplace triage: curbstoner detection, scam
  patterns, Carfax reading, trim ID, PPI checklist, defect-anchored negotiation. This is the
  buyer-side skill.
- `dealer-*` (23 skills) — dealership *operations* skills. See `SOURCES.md` for which of these
  are actually useful to a buyer and which are noise.

Invoke by asking naturally, e.g. "Help me find a reliable used car under $12,000 near <metro>."

## Hard rules for this repo

- Never commit a document containing your SSN, driver's licence number, full account numbers, or
  a signed credit application. Financing paperwork stays out. `.gitignore` blocks the obvious
  cases but it is not a substitute for looking before you commit.
- This repo is **public**. Seller names, phone numbers, and home addresses from listings are
  other people's personal data. Redact before committing.
- A VERDICT from a skill is a filter, not a purchase decision. Nothing here replaces a
  pre-purchase inspection by a mechanic you chose and paid.
