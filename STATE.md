# Session state — 2026-07-26

Resume file. Everything needed to continue after a `/clear`. Read this plus `GARAGE.md`
and `PLAYBOOK.md` and you have the whole picture.

## Repo

`github.com/tj-guruvelli/carDealer`, local at `sec-brain/CarDealerships/` (nested git repo,
ignored by sec-brain's `.gitignore`).

Commits: `1c18cf9` workspace → `bfb1158` playbook + MCP → `e885775` CarsXE + triage →
`b9512a2` GARAGE → `3224a33` otd fix + tests.

| File | What it holds |
|---|---|
| `GARAGE.md` | TJ's criteria, shortlist with dated targets, per-car known problems, Jaguar XJ inspection + negotiation ladder, test-drive list |
| `PLAYBOOK.md` | Negotiation method and the two agent-failure guards |
| `SOURCES.md` | Provenance + vetting for everything installed; triage of everything rejected |
| `tools/otd.py` | Out-the-door cost + weighted scoring. 16 tests in `test_otd.py`, all green |

## Done

**310 car/insurance skills installed, global, in `~/.claude/skills/`:**
191 `fduins-*`, 75 `marketcheck-*`, 23 `dealer-*`, 12 `carsxe-*`, 7 `iterlayer-*`,
`used-car-finder`, `car-research`.

The four that matter most for buying:
- `car-research` — 6-phase research and weighted decision matrix. **No API key.** Start here.
- `marketcheck-dealer-deal-finder` — fair-price validation, DOM leverage. Needs key.
- `carsxe-vehicle-history` / `carsxe-lien-theft` — title brands, accidents, odometer, liens. Needs key.
- `used-car-finder` — private-party listing triage under $15k. No key.

**MCP wired:** `marketcheck` (HTTP, `${MARKETCHECK_API_KEY}`) in both `.mcp.json` files.

## Blocked on TJ

Two env vars. Never paste keys into chat.

```powershell
[Environment]::SetEnvironmentVariable('MARKETCHECK_API_KEY','<key>','User')
[Environment]::SetEnvironmentVariable('CARSXE_API_KEY','<key>','User')
```

Marketcheck free tier: 500 calls/month, 100-mile radius cap, "+ data fees" on every tier.
A deal-finder query burns 3-4 calls.

Six intake answers still outstanding: ZIP, budget floor/ceiling, new or used, private party or
dealer, body style, passengers.

## Outstanding work

**14 MCP servers, none wired.** Parallel job — serial cloning timed out twice at 2 min.
Strongest first:

| Repo | Why |
|---|---|
| `taimoorgit/vin-lookup-mcp` | Free NHTSA vPIC, **no API key**. Do this one first |
| `markswendsen-code/mcp-carmax` | Real buying channel |
| `markswendsen-code/mcp-carvana` | Real buying channel |
| `markswendsen-code/mcp-carecom` | Cars.com |
| `cardog-ai/mcp-server`, `carvectorio/carvector-mcp`, `simons-hub/car-falcon-mcp`, `vehiclesdb/vehicles`, `Geeksfino/kb-mcp-server`, `quotor/home-auto-insurance-quotes` | Lower value, mostly redundant or paid |
| `SiddarthaKoppaka/car_deals_search_mcp` | **Anti-bot evasion.** Rejected unless TJ overrides |
| `antonlunden/vehicle-mcp` | Remote door unlock on a physical car. Out of scope |
| `markswendsen-code/mcp-enterprise` | Rental + stealth automation on a live session |

## Standing constraints

1. **No outbound message to any dealer without TJ seeing it first.** No "is this consequential"
   judgment call delegated to the agent. This is rule 1 of `PLAYBOOK.md`, from a real failure.
2. Dedicated phone number and email alias for all outreach, never TJ's primary. An agent
   auto-filled a real number into dealer forms and the calls never stopped.
3. One thread per dealer. An agent replied to the wrong negotiation thread and leaked to a
   competing dealer.
4. One variable at a time: out-the-door price alone. Trade-in and financing come after.
5. Agent stops at the credit application.
6. Vet every third-party skill against `docs/skill-vetting.md` before install. CarsXE's
   `commands/auth.md` was rejected on that basis — it asked for the API key in chat and
   interpolated it into a shell string.
7. The repo is **public**. Redact seller names, phone numbers, addresses. Never commit
   financing paperwork or identity documents.

## Known caveats

- Part of the `fduins-*` batch uses plain `http://` hosts and Chinese-market sources
  (Autohome, Dongchedi). Fine as reference, not as US price data.
- `~/.claude/skills/` now holds 1991 directories total. Skill-list pollution is real; pruning
  to the buyer-relevant dozen is a standing offer.
- CarsXE passes its key as a URL query parameter, so it can land in logs. Rotate if the
  machine is shared.
