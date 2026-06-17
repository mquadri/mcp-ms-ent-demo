"""SQLite persistence for investigations, topology, and recommendations."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from .models import Investigation, Recommendation, TopologyEdge, TopologyNode, utc_now_iso


DEFAULT_DB_PATH = Path("agents/.data/phase2_devops_agent.db")


class AgentStore:
    def __init__(self, db_path: str | Path = DEFAULT_DB_PATH) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                create table if not exists investigations (
                    id text primary key,
                    status text not null,
                    severity text not null,
                    payload_json text not null,
                    created_at text not null,
                    updated_at text not null
                );

                create table if not exists investigation_events (
                    id integer primary key autoincrement,
                    investigation_id text not null,
                    event_type text not null,
                    payload_json text not null,
                    created_at text not null,
                    foreign key (investigation_id) references investigations(id)
                );

                create table if not exists topology_nodes (
                    node_id text primary key,
                    kind text not null,
                    name text not null,
                    payload_json text not null,
                    updated_at text not null
                );

                create table if not exists topology_edges (
                    source text not null,
                    target text not null,
                    relationship text not null,
                    updated_at text not null,
                    primary key (source, target, relationship)
                );

                create table if not exists recommendations (
                    id text primary key,
                    priority integer not null,
                    area text not null,
                    payload_json text not null,
                    created_at text not null
                );
                """
            )

    def save_investigation(self, investigation: Investigation) -> None:
        now = utc_now_iso()
        investigation.updated_at = now
        with self._connect() as conn:
            conn.execute(
                """
                insert into investigations (id, status, severity, payload_json, created_at, updated_at)
                values (?, ?, ?, ?, ?, ?)
                on conflict(id) do update set
                    status=excluded.status,
                    severity=excluded.severity,
                    payload_json=excluded.payload_json,
                    updated_at=excluded.updated_at
                """,
                (
                    investigation.investigation_id,
                    investigation.status,
                    investigation.severity,
                    json.dumps(investigation.to_dict(), indent=2),
                    investigation.created_at,
                    investigation.updated_at,
                ),
            )

    def add_event(self, investigation_id: str, event_type: str, payload: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                insert into investigation_events (investigation_id, event_type, payload_json, created_at)
                values (?, ?, ?, ?)
                """,
                (investigation_id, event_type, json.dumps(payload, indent=2), utc_now_iso()),
            )

    def save_topology(self, nodes: list[TopologyNode], edges: list[TopologyEdge]) -> None:
        now = utc_now_iso()
        with self._connect() as conn:
            for node in nodes:
                conn.execute(
                    """
                    insert into topology_nodes (node_id, kind, name, payload_json, updated_at)
                    values (?, ?, ?, ?, ?)
                    on conflict(node_id) do update set
                        kind=excluded.kind,
                        name=excluded.name,
                        payload_json=excluded.payload_json,
                        updated_at=excluded.updated_at
                    """,
                    (node.node_id, node.kind, node.name, json.dumps(node.to_dict(), indent=2), now),
                )
            for edge in edges:
                conn.execute(
                    """
                    insert into topology_edges (source, target, relationship, updated_at)
                    values (?, ?, ?, ?)
                    on conflict(source, target, relationship) do update set
                        updated_at=excluded.updated_at
                    """,
                    (edge.source, edge.target, edge.relationship, now),
                )

    def save_recommendations(self, recommendations: list[Recommendation]) -> None:
        with self._connect() as conn:
            for rec in recommendations:
                conn.execute(
                    """
                    insert into recommendations (id, priority, area, payload_json, created_at)
                    values (?, ?, ?, ?, ?)
                    on conflict(id) do update set
                        priority=excluded.priority,
                        area=excluded.area,
                        payload_json=excluded.payload_json
                    """,
                    (
                        rec.recommendation_id,
                        rec.priority,
                        rec.area,
                        json.dumps(rec.to_dict(), indent=2),
                        rec.created_at,
                    ),
                )

    def load_recent_investigations(self, limit: int = 20) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "select payload_json from investigations order by updated_at desc limit ?",
                (limit,),
            ).fetchall()
        return [json.loads(row["payload_json"]) for row in rows]

    def summary(self) -> dict[str, int | str]:
        with self._connect() as conn:
            investigations = conn.execute("select count(*) as count from investigations").fetchone()["count"]
            events = conn.execute("select count(*) as count from investigation_events").fetchone()["count"]
            nodes = conn.execute("select count(*) as count from topology_nodes").fetchone()["count"]
            edges = conn.execute("select count(*) as count from topology_edges").fetchone()["count"]
            recommendations = conn.execute("select count(*) as count from recommendations").fetchone()["count"]
        return {
            "db_path": str(self.db_path),
            "investigations": investigations,
            "events": events,
            "topology_nodes": nodes,
            "topology_edges": edges,
            "recommendations": recommendations,
        }
