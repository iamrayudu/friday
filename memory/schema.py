"""
Friday Memory Schema
--------------------
Defines all ChromaDB collections and their metadata contracts.
Think of this as the shape of Friday's brain.

DESIGN DECISION (2026-03-11):
- ONE `frameworks` collection holds ALL frameworks regardless of domain (MBA, PM, strategy, consulting)
- Domain separation is handled via metadata fields, NOT separate collections
- This allows a single query to retrieve across domains when needed,
  and metadata filters to narrow when domain-specific retrieval is required
- Retrieval pattern: search(collection, query, filters={"domain": "pm"}) for domain-specific
                     search(collection, query) for cross-domain (agent context building)

CHANGELOG:
- 2026-03-11 | created initial schema: personal, frameworks, episodes, insights, cases
- 2026-03-11 | added `knowledge` collection for deep analytical articles/analyses
- 2026-03-11 | expanded `frameworks` metadata: added domain, applicability, author fields
               so MBA and PM frameworks coexist in one collection, filtered by metadata
"""

COLLECTIONS = {
    "personal": {
        "name": "personal_knowledge",
        "description": "Who Sudheer is — background, skills, strengths, weaknesses",
        "metadata_fields": ["type", "domain", "importance"]
        # type: background | skills | industry_context | preference
        # domain: professional | personal | health | finance
        # importance: 1-10
    },
    "frameworks": {
        "name": "frameworks",
        "description": "All frameworks, methodologies, mental models — any domain. Filter by metadata.",
        "metadata_fields": ["type", "name", "use_case", "domain", "applicability", "author", "source"]
        # type:          framework | methodology | mental_model | template | boundary_condition
        # use_case:      strategy | industry_analysis | operations | finance | product | general
        # domain:        mba | pm | strategy | consulting | innovation | business | general
        # applicability: B2B | B2C | startup | enterprise | high_consideration | any
        # author:        source author if known (optional)
        # source:        article/book title if known (optional)
    },
    "episodes": {
        "name": "episodes",
        "description": "Specific things that happened — events, moments, conversations",
        "metadata_fields": ["type", "date", "topic", "emotion", "importance"]
        # type: event | conversation | decision | achievement | struggle
        # topic: work | health | finance | relationships | learning
        # importance: 0.0-1.0
    },
    "insights": {
        "name": "insights",
        "description": "Friday's derived patterns and observations about Sudheer",
        "metadata_fields": ["type", "domain", "generated_on", "confidence"]
        # type: pattern | trend | recommendation
        # confidence: low | medium | high
    },
    "cases": {
        "name": "case_memory",
        "description": "MBA case analyses Sudheer has done — what worked, what didn't",
        "metadata_fields": ["type", "date", "industry", "frameworks_used", "outcome"]
        # type: past_case | case_note | case_insight
    },
    "knowledge": {
        "name": "knowledge",
        "description": "Deep processed knowledge — articles, books, analyses with full critical thinking",
        "metadata_fields": [
            "chunk_type",    # principle | limitation | comparison | application | bias | tension | insight
            "framework",     # primary framework discussed e.g. JTBD, OKR, disruptive_innovation
            "related_to",    # comma-separated related frameworks e.g. "personas,crossing_the_chasm"
            "source",        # article/book title
            "author",        # who wrote/analysed it
            "domain",        # pm | strategy | consulting | innovation | business | general
            "applicability", # when to apply: B2B | B2C | startup | enterprise | high_consideration | any
            "importance"     # high | medium | low
        ]
        # This collection is for ANALYTICAL knowledge, not just reference.
        # Use when: agent role definition, consulting work, PM analysis, strategic thinking
        # Retrieval: semantic search by concept — "where does JTBD break?" pulls limitations chunk
    }
}
