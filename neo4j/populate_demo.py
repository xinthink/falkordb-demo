"""
Neo4j Server Demo - Movie Graph Database

Adapted from https://github.com/xinthink/falkordb-demo
Uses the Neo4j Python driver against a Docker-hosted instance.
Same movies dataset and demo stages as the FalkorDB variants.

Usage:
    python populate_demo.py              # Populate and run demo queries
    python populate_demo.py --reset      # Drop existing data first
"""

import argparse
from neo4j import GraphDatabase

BOLT_URI = "bolt://localhost:7687"
AUTH = ("neo4j", "movies_demo")


def print_section(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print("=" * 60)


def print_query_result(cypher: str, records) -> None:
    print(f"\nCypher: {cypher}")
    print("Results:")
    for record in records:
        print(f"  {dict(record)}")


def run_query(driver, cypher):
    """Execute a write query and return records."""
    with driver.session() as session:
        result = session.run(cypher)
        return [record for record in result]


def populate_movies_graph(driver) -> None:
    print_section("Populating Movies Graph")

    cypher = """
    CREATE
      (matrix:Movie {title: 'The Matrix', released: 1999, tagline: 'Welcome to the Real World'}),
      (johnWick:Movie {title: 'John Wick', released: 2014, tagline: 'Don\\'t set him off'}),
      (cloudAtlas:Movie {title: 'Cloud Atlas', released: 2012, tagline: 'Everything is connected'}),

      (keanu:Person {name: 'Keanu Reeves', born: 1964}),
      (carrie:Person {name: 'Carrie-Anne Moss', born: 1967}),
      (laurence:Person {name: 'Laurence Fishburne', born: 1961}),
      (hugo:Person {name: 'Hugo Weaving', born: 1960}),
      (lily:Person {name: 'Lilly Wachowski', born: 1967}),
      (lana:Person {name: 'Lana Wachowski', born: 1965}),
      (chad:Person {name: 'Chad Stahelski', born: 1968}),

      (keanu)-[:ACTED_IN {roles: ['Neo']}]->(matrix),
      (carrie)-[:ACTED_IN {roles: ['Trinity']}]->(matrix),
      (laurence)-[:ACTED_IN {roles: ['Morpheus']}]->(matrix),
      (hugo)-[:ACTED_IN {roles: ['Agent Smith']}]->(matrix),
      (keanu)-[:ACTED_IN {roles: ['John Wick']}]->(johnWick),
      (hugo)-[:ACTED_IN {roles: ['Bill Smoke', 'Haskell Moore']}]->(cloudAtlas),

      (lily)-[:DIRECTED]->(matrix),
      (lana)-[:DIRECTED]->(matrix),
      (chad)-[:DIRECTED]->(johnWick),
      (lily)-[:DIRECTED]->(cloudAtlas),
      (lana)-[:DIRECTED]->(cloudAtlas),

      (keanu)-[:WORKED_WITH]->(chad)

    RETURN 'Graph populated successfully' AS result
    """

    records = run_query(driver, cypher)
    print(f"  {records[0]['result']}")

    count_movies = run_query(driver, "MATCH (m:Movie) RETURN count(m) AS count")
    count_people = run_query(driver, "MATCH (p:Person) RETURN count(p) AS count")
    count_relations = run_query(driver, "MATCH ()-[r]->() RETURN count(r) AS count")

    print(f"\n  Summary:")
    print(f"    Movies: {count_movies[0]['count']}")
    print(f"    People: {count_people[0]['count']}")
    print(f"    Relationships: {count_relations[0]['count']}")


def demo_basic_queries(driver) -> None:
    print_section("Stage 1: Basic Queries (MATCH & RETURN)")

    cypher = "MATCH (p:Person) WHERE p.born > 1965 RETURN p.name, p.born"
    records = run_query(driver, cypher)
    print_query_result(cypher, records)

    cypher = "MATCH (m:Movie {title: 'The Matrix'}) RETURN m.title, m.released, m.tagline"
    records = run_query(driver, cypher)
    print_query_result(cypher, records)


def demo_pattern_queries(driver) -> None:
    print_section("Stage 2: Pattern Queries (Relationships)")

    cypher = "MATCH (p:Person {name: 'Keanu Reeves'})-[:ACTED_IN]->(m:Movie) RETURN m.title, m.released"
    records = run_query(driver, cypher)
    print_query_result(cypher, records)

    cypher = """
    MATCH (p:Person)-[:DIRECTED]->(:Movie {title: 'The Matrix'})
    MATCH (p)-[:DIRECTED]->(:Movie {title: 'Cloud Atlas'})
    RETURN p.name
    """
    records = run_query(driver, cypher)
    print_query_result(cypher, records)


def demo_aggregation(driver) -> None:
    print_section("Stage 3: Aggregation & Ordering")

    cypher = """
    MATCH (p:Person)-[:ACTED_IN|DIRECTED]->(m:Movie)
    RETURN p.name, count(m) AS movieCount
    ORDER BY movieCount DESC
    """
    records = run_query(driver, cypher)
    print_query_result(cypher, records)


def demo_data_modification(driver) -> None:
    print_section("Stage 4: Data Modification (SET & MERGE)")

    cypher = "MATCH (p:Person {name: 'Keanu Reeves'}) SET p:Star RETURN p.name, labels(p) AS labels"
    records = run_query(driver, cypher)
    print_query_result(cypher, records)

    cypher = """
    MATCH (l:Person {name: 'Laurence Fishburne'}), (k:Person {name: 'Keanu Reeves'})
    MERGE (l)-[r:FRIEND_OF]->(k)
    RETURN l.name, type(r) AS relationship, k.name
    """
    records = run_query(driver, cypher)
    print_query_result(cypher, records)


def demo_advanced_queries(driver) -> None:
    print_section("Bonus: Advanced Graph Queries")

    cypher = """
    MATCH (p1:Person)-[:ACTED_IN]->(m:Movie)<-[:ACTED_IN]-(p2:Person)
    WHERE p1.name < p2.name
    RETURN p1.name, p2.name, m.title
    ORDER BY p1.name, p2.name
    """
    records = run_query(driver, cypher)
    print_query_result("Find co-actors:", records)

    cypher = """
    MATCH (p:Person {name: 'Keanu Reeves'})-[r]-(related)
    RETURN p.name, type(r) AS relationship, related.name AS relatedPerson
    """
    records = run_query(driver, cypher)
    print_query_result("Keanu Reeves network:", records)


def main() -> None:
    parser = argparse.ArgumentParser(description="Neo4j Server Demo - Movies Graph")
    parser.add_argument("-r", "--reset", action="store_true", help="Reset graph data before populating")
    args = parser.parse_args()

    print_section("Neo4j Server Movies Demo")
    print(f"\n  Connecting to {BOLT_URI}...")

    driver = GraphDatabase.driver(BOLT_URI, auth=AUTH)
    driver.verify_connectivity()
    print("  Connected.")

    existing = run_query(driver, "MATCH (n) RETURN count(n) AS count LIMIT 1")
    node_count = existing[0]["count"] if existing else 0

    if node_count > 0:
        print(f"\n  Existing graph found with {node_count} nodes.")
        if args.reset:
            print("  --reset: Deleting existing data...")
            run_query(driver, "MATCH (n) DETACH DELETE n")
            populate_movies_graph(driver)
        else:
            print("  Use --reset to start fresh. Proceeding with existing data.")
    else:
        populate_movies_graph(driver)

    demo_basic_queries(driver)
    demo_pattern_queries(driver)
    demo_aggregation(driver)
    demo_data_modification(driver)
    demo_advanced_queries(driver)

    driver.close()

    print_section("Demo Complete")
    print(f"\n  Data persists in Neo4j. Open http://localhost:7474 to explore it.")
    print("  To reset: python populate_demo.py --reset")


if __name__ == "__main__":
    main()
