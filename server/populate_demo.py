"""
FalkorDB Server Demo - Movie Graph Database

Adapted from https://github.com/xinthink/falkordb-demo
Uses the FalkorDB server client (not embedded Lite) against a Docker-hosted instance.

Usage:
    python populate_demo.py              # Populate and run demo queries
    python populate_demo.py --reset      # Drop existing data first
"""

import argparse
from falkordb import FalkorDB

DB_HOST = "localhost"
DB_PORT = 6379
GRAPH_NAME = "movies"


def print_section(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print("=" * 60)


def print_query_result(cypher: str, result) -> None:
    print(f"\nCypher: {cypher}")
    print("Results:")
    for row in result.result_set:
        print(f"  {row}")


def populate_movies_graph(graph) -> None:
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

    result = graph.query(cypher)
    print(f"  {result.result_set[0][0]}")

    count_movies = graph.query("MATCH (m:Movie) RETURN count(m) AS count")
    count_people = graph.query("MATCH (p:Person) RETURN count(p) AS count")
    count_relations = graph.query("MATCH ()-[r]->() RETURN count(r) AS count")

    print(f"\n  Summary:")
    print(f"    Movies: {count_movies.result_set[0][0]}")
    print(f"    People: {count_people.result_set[0][0]}")
    print(f"    Relationships: {count_relations.result_set[0][0]}")


def demo_basic_queries(graph) -> None:
    print_section("Stage 1: Basic Queries (MATCH & RETURN)")

    cypher = "MATCH (p:Person) WHERE p.born > 1965 RETURN p.name, p.born"
    result = graph.query(cypher)
    print_query_result(cypher, result)

    cypher = "MATCH (m:Movie {title: 'The Matrix'}) RETURN m.title, m.released, m.tagline"
    result = graph.query(cypher)
    print_query_result(cypher, result)


def demo_pattern_queries(graph) -> None:
    print_section("Stage 2: Pattern Queries (Relationships)")

    cypher = "MATCH (p:Person {name: 'Keanu Reeves'})-[:ACTED_IN]->(m:Movie) RETURN m.title, m.released"
    result = graph.query(cypher)
    print_query_result(cypher, result)

    cypher = """
    MATCH (p:Person)-[:DIRECTED]->(:Movie {title: 'The Matrix'})
    MATCH (p)-[:DIRECTED]->(:Movie {title: 'Cloud Atlas'})
    RETURN p.name
    """
    result = graph.query(cypher)
    print_query_result(cypher, result)


def demo_aggregation(graph) -> None:
    print_section("Stage 3: Aggregation & Ordering")

    cypher = """
    MATCH (p:Person)-[:ACTED_IN|DIRECTED]->(m:Movie)
    RETURN p.name, count(m) AS movieCount
    ORDER BY movieCount DESC
    """
    result = graph.query(cypher)
    print_query_result(cypher, result)


def demo_data_modification(graph) -> None:
    print_section("Stage 4: Data Modification (SET & MERGE)")

    cypher = "MATCH (p:Person {name: 'Keanu Reeves'}) SET p:Star RETURN p.name, labels(p) AS labels"
    result = graph.query(cypher)
    print_query_result(cypher, result)

    cypher = """
    MATCH (l:Person {name: 'Laurence Fishburne'}), (k:Person {name: 'Keanu Reeves'})
    MERGE (l)-[r:FRIEND_OF]->(k)
    RETURN l.name, type(r) AS relationship, k.name
    """
    result = graph.query(cypher)
    print_query_result(cypher, result)


def demo_advanced_queries(graph) -> None:
    print_section("Bonus: Advanced Graph Queries")

    cypher = """
    MATCH (p1:Person)-[:ACTED_IN]->(m:Movie)<-[:ACTED_IN]-(p2:Person)
    WHERE p1.name < p2.name
    RETURN p1.name, 'co-acted with', p2.name, 'in', m.title
    ORDER BY p1.name, p2.name
    """
    result = graph.query(cypher)
    print_query_result("Find co-actors:", result)

    cypher = """
    MATCH (p:Person {name: 'Keanu Reeves'})-[r]-(related)
    RETURN p.name, type(r) AS relationship, related.name AS relatedPerson
    """
    result = graph.query(cypher)
    print_query_result("Keanu Reeves network:", result)


def main() -> None:
    parser = argparse.ArgumentParser(description="FalkorDB Server Demo - Movies Graph")
    parser.add_argument("-r", "--reset", action="store_true", help="Reset graph data before populating")
    args = parser.parse_args()

    print_section("FalkorDB Server Movies Demo")
    print(f"\n  Connecting to {DB_HOST}:{DB_PORT}...")
    db = FalkorDB(host=DB_HOST, port=DB_PORT)
    graph = db.select_graph(GRAPH_NAME)
    print(f"  Graph: {GRAPH_NAME}")

    existing = graph.query("MATCH (n) RETURN count(n) AS count LIMIT 1")
    node_count = existing.result_set[0][0] if existing.result_set else 0

    if node_count > 0:
        print(f"\n  Existing graph found with {node_count} nodes.")
        if args.reset:
            print("  --reset: Deleting existing data...")
            graph.query("MATCH (n) DETACH DELETE n")
            populate_movies_graph(graph)
        else:
            print("  Use --reset to start fresh. Proceeding with existing data.")
    else:
        populate_movies_graph(graph)

    demo_basic_queries(graph)
    demo_pattern_queries(graph)
    demo_aggregation(graph)
    demo_data_modification(graph)
    demo_advanced_queries(graph)

    print_section("Demo Complete")
    print(f"\n  Data persists in FalkorDB. Open http://localhost:3000 to explore it.")
    print("  To reset: python populate_demo.py --reset")


if __name__ == "__main__":
    main()
