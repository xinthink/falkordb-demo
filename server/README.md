# FalkorDB Server Demo — Docker + Persistence

A **server-based** variant of the FalkorDB movies graph demo. Unlike the Lite version (embedded, single-file database), this runs FalkorDB as a Docker container with the Browser UI at `http://localhost:3000` and data persisted via bind mount + AOF.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (with `docker compose`)
- Python 3.8+ (no `uv` required)
- `pip`

## Quick Start

```bash
# 1. Start FalkorDB server + browser
docker compose up -d

# 2. Install Python client
pip install falkordb

# 3. Populate the movies graph and run demo queries
python populate_demo.py
```

Open **http://localhost:3000** to explore the graph visually. Select the `movies` graph and try:

```cypher
MATCH (p:Person)-[:ACTED_IN]->(m:Movie) RETURN p.name, m.title
```

## Reset Data

```bash
python populate_demo.py --reset
```

## Stop & Clean Up

```bash
docker compose down           # stops/removes container, data persists in ./falkordb-data
docker compose down -v        # also removes anonymous volumes
rm -rf falkordb-data/         # wipe persisted data
```

## Data Persistence

The `docker-compose.yml` uses two mechanisms to survive restarts:

| Mechanism | How |
|-----------|-----|
| **Bind mount** | `./falkordb-data` on host → `/var/lib/falkordb/data` in container |
| **AOF** | `REDIS_ARGS=--appendonly yes` logs every write, replayed on restart |

After `docker compose restart`, all graph data is intact.

### AOF files on host

```
falkordb-data/
  appendonlydir/
    appendonly.aof.1.base.rdb     # base snapshot
    appendonly.aof.1.incr.aof     # incremental writes
    appendonly.aof.manifest
```

## Server vs Lite

| Aspect | Lite (`main.py`) | Server (`server/`) |
|--------|------------------|--------------------|
| Database | Embedded, file-based (`falkordb_demo.db`) | Docker container (Redis + FalkorDB module) |
| Browser UI | Not available | `http://localhost:3000` |
| Python client | `falkordblite` | `falkordb` |
| Persistence | Local `.db` file | AOF files via bind mount |
| Python version | 3.13+ | 3.8+ |
