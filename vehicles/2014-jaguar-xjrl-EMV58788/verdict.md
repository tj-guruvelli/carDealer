# 2014 Jaguar XJRL — VIN SAJWA2EK8EMV58788

```
VERDICT: KILL
Year/Make/Model/Trim: 2014 Jaguar XJRL (long wheelbase), 5.0L supercharged V8, 550 hp, RWD
Ask: $26,850 (was $27,850) / Salvage-auction price 4 months earlier: $3,900 to $6,500
Seller: Precision Auto Sales, Mesquite TX
Seller signal: RED — retailing a car bought out of a salvage auction at ~5x
Body-text flags: none needed; the VIN history is the flag
Next step: WALK
```

**Insurance total loss, sold through salvage auctions in August 2025, retitled in Texas the
following month, now offered at roughly five times what it brought at auction.**

## The evidence — listing history, verbatim from the data

| Date | Where | Price | Miles |
|---|---|---|---|
| Mar 2021 | Reed Nissan / iRide, FL | $41,991 → $40,991 | 27,480 |
| Oct 2021 | Private seller | $43,500 → $41,000 | 31,825 |
| Jan 2022 – Sep 2023 | CarGurus, Midland TX | $40,000 → **$35,995** | 34,000 → 42,500 |
| **~2 year gap** | | | |
| **2025-06-11** | **IAA (Insurance Auto Auctions), Westchester IL** | — | disposition **SOLD** |
| Jul–Aug 2025 | **SCA Auction**, North Miami Beach FL | **$3,900 / $5,800 / $6,500** | 46,888 |
| Aug 2025 | Ridesafely (PA), Bid Export (FL), Auto4export (GA), Bid N Drive (GA), Bid Golive (FL), Auctioncarz (OH) | — | 46,888 |
| **2025-09-17** | **New Texas title issued** | — | 46,888 |
| Nov 2025 – now | Precision Auto Sales, Mesquite TX | $27,850 → **$26,850** | 46,888 |

Every seller in the August 2025 cluster is a salvage or export auction platform. SCA Auction is
a salvage auction house. Ridesafely is a salvage auction broker. "Bid Export" and "Auto4export"
sell damaged vehicles into the export market — the channel for cars that cannot be retitled
cleanly in the US.

## Why this is decisive

1. **IAA record with disposition SOLD.** Insurance Auto Auctions handles vehicles an insurer has
   taken possession of. That is the total-loss pathway.
2. **It brought $3,900 to $6,500.** A 2014 XJR that was worth $35,995 in retail 20 months earlier
   does not sell for $3,900 unless it is wrecked, flooded, or otherwise destroyed.
3. **New Texas title one month after the salvage sale.** Fresh state, fresh paper.
4. **Odometer frozen at 46,888** across every salvage listing and every Precision Auto Sales
   listing since. It has not been driven; it has been moved and relisted.
5. **The spread is the business model.** Roughly $21,000 between what it cost at auction and what
   it is being asked for now.

## What the title report says, and what it does not

The NMVTIS brand field currently reads **"Clear: No brand exists for the vehicle."** That is the
point of a title wash — the brand does not follow the car into the new state. The junk and salvage
record, and the auction price history, are what expose it. A buyer looking only at "clean title"
would have missed this entirely.

Also present, unexplained: an odometer jump from **4,256 miles (2021-03-23)** to **27,480 miles
(2021-04-16)** — 23,224 miles in 24 days. Either a reporting error or a discrepancy worth
answering before anyone spends money here.

Title path FL → FL → MN → MN → TX. **Minnesota 2023 to 2025** also fails the southern-states
sourcing rule in `GARAGE.md` — two winters of road salt.

No theft record. No active lien. Previously listed on eBay Motors (item 381261401828).

## Sources

- `mcp__carsxe__get-vehicle-history` — junk/salvage records, title history, odometer chain
- `mcp__carsxe__get-lien-theft` — no theft, no lien; confirmed XJRL 5.0L S/C V8, 550 hp
- `mcp__marketcheck__get_car_history` — the 43-entry listing history above
- `mcp__vin-lookup__decode_vin` (NHTSA vPIC, free) — confirmed 5.0L V8 vs the 3.0L V6

## The general lesson for this search

Marketcheck's own tool documentation says: *"Carfax data on this server is incomplete and
unreliable... do NOT infer ownership history, title status, or any other meaning from any
`carfax_*` value."* Listing price history caught what a title-status field would not.

**Run the full three-check on every candidate before a test drive:**
`get-vehicle-history` + `get-lien-theft` + `get_car_history`. The salvage-auction cluster in the
listing history is the tell.
