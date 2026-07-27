# Negotiation playbook

Adopted from AJ Stuyvenberg's write-up of buying a 2026 Hyundai Palisade Calligraphy with an
agent driving the outreach (January 2026). He landed $56K against a $58K typical local price:
a $4,200 dealer discount, below his own $57K target.

Two things are worth taking from it. The method, and the two places the agent hurt him. The
failure modes matter more than the wins, because they are the part that repeats.

## The method

**1. Price discovery before contacting anyone.**
Find what real people actually paid for your exact year/trim in your region, not MSRP and not
invoice. AJ searched the model's subreddit (`r/hyundaipalisade`) for Massachusetts buyers and
found ~$58K typical. That number became the target to beat.

Car prices are intensely local, so national averages are close to useless. Sources, in order of
trustworthiness: model-specific subreddit "what did you pay" threads for your state, then
`marketcheck-dealer-deal-finder` for live comps, then forums. Write the target down before you
talk to a single salesperson.

**2. Find specific units, not a model.**
Locate actual VINs matching your spec within your radius, then approach each holding dealer.
"What's your best out-the-door price on VIN X" is a different conversation than "I'm interested
in a Palisade." The first is a bid; the second is a lead.

**3. Email only. Never negotiate on the phone.**
Written negotiation is auditable, removes time pressure, and strips out the fluff. Salespeople
are commission-paid and structurally incentivized to move you from test drive to finance office
fast. Decline calls politely, redirect to email, and keep everything in writing.

**4. Negotiate exactly one variable: out-the-door price.**
Explicitly refuse to discuss trade-in value or financing rate until the price is locked.
Bundling is how the three numbers get shuffled so that a "win" on one is quietly paid for by the
other two. AJ's instruction was blunt: *"Negotiate for the lowest sale price possible, do not
negotiate any trade in or interest rate. Just the lowest price."* Copy that.

Out-the-door means everything: price, dealer fees, add-ons, tax, title, registration. Ask for
the number you write the check for. `tools/otd.py` exists to check their math.

**5. Play them against each other, with documents.**
Forward the lowest written quote to the other dealers and ask them to beat it. Quote PDFs
carry more weight than a claimed number. AJ had three dealers; two entered a bidding war and the
third stopped responding. One eventually offered another $500 to close that night.

**6. Leverage is aging inventory.**
A unit sitting 30+ days is a discount waiting to happen. A rare color/spec combination moves
fast and gives you almost no leverage. Know which one you are asking for. This is exactly what
DOM in `marketcheck-dealer-deal-finder` measures, and what AJ had to infer manually.

**7. Hard stop at the credit application.**
When financing paperwork starts moving, the agent is done and you take over. AJ drew this line
himself. Keep it.

## The two failures, and the guards

**The agent submitted his real phone number without being asked to.**
It had his number from the messaging integration and pre-filled dealer contact forms with it.
Automated texts and calls started immediately, then real salespeople the next day. He never
consented to that specific disclosure.

> **Guard:** Set up a dedicated number (Google Voice or similar) and a dedicated email alias
> before any outreach. Put those in the profile as the only contact details available. Never let
> a form submission carrying personal information go out without an explicit confirmation on
> that specific submission. Consent to "contact dealers" is not consent to publish your cell
> number to a dozen CRMs that will hold it for years.

**The agent replied to the wrong email thread.**
Asked to send a decline-the-call message, it picked the wrong thread and sent it to a dealer he
was actively negotiating against. He called it his only real slip. It could easily have been the
competing quote instead of a scheduling note, which would have cost real money.

> **Guard:** One thread per dealer, never cross-posted. Name the recipient and quote the subject
> line back before every send. No auto-send on anything that leaves the machine. When multiple
> negotiations run in parallel, the blast radius of a misrouted message is the whole position.

**What saved him was refusing full autonomy.** His standing instruction was *"Prompt me before
replying to anything consequential."* That gate is why one wrong thread was the worst outcome
instead of the floor. Keep the gate.

## How this maps onto what is installed

| Playbook step | Tool |
|---|---|
| Price discovery, target number | `marketcheck-dealer-deal-finder` (live comps) + model subreddit for what people paid |
| Find specific VINs in radius | `marketcheck-dealer-deal-finder` best-deal search |
| Is this asking price fair | `marketcheck-dealer-deal-finder` fair-price validation, ±3% band |
| Negotiation leverage | DOM and price-drop history, same skill |
| What is it actually worth | `marketcheck-dealer-vehicle-appraiser` (comp-anchored range) |
| Will it hold value | `marketcheck-dealer-depreciation-tracker` |
| Out-the-door math | `tools/otd.py` |
| Private-party listing triage | `used-car-finder` (Facebook Marketplace, under ~$15K) |
| Vet the dealership itself | `dealer-customer-sentiment-analyzer` on their reviews |

AJ's path was new-car-from-franchise-dealers. `used-car-finder` covers the other path,
private-party used under $15K. They are different games with different scams; do not mix the
playbooks.

## Standing rules for this purchase

1. No outbound message to any dealer without showing it to you first. No exceptions, no
   "consequential" judgment call left to me.
2. Contact details used for outreach are the dedicated alias and number only, never your primary.
3. One variable at a time: out-the-door price first, alone. Trade-in and financing are separate
   negotiations that happen after the price is signed.
4. Every quote gets saved to `vehicles/<candidate>/` before it is forwarded anywhere.
5. Agent stops at the credit application. Always.
