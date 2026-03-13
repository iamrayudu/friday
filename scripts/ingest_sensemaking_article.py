"""
Ingest: Sensemaking Article Deep Analysis → `knowledge` collection
--------------------------------------------------------------------
Source: Madsbjerg & Rasmussen — HBR / The Moment of Clarity
        ReD Associates (strategy consultancy applying human sciences)

DESIGN NOTES:
- Standalone reusable frameworks go to `frameworks` (see ingest_sensemaking_frameworks.py)
- This file stores the ANALYTICAL knowledge: critical thinking, stress tests,
  biases, cross-framework connections, and consulting application
- Cases (Lego, BeerCo, Coloplast) embedded as illustrations, not standalone chunks
- Domain: consulting,strategy (multi-domain)

CHUNKS (13 total):
 1. km_sensemaking_core_principle        — Core principle: phenomenology vs hypothesis testing
 2. km_sensemaking_confirmation_bias     — Organizational confirmation bias as the root failure
 3. km_sensemaking_step1_reframe         — Step 1 deep: outside-in reframe mechanism
 4. km_sensemaking_step2_data            — Step 2 deep: fieldwork without hypotheses
 5. km_sensemaking_step3_patterns        — Step 3 deep: onion layers and where insight lives
 6. km_sensemaking_step4_insight         — Step 4 deep: translating root-cause into specification
 7. km_sensemaking_step5_impact          — Step 5 deep: from insight to cascade
 8. km_sensemaking_three_level_practice  — Three-level diagnostic applied in engagements
 9. km_sensemaking_stress_works          — When sensemaking works: right conditions
10. km_sensemaking_stress_breaks         — When sensemaking breaks: failure modes
11. km_sensemaking_bias_flags            — Cognitive / organizational biases that block sensemaking
12. km_sensemaking_vs_jtbd               — Sensemaking vs JTBD: integration and contrast
13. km_sensemaking_consulting_diagnostic — Consulting diagnostic: when to recommend sensemaking

CHANGELOG:
- 2026-03-11 | created: 13 analytical sensemaking chunks into knowledge collection

Usage:
    python scripts/ingest_sensemaking_article.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from memory.store import upsert, count

COLLECTION = "knowledge"

CHUNKS = [

    # ── 1. Core Principle ────────────────────────────────────────────────────
    {
        "id": "km_sensemaking_core_principle",
        "text": """Sensemaking — Core Principle:

The central claim of Madsbjerg & Rasmussen (ReD Associates): conventional research
(surveys, analytics, focus groups) is structurally incapable of answering the most
important questions about customer behavior — not because it is badly executed,
but because it is epistemologically limited.

Conventional research assumes: you know the right question, you have plausible hypotheses,
you are testing what you already suspect. It is hypothesis-driven science.

Sensemaking assumes: you do NOT know the right question. The goal is to understand
the customer's world on its own terms — what it feels like to live a certain kind of life.
This is phenomenological research — the study of lived experience.

The practical failure mode sensemaking addresses:
Companies generate increasing volumes of data, increasingly sophisticated analytics,
and produce increasingly precise answers to the wrong questions.
The methodology gap is not data quantity — it is data type.
No amount of survey data can surface what you don't know to ask.

LEGO example: Despite detailed market research, LEGO nearly failed because they
were studying toy preferences, not the role of play in children's identity development.
The insight that saved LEGO came from watching a German boy describe his worn-out sneakers
as evidence of mastery — something no survey would have captured.
Sensemaking surfaced the job: give children a way to demonstrate competence and mastery.

Key distinction: Sensemaking is not qualitative research. Qualitative research (interviews)
still tests hypotheses. Sensemaking enters the field with open phenomena, not pre-formed hypotheses.""",
        "metadata": {
            "chunk_type": "principle",
            "framework": "sensemaking",
            "related_to": "phenomenology,jtbd,qualitative_research",
            "source": "The Moment of Clarity — HBR / Madsbjerg & Rasmussen",
            "author": "Christian Madsbjerg, Mikkel Rasmussen",
            "domain": "consulting,strategy",
            "applicability": "enterprise,B2C",
            "importance": "high"
        }
    },

    # ── 2. Organizational Confirmation Bias ──────────────────────────────────
    {
        "id": "km_sensemaking_confirmation_bias",
        "text": """Sensemaking — Organizational Confirmation Bias as Root Failure:

The deeper organizational problem sensemaking solves is not a research methodology gap —
it is systemic confirmation bias baked into corporate decision-making.

Most companies approach customer research with pre-existing internal theories:
we know our product, we know our category, we know what drives purchase.
Research is then used to validate (or adjust at the margins) these internal theories.
The company's frame of reference is treated as ground truth.

This is inside-out thinking: starting from the company's agenda, metrics, and assumptions,
and using research to confirm or improve them. The company's theory is the unit of analysis.

The failure this causes:
1. Innovation pipelines full of incremental improvements to the wrong product
2. Launch failures despite positive concept testing (customers said yes; behavior said no)
3. Growing gap between NPS scores and actual retention (metrics diverge from lived experience)
4. Strategy that optimizes for a market that no longer resembles the customer's reality

ReD Associates case (BeerCo): A major beer company facing declining bar sales
had exhausted conventional research without finding an explanation.
Inside-out question: "How do we improve promotional effectiveness with bar owners?"
Outside-in sensemaking: "What is it like to run a small bar?"
Discovery: bar owners were not primarily motivated by promotions — they were trying to
maintain their identity as independent operators, not become an extension of a brand's distribution.
The marketing program was solvable only by reframing the relationship, not improving the promotion.

The consulting intervention that applies here: explicitly surface the internal theory
the client is using before designing any research. That theory is itself the first hypothesis to test.""",
        "metadata": {
            "chunk_type": "bias",
            "framework": "sensemaking",
            "related_to": "confirmation_bias,inside_out_reframe,organizational_behavior",
            "source": "The Moment of Clarity — HBR / Madsbjerg & Rasmussen",
            "author": "Christian Madsbjerg, Mikkel Rasmussen",
            "domain": "consulting,strategy",
            "applicability": "enterprise",
            "importance": "high"
        }
    },

    # ── 3. Step 1: Outside-In Reframe ────────────────────────────────────────
    {
        "id": "km_sensemaking_step1_reframe",
        "text": """Sensemaking Step 1 Deep — Outside-In Reframe:

The first move in sensemaking is not entering the field — it is rewriting the question.
Before any research is designed, the research brief must be stripped of company-agenda language
and reframed around the customer's phenomenon.

Why this step matters:
Research follows the question. If the question is inside-out, the field observations
will be filtered through that lens and the unexpected will not register.
The question is not just a starting point — it is the entire aperture of the research.

Diagnostic test for inside-out questions:
Does your research question contain:
- A company metric?         (revenue, churn, sales, growth) → inside-out
- A product category?       (our ostomy product, our toy line) → inside-out
- A solution assumption?    (how do we make X better?) → inside-out
- An internal hypothesis?   (we think it's because...) → likely inside-out

Examples of the reframe:
  Inside-out: "How do we grow ostomy product sales?" (Coloplast)
  Outside-in: "What is it like to live with an ostomy?"
  → Discovery: the product category was wrong. Customers needed to reclaim their identity
    as sexually capable people, not a better medical device. This insight rewrote the entire
    positioning, packaging, and product design.

  Inside-out: "How do we increase toy revenue in China?" (LEGO)
  Outside-in: "What is the role of play in the lives of Chinese children?"
  → Discovery: children's play was structured, achievement-oriented, and tied to identity —
    the complete opposite of the Western conception LEGO was building products around.

The reframe step is often where sensemaking creates its first consulting value:
clients frequently don't know their question is inside-out until someone names it.""",
        "metadata": {
            "chunk_type": "application",
            "framework": "sensemaking",
            "related_to": "inside_out_reframe,research_design,consulting",
            "source": "The Moment of Clarity — HBR / Madsbjerg & Rasmussen",
            "author": "Christian Madsbjerg, Mikkel Rasmussen",
            "domain": "consulting,strategy",
            "applicability": "enterprise,B2C",
            "importance": "high"
        }
    },

    # ── 4. Step 2: Fieldwork Without Hypotheses ──────────────────────────────
    {
        "id": "km_sensemaking_step2_data",
        "text": """Sensemaking Step 2 Deep — Fieldwork Without Hypotheses:

Conventional qualitative research (customer interviews, focus groups) enters the field
with a discussion guide designed to probe existing hypotheses.
Sensemaking fieldwork is structurally different: researchers enter with open phenomena,
not a list of hypotheses to confirm or disprove.

The practical implication:
- Researchers are looking for what is surprising, contradictory, or mundane but unexplained
- The goal is to experience how customers experience their world — not to gather opinions about products
- Observation methods: ethnographic immersion, contextual inquiry, in-home visits, shadowing
- Data type: behavioral observation + verbal account + artifact analysis (what objects surround them?)

The hidden value: customers cannot articulate the most important information.
They can tell you what they think. They cannot tell you why they feel what they feel,
what social pressures they are navigating, or what identity they are protecting.
Only observation reveals what people cannot self-report.

Researcher skill required:
This step requires people trained in human sciences — anthropology, sociology, cultural psychology.
Standard market researchers are trained to test hypotheses; sensemaking requires researchers
who can sit with ambiguity and recognize signal in unexpected places.
This is a capability gap in most corporate environments — it is not a budget gap.

Boundary condition:
This step cannot be rushed or telescoped. Immersion requires time.
If the business question is urgent and time-constrained (2 weeks to a decision),
sensemaking is the wrong tool — its power requires the depth that immersion generates.""",
        "metadata": {
            "chunk_type": "application",
            "framework": "sensemaking",
            "related_to": "ethnography,qualitative_research,research_design",
            "source": "The Moment of Clarity — HBR / Madsbjerg & Rasmussen",
            "author": "Christian Madsbjerg, Mikkel Rasmussen",
            "domain": "consulting,strategy",
            "applicability": "enterprise,B2C",
            "importance": "medium"
        }
    },

    # ── 5. Step 3: Pattern Layers ────────────────────────────────────────────
    {
        "id": "km_sensemaking_step3_patterns",
        "text": """Sensemaking Step 3 Deep — Onion Layers and Where Insight Lives:

Pattern-finding in sensemaking operates across three layers of depth.
The analytical error most research makes is stopping at the outer layer.

Layer 1 — Observable behavior (outer):
What customers DO. Measurable, visible, trackable.
"Customers who use our product 3+ times/week have higher retention."
"Bar owners switch brands when pricing drops by X%."
Data type: behavioral analytics, purchase data, frequency metrics.
What you can do with it: optimize, A/B test, improve the existing product.

Layer 2 — Habits and practices (middle):
How customers organize their lives around the product.
The routines, workarounds, compensating behaviors, and rituals they've built.
"Coloplast users don't use the product in the morning — they build routines around avoidance."
Data type: ethnographic observation, diary studies, shadowing.
What you can do with it: improve product UX, remove friction, redesign onboarding.

Layer 3 — Root cause (inner):
The underlying beliefs, fears, identity stakes, and social pressures.
This is what DRIVES layers 1 and 2 — the WHY behind the behavior pattern.
"Coloplast users are not managing a medical condition — they are managing their identity
as sexually and socially capable people. The ostomy device threatens that identity."
Data type: only accessible through prolonged immersion and skilled interpretation.
What you can do with it: rewrite the product's purpose, the brand's position, the company's theory.

The key principle: Root cause insights do not improve existing products — they transform
what business the company believes it is in. Surface findings produce product changes.
Root-cause insights produce category redefinitions.""",
        "metadata": {
            "chunk_type": "principle",
            "framework": "sensemaking",
            "related_to": "jtbd,pattern_recognition,root_cause_analysis",
            "source": "The Moment of Clarity — HBR / Madsbjerg & Rasmussen",
            "author": "Christian Madsbjerg, Mikkel Rasmussen",
            "domain": "consulting,strategy",
            "applicability": "enterprise,B2C",
            "importance": "high"
        }
    },

    # ── 6. Step 4: Creating the Insight ──────────────────────────────────────
    {
        "id": "km_sensemaking_step4_insight",
        "text": """Sensemaking Step 4 Deep — Translating Root-Cause Into Buildable Specification:

The insight step is where raw Layer 3 pattern becomes a usable strategic direction.
This is the hardest step to teach — and the one most often done poorly.

What an insight is NOT:
- A restatement of the observation ("customers feel embarrassed about their ostomy")
- A hypothesis to be tested ("we think identity matters")
- A customer quote ("they said they want to feel normal")

What an insight IS:
A translation of the root-cause pattern into a specification of what the company must deliver
to actually serve the customer's deepest need.

Test for a real insight: Does it reorganize the company's theory of what business it is in?
- Coloplast: "We are not in the medical device business. We are in the identity reclamation business
  for people whose bodies have been altered." → This insight rewrote R&D, product design, packaging, and sales training.
- LEGO: "We are not in the toy business. We are in the mastery-and-competence development business for children."
  → This changed what sets LEGO built, how they talked to parents, and what age ranges they targeted.

The diagnostic question to test if you have a real insight:
Does this insight cascade — does it simultaneously change what you build, how you sell it,
how you market it, and how you support it? If the insight only changes one of these, it is a surface finding.

The insight gap in organizations:
Most companies stop at observation and call it insight. Consultants often do too.
A real insight requires someone willing to say: everything we thought about this business was wrong.""",
        "metadata": {
            "chunk_type": "principle",
            "framework": "sensemaking",
            "related_to": "strategic_insight,consulting,innovation",
            "source": "The Moment of Clarity — HBR / Madsbjerg & Rasmussen",
            "author": "Christian Madsbjerg, Mikkel Rasmussen",
            "domain": "consulting,strategy",
            "applicability": "enterprise,B2C",
            "importance": "high"
        }
    },

    # ── 7. Step 5: Business Impact Cascade ───────────────────────────────────
    {
        "id": "km_sensemaking_step5_impact",
        "text": """Sensemaking Step 5 Deep — From Root-Cause Insight to Business Cascade:

Step 5 is where sensemaking hands off to conventional strategy.
Once a genuine root-cause insight exists, standard innovation tools apply.

The cascade signal:
A real sensemaking insight produces a cascade — simultaneous implications across functions.
This is the diagnostic test that distinguishes a real insight from a surface finding.

Coloplast cascade:
- R&D: new product categories addressing intimacy and body image, not just stoma management
- Packaging: removed clinical aesthetic, introduced lifestyle imagery
- Sales training: reps trained to discuss identity and sexuality, not just product specs
- Marketing: shifted from problem-solution messaging to aspiration + normalcy messaging
- Market definition: redefined competitor set (not other ostomy devices — anything preventing normal life)

LEGO cascade:
- Product design: sets designed around achievable mastery (complexity levels, collectability)
- Age range: expanded investment in older children who could demonstrate competence
- Marketing: shifted from "fun" to "pride of building"
- Licensing: partners who reinforce mastery identity (Star Wars, Technic)

The organizational will problem:
Step 5 is where sensemaking most often fails — not because the insight was wrong,
but because the organization lacks the will to act on findings that challenge core assumptions.
The insight may be correct and still be ignored.
This is not a sensemaking failure — it is an organizational failure.
The consulting implication: generating the insight is necessary but not sufficient.
Change management and executive sponsorship must be secured before the research, not after.""",
        "metadata": {
            "chunk_type": "application",
            "framework": "sensemaking",
            "related_to": "change_management,strategy,innovation,consulting",
            "source": "The Moment of Clarity — HBR / Madsbjerg & Rasmussen",
            "author": "Christian Madsbjerg, Mikkel Rasmussen",
            "domain": "consulting,strategy",
            "applicability": "enterprise",
            "importance": "high"
        }
    },

    # ── 8. Three-Level Diagnostic in Practice ────────────────────────────────
    {
        "id": "km_sensemaking_three_level_practice",
        "text": """Three-Level Diagnostic — Applied in Consulting Engagements:

The three-level diagnostic (Knowns / Hypotheticals / Big Unknowns) is the first tool
to reach for in any engagement where existing research isn't working.

In practice, the triage conversation looks like this:

Opening diagnostic question:
"Walk me through the best explanation you currently have for this problem."

If the client says: "We know the answer — our churn is driven by X and Y, we have data."
→ Level 1. Sensemaking is overkill. Recommend analytics or A/B optimization.

If the client says: "We think it's one of these 3 things: pricing, onboarding, or product gaps."
→ Level 2. Sensemaking is possible but not necessary. Qualitative research + targeted interviews.
Standard consulting research design applies.

If the client says: "We honestly don't know. We've tried everything. Our research doesn't explain it."
→ Level 3. This is the sensemaking brief. Conventional tools can't solve this —
they're designed to test hypotheses that don't exist yet.

The most common diagnostic error:
Clients present Level 3 problems with Level 2 confidence.
They believe they have hypotheses when they are actually guessing.
The signal: every hypothesis they offer is plausible but none has predictive power —
they fit the evidence but don't change what the team would do next.

Consulting intervention: ask the client to tell you which hypothesis, if confirmed,
would change their strategy most significantly. If they can't answer that — they are at Level 3.

ReD diagnostic shortcut: "If your research came back and said X is the driver —
what would you do differently?" If the answer is "we'd optimize X," they're at Level 1-2.
If the answer is "we'd probably still be confused," they're at Level 3.""",
        "metadata": {
            "chunk_type": "application",
            "framework": "three_level_diagnostic",
            "related_to": "sensemaking,research_design,consulting,problem_diagnosis",
            "source": "The Moment of Clarity — HBR / Madsbjerg & Rasmussen",
            "author": "Christian Madsbjerg, Mikkel Rasmussen",
            "domain": "consulting,strategy",
            "applicability": "any",
            "importance": "high"
        }
    },

    # ── 9. When Sensemaking Works ─────────────────────────────────────────────
    {
        "id": "km_sensemaking_stress_works",
        "text": """Sensemaking — When It Works (Right Conditions):

Sensemaking produces its highest-leverage insights when:

1. The problem is Level 3 (Big Unknowns):
   Existing research has been tried. Results are contradictory, thin, or wrong.
   The company doesn't know what it doesn't know. No current hypothesis is satisfying.

2. The behavior is culturally or socially determined:
   Products or services where purchase/use is shaped by identity, social pressure, cultural norms.
   Healthcare, education, financial services, FMCG. Not fast-moving consumer tech.
   When the "why" behind behavior is invisible to the customer themselves.

3. The market is rich with unmet latent demand:
   Many people could use this product but don't. Non-consumption is the primary competitor.
   Or: customers use the product but not for the intended purpose — and nobody knows why.

4. The company has organizational will:
   Senior leadership is willing to act on findings that challenge assumptions.
   This must be pre-committed before the research begins — the insight will challenge something.

5. The time horizon allows immersion:
   At least weeks of field research. Not a 2-week sprint. Not a survey that substitutes.

Cases where it delivered:
- Coloplast: from declining medical device brand to growing lifestyle brand (Scandinavian market)
- LEGO: from near-bankruptcy to the world's most valuable toy company
- BeerCo (unnamed): reframed bar owner relationship, unlocked B2B growth in stalled segment""",
        "metadata": {
            "chunk_type": "application",
            "framework": "sensemaking",
            "related_to": "three_level_diagnostic,jtbd,research_design",
            "source": "The Moment of Clarity — HBR / Madsbjerg & Rasmussen",
            "author": "Christian Madsbjerg, Mikkel Rasmussen",
            "domain": "consulting,strategy",
            "applicability": "enterprise,B2C",
            "importance": "high"
        }
    },

    # ── 10. When Sensemaking Breaks ───────────────────────────────────────────
    {
        "id": "km_sensemaking_stress_breaks",
        "text": """Sensemaking — When It Breaks (Failure Modes):

1. Applied to Level 1 or Level 2 problems:
   Using sensemaking when hypotheses already exist and could simply be tested.
   Result: expensive and slow answer to a question that didn't require it.
   The methodology is powerful but not cheap — reserve it for Level 3.

2. No organizational will to act on findings:
   The most common failure. The insight is correct. The organization rejects it.
   Research findings that challenge core assumptions require executive sponsorship in advance.
   If sponsorship isn't secured before the research, the report is likely to die on a shelf.

3. Applied in fast-moving consumer technology markets:
   When market dynamics move faster than the immersion cycle allows.
   By the time the ethnographic research is complete, the market has shifted.
   Consumer tech, social media, fast-fashion: sensemaking's time requirement is a structural limitation.

4. Applied to known-solution problems:
   When the market problem is execution, not insight.
   "Our app has bad load times" is not a sensemaking problem — it's an engineering problem.
   Sensemaking is for understanding-gaps, not execution-gaps.

5. Using inexperienced researchers:
   Sensemaking requires human-science-trained researchers who can sit with ambiguity.
   Standard MBAs or market researchers are not equipped for phenomenological observation.
   Using the wrong researchers produces rich anecdotes that don't synthesize into insight.

6. The company mistakes sensemaking for ethnographic decoration:
   Using immersive research to create compelling stories that confirm existing strategy.
   This is confirmation bias with better photography. Not sensemaking.
   Signal: if the research came back and confirmed everything the client already believed, question it.""",
        "metadata": {
            "chunk_type": "limitation",
            "framework": "sensemaking",
            "related_to": "three_level_diagnostic,research_design,consulting",
            "source": "The Moment of Clarity — HBR / Madsbjerg & Rasmussen",
            "author": "Christian Madsbjerg, Mikkel Rasmussen",
            "domain": "consulting,strategy",
            "applicability": "enterprise,B2C",
            "importance": "high"
        }
    },

    # ── 11. Bias Flags ────────────────────────────────────────────────────────
    {
        "id": "km_sensemaking_bias_flags",
        "text": """Sensemaking — Cognitive and Organizational Biases to Flag:

1. Inside-out framing bias (most pervasive):
   Treating the company's frame of reference as ground truth for research design.
   Symptom: all research questions begin with "how do we..." or reference company metrics.
   Counter: rewrite every question to start with "what is it like to..."

2. Hypothesis laundering:
   Presenting Level 3 problems with Level 2 confidence — acting as if hypotheses exist
   when they don't have predictive power. Dressing intuition as analysis.
   Counter: ask "which hypothesis, if confirmed, would change your strategy most?"

3. Anecdote overweighting:
   Taking one vivid field observation and treating it as the whole insight.
   One compelling story is data, not pattern. Pattern requires multiple independent signals.
   Counter: don't present insight until the same root cause explains at least 3 different cases.

4. Premature closure:
   Stopping at Layer 1 or 2 because those findings are legible and safe.
   Layer 3 findings challenge assumptions — there is organizational incentive to stop before reaching them.
   Counter: explicitly ask "what would the Layer 3 explanation be?" even when Layer 2 feels sufficient.

5. Ethnographic decoration:
   Using immersive research to produce compelling stories that confirm existing strategy.
   This makes executives feel good. It doesn't change anything.
   Counter: if research findings are uniformly validating, be suspicious. Reality is more complex.

6. Capability substitution bias:
   Assigning sensemaking research to standard market researchers who are not trained for it.
   Result: good data collection; poor synthesis; no root-cause insight.
   Counter: be explicit about the researcher profile required before the engagement begins.""",
        "metadata": {
            "chunk_type": "bias",
            "framework": "sensemaking",
            "related_to": "confirmation_bias,consulting,research_design",
            "source": "The Moment of Clarity — HBR / Madsbjerg & Rasmussen",
            "author": "Christian Madsbjerg, Mikkel Rasmussen",
            "domain": "consulting,strategy",
            "applicability": "any",
            "importance": "high"
        }
    },

    # ── 12. Sensemaking vs JTBD ───────────────────────────────────────────────
    {
        "id": "km_sensemaking_vs_jtbd",
        "text": """Sensemaking vs JTBD — Integration and Contrast:

Both frameworks share a core commitment: understand what the customer is actually trying to do,
not what the company thinks they want. Both reject inside-out framing.
Both require going beyond survey data into the texture of customer experience.

Where they differ:

UNIT OF ANALYSIS:
- JTBD: the JOB — what functional, emotional, and social progress the customer is trying to make.
  JTBD asks: "What job are they hiring this product to do?"
- Sensemaking: the PHENOMENON — what is it like to live this kind of life?
  Sensemaking asks: "What is the texture of the customer's world before any product is involved?"

ENTRY POINT:
- JTBD: begins with a product or category and works backward to the job.
  You have a product; you want to understand how it fits the customer's life.
- Sensemaking: begins with no product in mind. Enter the customer's world.
  You start with a life situation, not a product category.

DEPTH:
- JTBD is more bounded — the job is the unit. You can complete JTBD research faster.
- Sensemaking is more open — you don't know what you're looking for until you find it.
  Sensemaking takes longer but surfaces things JTBD can't pre-specify.

WHEN TO USE WHICH:
- Use JTBD when: you have a product or category and want to understand the competitive landscape,
  build better features, or understand why customers switch.
- Use sensemaking when: conventional research has failed, the problem is Level 3,
  and you don't yet know what question to ask.

INTEGRATED APPROACH:
Sensemaking (discover the phenomenon) → JTBD (identify the jobs within the phenomenon)
The Coloplast case shows this: sensemaking revealed the identity phenomenon →
JTBD would then identify the specific functional/emotional/social jobs within that landscape.
The two frameworks are sequential, not competing.""",
        "metadata": {
            "chunk_type": "comparison",
            "framework": "sensemaking",
            "related_to": "jtbd,research_design,consulting,strategy",
            "source": "The Moment of Clarity — HBR / Madsbjerg & Rasmussen",
            "author": "Christian Madsbjerg, Mikkel Rasmussen",
            "domain": "consulting,strategy,pm",
            "applicability": "any",
            "importance": "high"
        }
    },

    # ── 13. Consulting Diagnostic ─────────────────────────────────────────────
    {
        "id": "km_sensemaking_consulting_diagnostic",
        "text": """Sensemaking — Consulting Diagnostic: When to Recommend It:

Use this diagnostic when a client presents a business problem and you need to determine
whether sensemaking is the appropriate recommendation.

STEP 1 — Identify the level (Three-Level Diagnostic):
Ask: "What is your best current explanation for this problem?"
- Clear causality + data → Level 1 → do NOT recommend sensemaking
- Plausible hypotheses, uncertain which → Level 2 → standard qualitative research
- No clear hypothesis, repeated research failures → Level 3 → sensemaking candidate

STEP 2 — Check the problem type:
Is the problem about BEHAVIOR that is:
- Culturally or socially determined?          → sensemaking-appropriate
- Identity-sensitive (healthcare, education)? → sensemaking-appropriate
- Fast-moving / technology-driven?            → sensemaking probably too slow
- Execution-based (we know the problem)?      → not a sensemaking problem

STEP 3 — Assess organizational preconditions:
1. Is senior leadership willing to hear that their current theory is wrong?
2. Is there budget and timeline for immersive research (weeks, not days)?
3. Is there human-science research capability available?
If NO to any: sensemaking will either not be executed properly or its findings will be ignored.

STEP 4 — Frame the sensemaking brief (if proceeding):
Rewrite the client's brief using outside-in framing.
Identify the phenomenon (not the product) to research.
Define the Level 3 unknown explicitly as the scope.

QUICK DIAGNOSTIC CARD:
- "We have data but it's contradictory" → Level 3 → sensemaking
- "Our innovations keep failing at launch" → Level 3 candidate → check conditions
- "We know the problem, we need the solution" → Level 1/2 → do not recommend
- "Our customers are not who we thought" → Level 3 → sensemaking
- "We need insights fast" → not sensemaking — time requirement is structural""",
        "metadata": {
            "chunk_type": "application",
            "framework": "sensemaking",
            "related_to": "three_level_diagnostic,consulting,research_design,jtbd",
            "source": "The Moment of Clarity — HBR / Madsbjerg & Rasmussen",
            "author": "Christian Madsbjerg, Mikkel Rasmussen",
            "domain": "consulting,strategy",
            "applicability": "any",
            "importance": "high"
        }
    },
]


def ingest():
    print(f"\n── Ingesting Sensemaking Article → [{COLLECTION}] ({len(CHUNKS)} chunks) ──\n")
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
