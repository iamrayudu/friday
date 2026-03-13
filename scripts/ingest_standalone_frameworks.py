"""
Ingest: Standalone PM Frameworks extracted from JTBD article
-------------------------------------------------------------
Source: Know Your Customers Jobs to Be Done — HBR
        Christensen, Hall, Dillon, Duncan

These frameworks were referenced/defined in the JTBD article as standalone concepts.
They are stored in the `frameworks` collection (same as MBA frameworks) with domain:pm.
This is NOT a duplication of ingest_jtbd.py — that file stores deep JTBD analysis in `knowledge`.
This file stores each framework as a standalone reusable reference in `frameworks`.

DESIGN NOTES:
- All go into `frameworks` collection (not a separate pm_knowledge collection)
- Filtered at query time via metadata: domain="pm"
- Cross-domain queries (no filter) will return these alongside MBA frameworks when relevant

CHANGELOG:
- 2026-03-11 | created: 5 standalone PM frameworks from JTBD article
               (Personas, Disruptive Innovation, Crossing the Chasm,
                Non-consumption Analysis, PMF Pricing Signal)

Usage:
    python scripts/ingest_standalone_frameworks.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from memory.store import upsert, count

COLLECTION = "frameworks"

CHUNKS = [

    # ── 1. Persona-Based Segmentation ────────────────────────────────────────
    {
        "id": "fw_personas_001",
        "text": """Persona-Based Segmentation Framework:
Use when: designing communication tone, empathy mapping, understanding who your user is.
Structure: Define a representative archetype with — demographics, psychographics,
           goals, frustrations, behaviors, and a name/face to make them tangible.

What it answers: WHO is the customer?
What it does NOT answer: WHY they buy or what job they are hiring the product to do.

Best practice: Use personas alongside JTBD — personas tell you HOW to talk to customers,
JTBD tells you WHAT to build for them.

Boundary conditions:
- Personas alone are insufficient for product decisions — same demographic can have wildly different jobs
- Intercom finding: personas gave "too many typical users with little in common" — no actionable signal
- Do not confuse persona (description) with job (motivation) — they operate at different levels
- Personas are most useful for: onboarding copy, marketing messaging, support tone
- Personas are weakest for: feature prioritization, pricing, market sizing""",
        "metadata": {
            "type": "framework",
            "name": "persona_based_segmentation",
            "use_case": "user_research,product_design,marketing",
            "domain": "pm",
            "applicability": "any",
            "author": "various — common UX/product practice",
            "source": "Referenced in: Know Your Customers JTBD — HBR"
        }
    },

    # ── 2. Disruptive Innovation Theory ───────────────────────────────────────
    {
        "id": "fw_disruptive_innovation_001",
        "text": """Disruptive Innovation Theory (Christensen):
Use when: analyzing competitive dynamics, identifying which incumbents are vulnerable,
          finding entry points for new players, understanding where a market is going.

What it answers: WHERE is the market vulnerable and who is at risk?
What it does NOT answer: What should the disruptor actually build?

Core mechanism:
- Incumbents overshoot mainstream needs, moving upmarket for higher margins
- Disruptors enter from the bottom (low-end) or a new market (non-consumers)
- Incumbents rationally ignore the disruptor — until it's too late
- Disruption moves upmarket over time, eventually taking the mainstream

How to use alongside JTBD:
Step 1 (Disruption): Identify where incumbents are overserving and who is being ignored
Step 2 (JTBD): Understand the underserved job in that gap — what does the winner need to deliver?

Boundary conditions:
- Disruption theory explains competitive dynamics, NOT what to build — never use it alone for product decisions
- Sustaining innovation (making a good product better) is NOT disruption — don't conflate
- Not every startup is a disruptor — most are sustaining players in a new market
- The theory is retrospective — easier to identify disruption after it happens than before""",
        "metadata": {
            "type": "framework",
            "name": "disruptive_innovation",
            "use_case": "strategy,competitive_analysis,market_entry",
            "domain": "strategy",
            "applicability": "any",
            "author": "Clayton Christensen",
            "source": "Referenced in: Know Your Customers JTBD — HBR"
        }
    },

    # ── 3. Crossing the Chasm ─────────────────────────────────────────────────
    {
        "id": "fw_crossing_chasm_001",
        "text": """Crossing the Chasm (Geoffrey Moore):
Use when: planning go-to-market strategy, understanding why early traction doesn't scale,
          designing for different customer segments as a product matures.

What it answers: Why do products succeed with early adopters but fail to reach the mainstream?

Technology Adoption Lifecycle segments:
- Innovators       → want novelty, tolerate bugs, small group
- Early Adopters   → visionaries, buy for competitive advantage or identity
- Early Majority   → pragmatists, buy for productivity, need references and proof
- Late Majority    → skeptics, buy when it's the standard
- Laggards         → resist until forced

The Chasm: the gap between Early Adopters and Early Majority.
Early adopters buy vision. Early majority buy proven value. These require different products,
messaging, support, and pricing.

JTBD integration insight:
Early adopters and early majority have DIFFERENT JOBS for the same product.
- Early adopters: hire for social/emotional job (feel cutting-edge, gain competitive advantage)
- Early majority: hire for functional job (reduce cost, save time, solve a real workflow problem)
Same product, different jobs → different positioning, onboarding, and experience needed at each stage.

Boundary conditions:
- The chasm exists in technology markets — less pronounced in commodity or regulated markets
- If your early adopter messaging focuses on 'transformation,' your majority messaging must focus on 'results'
- Crossing the chasm often requires narrowing focus to ONE beachhead segment first, not expanding""",
        "metadata": {
            "type": "framework",
            "name": "crossing_the_chasm",
            "use_case": "go_to_market,product_strategy,growth",
            "domain": "pm",
            "applicability": "startup,enterprise",
            "author": "Geoffrey Moore",
            "source": "Referenced in: Know Your Customers JTBD — HBR"
        }
    },

    # ── 4. Non-Consumption Analysis ───────────────────────────────────────────
    {
        "id": "fw_nonconsumption_001",
        "text": """Non-Consumption Analysis (Mental Model):
Use when: defining the real competitive landscape, identifying untapped markets,
          understanding why adoption is low despite apparent demand.

Core idea: Your biggest competitor is often NOT another product — it is the customer
choosing to do nothing, use a workaround, or stay with the status quo.

SNHU example: The online MBA wasn't competing with Harvard or Wharton.
It was competing with the decision not to enroll at all. Reframing this changed everything
about how they marketed, onboarded, and supported students.

How to apply:
1. Map ALL alternatives including: nothing, workaround, hiring someone, ignoring the problem
2. Ask: what makes 'doing nothing' feel safe or acceptable to the customer?
3. If non-consumption is the main alternative, the product problem is: make the first step feel safe
4. Your onboarding and first-mile experience matters more than features

Boundary conditions:
- Only useful when there IS latent demand that isn't converting — if nobody wants the product, this isn't the issue
- Non-consumption analysis works best combined with JTBD interview data
- In B2B: the non-consumption alternative is often internal tooling, spreadsheets, or manual processes
- Pricing: if non-consumption is the competitor, the question isn't 'are we cheaper than X' but
  'is the cost of switching from nothing worth it to the customer?'""",
        "metadata": {
            "type": "mental_model",
            "name": "non_consumption_analysis",
            "use_case": "market_analysis,competitive_analysis,go_to_market",
            "domain": "pm",
            "applicability": "any",
            "author": "Christensen — extended in JTBD literature",
            "source": "Referenced in: Know Your Customers JTBD — HBR"
        }
    },

    # ── 5. PMF Pricing Signal ─────────────────────────────────────────────────
    {
        "id": "fw_pmf_pricing_signal_001",
        "text": """PMF Pricing Signal Framework (Mental Model):
Use when: evaluating whether a product has real product-market fit,
          stress-testing PMF claims, advising early-stage companies.

Core idea: When a product solves the full job (functional + emotional + social),
customers do not negotiate on price. Price sensitivity is a signal of partial job fulfillment.

The condo case: After solving the emotional job (grief of letting go), the company raised
prices by $3,500 and grew 25% in a market down 49%. Solving the full job = pricing power.

PMF diagnostic questions:
1. When a customer asks for a discount, what happens? (If team says 'we usually give it' → partial PMF)
2. Do customers refer others unprompted? (Real PMF: customers advocate because alternative is worse)
3. Would customers be very disappointed if the product disappeared? (Sean Ellis test: >40% = PMF signal)
4. Are customers using the product for the job you designed it for? (Misuse = fragile PMF)

Fragile PMF warning signs:
- High retention but low referral → customers are locked in, not in love
- Price sensitivity despite good engagement → solving functional job only, emotional layer missing
- Intercom pattern: 'one-size-fits-none' — retained customers using product for the wrong job

Boundary conditions:
- Pricing power alone is not PMF — luxury goods command high prices without solving deep jobs
- B2B PMF signals differ: look for expansion revenue, champion behavior, and renewal rates
- Early-stage: PMF is a direction, not a destination — it's always partial until you find the full job""",
        "metadata": {
            "type": "mental_model",
            "name": "pmf_pricing_signal",
            "use_case": "pmf,pricing,strategy,consulting",
            "domain": "pm",
            "applicability": "startup,B2B,B2C",
            "author": "Derived from Christensen JTBD + Sean Ellis PMF test",
            "source": "Referenced in: Know Your Customers JTBD — HBR"
        }
    },
]


def ingest():
    print(f"\n── Ingesting Standalone PM Frameworks → [{COLLECTION}] ({len(CHUNKS)} chunks) ──\n")
    for chunk in CHUNKS:
        upsert(
            collection_name=COLLECTION,
            text=chunk["text"],
            metadata=chunk["metadata"],
            doc_id=chunk["id"]
        )
    print(f"\n✓ Done. Total in [{COLLECTION}]: {count(COLLECTION)}\n")


if __name__ == "__main__":
    ingest()
