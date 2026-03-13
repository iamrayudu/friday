"""
Inspect Friday's memory.
Usage:
    python scripts/inspect_memory.py                      # list all collections + counts
    python scripts/inspect_memory.py frameworks           # show all chunks in a collection
    python scripts/inspect_memory.py frameworks "swot"    # search a collection
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from memory.store import list_collections, count, get_all, search

def main():
    args = sys.argv[1:]

    # No args → show overview
    if not args:
        print("\n── Friday Memory Overview ──\n")
        collections = list_collections()
        if not collections:
            print("  No collections yet. Run: python scripts/populate.py")
            return
        for name in collections:
            print(f"  {name:<30} {count(name)} chunks")
        print()
        return

    collection_name = args[0]

    # Collection + search query
    if len(args) == 2:
        query = args[1]
        print(f"\n── Search [{collection_name}] for: '{query}' ──\n")
        results = search(collection_name, query, n=5)
        for i, r in enumerate(results, 1):
            print(f"[{i}] score: {r['score']} | meta: {r['metadata']}")
            print(f"    {r['text'][:200]}...")
            print()
        return

    # Collection only → dump all
    print(f"\n── All chunks in [{collection_name}] ──\n")
    chunks = get_all(collection_name)
    if not chunks:
        print("  Empty.")
        return
    for chunk in chunks:
        print(f"id: {chunk['id']}")
        print(f"meta: {chunk['metadata']}")
        print(f"text: {chunk['text'][:300]}...")
        print("─" * 60)

if __name__ == "__main__":
    main()
