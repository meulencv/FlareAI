import math
import sqlite3
from contextlib import contextmanager
from pathlib import Path

RESERVE_PER_IMAGE = 450000


class Budget:
    def __init__(self, path, cap_usd=2, legacy_spent_usd=0):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as connection:
            connection.executescript("CREATE TABLE IF NOT EXISTS account (id INTEGER PRIMARY KEY, cap INTEGER NOT NULL, legacy INTEGER NOT NULL);"
                                     "CREATE TABLE IF NOT EXISTS reservations (id TEXT PRIMARY KEY, images INTEGER NOT NULL, reserved INTEGER NOT NULL, actual INTEGER);")
            connection.execute("INSERT OR IGNORE INTO account VALUES (1,?,?)", (math.floor(cap_usd * 1000000), math.ceil(legacy_spent_usd * 1000000)))

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.path, timeout=5)
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def status(self):
        with self.connect() as connection:
            cap, legacy = connection.execute("SELECT cap,legacy FROM account WHERE id=1").fetchone()
            used = legacy + connection.execute("SELECT coalesce(sum(coalesce(actual,reserved)),0) FROM reservations").fetchone()[0]
        return {"cap_usd": cap / 1000000, "used_or_reserved_usd": used / 1000000,
                "remaining_usd": max(0, cap - used) / 1000000}

    def reserve(self, identifier, images=2):
        if type(images) is not int or not 1 <= images <= 2:
            raise ValueError("Como máximo dos imágenes por consulta")
        with self.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            if connection.execute("SELECT 1 FROM reservations WHERE id=?", (identifier,)).fetchone():
                return
            cap, legacy = connection.execute("SELECT cap,legacy FROM account WHERE id=1").fetchone()
            used = legacy + connection.execute("SELECT coalesce(sum(coalesce(actual,reserved)),0) FROM reservations").fetchone()[0]
            if used + images * RESERVE_PER_IMAGE > cap:
                raise ValueError("Presupuesto de pruebas insuficiente. No se ha iniciado ninguna llamada.")
            connection.execute("INSERT INTO reservations VALUES (?,?,?,NULL)", (identifier, images, images * RESERVE_PER_IMAGE))

    def release_unbilled(self, identifier, proof):
        if not isinstance(proof, dict) or proof.get("status") not in {"completed", "failed"} or proof.get("call_attempt_count") != 0 or not proof.get("run_id"):
            raise ValueError("Falta evidencia de que no hubo llamadas de visión")
        with self.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute("SELECT reserved,actual FROM reservations WHERE id=?", (identifier,)).fetchone()
            if row is None or row[1] not in (None, row[0]):
                raise ValueError("No se modifica una liquidación de consumo conocido")
            connection.execute("CREATE TABLE IF NOT EXISTS reconciliations (id TEXT PRIMARY KEY, run_id TEXT NOT NULL, previous INTEGER)")
            connection.execute("INSERT OR IGNORE INTO reconciliations VALUES (?,?,?)", (identifier, proof["run_id"], row[1]))
            connection.execute("UPDATE reservations SET actual=0 WHERE id=?", (identifier,))

    def reconcile_actual(self, identifier, proof):
        if not isinstance(proof, dict):
            raise ValueError("Falta evidencia de ejecución")
        results = proof.get("results", [])
        if proof.get("status") != "completed" or not proof.get("run_id") or len(results) != len(proof.get("selected", [])):
            raise ValueError("Faltan resultados completos para conciliar")
        costs = [item.get("usage_cost_usd") for item in results]
        if any(type(cost) not in (float, int) or not math.isfinite(cost) or cost < 0 for cost in costs):
            raise ValueError("Faltan recibos de coste válidos")
        actual = sum(math.ceil(cost * 1000000) for cost in costs)
        with self.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute("SELECT reserved,actual FROM reservations WHERE id=?", (identifier,)).fetchone()
            if row is None or row[1] == actual:
                return
            if row[1] not in (None, row[0]):
                raise ValueError("No se sustituye una liquidación de coste conocido")
            connection.execute("CREATE TABLE IF NOT EXISTS reconciliations (id TEXT PRIMARY KEY, run_id TEXT NOT NULL, previous INTEGER)")
            connection.execute("INSERT OR IGNORE INTO reconciliations VALUES (?,?,?)", (identifier, proof["run_id"], row[1]))
            connection.execute("UPDATE reservations SET actual=? WHERE id=?", (actual, identifier))

    def settle(self, identifier, costs):
        with self.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute("SELECT images,reserved,actual FROM reservations WHERE id=?", (identifier,)).fetchone()
            if row is None or row[2] is not None:
                return
            if costs is None:
                actual = row[1]
            else:
                if len(costs) > row[0]:
                    raise ValueError("La ejecución supera el número de imágenes reservado")
                actual = sum(math.ceil(cost * 1000000) if type(cost) in (float, int) and math.isfinite(cost) and cost >= 0
                             else RESERVE_PER_IMAGE for cost in costs)
            connection.execute("UPDATE reservations SET actual=? WHERE id=?", (actual, identifier))
