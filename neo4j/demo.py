"""
Neo4j Python Query Demo

Demonstrates core Neo4j Python driver query patterns:
  - Connecting & verifying connectivity
  - Reading data (MATCH ... RETURN) — iteration, dict, single
  - Parameterized queries to prevent injection
  - Updating nodes (SET)
  - Upsert with MERGE
  - Transaction management (explicit commit/rollback)
  - Clean shutdown

Prerequisite: run populate_demo.py first to load the movies dataset.

Usage:
    python demo.py
"""

from neo4j import GraphDatabase

BOLT_URI = "bolt://localhost:7687"
AUTH = ("neo4j", "movies_demo")


# ─── 1. Connection ──────────────────────────────────────────

def connect():
    """Create and verify a driver connection."""
    driver = GraphDatabase.driver(BOLT_URI, auth=AUTH)
    driver.verify_connectivity()
    print(f"Connected to {BOLT_URI}")
    return driver


# ─── 2. Reading data ────────────────────────────────────────

def read_examples(driver):
    """Demonstrate different ways to consume query results."""
    with driver.session() as session:
        # Iterate over all records
        print("\n── All movies:")
        result = session.run("MATCH (m:Movie) RETURN m.title, m.released")
        for record in result:
            print(f"  {record['m.title']} ({record['m.released']})")

        # Access as dict
        print("\n── As dict:")
        result = session.run("MATCH (p:Person) RETURN p.name, p.born")
        for record in result:
            print(f"  {dict(record)}")

        # Single record
        print("\n── Single record:")
        result = session.run(
            "MATCH (p:Person {name: 'Keanu Reeves'}) RETURN p"
        )
        single = result.single()
        if single:
            print(f"  {single['p']}")  # Neo4j Node object
        else:
            print("  (no match — run populate_demo.py first)")


# ─── 3. Pattern matching through relationships ──────────────

def pattern_queries(driver):
    """Traverse relationships in Cypher."""
    print("\n── Keanu's movies:")
    with driver.session() as session:
        result = session.run(
            "MATCH (p:Person {name: 'Keanu Reeves'})-[:ACTED_IN]->(m:Movie) "
            "RETURN m.title, m.released"
        )
        for record in result:
            print(f"  {record['m.title']} ({record['m.released']})")


# ─── 4. Parameterized queries ───────────────────────────────

def parameterized_example(driver):
    """Use $parameters to prevent Cypher injection."""
    with driver.session() as session:
        # Never string-format user input into Cypher!
        # ✅ CORRECT — use $parameters:
        print("\n── Parameterized (born > $year):")
        result = session.run(
            "MATCH (p:Person) WHERE p.born > $year "
            "RETURN p.name, p.born ORDER BY p.born",
            year=1965,
        )
        for record in result:
            print(f"  {record['p.name']} ({record['p.born']})")

        # Dict-style params:
        print("\n── Dict params (name = $name):")
        result = session.run(
            "MATCH (p:Person {name: $name})-[:DIRECTED]->(m:Movie) "
            "RETURN m.title",
            {"name": "Lana Wachowski"},
        )
        for record in result:
            print(f"  {record['m.title']}")


# ─── 5. Updating nodes (SET) ────────────────────────────────

def update_example(driver):
    """Add a property and label, then verify."""
    with driver.session() as session:
        session.run(
            "MATCH (p:Person {name: $name}) SET p.rating = $rating",
            name="Keanu Reeves", rating="★",
        )
        print("\n── After SET rating:")
        result = session.run(
            "MATCH (p:Person {name: 'Keanu Reeves'}) "
            "RETURN p.name, p.rating, labels(p) AS labels"
        )
        for r in result:
            print(f"  {r['p.name']}: rating={r['p.rating']}, labels={r['labels']}")


# ─── 6. Upsert with MERGE ───────────────────────────────────

def merge_example(driver):
    """MERGE creates only if not already present (idempotent)."""
    with driver.session() as session:
        # MERGE a node
        session.run(
            "MERGE (p:Person {name: $name}) "
            "ON CREATE SET p.born = $born "
            "ON MATCH SET p.last_seen = $ts",
            name="Morpheus", born=1972, ts="2026-06",
        )
        # MERGE a relationship
        session.run(
            "MATCH (m:Person {name: 'Morpheus'}), "
            "      (k:Person {name: 'Keanu Reeves'}) "
            "MERGE (m)-[:KNOWS]->(k)",
        )
        print("\n── After MERGE (Morpheus):")
        result = session.run("MATCH (p:Person {name: 'Morpheus'}) RETURN p")
        for r in result:
            print(f"  {dict(r['p'])}")


# ─── 7. Transaction management ──────────────────────────────

def transaction_example(driver):
    """Explicit write transaction — atomic multi-statement."""
    print("\n── Write transaction:")
    with driver.session() as session:
        tx = session.begin_transaction()
        try:
            tx.run("CREATE (n:Note {content: 'tx note 1'})")
            tx.run("CREATE (n:Note {content: 'tx note 2'})")
            tx.commit()
            print("  Committed 2 notes atomically")
        except Exception as e:
            tx.rollback()
            print(f"  Rolled back: {e}")

    # Read-back
    with driver.session() as session:
        tx = session.begin_transaction()
        result = tx.run("MATCH (n:Note) RETURN n.content")
        for r in result:
            print(f"  Note: {r['n.content']}")
        tx.commit()

    # Cleanup
    with driver.session() as session:
        session.run("MATCH (n:Note) DETACH DELETE n")
        print("  Deleted all Note nodes")


# ─── Main ──────────────────────────────────────────────────

def main():
    driver = connect()
    try:
        read_examples(driver)
        pattern_queries(driver)
        parameterized_example(driver)
        update_example(driver)
        merge_example(driver)
        transaction_example(driver)

        print(f"\nDone. Open http://localhost:7474 to explore the graph.")
    finally:
        driver.close()
        print("Connection closed.")


if __name__ == "__main__":
    main()
