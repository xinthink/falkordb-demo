"""
FalkorDB Lite Demo - Movies Graph Database

This script demonstrates graph database operations using FalkorDB Lite
with a movies dataset (Person/Movie nodes and their relationships).

Usage:
    python main.py                 # Run demo (skip if data exists)
    python main.py --reset         # Reset graph and repopulate with fresh data
    python main.py -r              # Short form for --reset
    python main.py --cleanup       # Run demo and auto-cleanup
    python main.py -c              # Short form for --cleanup
"""

import argparse
from redislite.falkordb_client import FalkorDB

# Configuration
DB_PATH = "falkordb_demo.db"
GRAPH_NAME = "movies"


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def print_query_result(cypher: str, result) -> None:
    """Print query results in a formatted way."""
    print(f"\nCypher: {cypher}")
    print(f"Results:")
    for row in result.result_set:
        print(f"  {row}")


def populate_movies_graph(graph) -> None:
    """
    Populate the graph with movies data.

    Creates:
    - 3 Movie nodes: The Matrix, John Wick, Cloud Atlas
    - 7 Person nodes with their birth years
    - ACTED_IN relationships with roles
    - DIRECTED relationships
    - WORKED_WITH relationships
    """
    print_section("Populating Movies Graph")

    # Create all nodes and relationships in a single CREATE statement
    # This is more efficient and avoids Cypher WITH clause issues
    cypher = """
    CREATE
      // Movie nodes
      (matrix:Movie {title: 'The Matrix', released: 1999, tagline: 'Welcome to the Real World'}),
      (johnWick:Movie {title: 'John Wick', released: 2014, tagline: 'Don\\'t set him off'}),
      (cloudAtlas:Movie {title: 'Cloud Atlas', released: 2012, tagline: 'Everything is connected'}),

      // Person nodes
      (keanu:Person {name: 'Keanu Reeves', born: 1964}),
      (carrie:Person {name: 'Carrie-Anne Moss', born: 1967}),
      (laurence:Person {name: 'Laurence Fishburne', born: 1961}),
      (hugo:Person {name: 'Hugo Weaving', born: 1960}),
      (lily:Person {name: 'Lilly Wachowski', born: 1967}),
      (lana:Person {name: 'Lana Wachowski', born: 1965}),
      (chad:Person {name: 'Chad Stahelski', born: 1968}),

      // ACTED_IN relationships
      (keanu)-[:ACTED_IN {roles: ['Neo']}]->(matrix),
      (carrie)-[:ACTED_IN {roles: ['Trinity']}]->(matrix),
      (laurence)-[:ACTED_IN {roles: ['Morpheus']}]->(matrix),
      (hugo)-[:ACTED_IN {roles: ['Agent Smith']}]->(matrix),
      (keanu)-[:ACTED_IN {roles: ['John Wick']}]->(johnWick),
      (hugo)-[:ACTED_IN {roles: ['Bill Smoke', 'Haskell Moore']}]->(cloudAtlas),

      // DIRECTED relationships
      (lily)-[:DIRECTED]->(matrix),
      (lana)-[:DIRECTED]->(matrix),
      (chad)-[:DIRECTED]->(johnWick),
      (lily)-[:DIRECTED]->(cloudAtlas),
      (lana)-[:DIRECTED]->(cloudAtlas),

      // WORKED_WITH relationship
      (keanu)-[:WORKED_WITH]->(chad)

    RETURN 'Graph populated successfully' AS result
    """

    result = graph.query(cypher)
    print(f"  {result.result_set[0][0]}")

    # Show summary
    count_movies = graph.query("MATCH (m:Movie) RETURN count(m) AS count")
    count_people = graph.query("MATCH (p:Person) RETURN count(p) AS count")
    count_relations = graph.query("MATCH ()-[r]->() RETURN count(r) AS count")

    print(f"\n  Summary:")
    print(f"    Movies: {count_movies.result_set[0][0]}")
    print(f"    People: {count_people.result_set[0][0]}")
    print(f"    Relationships: {count_relations.result_set[0][0]}")


def demo_basic_queries(graph) -> None:
    """
    Stage 1: Basic MATCH & RETURN queries.

    Demonstrates:
    - Finding nodes with WHERE clause
    - Finding nodes by property value
    """
    print_section("Stage 1: Basic Queries (MATCH & RETURN)")

    # Exercise 1: Find people born after 1965
    cypher = "MATCH (p:Person) WHERE p.born > 1965 RETURN p.name, p.born"
    result = graph.query(cypher)
    print_query_result(cypher, result)

    # Exercise 2: Find movie by title
    cypher = "MATCH (m:Movie {title: 'The Matrix'}) RETURN m.title, m.released, m.tagline"
    result = graph.query(cypher)
    print_query_result(cypher, result)


def demo_pattern_queries(graph) -> None:
    """
    Stage 2: Pattern matching with relationships.

    Demonstrates:
    - Finding related nodes through relationships
    - Finding common patterns across paths
    """
    print_section("Stage 2: Pattern Queries (Relationships)")

    # Exercise 3: Find Keanu Reeves' movies
    cypher = "MATCH (p:Person {name: 'Keanu Reeves'})-[:ACTED_IN]->(m:Movie) RETURN m.title, m.released"
    result = graph.query(cypher)
    print_query_result(cypher, result)

    # Exercise 4: Find directors of both The Matrix and Cloud Atlas
    cypher = """
    MATCH (p:Person)-[:DIRECTED]->(:Movie {title: 'The Matrix'})
    MATCH (p)-[:DIRECTED]->(:Movie {title: 'Cloud Atlas'})
    RETURN p.name
    """
    result = graph.query(cypher)
    print_query_result(cypher, result)


def demo_aggregation(graph) -> None:
    """
    Stage 3: Aggregation and ordering.

    Demonstrates:
    - COUNT() aggregation
    - ORDER BY for sorting
    - Multiple relationship types in one query
    """
    print_section("Stage 3: Aggregation & Ordering")

    # Exercise 5: Count movies per person, ordered by count DESC
    cypher = """
    MATCH (p:Person)-[:ACTED_IN|DIRECTED]->(m:Movie)
    RETURN p.name, count(m) AS movieCount
    ORDER BY movieCount DESC
    """
    result = graph.query(cypher)
    print_query_result(cypher, result)


def demo_data_modification(graph) -> None:
    """
    Stage 4: Data modification operations.

    Demonstrates:
    - SET: Adding labels to existing nodes
    - MERGE: Creating relationships only if they don't exist
    """
    print_section("Stage 4: Data Modification (SET & MERGE)")

    # Exercise 6: Add Star label to Keanu Reeves
    cypher = "MATCH (p:Person {name: 'Keanu Reeves'}) SET p:Star RETURN p.name, labels(p) AS labels"
    result = graph.query(cypher)
    print_query_result(cypher, result)

    # Verify the Star label was added
    cypher_verify = "MATCH (p:Star) RETURN p.name, labels(p)"
    result_verify = graph.query(cypher_verify)
    print_query_result("Verify Star label:", result_verify)

    # Exercise 7: Create FRIEND_OF relationship (using MERGE to avoid duplicates)
    cypher = """
    MATCH (l:Person {name: 'Laurence Fishburne'}), (k:Person {name: 'Keanu Reeves'})
    MERGE (l)-[r:FRIEND_OF]->(k)
    RETURN l.name, type(r) AS relationship, k.name
    """
    result = graph.query(cypher)
    print_query_result(cypher, result)


def demo_additional_queries(graph) -> None:
    """
    Additional interesting queries to demonstrate graph capabilities.

    Demonstrates:
    - Path queries with variable length
    - Shortest path
    - Complex pattern matching
    """
    print_section("Bonus: Advanced Graph Queries")

    # Find all co-actors (people who acted in the same movie)
    cypher = """
    MATCH (p1:Person)-[:ACTED_IN]->(m:Movie)<-[:ACTED_IN]-(p2:Person)
    WHERE p1.name < p2.name
    RETURN p1.name, 'co-acted with', p2.name, 'in', m.title
    ORDER BY p1.name, p2.name
    """
    result = graph.query(cypher)
    print_query_result("Find co-actors:", result)

    # Find the complete network around Keanu Reeves
    cypher = """
    MATCH (p:Person {name: 'Keanu Reeves'})-[r]-(related)
    RETURN p.name, type(r) AS relationship, related.name AS relatedPerson
    """
    result = graph.query(cypher)
    print_query_result("Keanu Reeves network:", result)


def cleanup_graph(graph) -> None:
    """
    Clean up all data from the graph.

    Args:
        graph: The FalkorDB graph instance

    WARNING: This will delete all nodes and relationships.
    """
    print_section("Cleanup: Deleting All Data")
    cypher = "MATCH (n) DETACH DELETE n"
    graph.query(cypher)
    print("  All data deleted from graph.")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="FalkorDB Lite Demo - Movies Graph Database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py              Run demo
  python main.py --reset      Reset graph and repopulate with fresh data
  python main.py -r           Short form for --reset
  python main.py --cleanup    Cleanup database after demo
  python main.py -c           Short form for --cleanup
        """
    )
    parser.add_argument(
        "-r", "--reset",
        action="store_true",
        help="Reset graph and repopulate with fresh data"
    )
    parser.add_argument(
        "-c", "--cleanup",
        action="store_true",
        help="Automatically cleanup database after demo"
    )
    return parser.parse_args()


def main() -> None:
    """Main entry point for the FalkorDB Lite demo."""
    args = parse_args()

    print_section("FalkorDB Lite Movies Demo")

    # Initialize FalkorDB Lite
    print(f"\n  Initializing FalkorDB Lite...")
    print(f"  Database path: {DB_PATH}")
    db = FalkorDB(DB_PATH)

    # Select/create the movies graph
    graph = db.select_graph(GRAPH_NAME)
    print(f"  Graph name: {GRAPH_NAME}")

    # Check if graph already has data
    existing = graph.query("MATCH (n) RETURN count(n) AS count LIMIT 1")
    node_count = existing.result_set[0][0] if existing.result_set else 0

    if node_count > 0:
        print(f"\n  Existing graph found with {node_count} nodes.")
        if args.reset:
            print("  --reset: Deleting existing data and starting fresh...")
            graph.query("MATCH (n) DETACH DELETE n")
            populate_movies_graph(graph)
        else:
            print("  Use --reset to start with fresh data.")
            print("  Proceeding with existing data.")
    else:
        populate_movies_graph(graph)

    # Run all demo sections
    demo_basic_queries(graph)
    demo_pattern_queries(graph)
    demo_aggregation(graph)
    demo_data_modification(graph)
    demo_additional_queries(graph)

    # Cleanup if requested
    if args.cleanup:
        cleanup_graph(graph)

    print_section("Demo Complete")
    print(f"\n  Database file: {DB_PATH}")
    if args.cleanup:
        print("  Database cleaned up. Use without --cleanup to persist data.")
    else:
        print("  Data persists between runs - use --cleanup to auto-delete.")


if __name__ == "__main__":
    main()
