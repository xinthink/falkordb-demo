# Neo4j Server Demo — Docker + Persistence

A **Neo4j** variant of the FalkorDB movies graph demo. Runs Neo4j as a Docker container with the Browser UI at `http://localhost:7474` and data persisted via bind mount. Uses the same movies dataset and Cypher queries to demonstrate graph database portability.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (with `docker compose`)
- Python 3.8+
- `pip`

## Quick Start

```bash
# 1. Start Neo4j
docker compose up -d

# 2. Install Python driver
pip install neo4j

# 3. Populate the movies graph and run demo queries
python populate_demo.py
```

Open **http://localhost:7474** to explore the graph visually. Sign in with:
- Username: `neo4j`
- Password: `movies_demo`

Then try:

```cypher
MATCH (p:Person)-[:ACTED_IN]->(m:Movie) RETURN p.name, m.title
```

## Reset Data

```bash
python populate_demo.py --reset
```

## Stop & Clean Up

```bash
docker compose down           # stops/removes container, data persists in ./neo4j-data
docker compose down -v        # also removes anonymous volumes
rm -rf neo4j-data/            # wipe persisted data
```

## Data Persistence

The `docker-compose.yml` mounts `./neo4j-data` to `/data` inside the container. Neo4j writes transaction logs and store files here, so data survives `docker compose restart`.

## Neo4j vs FalkorDB Server

| Aspect | FalkorDB Server | Neo4j |
|--------|----------------|-------|
| Protocol | Redis (6379) | Bolt (7687) |
| Browser UI | `http://localhost:3000` | `http://localhost:7474` |
| Python driver | `falkordb` | `neo4j` |
| Auth | Redis password | Username + password |
| Query language | OpenCypher | Cypher (with extensions) |
| Dataset | Same | Same |
| Cypher compatibility | Full | Full |

## Cypher Compatibility Notes

The demo queries are standard Cypher and work on both FalkorDB and Neo4j without changes. Key compatible patterns:
- `CREATE` with comma-separated patterns
- `MATCH ... WHERE ... RETURN`
- `MATCH` with relationship types (`[:ACTED_IN]`)
- `MERGE` for idempotent relationship creation
- `SET` for adding labels
- `count()`, `ORDER BY`, `DETACH DELETE`
