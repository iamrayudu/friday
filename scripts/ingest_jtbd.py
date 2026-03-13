"""
Ingest: Jobs-to-be-Done (JTBD) — HBR Article
Christensen, Hall, Dillon, Duncan

This is a template for how to ingest any deep analytical article.
Each chunk = one retrievable concept. NOT one section.

Usage:
    python scripts/ingest_jtbd.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from memory.store import add, count

COLLECTION = "knowledge"

CHUNKS = [

    # ── CHUNK 1: Core Principle ──────────────────────────────────────────────
    {
        "id": "jtbd_core_principle",
        "text": """JTBD Core Principle — The one sentence that is everything:
Customers don't buy products. They hire solutions to make progress in a specific circumstance.

The causal driver of purchase is NOT a trait or demographic. It is a circumstance in which
a person is struggling to make progress toward something that matters to them.
That struggle is the 'job.'

Source lens: B2C, US-centric, large-company adjacent. Cases are retrospective success stories.
This is an academic-practitioner hybrid (HBR) — theorist + practitioner co-authored.""",
        "metadata": {
            "chunk_type": "principle",
            "framework": "JTBD",
            "related_to": "personas,disruptive_innovation,crossing_the_chasm",
            "source": "Know Your Customers Jobs to Be Done — HBR",
            "author": "Christensen, Hall, Dillon, Duncan",
            "domain": "pm,strategy,innovation",
            "applicability": "any",
            "importance": "high"
        }
    },

    # ── CHUNK 2: 3-Layer Job Model ────────────────────────────────────────────
    {
        "id": "jtbd_three_layers",
        "text": """JTBD — The 3 Layers of Every Job:

1. Functional dimension — the practical task to be done
   (move into a smaller space, get a college credential, carry snacks without a mess)

2. Emotional dimension — how the person wants to FEEL during or after doing that task
   (relief from anxiety, pride in graduating, no guilt about overindulging)

3. Social dimension — how the person wants to be PERCEIVED by others while doing it
   (responsible parent, self-made graduate, competent professional)

Most companies solve for functional only.
The companies that win solve for all three.

Application: When analyzing any product, ask: which layers does it solve?
Which layers are competitors ignoring? That gap is the opportunity.""",
        "metadata": {
            "chunk_type": "principle",
            "framework": "JTBD",
            "related_to": "product_design,pmf",
            "source": "Know Your Customers Jobs to Be Done — HBR",
            "author": "Christensen, Hall, Dillon, Duncan",
            "domain": "pm,product,strategy",
            "applicability": "any",
            "importance": "high"
        }
    },

    # ── CHUNK 3: Circumstances Beat Demographics ──────────────────────────────
    {
        "id": "jtbd_circumstances_vs_demographics",
        "text": """JTBD Insight — Circumstances beat demographics as a segmentation lens:

The condo case: All buyers were labeled 'downsizers.' That demographic told the company nothing.
The real segmentation cut: people who are emotionally ready to move but held back by anxiety
of what to let go. That is a completely different customer than 'retiree, income bracket X.'

Demographics describe. Circumstances explain. Jobs predict.

Implication for PM/consulting work:
- Stop segmenting by who the customer is (age, income, role)
- Start segmenting by what situation they're in when the job arises
- Ask: 'When does the struggle happen? What triggers the hire?'

B2B version: Two CMOs at similar-sized companies — one is trying to justify budget to a new CFO
(job: defensibility), another is trying to prove marketing ROI before Q4 review (job: speed of proof).
Same demographic. Different job. Different product pitch needed.""",
        "metadata": {
            "chunk_type": "insight",
            "framework": "JTBD",
            "related_to": "personas,market_segmentation",
            "source": "Know Your Customers Jobs to Be Done — HBR",
            "author": "Christensen, Hall, Dillon, Duncan",
            "domain": "pm,strategy,consulting",
            "applicability": "any",
            "importance": "high"
        }
    },

    # ── CHUNK 4: Real Competitor = Non-consumption ────────────────────────────
    {
        "id": "jtbd_nonconsumption_competitor",
        "text": """JTBD Insight — The real competitor is often inaction / non-consumption:

SNHU's online program was not competing with other colleges.
It was competing with the decision to NOT enroll at all.

This is one of the most underused mental models in PMF thinking.
If you define competition too narrowly, you miss that your biggest competitor is the status quo.

How to find non-consumption:
- Who SHOULD be using your product but isn't?
- What are they doing instead? (Including: nothing)
- What makes 'doing nothing' feel safe or acceptable to them?
- If switching away from 'nothing' is the real barrier, your UX/onboarding problem is bigger than your product problem.

Consulting application: When a client says 'our competitors are X and Y,'
always ask: 'What does the customer do when they choose neither X nor Y?'
That answer often reveals the real market.""",
        "metadata": {
            "chunk_type": "insight",
            "framework": "JTBD",
            "related_to": "competitive_analysis,pmf,disruptive_innovation",
            "source": "Know Your Customers Jobs to Be Done — HBR",
            "author": "Christensen, Hall, Dillon, Duncan",
            "domain": "pm,strategy,consulting",
            "applicability": "any",
            "importance": "high"
        }
    },

    # ── CHUNK 5: Hidden Emotional Blockers ────────────────────────────────────
    {
        "id": "jtbd_hidden_emotional_blockers",
        "text": """JTBD Insight — Hidden emotional weight blocks purchase even when the product is right:

The dining room table case: Condo buyers said they wanted a large living room.
Real blocker: grief. The dining table represented the family's life together.
Giving it up wasn't a space decision — it was a loss ritual.

The company was losing sales not because of bad product features but because
they hadn't addressed the emotional inertia keeping buyers stuck.
Until Moesta named it, nobody in the company could see it.

How this shows up in product work:
- Customers say one thing (stated preference), do another (actual behavior)
- The friction is often emotional or social, not functional
- If conversion is low but intent seems high, dig for the emotional blocker

Research method: Ask not just 'what do you want' but 'what would have to be true
for you to feel comfortable making this decision today?'""",
        "metadata": {
            "chunk_type": "insight",
            "framework": "JTBD",
            "related_to": "user_research,conversion,pmf",
            "source": "Know Your Customers Jobs to Be Done — HBR",
            "author": "Christensen, Hall, Dillon, Duncan",
            "domain": "pm,product,consulting",
            "applicability": "high_consideration,B2C,B2B",
            "importance": "high"
        }
    },

    # ── CHUNK 6: Product Design Principles from JTBD ──────────────────────────
    {
        "id": "jtbd_product_design_principles",
        "text": """JTBD — 3 Product Design Principles that follow from the framework:

1. Design the full EXPERIENCE, not just the object.
   American Girl sells a ritual — the unboxing, the store visit, the mother-daughter memory.
   Competitors who built cheaper dolls missed this. They solved the functional job (toy),
   not the emotional job (mother-daughter bonding memory).

2. Good innovations solve problems that had no adequate prior solution.
   The condo breakthrough: move without the grief. That was a third option that didn't exist.
   The job was real, the market was real, the solution was missing.

3. Align PROCESSES to the job, not just the product.
   SNHU's breakthrough wasn't a better curriculum. It was:
   - 8.5-minute callback after inquiry
   - Adviser who noticed if a student hadn't logged in by Wednesday
   - Laptop replacement if needed
   The product was just the credential. The job included feeling supported enough to finish.

PM implication: Your roadmap shouldn't just be feature lists.
Ask: what processes, touchpoints, and support structures does the full job require?""",
        "metadata": {
            "chunk_type": "application",
            "framework": "JTBD",
            "related_to": "product_design,ux,roadmap",
            "source": "Know Your Customers Jobs to Be Done — HBR",
            "author": "Christensen, Hall, Dillon, Duncan",
            "domain": "pm,product",
            "applicability": "any",
            "importance": "high"
        }
    },

    # ── CHUNK 7: Pricing Power Signal ─────────────────────────────────────────
    {
        "id": "jtbd_pricing_power_signal",
        "text": """JTBD Business Signal — Pricing power as a PMF test:

When you solve the full job (functional + emotional + social), customers don't negotiate on price.
They are buying relief and progress, not features.

Condo case: After reframing around moving services and storage solutions:
- Raised prices by $3,500
- Grew 25% in a market that was DOWN 49%

This is the pricing power signal of real PMF.

How to test this in your own product:
- If customers are highly price-sensitive, you are probably solving a partial job
- If the emotional or social layer is unaddressed, a cheaper competitor can always undercut you
- Real PMF: customers pay more and refer others, because the alternative (not solving the job) is worse

Consulting diagnostic: Ask the founding team — 'What happens when a customer asks for a discount?'
If the answer is 'we usually give it,' they don't have real PMF yet.""",
        "metadata": {
            "chunk_type": "insight",
            "framework": "JTBD",
            "related_to": "pmf,pricing,business_model",
            "source": "Know Your Customers Jobs to Be Done — HBR",
            "author": "Christensen, Hall, Dillon, Duncan",
            "domain": "strategy,business,consulting",
            "applicability": "any",
            "importance": "high"
        }
    },

    # ── CHUNK 8: Stress Test — Where JTBD Works ───────────────────────────────
    {
        "id": "jtbd_stress_test_works",
        "text": """JTBD Stress Test — Where the framework holds strongly:

1. High-consideration purchases with real emotional or social stakes
   (homes, education, healthcare, identity products, career tools)

2. Categories where customers are clearly dissatisfied with existing options
   (they're using workarounds, complaining, switching frequently)

3. B2B contexts where the buyer and user are DIFFERENT people
   (Intercom case: the person paying ≠ the person using the tool)
   In these cases, there are two separate jobs to understand simultaneously.

4. Markets with significant non-consumption
   (people who should be in the market but aren't — biggest growth opportunity)

5. When you need to explain WHY existing customers churn or stay
   (retroactive job-loss analysis — what job did they hire us for, which we stopped delivering?)""",
        "metadata": {
            "chunk_type": "limitation",
            "framework": "JTBD",
            "related_to": "pmf,market_analysis",
            "source": "Know Your Customers Jobs to Be Done — HBR",
            "author": "Christensen, Hall, Dillon, Duncan",
            "domain": "pm,strategy,consulting",
            "applicability": "high_consideration,B2B,B2C",
            "importance": "high"
        }
    },

    # ── CHUNK 9: Stress Test — Where JTBD Breaks ──────────────────────────────
    {
        "id": "jtbd_stress_test_breaks",
        "text": """JTBD Stress Test — Where the framework gets harder or breaks:

1. Commodity markets — JTBD gives insight but not differentiation.
   Knowing customers want cheap gasoline doesn't help you build a new product.

2. Habit-driven, low-consideration purchases — when someone grabs a soda at a vending machine,
   the 'job' is real but shallow. Emotional and social layers barely exist.
   JTBD analysis here produces little actionable signal.

3. Platform / multi-sided markets — the article says nothing about this.
   In a marketplace: buyer's job ≠ seller's job. Resolving both simultaneously is a design
   problem the framework doesn't address.

4. Early-stage startups with no customers yet — JTBD requires interviews with actual buyers and
   non-buyers. If you have no one who has hired or fired your product, you are hypothesizing,
   not discovering. The framework is DIAGNOSTIC, not generative from zero.

5. Genuinely novel categories — for truly new products (early smartphone, AirPods), customers
   didn't know they had the job until the product existed. This is the gap JTBD shares with
   most customer research methods — you can't interview for a job that isn't yet imaginable.""",
        "metadata": {
            "chunk_type": "limitation",
            "framework": "JTBD",
            "related_to": "pmf,market_analysis,platform_strategy",
            "source": "Know Your Customers Jobs to Be Done — HBR",
            "author": "Christensen, Hall, Dillon, Duncan",
            "domain": "pm,strategy,consulting",
            "applicability": "any",
            "importance": "high"
        }
    },

    # ── CHUNK 10: Bias Flags ───────────────────────────────────────────────────
    {
        "id": "jtbd_bias_flags",
        "text": """JTBD Article — Critical Bias Flags to hold alongside the framework:

1. Survivorship bias — STRONG.
   Every case here worked. You don't see companies that ran JTBD interviews, found a clear job,
   built the product, and still failed because of distribution, timing, or competition.
   The framework is presented as sufficient. It is NECESSARY but NOT SUFFICIENT.

2. Retconning — MODERATE.
   Pleasant Rowland (American Girl) is described as intuitively understanding the job preteen girls needed.
   But this is told backwards. Did she articulate the 3-layer job before building, or did she
   build something she believed in and it happened to resonate? The distinction matters:
   JTBD is being used as an explanatory lens applied AFTER success.

3. Stated vs actual behavior — HANDLED WELL.
   The dining table example is a textbook case of customers unable to state the true blocker.
   This is where the framework actively earns its keep.

4. Academic-market gap — LOW for this article.
   The Intercom sidebar is particularly honest — it shows the messiness of discovering jobs
   in an early-stage startup with four engineers. Real world tension is visible.""",
        "metadata": {
            "chunk_type": "bias",
            "framework": "JTBD",
            "related_to": "critical_thinking,research_methods",
            "source": "Know Your Customers Jobs to Be Done — HBR",
            "author": "Christensen, Hall, Dillon, Duncan",
            "domain": "pm,strategy,consulting",
            "applicability": "any",
            "importance": "high"
        }
    },

    # ── CHUNK 11: JTBD vs Personas ────────────────────────────────────────────
    {
        "id": "jtbd_vs_personas",
        "text": """Framework Comparison — JTBD vs Persona-based segmentation:

Personas: describe WHO the customer is (demographics, psychographics, behaviors)
JTBD: describes WHAT the customer is trying to do (the job in a specific circumstance)

You can be the same demographic and have completely different jobs:
- Two 35-year-old women buying running shoes
  → One training for a marathon (job: performance and achievement)
  → One post-breakup (job: reclaiming identity through physical change)
- Same persona. Different job. Needs different product, marketing, and experience.

Intercom's finding: Personas gave them 'too many typical users with little in common.'
The persona was descriptively accurate but strategically useless.

When to use which:
- Personas: useful for tone, communication style, empathy in design
- JTBD: useful for product definition, feature prioritization, pricing, positioning
- Best: combine them — persona tells you how to talk to them, JTBD tells you what to build""",
        "metadata": {
            "chunk_type": "comparison",
            "framework": "JTBD",
            "related_to": "personas,user_research,product_design",
            "source": "Know Your Customers Jobs to Be Done — HBR",
            "author": "Christensen, Hall, Dillon, Duncan",
            "domain": "pm,product,strategy",
            "applicability": "any",
            "importance": "high"
        }
    },

    # ── CHUNK 12: JTBD vs Disruptive Innovation ───────────────────────────────
    {
        "id": "jtbd_vs_disruptive_innovation",
        "text": """Framework Comparison — JTBD vs Disruptive Innovation (Christensen's own distinction):

Disruptive Innovation theory: explains COMPETITIVE DYNAMICS
— Which companies are at risk and from whom? Where is the market moving?

JTBD: explains WHAT TO BUILD
— What progress does the customer need to make? What job is going unfulfilled?

They are COMPLEMENTARY, not substitutes. Use both:

Step 1 (Disruption lens): Map the market. Where is the trajectory going?
  Who is overserving the mainstream? Where is the foothold for a disruptor?

Step 2 (JTBD lens): Once you know where to play, figure out what to build.
  What is the underserved or non-consumed job in that space?

For consulting work:
- Disruption tells you WHERE the market is vulnerable
- JTBD tells you WHAT the winning product needs to deliver
- Together: you can identify the opportunity AND define the solution""",
        "metadata": {
            "chunk_type": "comparison",
            "framework": "JTBD",
            "related_to": "disruptive_innovation,market_strategy",
            "source": "Know Your Customers Jobs to Be Done — HBR",
            "author": "Christensen, Hall, Dillon, Duncan",
            "domain": "strategy,consulting,innovation",
            "applicability": "enterprise,startup",
            "importance": "high"
        }
    },

    # ── CHUNK 13: JTBD + Crossing the Chasm ──────────────────────────────────
    {
        "id": "jtbd_vs_crossing_the_chasm",
        "text": """Framework Integration — JTBD + Crossing the Chasm (Geoffrey Moore):

Moore: Early adopters and early majority have different psychographics → need different pitches.
JTBD adds: They also have DIFFERENT JOBS.

Example — same productivity tool, two different segments:
- Early adopters hire it for: feeling like a cutting-edge professional (social + emotional job)
- Early majority hires it for: stop losing time to disorganized workflows (functional job)

Same product. Different jobs. Requires different:
- Positioning and messaging
- Onboarding and experience design
- Support model
- Pricing signals

This is why early-stage startups who nail early adopters often struggle to cross the chasm:
they've optimized their product and messaging for one job, but the majority has a different job.

Application: When planning a go-to-market, ask — does our product solve the MAJORITY's job,
or just the early adopter's? If they differ, what needs to change before we scale?""",
        "metadata": {
            "chunk_type": "comparison",
            "framework": "JTBD",
            "related_to": "crossing_the_chasm,go_to_market,product_strategy",
            "source": "Know Your Customers Jobs to Be Done — HBR",
            "author": "Christensen, Hall, Dillon, Duncan",
            "domain": "pm,strategy,go_to_market",
            "applicability": "startup,enterprise",
            "importance": "high"
        }
    },

    # ── CHUNK 14: PM/Consultant Diagnostic & Open Tension ────────────────────
    {
        "id": "jtbd_pm_application_and_tension",
        "text": """JTBD — PM/Consultant Diagnostic + Open Tension to hold:

DIAGNOSTIC — Walk into any early-stage company and ask:
1. What circumstance triggers the customer to look for a solution?
2. What progress are they trying to make? (functional, emotional, social)
3. Who or what are they REALLY competing with? (including non-consumption)
4. What emotional or social blockers are preventing purchase?
5. What processes — not just product features — does the full job require?

If the team can't answer all five clearly, they don't know their customer's job.
Almost always, they know demographics and assume that's enough. It is not.

OPEN TENSION — Retention without job fulfillment:
What happens when customers keep using a product even when it isn't doing the job well?
Switching costs, inertia, and network lock-in mean customers often stay with bad solutions.
Intercom's 'one-size-fits-none' — retained customers using the product for the wrong job.
Retention without deep job fulfillment is FRAGILE PMF.

Question: Is the correct startup strategy to make switching easy first, solve the job second?
This is unresolved. Worth thinking about when evaluating moat strategies.

Key takeaway to remember:
Demographics describe. Circumstances explain. Jobs predict.
When you solve the full job: price becomes secondary, competitors become irrelevant,
and your processes become the moat.""",
        "metadata": {
            "chunk_type": "application",
            "framework": "JTBD",
            "related_to": "pmf,consulting,retention,moat",
            "source": "Know Your Customers Jobs to Be Done — HBR",
            "author": "Christensen, Hall, Dillon, Duncan",
            "domain": "pm,consulting,strategy",
            "applicability": "any",
            "importance": "high"
        }
    },
]


def ingest():
    print(f"\n── Ingesting JTBD Article → [{COLLECTION}] ({len(CHUNKS)} chunks) ──\n")
    for chunk in CHUNKS:
        add(
            collection_name=COLLECTION,
            text=chunk["text"],
            metadata=chunk["metadata"],
            doc_id=chunk["id"]
        )
    print(f"\n✓ Done. Total in [{COLLECTION}]: {count(COLLECTION)}\n")


if __name__ == "__main__":
    ingest()
