# FalkorDB Lite Demo - Movies Graph Database

A comprehensive demonstration of FalkorDB Lite graph database operations using a movies dataset (Person/Movie nodes with ACTED_IN/DIRECTED/WORKED_WITH relationships).

> **Server variants**: See [`server/`](server/) for FalkorDB (Docker) or [`neo4j/`](neo4j/) for Neo4j (Docker) — same dataset, same Cypher queries, different engines.

## Overview

This demo showcases the classic "Hello World" of graph databases - a movies dataset featuring:
- **Movie nodes**: The Matrix, John Wick, Cloud Atlas
- **Person nodes**: Actors and directors (Keanu Reeves, Carrie-Anne Moss, etc.)
- **Relationships**: ACTED_IN, DIRECTED, WORKED_WITH

## Prerequisites

- Python 3.13 or higher (FalkorDB Lite requires 3.12+)
- `uv` package manager (recommended) or `pip`

## Installation

### Using uv (recommended)
```bash
uv sync
```

### Using pip
```bash
pip install falkordblite
```

## Usage

### Run with uv (recommended)
```bash
uv run python main.py              # Run demo (skip if data exists)
uv run python main.py --reset      # Reset graph and repopulate with fresh data
uv run python main.py -r           # Short form for --reset
uv run python main.py --cleanup    # Run demo and auto-cleanup
uv run python main.py -c           # Short form for --cleanup
```

### Run with pip
```bash
python main.py                     # Run demo (skip if data exists)
python main.py --reset             # Reset graph and repopulate with fresh data
python main.py -r                  # Short form for --reset
python main.py --cleanup           # Run demo and auto-cleanup
python main.py -c                  # Short form for --cleanup
```

## What the Demo Does

The script walks through 4+ stages of Cypher query patterns:

### Stage 1: Basic Queries (MATCH & RETURN)
- Find people born after 1965
- Find a movie by title

### Stage 2: Pattern Queries (Relationships)
- Find all movies Keanu Reeves acted in
- Find directors who directed both The Matrix and Cloud Atlas

### Stage 3: Aggregation & Ordering
- Count movies per person, ordered by count DESC

### Stage 4: Data Modification (SET & MERGE)
- Add a "Star" label to Keanu Reeves
- Create a FRIEND_OF relationship between Laurence and Keanu

### Bonus: Advanced Queries
- Find co-actors (people who acted in the same movie)
- Explore Keanu Reeves' complete network

## Expected Output

```
============================================================
  FalkorDB Lite Movies Demo
============================================================

  Initializing FalkorDB Lite...
  Database path: falkordb_demo.db
  Graph name: movies

============================================================
  Populating Movies Graph
============================================================

  Nodes created
  Relationships created

  Summary:
    Movies: 3
    People: 7
    Relationships: 12

[... query results for each stage ...]

============================================================
  Demo Complete
============================================================

  Database file: falkordb_demo.db
  Data persists between runs - use --cleanup to auto-delete
```

## Data Persistence

The database is stored in `falkordb_demo.db` and persists between runs. Data is preserved by default - use `--cleanup` flag to auto-delete after the demo.

## Clean Up

To reset the database, delete the `.db` file:
```bash
rm falkordb_demo.db
```

Or run with `--cleanup` to auto-delete after the demo:
```bash
python main.py --cleanup
```

## Resources

- [FalkorDB Lite Documentation](https://docs.falkordb.com/operations/falkordblite.html)
- [Cypher Query Language Reference](https://docs.falkordb.com/operations/cypher.html)
