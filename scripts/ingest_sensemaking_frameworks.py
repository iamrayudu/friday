"""
Ingest: Sensemaking Standalone Frameworks → `frameworks` collection
--------------------------------------------------------------------
Source: Madsbjerg & Rasmussen — HBR / The Moment of Clarity
        ReD Associates (strategy consultancy applying human sciences)

These are the 3 reusable tools extracted from the Sensemaking article.
They live in `frameworks` because they are usable independently of the article's analysis.
The full analytical breakdown (stress tests, biases, case studies, connections) lives in `knowledge`.

FRAMEWORKS EXTRACTED:
1. fw_sensemaking_5steps       — The 5-step sensemaking process (methodology)
2. fw_three_level_diagnostic   — Knowns / Hypotheticals / Big Unknowns (diagnostic tool)
3. fw_inside_out_reframe       — Inside-out vs outside-in question reframe (mental model)

DOMAIN: consulting (all three — these are consulting-practice tools)
APPLICABILITY: enterprise for 1 & 2, any for 3

CHANGELOG:
- 2026-03-11 | created: 3 standalone sensemaking tools into frameworks collection

Usage:
    python scripts/ingest_sensemaking_frameworks.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from memory.store import upsert, count

COLLECTION = "frameworks"

CHUNKS = [

    # ── 1. Sensemaking 5-Step Process ────────────────────────────────────────
    {
        "id": "fw_sensemaking_5steps",
        "text": """Sensemaking Methodology — 5-Step Process (Madsbjerg & Rasmussen / ReD Associates):

Use when: conventional research (surveys, focus groups, analytics) has already been done
and is producing contradictory, thin, or insufficient insight about customer behavior.
Most powerful in: healthcare, education, FMCG, financial services — any market where
customer behavior is shaped by deep cultural, social, or identity dynamics.

THE 5 STEPS:

Step 1: Reframe the problem as a phenomenon (outside-in)
  From: "How do we grow our ostomy sales?" (company's problem)
  To:   "What is it like to live with an ostomy?" (customer's lived experience)
  This removes the company's agenda from the research question.
  Rule: If your question contains a company metric, it is inside-out. Reframe it.

Step 2: Collect data without hypotheses
  Go into the field with open-ended phenomenological questions.
  Observe without a destination. Let unexpected signals surface.
  Standard research tests hypotheses you already have.
  Sensemaking is designed to discover what you don't know to ask.

Step 3: Look for patterns — peel the onion
  Layer 1 (outer): observable behavior — what they do
  Layer 2 (middle): habits and practices — routines, workarounds
  Layer 3 (inner): root cause — underlying beliefs, fears, identity, social pressure
  Most research stops at Layer 1. Insight lives at Layer 3.

Step 4: Create the key insight
  The insight is the translation of Layer 3 patterns into a buildable specification.
  Test: does this insight reorganize the company's theory of what business it is in?
  Surface finding → product improvement. Root-cause insight → company transformation.

Step 5: Build the business impact
  Once a genuine root-cause insight exists, standard innovation strategy applies.
  Signal of a real insight: it cascades across R&D, manufacturing, marketing, sales simultaneously.

Boundary conditions:
- Requires skilled human-sciences researchers — not standard market research capability
- Requires organizational will to act on findings that challenge core assumptions
- Breaks down when market moves faster than the immersion requires (tech/consumer)
- Breaks down when the problem is actually Level 1 or 2 — don't apply sensemaking to known problems
- Not a guarantee of business success — generates insight, not organizational will to act""",
        "metadata": {
            "type": "methodology",
            "name": "sensemaking_5steps",
            "use_case": "customer_research,innovation,strategy",
            "domain": "consulting,strategy",
            "applicability": "enterprise,B2C,B2B",
            "author": "Christian Madsbjerg, Mikkel Rasmussen — ReD Associates",
            "source": "The Moment of Clarity — HBR / Madsbjerg & Rasmussen"
        }
    },

    # ── 2. Three-Level Diagnostic ─────────────────────────────────────────────
    {
        "id": "fw_three_level_diagnostic",
        "text": """Three-Level Problem Diagnostic (Madsbjerg & Rasmussen):

Use when: triage — determining WHICH type of research method is appropriate BEFORE designing research.
This is the first tool to reach for when a client presents a problem with existing research that isn't working.

THE THREE LEVELS:

Level 1 — Knowns:
  The company understands the problem space. Data exists. Hypotheses are clear.
  Method: standard analytics, A/B testing, optimization. Sensemaking is overkill here.
  Signal: "We know our churn rate is 12% and we know the 3 reasons from exit surveys."

Level 2 — Hypotheticals:
  The company has partial understanding. Hypotheses exist but are uncertain.
  Method: qualitative research, customer interviews, hypothesis testing.
  Signal: "We think pricing is the issue but we're not sure — here are 3 possible explanations."

Level 3 — Big Unknowns:
  The company does not know what it doesn't know.
  Method: sensemaking / ethnographic research / phenomenon-framing.
  Conventional tools CANNOT reach here — they are designed to test hypotheses that don't exist yet.
  Signal: "Full innovation pipeline, consistent launch failures, no clear explanation why."

THE CRITICAL DIAGNOSTIC ERROR:
Companies routinely misdiagnose Level 3 problems as Level 2 and apply hypothesis-testing tools.
Result: increasingly precise answers to the wrong question. The problem gets worse, not better.

How to use this in a consulting engagement:
1. Ask the client to describe their best current explanation for the problem.
2. If they have 2-3 plausible hypotheses → Level 2. Design targeted qualitative research.
3. If they can't formulate a clear hypothesis → Level 3. Sensemaking is the appropriate method.
4. If they have data and clear causality → Level 1. Optimize, don't research.

Boundary condition: most clients present Level 3 problems with Level 2 confidence.
The consulting intervention is often just correctly diagnosing which level they are at.""",
        "metadata": {
            "type": "framework",
            "name": "three_level_diagnostic",
            "use_case": "consulting,problem_diagnosis,research_design",
            "domain": "consulting,strategy",
            "applicability": "any",
            "author": "Christian Madsbjerg, Mikkel Rasmussen — ReD Associates",
            "source": "The Moment of Clarity — HBR / Madsbjerg & Rasmussen"
        }
    },

    # ── 3. Inside-Out vs Outside-In Reframe ───────────────────────────────────
    {
        "id": "fw_inside_out_reframe",
        "text": """Inside-Out vs Outside-In Question Reframe (Mental Model):

Use when: diagnosing why a research brief, strategy question, or innovation challenge
is producing insufficient insight. Applicable to any domain — consulting, PM, MBA cases.

THE REFRAME:

Inside-out question: starts from the company's metric, product, or problem.
  "How do we reduce churn?"
  "How do we grow toy revenue in China?"
  "How do we improve our promotional effectiveness with bar owners?"
  These questions assume the company's frame of reference is the right one.
  They are hypothesis-laden before research begins.

Outside-in question: starts from the customer's lived experience.
  "How do our customers experience banking, and what makes them stay or leave?"
  "What is the role of play in the lives of Chinese children?"
  "What is it like to be a bar owner running a small venue?"
  These questions enter the customer's world without a destination.
  They allow the unexpected to surface.

THE TEST for inside-out vs outside-in:
Does your question contain a company metric (revenue, churn, growth, sales)?
→ Inside-out. Reframe around the customer's experience.
Does your question assume a product category or solution exists?
→ Inside-out. Reframe around the job or phenomenon the customer faces.

APPLICATION BEYOND RESEARCH:
This mental model applies to MBA case framing, product roadmap questions, go-to-market strategy:
- "Should we add feature X?" → inside-out. Reframe: "What job are customers trying to do that X might serve?"
- "How do we enter market Y?" → inside-out. Reframe: "What does the customer experience in market Y look like today?"
- "Why is our NPS declining?" → inside-out. Reframe: "What has changed in how customers experience our product?"

Boundary condition:
Both framings are needed. Inside-out is necessary for business decisions.
Outside-in is necessary for accurate customer understanding.
The error is using inside-out framing during the DISCOVERY phase — before you understand the customer.
Once you understand the customer, inside-out framing is appropriate for building and deciding.""",
        "metadata": {
            "type": "mental_model",
            "name": "inside_out_reframe",
            "use_case": "research_design,consulting,product_strategy,mba_cases",
            "domain": "consulting,strategy,pm,mba",
            "applicability": "any",
            "author": "Madsbjerg & Rasmussen — ReD Associates",
            "source": "The Moment of Clarity — HBR / Madsbjerg & Rasmussen"
        }
    },
]


def ingest():
    print(f"\n── Ingesting Sensemaking Frameworks → [{COLLECTION}] ({len(CHUNKS)} chunks) ──\n")
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
