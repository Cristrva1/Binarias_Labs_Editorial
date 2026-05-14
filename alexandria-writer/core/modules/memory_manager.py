#!/usr/bin/env python3
"""
Alexandria Writer — Memory Manager
Sistema de memoria persistente para el proyecto TSBN.
Integra concepts de agentmemory, claude-mem y mempalace.

Uso:
    from modules.memory_manager import MemoryManager
    mem = MemoryManager()
    mem.store("personaje_elena", {"nombre": "Elena", "edad": 32, "motivacion": "..."})
    data = mem.retrieve("personaje_elena")
    related = mem.search("fe y superacion")
"""

import os
import json
import sqlite3
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime


class MemoryManager:
    """
    Gestor de memoria persistente para el proyecto de escritura.
    Usa SQLite + FTS5 para búsqueda de texto + JSON para datos estructurados.
    Inspirado en claude-mem (hybrid search) y agentmemory (knowledge graphs).
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.db_path = self.project_root / "memory" / "alexandria_memory.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Inicializa la base de datos con tablas para memoria, tags y relaciones."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("PRAGMA journal_mode=WAL")

            # Tabla principal de memoria
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    category TEXT NOT NULL,
                    content TEXT NOT NULL,
                    data_json TEXT,
                    tags TEXT,
                    importance REAL DEFAULT 1.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    access_count INTEGER DEFAULT 0
                )
            """)

            # Índice de búsqueda de texto
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
                    key, content, tags,
                    content='memory',
                    content_rowid='id'
                )
            """)

            # Tabla de relaciones (knowledge graph)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS relations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_key TEXT NOT NULL,
                    target_key TEXT NOT NULL,
                    relation_type TEXT NOT NULL,
                    strength REAL DEFAULT 1.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(source_key, target_key, relation_type)
                )
            """)

            # Triggers para mantener FTS sincronizado
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS memory_ai AFTER INSERT ON memory BEGIN
                    INSERT INTO memory_fts(rowid, key, content, tags)
                    VALUES (new.id, new.key, new.content, new.tags);
                END
            """)
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS memory_ad AFTER DELETE ON memory BEGIN
                    INSERT INTO memory_fts(memory_fts, rowid, key, content, tags)
                    VALUES ('delete', old.id, old.key, old.content, old.tags);
                END
            """)
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS memory_au AFTER UPDATE ON memory BEGIN
                    INSERT INTO memory_fts(memory_fts, rowid, key, content, tags)
                    VALUES ('delete', old.id, old.key, old.content, old.tags);
                    INSERT INTO memory_fts(rowid, key, content, tags)
                    VALUES (new.id, new.key, new.content, new.tags);
                END
            """)

            conn.commit()

    def store(self, key: str, content: str, category: str = "general",
              data: Optional[Dict] = None, tags: Optional[List[str]] = None,
              importance: float = 1.0) -> bool:
        """
        Almacena un recuerdo en la memoria persistente.

        Args:
            key: Identificador único (ej: "personaje_elena", "capitulo_3")
            content: Texto descriptivo para búsqueda
            category: Tipo (personaje, trama, mundo, investigacion, sesion, etc.)
            data: Datos estructurados (dict)
            tags: Lista de etiquetas
            importance: 0.0 - 10.0 (prioridad de retención)
        """
        try:
            tags_str = ",".join(tags) if tags else ""
            data_json = json.dumps(data, ensure_ascii=False) if data else None

            with sqlite3.connect(str(self.db_path)) as conn:
                conn.execute("""
                    INSERT INTO memory (key, category, content, data_json, tags, importance, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(key) DO UPDATE SET
                        content=excluded.content,
                        data_json=excluded.data_json,
                        tags=excluded.tags,
                        importance=excluded.importance,
                        updated_at=excluded.updated_at,
                        access_count=access_count+1
                """, (key, category, content, data_json, tags_str, importance, datetime.now().isoformat()))
                conn.commit()
            return True
        except Exception as e:
            print(f"[MemoryManager] Error almacenando '{key}': {e}")
            return False

    def retrieve(self, key: str) -> Optional[Dict[str, Any]]:
        """Recupera un recuerdo por su clave exacta."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM memory WHERE key = ?", (key,)
            ).fetchone()

            if row:
                # Incrementar contador de acceso
                conn.execute(
                    "UPDATE memory SET access_count = access_count + 1 WHERE key = ?",
                    (key,)
                )
                conn.commit()

                return {
                    "key": row["key"],
                    "category": row["category"],
                    "content": row["content"],
                    "data": json.loads(row["data_json"]) if row["data_json"] else None,
                    "tags": row["tags"].split(",") if row["tags"] else [],
                    "importance": row["importance"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "access_count": row["access_count"]
                }
        return None

    def search(self, query: str, category: Optional[str] = None,
               limit: int = 10) -> List[Dict[str, Any]]:
        """
        Búsqueda híbrida: FTS5 + ranking por importancia y accesos.
        """
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row

            if category:
                rows = conn.execute("""
                    SELECT m.* FROM memory m
                    JOIN memory_fts fts ON m.id = fts.rowid
                    WHERE memory_fts MATCH ? AND m.category = ?
                    ORDER BY rank ASC, m.importance DESC, m.access_count DESC
                    LIMIT ?
                """, (query, category, limit)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT m.* FROM memory m
                    JOIN memory_fts fts ON m.id = fts.rowid
                    WHERE memory_fts MATCH ?
                    ORDER BY rank ASC, m.importance DESC, m.access_count DESC
                    LIMIT ?
                """, (query, limit)).fetchall()

            return [{
                "key": r["key"],
                "category": r["category"],
                "content": r["content"][:300],
                "tags": r["tags"].split(",") if r["tags"] else [],
                "importance": r["importance"],
                "updated_at": r["updated_at"]
            } for r in rows]

    def add_relation(self, source: str, target: str, relation_type: str,
                     strength: float = 1.0) -> bool:
        """
        Añade una relación al knowledge graph.
        Ej: add_relation("personaje_elena", "personaje_carlos", "enemigo", 0.9)
        """
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.execute("""
                    INSERT INTO relations (source_key, target_key, relation_type, strength)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(source_key, target_key, relation_type) DO UPDATE SET
                        strength=excluded.strength
                """, (source, target, relation_type, strength))
                conn.commit()
            return True
        except Exception as e:
            print(f"[MemoryManager] Error en relación: {e}")
            return False

    def get_relations(self, key: str, relation_type: Optional[str] = None) -> List[Dict]:
        """Obtiene todas las relaciones de una entidad."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            if relation_type:
                rows = conn.execute("""
                    SELECT * FROM relations
                    WHERE source_key = ? AND relation_type = ?
                    ORDER BY strength DESC
                """, (key, relation_type)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT * FROM relations
                    WHERE source_key = ? OR target_key = ?
                    ORDER BY strength DESC
                """, (key, key)).fetchall()

            return [dict(r) for r in rows]

    def get_graph(self) -> Dict[str, Any]:
        """Exporta el knowledge graph completo para visualización."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            nodes = conn.execute("SELECT key, category, content, tags FROM memory").fetchall()
            edges = conn.execute("SELECT source_key, target_key, relation_type, strength FROM relations").fetchall()

        return {
            "nodes": [{"id": n["key"], "category": n["category"],
                       "label": n["content"][:50], "tags": n["tags"]} for n in nodes],
            "edges": [{"source": e["source_key"], "target": e["target_key"],
                       "relation": e["relation_type"], "strength": e["strength"]} for e in edges]
        }

    def export_to_json(self, output_path: Optional[Path] = None) -> str:
        """Exporta toda la memoria a JSON."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM memory ORDER BY updated_at DESC").fetchall()
            data = [dict(r) for r in rows]

        out = output_path or (self.project_root / "memory" / "alexandria_memory_export.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return str(out)


# --- CLI de prueba ---
if __name__ == "__main__":
    print("=" * 60)
    print("   ALEXANDRIA MEMORY MANAGER — Test")
    print("=" * 60)

    mem = MemoryManager()

    # Almacenar datos de prueba
    mem.store("personaje_arturo",
              "Arturo Ledezma Ruan es el protagonista de TSBN. Farmacéutico que deja su trabajo.",
              category="personaje",
              data={"nombre": "Arturo Ledezma Ruan", "profesion": "Farmacéutico", "edad": 35},
              tags=["protagonista", "tsbn", "farmacéutico", "superación"],
              importance=9.0)

    mem.store("tema_resiliencia",
              "La resiliencia es el tema central de TSBN: capacidad de superar adversidades.",
              category="tema",
              tags=["resiliencia", "tema_central", "autoayuda"],
              importance=10.0)

    mem.store("capitulo_1",
              "Capítulo 1: La decisión. Arturo decide dejar su trabajo en la farmacia.",
              category="trama",
              tags=["capitulo", "inciting_incident", "trabajo"],
              importance=8.0)

    # Relaciones
    mem.add_relation("personaje_arturo", "tema_resiliencia", "encarna", 0.95)
    mem.add_relation("personaje_arturo", "capitulo_1", "protagonista_de", 1.0)

    # Búsqueda
    print("\n🔍 Búsqueda 'superación':")
    for r in mem.search("superación"):
        print(f"  [{r['category']}] {r['key']}: {r['content'][:60]}...")

    print("\n📊 Knowledge Graph:")
    graph = mem.get_graph()
    print(f"  Nodos: {len(graph['nodes'])}, Aristas: {len(graph['edges'])}")

    print("\n💾 Exportando memoria...")
    path = mem.export_to_json()
    print(f"  Guardado en: {path}")
