"""
Ingest: Product-Market Fit — Tren Griffin / 25iq synthesis
-----------------------------------------------------------
Source: Tren Griffin — 25iq blog (PMF synthesis)
Type: Curated synthesis of practitioner thinking
Voices: Rachleff, Andreessen, Blank, Altman, Horowitz, Wilson, Dixon, Palihapitiya, others

SOURCE CONTEXT (important for retrieval interpretation):
- US venture-backed tech lens, primarily B2C or horizontal SaaS
- Opinion and reported observation — NOT data-backed research
- Survivorship bias is severe — all examples are from winner's circle
- The 70% premature scaling stat (Startup Genome) is cited without source scrutiny
- Treat as high-quality practitioner signal, not universal law
- Apply with caution to: bootstrapped companies, B2B enterprise, regulated industries,
  non-US markets, deep tech / hardware, or pre-customer stage startups

RELATES_TO (existing stored knowledge):
- jtbd_core_principle, jtbd_nonconsumption_competitor (knowledge collection)
- fw_crossing_chasm_001, fw_nonconsumption_001, fw_pmf_pricing_signal_001 (frameworks collection)

CHUNKS: 15
CHANGELOG:
- 2026-03-11 | created: 15 chunks covering core principles, market mental models,
               customer-level diagnostics, operational pitfalls, stress tests,
               bias flags, cross-framework integrations, and consulting diagnostics

Usage:
    python scripts/ingest_pmf_article.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from memory.store import upsert, count

COLLECTION = "knowledge"

CHUNKS = [

    # ── 1. Core Principle ─────────────────────────────────────────────────────
    {
        "id": "pmf_core_principle",
        "text": """PMF Core Principle — The market decides, and the sequence is sacred:

You do not get to decide if you have PMF. The market decides.
Your only job is to find the right market fast, test your value hypothesis honestly,
and refuse to scale until the pull signal is undeniable.

The second principle underneath — and the one that separates consultants from students:
THE SEQUENCE IS SACRED.
  1. Value hypothesis first — what are you building, who is desperate for it, what is the business model?
  2. Growth hypothesis second — how do you acquire and retain customers at scale?
  3. Scaling third — only after the pull signal is confirmed.

Collapsing those phases is the single most reliable way to die.
Most founders know PMF matters. Very few actually honor the sequence.
They get early traction, feel the pull, and immediately shift into growth mode.
That gap between early adopter love and mainstream market pull is where the graveyard is.

Source: Tren Griffin synthesis — Rachleff, Andreessen, Blank, Altman, Horowitz""",
        "metadata": {
            "chunk_type": "principle",
            "framework": "pmf",
            "related_to": "jtbd_core_principle,pmf_rachleff_hierarchy,pmf_bpmf_apmf_line",
            "source": "PMF Synthesis — Tren Griffin / 25iq",
            "author": "Rachleff, Andreessen, Blank, Altman et al. (curated by Griffin)",
            "domain": "pm",
            "applicability": "startup,any",
            "importance": "high"
        }
    },

    # ── 2. Rachleff Hierarchy — Market Beats Team ──────────────────────────────
    {
        "id": "pmf_rachleff_hierarchy",
        "text": """PMF — Rachleff's Market Hierarchy (memorize this):

Great team + lousy market     → market wins. Team loses.
Lousy team + great market     → market wins. Team is replaceable.
Great team + great market     → something special happens.

Market wins in TWO of three scenarios. Team wins in ZERO.
Don Valentine's version: "Give me a giant market, always."
He is not saying team doesn't matter. He is saying you can replace people —
you cannot replace a market that doesn't exist.

Consulting implication — uncomfortable but important:
When a founder says "we have a great product but the market isn't responding,"
the honest answer is almost always: wrong market, wrong customer definition,
or wrong timing — NOT a distribution problem that more sales headcount will solve.
Market problems disguise themselves as execution problems constantly.

This is one of the most important reframes you can offer a founder.
Before diagnosing GTM, distribution, or team — diagnose the market.

Source: Andy Rachleff (Benchmark / Wealthfront / Stanford)""",
        "metadata": {
            "chunk_type": "principle",
            "framework": "pmf",
            "related_to": "pmf_core_principle,pmf_consulting_diagnostic",
            "source": "PMF Synthesis — Tren Griffin / 25iq",
            "author": "Rachleff, Valentine",
            "domain": "pm,consulting,strategy",
            "applicability": "startup,any",
            "importance": "high"
        }
    },

    # ── 3. Nonconsumption as Competitor — Market Lens ─────────────────────────
    {
        "id": "pmf_nonconsumption_market_lens",
        "text": """PMF — Nonconsumption as Competitor (market-level lens):

EXTENDS: fw_nonconsumption_001 (which covers the JTBD / product-level angle)
THIS CHUNK: adds the market-level and VC/PMF angle

Andreessen's version: in a terrible market, you will spend years looking for customers
who don't exist. The most dangerous competitor is not a rival company.
It is the status quo. It is the customer deciding to do nothing, tolerate the pain,
or use a cobbled-together workaround.

If you can't explain why customers are MOVING AWAY from nonconsumption toward your product,
you don't have a market thesis. You have a product hope.

Market diagnostic: Is demand being pulled out of you, or are you pushing it into the market?
Pull → market signal. Push → you might be in a nonconsumption trap.

How this shows up in PMF assessment:
- Low conversion despite high interest → nonconsumption is the real competitor
- High churn at the trial/onboarding stage → switching from nothing is harder than you thought
- Customers use the product once and disappear → the job isn't frequent or urgent enough
  to make moving away from nonconsumption feel permanently worth it

Source: Marc Andreessen""",
        "metadata": {
            "chunk_type": "insight",
            "framework": "pmf",
            "related_to": "fw_nonconsumption_001,jtbd_nonconsumption_competitor,pmf_core_principle",
            "source": "PMF Synthesis — Tren Griffin / 25iq",
            "author": "Marc Andreessen",
            "domain": "pm,strategy",
            "applicability": "startup,any",
            "importance": "high"
        }
    },

    # ── 4. First to PMF Wins, Not First to Market ──────────────────────────────
    {
        "id": "pmf_first_to_pmf_not_market",
        "text": """PMF Insight — First to PMF wins. First to market is irrelevant.

Facebook was not first (Friendster, MySpace). Google was not first (AltaVista, Yahoo).
Apple was not first in MP3 players, smartphones, or tablets.
What each did was find the specific configuration of product, experience, and business model
that made people feel the product was built exactly for them — and they did it faster than
anyone who had come before could find it.

Being early in a market that isn't ready is not an advantage. It is expensive exploration
that you pay for and a later entrant gets the benefit of.

Rachleff's point: the first company to achieve PMF with the mainstream market often becomes
structurally impossible to displace — not because their product is better, but because
the network, the data, or the switching cost created by reaching PMF first becomes the moat.

Consulting diagnostic:
When a founder says "we were first," ask:
"First to what? To launch? Or first to find what the market actually wanted?"
Those are completely different achievements.

Caveat: in markets with strong network effects, first to PMF with mainstream can mean
structural impossibility for competitors. Sequence still matters more than timing.

Source: Andy Rachleff""",
        "metadata": {
            "chunk_type": "insight",
            "framework": "pmf",
            "related_to": "pmf_rachleff_hierarchy,fw_disruptive_innovation_001",
            "source": "PMF Synthesis — Tren Griffin / 25iq",
            "author": "Rachleff",
            "domain": "pm,strategy",
            "applicability": "startup,any",
            "importance": "high"
        }
    },

    # ── 5. Early Adopter Love vs Mainstream Market Pull ────────────────────────
    {
        "id": "pmf_early_adopter_vs_mainstream",
        "text": """PMF — The Gap Between Early Adopter Love and Mainstream Market Pull:

EXTENDS: fw_crossing_chasm_001 (Moore's framework)
THIS CHUNK: adds the PMF/scaling consequence angle

Early adopters are motivated, forgiving, and vocal.
They use a half-built product and tell you it's great because they were miserable before.
PMF with early adopters is a starting point. PMF with the early majority is the business.
Most founders never make that distinction consciously — and scale into the majority
with a product that was only built for early adopters.

Why this is the most dangerous failure mode:
- Early adopter traction FEELS like PMF. NPS is high. Referrals happen.
- The founder raises a round on that signal and hires a sales team.
- The sales team goes after the early majority — who have different jobs, different risk tolerance,
  need proof and references, and won't forgive product gaps.
- The growth curve flattens. The company is now burning cash on a product
  that was never built for the customers they're selling to.

Alex Schultz's observation: the number one problem he sees is founders who think they have PMF
when they don't. Andreessen says you can always feel PMF. Both cannot be fully true.
The resolution: the feeling can be faked by early adopter enthusiasm.

Real-time diagnostic question (the one this article doesn't give you, but you need):
Is the pull coming from customers who found you, or customers you found?
If most of your customers came from founder network, warm intros, or early adopter communities —
you might not yet know if the mainstream market wants what you have.

Source: Andreessen, Schultz, Moore (implicit)""",
        "metadata": {
            "chunk_type": "insight",
            "framework": "pmf",
            "related_to": "fw_crossing_chasm_001,pmf_bpmf_apmf_line,pmf_bias_flags",
            "source": "PMF Synthesis — Tren Griffin / 25iq",
            "author": "Andreessen, Alex Schultz",
            "domain": "pm,strategy",
            "applicability": "startup,any",
            "importance": "high"
        }
    },

    # ── 6. What "Desperate" Customer Actually Means ────────────────────────────
    {
        "id": "pmf_desperate_customer",
        "text": """PMF — What "Desperate Customer" Actually Means:

Rachleff's value hypothesis framework: define what you're building, who is desperate for it,
and what business model you'll use to deliver it.
The word "desperate" is doing enormous work — and the article doesn't unpack it enough.

Desperate means ALL of the following are true simultaneously:
1. The pain is FREQUENT — not occasional, not once-a-quarter. It happens regularly.
2. The pain is URGENT — not tolerable. They've tried to fix it and failed.
3. The customer has already tried other things and been disappointed.
4. The customer would NOTICE IMMEDIATELY if you disappeared.
5. The customer has NO GOOD ALTERNATIVE — your absence leaves a real hole.

This is very different from: someone who thinks your product is cool,
would probably use it, tells friends it's interesting, and would find a workaround if you left.

The Chamath test (most underrated line in the article):
"Core product value is elusive and most products don't have any."
He is not being provocative. He is describing the base rate.
Most products are nice-to-have. They solve problems people have learned to live with.
They do not produce the visceral reaction that drives word-of-mouth, pricing power, and retention.

Consulting diagnostic:
Ask the team: "What would your best customers do if your product disappeared tomorrow?"
If the answer is "they'd find something else easily" → you are nice-to-have.
If the answer is "they'd be genuinely stuck" → you might be approaching desperate.

Source: Rachleff, Chamath Palihapitiya""",
        "metadata": {
            "chunk_type": "insight",
            "framework": "pmf",
            "related_to": "jtbd_hidden_emotional_blockers,pmf_core_value_and_retention,fw_pmf_pricing_signal_001",
            "source": "PMF Synthesis — Tren Griffin / 25iq",
            "author": "Rachleff, Chamath Palihapitiya",
            "domain": "pm,consulting",
            "applicability": "startup,any",
            "importance": "high"
        }
    },

    # ── 7. Core Product Value + Retention Curve (merged) ──────────────────────
    {
        "id": "pmf_core_value_and_retention",
        "text": """PMF — Core Product Value Is Elusive + The Retention Curve Diagnostic:

Chamath: core product value "is elusive and most products don't have any."
Base rate truth: most products are nice-to-have. They do not produce the visceral reaction
that drives organic word-of-mouth, pricing power, and retention.

The retention curve is the most honest PMF signal available:
- Retention curve FLATTENING → a cohort of users found lasting value. Core value exists.
- Retention curve DECLINING CONTINUOUSLY → no core value. Every other metric is noise.

When retention is declining:
- Growth hacks, content strategy, new feature roadmap → all distraction
- More sales headcount → burns cash to acquire customers you'll lose
- The correct move: stop scaling, go back to the job, find what breaks the decline

Corollary — what flattening retention tells you:
It tells you THAT value exists, not WHERE it exists.
Your next job is to find which customers are in the flat cohort, what job they're hiring for,
and how to replicate that systematically.

Alex Schultz: if your retention is not flat, you do not have PMF,
and you should not be focused on growing.

Source: Chamath Palihapitiya, Alex Schultz (Facebook)""",
        "metadata": {
            "chunk_type": "insight",
            "framework": "pmf",
            "related_to": "pmf_desperate_customer,pmf_early_adopter_vs_mainstream,jtbd_pricing_power_signal",
            "source": "PMF Synthesis — Tren Griffin / 25iq",
            "author": "Chamath Palihapitiya, Alex Schultz",
            "domain": "pm",
            "applicability": "startup,B2C,B2B",
            "importance": "high"
        }
    },

    # ── 8. Premature Scaling — Default Failure Mode + Viddy (merged) ──────────
    {
        "id": "pmf_premature_scaling",
        "text": """PMF — Premature Scaling: The Default Failure Mode:

Startup Genome finding: 70% of startups scaled prematurely along some dimension.
This is not a fringe failure mode. It is the DEFAULT failure mode.

The mechanism (Blank):
1. Intense investor pressure to show a growth trajectory
2. Founder declares early traction (from early adopters) as PMF
3. Company shifts into scale mode: sales headcount, marketing spend, hardened infrastructure
4. Growth curve flattens — product was only built for early adopters, not mainstream
5. Company is now burning cash on a product the majority doesn't deeply want

THE VIDDY CASE — the clearest illustration:
Used Facebook OpenGraph to reach millions of users before they had PMF.
The platform gave them distribution they hadn't earned.
When Facebook tightened the platform, the product had nothing underneath it —
no core value, no retention, no word of mouth.
It faded. The company sold for almost nothing.

The lesson is not "don't use platform distribution."
The lesson: if your growth is ENTIRELY DEPENDENT on an external channel,
you don't know yet whether you have PMF.
You know whether the channel works. Those are completely different things.

BPMF (before PMF): minimize burn, maximize learning speed.
APMF (after PMF): scale aggressively — every day of delay is competitive risk.
The fatal error: treating BPMF tactics as APMF tactics.

Source: Steve Blank, Startup Genome, Viddy case""",
        "metadata": {
            "chunk_type": "application",
            "framework": "pmf",
            "related_to": "pmf_bpmf_apmf_line,pmf_early_adopter_vs_mainstream,pmf_core_principle",
            "source": "PMF Synthesis — Tren Griffin / 25iq",
            "author": "Steve Blank, Startup Genome",
            "domain": "pm,consulting,strategy",
            "applicability": "startup,any",
            "importance": "high"
        }
    },

    # ── 9. BPMF vs APMF — The Sacred Divide ───────────────────────────────────
    {
        "id": "pmf_bpmf_apmf_line",
        "text": """PMF — BPMF vs APMF: The Sacred Divide and Why Founders Misread It:

BPMF (Before Product-Market Fit):
- Obsess on finding PMF. Nothing else matters.
- Minimize burn rate. Every dollar spent before PMF extends your runway to find it.
- Maximize learning speed. Iteration rate is your only competitive advantage.
- Do NOT hire a sales team. Do NOT build for scale. Do NOT optimize processes.

APMF (After Product-Market Fit):
- Scale aggressively. Every day of delay is competitive risk.
- Now hire sales, invest in distribution, raise a bigger round.
- Now optimize processes and infrastructure for scale.

The honest problem: how do you know which side of the line you're on?

Andreessen says you can always feel it — when PMF happens, it is unmistakable.
Schultz says the number one problem is founders who think they have it when they don't.
These cannot both be fully true. The resolution:
The feeling CAN be faked — by early adopter enthusiasm, platform-driven spikes,
founder network traction, or a trend that looks like a signal.

The PMF feeling you should be looking for is not "lots of people are using it."
It is: "we cannot keep up with demand, customers are pulling the product out of us,
and we have no good explanation for why growth is happening except that people desperately need this."

Consulting diagnostic:
Ask the founding team: "What is your evidence that the pull you're feeling
is coming from the mainstream market and not a forgiving early adopter segment?"
If they cannot answer that precisely, they are probably not where they think they are.

Source: Andreessen, Alex Schultz, Rachleff""",
        "metadata": {
            "chunk_type": "application",
            "framework": "pmf",
            "related_to": "pmf_core_principle,pmf_premature_scaling,pmf_consulting_diagnostic",
            "source": "PMF Synthesis — Tren Griffin / 25iq",
            "author": "Andreessen, Alex Schultz, Rachleff",
            "domain": "pm,consulting",
            "applicability": "startup,any",
            "importance": "high"
        }
    },

    # ── 10. Stress Test — B2B PMF ─────────────────────────────────────────────
    {
        "id": "pmf_stress_test_b2b",
        "text": """PMF Stress Test — B2B Enterprise: Slower Signal, Noisier Market:

The "market decides" principle holds in B2B — but the signal is slower and noisier.

Why B2B PMF is harder to read:
- A single six-figure contract can look like PMF when it is really founder-led selling
  into a personal network. Founder network ≠ market signal.
- Enterprise buyers have different incentives than enterprise users. The person who signs
  the contract is not the person who uses the product daily. (Ref: JTBD buyer ≠ user)
- Sales cycles are long enough that by the time you know the deal failed, runway is short.

The test: you need multiple customers who found YOU — not customers you found —
before the market signal is trustworthy in B2B.

Key distinctions:
- Inbound inquiry → weak market signal on its own, but better than outbound
- Customer-led expansion (upsell without sales push) → strong PMF signal
- Reference calls happening spontaneously → strong PMF signal
- Champion behavior (internal advocates selling for you) → strong PMF signal
- Renewal without negotiation → pricing power signal

Premature scaling trap in B2B:
Building a quota-carrying sales team before you have repeatable, scalable sales
from customers who found you. Founder-led sales does not prove a sales team will work.
It proves the founder can sell. Those are different problems.

Source: Griffin synthesis + B2B-specific extension""",
        "metadata": {
            "chunk_type": "limitation",
            "framework": "pmf",
            "related_to": "pmf_premature_scaling,pmf_bpmf_apmf_line,jtbd_stress_test_works",
            "source": "PMF Synthesis — Tren Griffin / 25iq",
            "author": "Griffin + B2B extension",
            "domain": "pm,consulting",
            "applicability": "B2B,enterprise",
            "importance": "high"
        }
    },

    # ── 11. Stress Test — NPS Benchmark ───────────────────────────────────────
    {
        "id": "pmf_stress_test_nps",
        "text": """PMF Stress Test — NPS 40+ Benchmark: What It Measures and What It Misses:

Rachleff says NPS 40+ signals you're on the right track.
He immediately qualifies it as less accurate than purchase behavior.
The qualification should come first.

What NPS actually measures:
- Customer satisfaction and recommendation intent at a point in time
- A lagging indicator of past experience, not a forward-looking market signal

What NPS does NOT measure:
- Switching cost — how embedded are you in their workflow?
- Urgency — would they be stuck without you, or mildly inconvenienced?
- Willingness to pay more — pricing power is independent of satisfaction
- Retention trajectory — NPS score tells you nothing about whether users come back

Failure cases:
- Product with NPS 50 and no pricing power → great satisfaction, no desperation
- Product with NPS 30 deeply embedded in a critical workflow → nobody leaves despite low scores
- NPS can be gamed through survey timing, customer success calls before the survey, etc.

Better PMF signals in order of reliability:
1. Retention curve behavior (flat cohort = value exists)
2. Expansion revenue without sales push (customers paying more without being asked)
3. Word-of-mouth driven inbound (customers finding you without paid acquisition)
4. Customers who would be "very disappointed" if product disappeared (Sean Ellis: >40%)
5. NPS — useful as one signal in a portfolio, not as the verdict

Source: Rachleff, Sean Ellis""",
        "metadata": {
            "chunk_type": "limitation",
            "framework": "pmf",
            "related_to": "pmf_core_value_and_retention,pmf_desperate_customer,fw_pmf_pricing_signal_001",
            "source": "PMF Synthesis — Tren Griffin / 25iq",
            "author": "Rachleff, Sean Ellis",
            "domain": "pm,consulting",
            "applicability": "startup,B2B,B2C",
            "importance": "high"
        }
    },

    # ── 12. Stress Test — Deep Tech / Hardware ────────────────────────────────
    {
        "id": "pmf_stress_test_deep_tech",
        "text": """PMF Stress Test — Deep Tech / Hardware: Framework Holds in Principle, Breaks in Process:

The build-measure-learn iteration speed assumed by the standard PMF model
can be two to three years in hardware. By the time you have market feedback, runway is gone.

Deep tech companies have to make bets on market readiness before they can test it directly.
The framework is right in principle — you still need a desperate customer.
The process for discovering it is fundamentally different.

What changes in deep tech / hardware:
- You cannot iterate weekly. You commit to a product direction 18-36 months out.
- Customer discovery must happen BEFORE the build, not during it.
- The "desperate customer" test is applied to a hypothesis, not a live product.
- Market timing risk is existential — being 3 years early in hardware means you run out of money
  before the market is ready, and someone else capitalizes on your market development.

What stays the same:
- You still need to find customers who are desperate for what you're building
- You still need to define the value hypothesis before the growth hypothesis
- You still should not scale distribution before you have confirmed the job
- The sequence is still sacred — the feedback loops are just slower

Consulting implication:
When advising a deep tech or hardware startup, the PMF diagnostic must go upstream —
into customer discovery, not product validation. The question is:
"Who is desperate enough to wait 2 years and pay for this when it ships?"
If they can't name 10 such customers, the market thesis is not ready.

Source: Griffin synthesis + deep tech extension""",
        "metadata": {
            "chunk_type": "limitation",
            "framework": "pmf",
            "related_to": "pmf_core_principle,jtbd_stress_test_breaks",
            "source": "PMF Synthesis — Tren Griffin / 25iq",
            "author": "Griffin + extension",
            "domain": "pm,strategy,consulting",
            "applicability": "enterprise,startup",
            "importance": "medium"
        }
    },

    # ── 13. Bias Flags ────────────────────────────────────────────────────────
    {
        "id": "pmf_bias_flags",
        "text": """PMF Article — Critical Bias Flags to Hold Alongside the Framework:

1. SURVIVORSHIP BIAS — severe and systematic.
   Apple, Google, Facebook, Intuit used to illustrate general principles.
   Companies that followed the same process and still failed due to timing, competition,
   or capital constraints are completely absent.
   The framework may be correct — but the evidence is entirely from the winner's circle.
   It is necessary, not sufficient.

2. THE SERENDIPITY ADMISSION is under-examined.
   Rachleff says serendipity plays a role but the process is consistent.
   The messier truth: some of the PMF stories involve significant luck in timing,
   in who founders happened to meet, in which platform opened up distribution at the right moment.
   Presenting a consistent process around serendipity risks giving founders false confidence
   that doing the right things guarantees the right outcome.

3. THE EARLY ADOPTER TRAP is embedded but never explicitly flagged.
   Almost every breakout success had an early adopter phase that looked like PMF before it became real PMF.
   The article tells you what PMF feels like after you have it.
   It does not give you a reliable real-time diagnostic for whether the love you're feeling
   is early adopter love or mainstream market pull — and THAT is the distinction that actually matters.

4. THE NPS PROXY is presented with more confidence than it deserves.
   See pmf_stress_test_nps for full breakdown.
   Presenting NPS as the headline PMF metric before qualifying it does real harm.

Holding these biases:
Use the framework as a strong prior, not a guaranteed process.
The practitioners who built these mental models are pattern-matching from their own context.
Your job as a consultant is to apply the pattern with awareness of what it misses.

Source: Tren Griffin synthesis — Sudheer's critical analysis""",
        "metadata": {
            "chunk_type": "bias",
            "framework": "pmf",
            "related_to": "jtbd_bias_flags,pmf_early_adopter_vs_mainstream,pmf_stress_test_nps",
            "source": "PMF Synthesis — Tren Griffin / 25iq",
            "author": "Griffin (synthesized) — bias analysis by Sudheer",
            "domain": "pm,consulting,strategy",
            "applicability": "any",
            "importance": "high"
        }
    },

    # ── 14. JTBD + PMF Integration ────────────────────────────────────────────
    {
        "id": "pmf_jtbd_integration",
        "text": """Framework Integration — JTBD + PMF: Two Halves of the Same Diagnostic:

JTBD (Christensen) gives you the CUSTOMER-LEVEL tool:
Understand the job — functional, emotional, social — the customer is trying to get done.
Build the product experience around that job.
Answers: WHY does a specific customer buy?

PMF (Rachleff / Andreessen) gives you the MARKET-LEVEL tool:
Confirm that enough customers share that job, that they are desperate enough to pull
the product out of you, and that the market is large and urgent enough to sustain a business.
Answers: Can that customer insight become a company?

You need BOTH. They fail without each other:
- JTBD without PMF validation: compelling customer insight serving a market of twelve people.
- PMF pursuit without JTBD depth: product that grows for a while, then loses customers
  because it never solved the real job — it just captured demand that existed in the environment.

The sequence in practice:
1. Use JTBD thinking to DISCOVER the real job (customer interviews, circumstance mapping)
2. Use PMF thinking to TEST whether the market for that job is real (retention, pull signal, market size)
3. Only scale when both are confirmed

The premature scaling / Crossing the Chasm connection:
Griffin's article describes the financial mechanism of failing to cross the chasm:
scale before confirming the mainstream market's job, burn the company trying to cross
a chasm you didn't know you were at.

Source: Christensen + Rachleff/Andreessen integration — Sudheer's synthesis""",
        "metadata": {
            "chunk_type": "comparison",
            "framework": "pmf",
            "related_to": "jtbd_core_principle,fw_crossing_chasm_001,pmf_core_principle,pmf_premature_scaling",
            "source": "PMF Synthesis — cross-framework integration",
            "author": "Christensen, Rachleff, Andreessen — integrated by Sudheer",
            "domain": "pm,strategy,consulting",
            "applicability": "any",
            "importance": "high"
        }
    },

    # ── 15. Consulting Diagnostic + Boundary Conditions ───────────────────────
    {
        "id": "pmf_consulting_diagnostic",
        "text": """PMF — The Consulting Diagnostic + Framework Boundary Conditions:

THE ONE QUESTION to walk into an early-stage company and ask:
"What is your specific evidence that the pull you are feeling is coming from
the mainstream market — and not from a forgiving early adopter segment?"

If they cannot answer that precisely:
- Everything they are planning to spend on growth is at risk
- They are probably BPMF thinking they are APMF
- The correct advice is: stop scaling, confirm the signal source first

Full diagnostic sequence:
1. Is your retention curve flat or declining? (Flat = proceed. Declining = stop everything.)
2. Who are your customers — did they find you, or did you find them?
3. What do customers do when you're down or unavailable? (Desperate vs. mildly inconvenienced?)
4. What is your expansion revenue doing without a sales push?
5. Can anyone other than the founders sell this product repeatably?

FRAMEWORK BOUNDARY CONDITIONS — when to apply with full confidence:
✓ Startup operating in markets with reasonably fast feedback loops
✓ Customer behavior is observable and measurable
✓ Iteration cycles are short enough to test within runway
✓ Unit economics allow for discovery before scale

WHEN THE FRAMEWORK BREAKS DOWN:
✗ Feedback loops are slow (deep tech, regulated industries, enterprise with 18-month cycles)
✗ Platform distribution masks absence of real PMF (Viddy problem)
✗ Market is outside US venture context — dynamics of CAC, word-of-mouth, investor pressure differ
✗ Pre-customer stage — framework is diagnostic, not generative from zero

Source: Griffin synthesis — consulting application by Sudheer""",
        "metadata": {
            "chunk_type": "application",
            "framework": "pmf",
            "related_to": "pmf_bpmf_apmf_line,pmf_rachleff_hierarchy,pmf_stress_test_b2b,pmf_stress_test_deep_tech",
            "source": "PMF Synthesis — Tren Griffin / 25iq",
            "author": "Griffin (synthesized) — consulting application by Sudheer",
            "domain": "pm,consulting",
            "applicability": "startup,B2B,B2C",
            "importance": "high"
        }
    },
]


def ingest():
    print(f"\n── Ingesting PMF Article → [{COLLECTION}] ({len(CHUNKS)} chunks) ──\n")
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
