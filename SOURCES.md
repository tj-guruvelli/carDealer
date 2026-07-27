# Sources, installs, and what they actually cover

Provenance for everything installed for this purchase. Each entry names where it came from,
what it does, and where it stops being useful. Vetting notes are what I checked, not vendor claims.

## Installed

### used-car-finder — the buyer-side skill
- Source: `github.com/pjdoland/used-car-finder`, MIT, 3 stars, 1 contributor, last push 2026-05-15.
- Installed to `~/.claude/skills/used-car-finder` via `git clone` (so `git pull` picks up updates).
- Covers: Facebook Marketplace private-party listings under ~$15K. Curbstoner detection from
  seller profile, scam patterns in body text, Carfax reading, trim ID from photos, PPI checklist,
  timing chain vs belt, defect-anchored negotiation, insurance by ACV.
- Does NOT cover: Craigslist, AutoTrader, CarGurus, Cars.com, Carvana, or dealer purchases. Those
  have different scam patterns and seller dynamics. Also assumes US market and US insurance.
- Vetting: read `SKILL.md` and `references/playwright-driving.md` in full. Pure markdown, no
  scripts, no network calls of its own. Explicitly refuses to handle credentials, halts on CAPTCHA
  rather than clicking through, and forbids writing search data (ZIP, budget, family situation) to
  long-term memory. Clean.

### dealer-ai-skills — 23 dealership *operations* skills
- Source: `github.com/arielcoro/dealer-ai-skills`, MIT, 1 star, last push 2026-06-04.
- Installed to `~/.claude/skills/dealer-*` (23 folders, copied from `skills/`).
- Vetting: 82 markdown files, 24 `plugin.json`, 4 HTML (landing page), 1 shell script
  (`reconstruct-history.sh`, the author's own git tooling, not invoked by any skill). Grepped for
  `curl|bash`, prompt-injection phrasing, credential/env reads, and outbound POST/webhook calls —
  no hits. Skills are prose instructions only.
- **Scope warning: these are written for people who SELL cars, not people who buy them.** The bulk
  is dealership SEO, AEO/GEO, GA4 attribution, call tracking, lifecycle email, and equity mining.
  Installing all 23 was the explicit ask; most will never fire for a buyer.
- The four with genuine buyer value, used as counter-intelligence:
  - `dealer-customer-sentiment-analyzer` — paste a dealership's Google/DealerRater reviews, get an
    honest department-level breakdown. Vet the store before you drive there.
  - `dealer-vdp-merchandising-review` — what a good vehicle detail page is supposed to contain.
    Reveals which required disclosures a listing is quietly missing.
  - `dealer-cta-audit` and `dealer-site-score` — the conversion playbook being run on you.
- To remove any of them: `Remove-Item -Recurse ~\.claude\skills\dealer-<name>`

### Marketcheck — 75 skills + hosted MCP server
- Source: `MarketcheckHub/marketcheck-cowork-plugin` (4 stars) and
  `MarketcheckHub/marketcheck-api-mcp`. Vendor-official, Marketcheck Cars Inc.
- The MCP Market listing for "Vehicle Deal Finder & Negotiator" is this repo's
  `plugins/dealer/skills/deal-finder`. "Inventory Intelligence" is `plugins/*/skills/inventory-intelligence`.
  Both came in with the bundle install; no separate download needed.
- Installed all 9 bundles (analyst, appraiser, auction-house, dealer, dealership-group, insurer,
  lender, lender-sales, manufacturer) = 75 bundle×skill pairs to `~/.claude/skills/marketcheck-*`.
- **Namespacing:** 41 distinct skill names appear across bundles, and same-named skills are NOT
  identical (all different hashes — `depreciation-tracker` alone ships 8 persona-specific
  variants). Installed as `marketcheck-<bundle>-<skill>` with the frontmatter `name:` rewritten
  to match the directory, so nothing collides and each persona's version stays addressable.
- MCP server vetting: read `services/base.py` and grepped the whole tree. Only outbound host is
  `api.marketcheck.com/v2`. Key read from the `MARKETCHECK_API_KEY` env var, never hardcoded. No
  `subprocess`, `os.system`, `eval`, `exec`, or `pickle` anywhere. Their `SECURITY.md` tells you
  not to commit the key. Clean.
- Wired as an HTTP server in `.mcp.json` (both here and at the sec-brain root) pointing at the
  hosted endpoint with `${MARKETCHECK_API_KEY}` interpolation. **The key is not in any file.**
- **Costs money.** Free tier is 500 calls/month, 5 calls/sec, 100-mile radius cap. Basic is
  $299/month. Every tier reads "+ data fees" on their pricing page, so $0 is the subscription,
  not guaranteed to be the bill. A single deal-finder query burns 3-4 calls, so free tier is
  roughly 125 lookups/month. Watch it.
- Buyer-relevant subset out of the 75: `marketcheck-dealer-deal-finder` (fair-price validation,
  DOM negotiation leverage), `marketcheck-dealer-vehicle-appraiser` (comp-anchored value range),
  `marketcheck-dealer-depreciation-tracker` (will it hold value),
  `marketcheck-analyst-dom-monitor`. The rest is dealer, lender, insurer, and equity-analyst work.

### CarsXE — 12 skills, installed WITHOUT the auth command
- Source: `carsxe/carsxe-claude-plugin` (2 stars). 27 markdown + 2 JSON + LICENSE. No scripts.
- Only outbound host is `api.carsxe.com`. No `subprocess`, `eval`, `base64`, `schtasks`/cron,
  or hook installation. Code side is clean.
- Installed as `~/.claude/skills/carsxe-*`: vehicle-history, market-value, vehicle-specs,
  vehicle-recalls, lien-theft, year-make-model, international-vin, plate-decoder,
  plate-image-recognition, vin-ocr, obd-decoder, vehicle-images. Each has a `NOTES.md` with
  source URL and install date per checklist section 7.
- **Fills the real gap Marketcheck leaves.** Marketcheck does listings and pricing; it does not
  do title brands, accident records, odometer history, or liens. `carsxe-vehicle-history` and
  `carsxe-lien-theft` are the "is this car legally clean" half of due diligence.
- **FINDING — `commands/auth.md` was deliberately NOT installed.** It violates
  `docs/skill-vetting.md` twice:
  - §4 (auto-reject): it asks you to paste the API key into chat — `/carsxe:auth YOUR_API_KEY`,
    and "If no key is provided, ask: Please provide your CarsXE API key."
  - §2: step 5 has the agent build a shell command with the key interpolated into the string
    (`export CARSXE_API_KEY=<KEY>` / `$env:CARSXE_API_KEY="<KEY>"`), which is the raw-string-into-
    shell pattern that caused the RCE on this machine.
  The 12 skills read `CARSXE_API_KEY` from the environment and work fine without that command.
  Set it as a user env var out-of-band, exactly like `MARKETCHECK_API_KEY`. Never paste a key
  into this chat.
- Separate note: CarsXE passes the key as a URL query parameter (`?key=...`). That is their API
  design, and it means the key can land in proxy and server logs. Treat it as lower-trust than a
  header-auth key and rotate it if the machine is ever shared.
- Costs money: CarsXE is a paid API. Check their current pricing before relying on it.

## Triage of the remaining marketplace listings

Reviewed from the MCP Market / Awesome Skills listings. None installed. Reasons are specific
because "not installed" without a reason is how a gap gets rediscovered three weeks later.

**Worth installing, free, no credential** — recommended next:
- `taimoorgit/vin-lookup-mcp` — NHTSA vPIC VIN decoding, public API, **no key required**. Free
  cross-check that a listing's stated year/make/model/engine matches the VIN before paying for
  any history report. Only reason it is not installed yet is that it was not explicitly asked for.

**Skip — actively risky:**
- `SiddarthaKoppaka/car-deals-search` — scrapes Cars.com, Autotrader, KBB with Puppeteer
  "stealth mode using anti-bot detection techniques". Evasion of bot protection, against those
  sites' terms, and the listing text it returns is untrusted content feeding an agent. 0 stars.
- `antonlunden` / `anton-lunden` "Vehicle" MCP — remote **unlock doors**, climate, and charging
  on a real Skoda. Nothing to do with buying a car, and handing an agent physical door-unlock is
  a capability that needs its own deliberate decision, not a bundled install. 1 star.
- `markswendsen-code` Enterprise Connector — headless "stealthy" Playwright against
  enterprise.com with persisted session cookies. Rental, not purchase, plus evasion plus a live
  authenticated session. 0 stars.

**Skip — wrong market:**
- `deusyu/car-advisor` and `deusyu/car-research` — sources are Dongchedi and Autohome, Chinese
  market, Xiaomi SU7 examples. No US data.
- `FDU-INS` Car Rental Search — Fliggy/Alibaba, Chinese rental market.

**Skip — wrong problem:**
- `a5c-ai` Automotive Cybersecurity (1.3k stars) — ISO/SAE 21434 TARA and SecOC for engineers
  building vehicle ECUs. High-quality and completely unrelated to buying one.
- `lionelsimai` Vehicle Lifecycle Management — fleet asset management framework.
- `nickytonline` Pimp My Ride — virtual car customization for a racing game.
- `RichardLimaDxD` Car Agent Python — a Django dealership backend, not a buyer tool.
- `Geeksfino/kb` — txtai semantic search. Would serve the Layer 3 document Q&A role, but this
  vault already has `server/` vault-recall (FTS5 + fastembed) doing exactly that.

**Skip — redundant:**
- `carvectorio` CarVector — specs, NHTSA recalls, OBD-II codes, complaints, TSBs. 0 stars, and
  the recall/complaint data is free from NHTSA directly, which `vin-lookup-mcp` already reaches.
- `simons-hub` Car Falcon — multi-site scraping plus KBB plus **Gmail delivery**. 0 stars and it
  wants mailbox access for a reporting convenience.
- `Cole-Cant-Code` AutoCIP — 52 tools, 35 reasoning frameworks, dual-LLM, 1 star. Ambitious and
  entirely unproven; the surface area is far too large to vet for the value it adds here.

## Evaluated, not installed

### used-car-price-search
- Source: `nomadamas/k-skill` (the 5,238 stars / 567 forks belong to that parent repo, not this
  skill). The "100/100 security score" is the Awesome Skills directory's own automated grade,
  which I did not verify.
- Queries SK Rent-a-Car Direct TagoBUY inventory by scraping `__NEXT_DATA__` from the page.
- **Korea-only, and rental-fleet-only.** No US inventory. Not applicable to this purchase.
  Also snapshot-based, so pricing and availability drift.

### Car Rental Search & Booking (FDU-INS, 53 stars)
- Fliggy (Alibaba travel network) car **rental** inventory via `flyai-cli`, Chinese market.
- Renting, not buying. No US purchase data. Not applicable.

### Cardog MCP (`cardog-ai`)
- Vehicle listing search, VIN market analysis, recalls, EV charging locator. Requires its own API
  key. 0 GitHub stars and not yet vetted.
- Deferred deliberately: it overlaps Marketcheck on listings and VIN market analysis, and adds a
  second paid credential plus a second unaudited server for capability already covered. Revisit
  only if Marketcheck's free tier proves too thin. Recalls are free from NHTSA directly.

### The self-install prompt pattern
Both the Dealer AI Guy site and its launch article push `Install this: <github url>` as the
"easiest path" — paste a URL and let the agent install itself. That shape is injection-adjacent:
a page telling a reading agent to install code is exactly the vector to distrust, regardless of
whether this particular repo is fine (it is). Both installs above were done by explicit clone plus
manual read, not by following a webpage's instructions.

## Similar repos found (GitHub search, not installed)

Buyer-side listing search:
- `passivebot/facebook-marketplace-scraper` and similar — Playwright + BeautifulSoup + Streamlit.
- MCP servers exist for Facebook Marketplace search via Chrome session cookies, and one covering
  Marketplace + eBay + Depop together.
- `Flipper-AI-Marketplace`, `Carlytics` — AI-powered Marketplace deal finders, both very early.
- Craigslist: a well-known project scraped and analyzed 1.7M used-car listings to find deals.

Data and validation:
- NHTSA vPIC is the free government VIN decoder; multiple wrapper libraries exist in every
  language, including one with an offline WMI fallback. Worth using to confirm a VIN's stated
  year/make/model/engine matches the listing, for free, before paying for any history report.

Nothing found was a better fit than `used-car-finder` for private-party triage. The scrapers add
listing volume, not judgment, and they carry the account-risk noted below.

## Standing risk note

`used-car-finder` can optionally drive Playwright against a logged-in Facebook session. That
combines untrusted content (seller-written listing text), a live authenticated session, and an
agent able to act in the browser. The skill's own guardrails are good (read-only navigation, stop
on challenge, never touch credentials), but the safest posture is still: keep it in paste mode, or
run it against a browser profile logged into a throwaway Facebook account rather than your primary.
Marketplace scraping is also against Facebook's terms and can get an account restricted.
