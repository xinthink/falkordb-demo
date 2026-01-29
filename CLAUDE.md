# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a single-file Python demo showcasing **FalkorDB Lite**, an embedded graph database. The demo uses a classic movies dataset (Person/Movie nodes with ACTED_IN/DIRECTED/WORKED_WITH relationships) to demonstrate Cypher query patterns.

**Key Technology:** FalkorDB Lite (embedded Redis + FalkorDB module) via `redislite.falkordb_client.FalkorDB`

## Commands

### Installation
```bash
uv sync              # Install dependencies (uses uv)
```

### Running the Demo
```bash
uv run python main.py              # Run demo (skip if data exists)
uv run python main.py --reset      # Reset graph and repopulate with fresh data
uv run python main.py -r           # Short form for --reset
uv run python main.py --cleanup    # Run demo and auto-cleanup
uv run python main.py -c           # Short form for --cleanup
```

### Clean Database
```bash
rm falkordb_demo.db   # Delete the database file to start fresh
```

## Architecture

**Single-file structure:** [`main.py`](main.py) contains all demo logic organized into stage-based functions:

| Function | Purpose |
|----------|---------|
| `populate_movies_graph()` | Creates all nodes (Movie/Person) and relationships in one Cypher CREATE statement |
| `demo_basic_queries()` | MATCH & RETURN patterns (WHERE filtering, property lookups) |
| `demo_pattern_queries()` | Relationship traversal and multi-pattern matching |
| `demo_aggregation()` | COUNT(), ORDER BY operations |
| `demo_data_modification()` | SET (add labels), MERGE (create relationships if not exist) |
| `demo_additional_queries()` | Advanced patterns (co-actors, network exploration) |
| `cleanup_graph()` | DETACH DELETE all nodes |

## Important Configuration

```python
DB_PATH = "falkordb_demo.db"      # Persistent database file location
GRAPH_NAME = "movies"             # Graph key name in FalkorDB
```

## Data Persistence

- Database file **persists between runs** (stored in `falkordb_demo.db`)
- Data is preserved by default (no cleanup unless `--cleanup` flag is used)
- If existing data is found, the script skips population by default
- Use `--reset` flag to force re-population
- Use `--cleanup` flag to auto-delete after demo
- The database is ignored by git (see `.gitignore`)

## Cypher Notes

When creating nodes and relationships in FalkorDB Lite:
- Use a single CREATE statement with comma-separated patterns for efficiency
- Avoid MATCH → CREATE chains without WITH clauses (not supported)
- All variable references must be within the same query scope

## Python Version

**Python 3.13** is required (FalkorDB Lite needs 3.12+, project specifies 3.13). See `.python-version`.
