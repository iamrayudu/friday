"""
Friday Knowledge Population Script
------------------------------------
Run this ONCE to seed Friday's memory with your background + MBA knowledge.
After this, knowledge grows automatically through conversation.

DESIGN NOTES:
- All frameworks (MBA, PM, strategy) live in ONE `frameworks` collection
- Domain separation is via metadata field `domain`, NOT separate collections
- Each chunk must include: type, name, use_case, domain, applicability
- `domain` values:  mba | pm | strategy | consulting | innovation | business | general
- `applicability`:  B2B | B2C | startup | enterprise | high_consideration | any

CHANGELOG:
- 2026-03-11 | created: personal background + 7 MBA framework chunks
- 2026-03-11 | updated: added `domain` and `applicability` to all framework metadata
               so MBA frameworks are tagged domain:mba and PM frameworks (added separately)
               are tagged domain:pm — all in same collection, filtered by metadata at query time

Usage:
    python scripts/populate.py
    python scripts/populate.py --section personal
    python scripts/populate.py --section frameworks
    python scripts/populate.py --section cases
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from memory.store import upsert, count

# ─────────────────────────────────────────────
# SECTION 1: YOUR PERSONAL BACKGROUND
# Fill this in with your real details
# ─────────────────────────────────────────────

PERSONAL = [
    {
        "id": "profile_background_001",
        "text": """Sudheer's professional background:
        [FILL IN: your industry, years of experience, roles held, companies, key projects]
        Example: 4 years in fintech, worked as a product analyst at X, led Y project.""",
        "metadata": {"type": "background", "domain": "professional", "importance": "10"}
    },
    {
        "id": "profile_skills_001",
        "text": """Sudheer's skills and strengths:
        Strong areas: [FILL IN — e.g., data analysis, financial modeling, SQL, Python]
        Communication style: [FILL IN — structured thinker, visual presenter, etc.]
        How he approaches problems: [FILL IN — first principles, frameworks, intuition]""",
        "metadata": {"type": "skills", "domain": "professional", "importance": "9"}
    },
    {
        "id": "profile_weaknesses_001",
        "text": """Sudheer's known weak areas and blind spots:
        [FILL IN: e.g., qualitative storytelling, stakeholder management, ambiguous data situations]
        Friday should proactively help compensate for these in case analyses.""",
        "metadata": {"type": "skills", "domain": "self_awareness", "importance": "9"}
    },
    {
        "id": "profile_mba_context_001",
        "text": """Sudheer's MBA context:
        [FILL IN: why he's doing an MBA, what he wants to get out of it,
        target industry post-MBA, what kind of cases he expects to see most]""",
        "metadata": {"type": "background", "domain": "education", "importance": "10"}
    },
    {
        "id": "profile_industry_001",
        "text": """Industry knowledge Sudheer brings from work:
        [FILL IN: specific industry dynamics he understands well,
        market knowledge, regulatory context, business model familiarity]
        This is his competitive edge in case discussions.""",
        "metadata": {"type": "industry_context", "domain": "professional", "importance": "8"}
    },
]

# ─────────────────────────────────────────────
# SECTION 2: MBA FRAMEWORKS
# These are pre-filled — expand as you learn more
# ─────────────────────────────────────────────

FRAMEWORKS = [
    {
        "id": "fw_harvard_case_001",
        "text": """Harvard Business Case Method — General Approach:
        Step 1: First read — grasp the big picture, what is the core tension or decision?
        Step 2: Identify the protagonist — who needs to decide, and what do they want?
        Step 3: Separate facts from assumptions. List both explicitly.
        Step 4: Frame the real problem (not the symptom presented).
        Step 5: Generate 2-3 distinct alternatives (avoid yes/no binaries).
        Step 6: Evaluate alternatives against explicit criteria (financial, strategic, operational).
        Step 7: Make a clear recommendation with implementation steps.

        Boundary conditions:
        - Never end on pure analysis — always answer "what should they do?"
        - Fence-sitting is penalized. Pick a side and defend it.
        - Time constraint (<20 mins): skip deep quant, lead with framework + insight + recommendation.""",
        "metadata": {"type": "methodology", "name": "harvard_case_method", "use_case": "general", "domain": "mba", "applicability": "any"}
    },
    {
        "id": "fw_swot_001",
        "text": """SWOT Analysis Framework:
        Use when: understanding competitive position, strategic options, entering a new market.
        Structure:
          Strengths     → internal, positive (what do we do better than competitors?)
          Weaknesses    → internal, negative (what limits us?)
          Opportunities → external, positive (what market forces favor us?)
          Threats       → external, negative (what could hurt us?)

        Best practice: Max 3-5 points per quadrant. Force prioritization.
        Boundary conditions:
        - SWOT describes, it does not prescribe. Always follow with SO/WO/ST/WT strategy mapping.
        - Don't confuse internal/external. Competitor behavior is a Threat, not a Weakness.
        - Avoid generic points ("we have a good team"). Be specific.""",
        "metadata": {"type": "framework", "name": "swot", "use_case": "strategy", "domain": "mba", "applicability": "any"}
    },
    {
        "id": "fw_porters_001",
        "text": """Porter's Five Forces Framework:
        Use when: analyzing industry attractiveness, entry/exit decisions, pricing power, competitive dynamics.
        Forces:
          1. Competitive Rivalry        — how intense is competition within the industry?
          2. Threat of New Entrants     — how easy is it for new players to enter?
          3. Threat of Substitutes      — can customers switch to something different?
          4. Bargaining Power of Buyers — how much power do customers have?
          5. Bargaining Power of Suppliers — how much power do input providers have?

        Best practice: Rate each force H/M/L, then synthesize to overall industry attractiveness.
        Boundary conditions:
        - This is an INDUSTRY analysis, not a company analysis. Do not conflate.
        - Define the industry boundary precisely first — too broad = meaningless result.
        - Combine with SWOT for a complete picture (Five Forces = external, SWOT includes internal).""",
        "metadata": {"type": "framework", "name": "porters_five_forces", "use_case": "industry_analysis", "domain": "mba", "applicability": "any"}
    },
    {
        "id": "fw_bcg_001",
        "text": """BCG Growth-Share Matrix:
        Use when: portfolio analysis, resource allocation across business units or products.
        Quadrants (axes: market growth rate vs relative market share):
          Stars     → high growth, high share — invest to maintain
          Cash Cows → low growth, high share  — harvest, fund other units
          Question Marks → high growth, low share — selective investment or divest
          Dogs      → low growth, low share   — divest or harvest

        Boundary conditions:
        - Only useful when a company has multiple distinct business units/products.
        - Market share alone doesn't tell the full story — watch for profitability nuance.
        - Don't apply to a single-product company.""",
        "metadata": {"type": "framework", "name": "bcg_matrix", "use_case": "portfolio_strategy", "domain": "mba", "applicability": "enterprise"}
    },
    {
        "id": "fw_value_chain_001",
        "text": """Porter's Value Chain Analysis:
        Use when: identifying where a company creates or loses value, finding cost or differentiation advantages.
        Primary Activities: Inbound logistics → Operations → Outbound logistics → Marketing & Sales → Service
        Support Activities: Firm infrastructure, HR management, Technology development, Procurement

        Best practice: Identify which 1-2 activities are the source of competitive advantage.
        Boundary conditions:
        - Don't list all activities robotically — focus on where differentiation happens.
        - Pair with VRIN framework to test if an advantage is sustainable.""",
        "metadata": {"type": "framework", "name": "value_chain", "use_case": "operations_strategy", "domain": "mba", "applicability": "enterprise"}
    },
    {
        "id": "fw_mece_001",
        "text": """MECE Principle (Mutually Exclusive, Collectively Exhaustive):
        Use when: structuring any analysis, breaking down a problem, building issue trees.
        Rule: Each bucket must not overlap (ME) and together they must cover everything (CE).

        Example: Segmenting revenue decline causes:
          Volume down vs Price down (ME + CE — every revenue issue is one or the other)

        Boundary conditions:
        - This is a structuring tool, not a framework for content.
        - Apply it before choosing your framework — helps define what you need to analyze.
        - In case discussions, MECE thinking signals strong consulting-style reasoning.""",
        "metadata": {"type": "methodology", "name": "mece", "use_case": "problem_structuring", "domain": "consulting", "applicability": "any"}
    },
    {
        "id": "fw_boundary_conditions_001",
        "text": """MBA Case Analysis — Boundary Conditions and Edge Cases:
        Time pressure (<30 mins total): Lead with framework choice + key insight + recommendation. Skip deep quant.
        Ambiguous data: State assumptions explicitly. Do sensitivity analysis on key numbers.
        Unknown industry: Use first principles + Porter's Five Forces to map dynamics quickly.
        No clear right answer: Pick a defensible position. Show you understand tradeoffs.
        Quantitative heavy case: Build a simple model, tell a story with the numbers. Don't just present them.
        Qualitative heavy case: Use frameworks to add structure. Show rigorous thinking, not just intuition.
        Conflicting data: Acknowledge conflict explicitly, explain which data you trust and why.
        Ethical dimension present: Name it, don't ignore it — shows maturity.""",
        "metadata": {"type": "boundary_conditions", "name": "general_boundary", "use_case": "general", "domain": "mba", "applicability": "any"}
    },
]

# ─────────────────────────────────────────────
# SECTION 3: PAST CASES (start empty, grows over time)
# ─────────────────────────────────────────────

CASES = [
    # Add entries as you complete cases:
    # {
    #   "id": "case_001",
    #   "text": """Case: [Company/Topic] — [Date]
    #   Industry: [industry]
    #   Frameworks used: [SWOT, Porter's, etc.]
    #   Core question: [what was the decision to make]
    #   My recommendation: [what I said]
    #   What worked: [what landed well]
    #   What to improve: [what was weak]
    #   Key insight: [the one thing I learned]""",
    #   "metadata": {"type": "past_case", "date": "2026-03-11", "industry": "retail", "outcome": "good"}
    # }
]


# ─────────────────────────────────────────────
# RUNNER
# ─────────────────────────────────────────────

def populate(section: str = "all"):
    sections = {
        "personal": ("personal_knowledge", PERSONAL),
        "frameworks": ("frameworks", FRAMEWORKS),
        "cases": ("case_memory", CASES),
    }

    to_run = sections if section == "all" else {section: sections[section]}

    for collection_name, chunks in to_run.values():
        print(f"\n── Populating [{collection_name}] ({len(chunks)} chunks) ──")
        for chunk in chunks:
            upsert(
                collection_name=collection_name,
                text=chunk["text"],
                metadata=chunk["metadata"],
                doc_id=chunk["id"]
            )
        print(f"   Total in collection: {count(collection_name)}")

    print("\n✓ Done. Friday's memory is ready.\n")


if __name__ == "__main__":
    section = sys.argv[2] if len(sys.argv) > 2 and sys.argv[1] == "--section" else "all"
    populate(section)
