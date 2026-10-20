"""ShashBesh adapter that delegates all game rules to the fixed Node Core package."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping
import hashlib
import json
import os
import select
import shutil
import subprocess
import threading
import time
import tarfile

from .protocols import PROTOCOL_VERSION

MAX_REQUEST_BYTES = 16 * 1024 * 1024
MAX_RESPONSE_BYTES = 16 * 1024 * 1024
MAX_PARALLEL_CORE_WORKERS = 1
_CORE_WORKER_SLOTS = threading.BoundedSemaphore(MAX_PARALLEL_CORE_WORKERS)
CORE_VERSION = "0.1.0-g0.65e1ec3"
CORE_SHA256 = "acf4e1ef6af55b81607b1a9df9e8b684b6ac6bf0d95b39a389bc5e57d3c001fe"


class ShashBeshEnvironment:
    environment_id = "shashbesh.core"
    version = "1.0.0"

    def __init__(self, core_package_root: str | Path | None = None, worker_timeout_seconds: float = 10.0, *, node_heap_mb: int | None = None):
        if worker_timeout_seconds <= 0 or worker_timeout_seconds > 60:
            raise ValueError("worker timeout must be in (0, 60]")
        if node_heap_mb is not None and (type(node_heap_mb) is not int or not 128 <= node_heap_mb <= 512):
            raise ValueError("Node heap budget must be 128–512 MiB")
        self.node_heap_mb = node_heap_mb
        default_root = Path(__file__).resolve().parent.parent / "artifacts" / "core" / CORE_VERSION / "package"
        self.core_package_root = Path(core_package_root or os.environ.get("SHASHBESH_CORE_PACKAGE", default_root)).resolve()
        self.artifact_root = self.core_package_root.parent
        self.worker_timeout_seconds = worker_timeout_seconds
        self._node = shutil.which("node")
        if not self._node:
            raise RuntimeError("Node.js is required for ShashBesh Core worker")
        self._verify_artifact()
        self._package = json.loads((self.core_package_root / "package.json").read_text(encoding="utf-8"))
        self._artifact_manifest = json.loads((self.artifact_root / "core-artifact-manifest.json").read_text(encoding="utf-8"))
        self.version = f"{self._package['version']}+env1.0.0"
        self.configuration: Mapping[str, Any] = {
            "protocol_version": PROTOCOL_VERSION,
            "core_version": self._package["version"],
            "core_artifact_sha256": self._artifact_manifest["artifactSha256"],
            "source_commit": self._artifact_manifest["sourceCommit"],
            "source_tree": self._artifact_manifest["sourceTree"],
            "player_mapping": {"1": 0, "2": 1},
            "dice_rng": "Engine.seeded-v1",
            "worker_timeout_seconds": worker_timeout_seconds,
        }
        self._worker_path = Path(__file__).with_name("shashbesh_worker.cjs")
        self._process: subprocess.Popen[bytes] | None = None
        self._slot_acquired = False
        self._request_id = 0
        self._read_buffer = bytearray()

    def _verify_artifact(self) -> None:
        manifest_path = self.artifact_root / "core-artifact-manifest.json"
        archive_path = self.artifact_root / "shashbesh-core.tgz"
        if not manifest_path.is_file() or not archive_path.is_file():
            raise RuntimeError("local Core artifact manifest/archive missing")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
        if digest != manifest.get("artifactSha256") or digest != CORE_SHA256:
            raise RuntimeError("Core artifact SHA-256 mismatch")
        if manifest.get("status") != "G2_PASS" or manifest.get("coreVersion") != CORE_VERSION:
            raise RuntimeError("Core artifact is not an approved G2 package")
        expected: dict[str, str] = {}
        with tarfile.open(archive_path, "r:gz") as archive:
            for member in archive.getmembers():
                if not member.isfile() or not member.name.startswith("package/"):
                    continue
                relative = member.name[len("package/"):]
                extracted = (self.core_package_root / relative).resolve()
                if not extracted.is_relative_to(self.core_package_root):
                    raise RuntimeError("unsafe Core archive path")
                if not extracted.is_file():
                    raise RuntimeError(f"Core extracted file missing: {relative}")
                source = archive.extractfile(member)
                assert source is not None
                expected[relative] = hashlib.sha256(source.read()).hexdigest()
        actual = {p.relative_to(self.core_package_root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in self.core_package_root.rglob("*") if p.is_file()}
        if expected != actual:
            raise RuntimeError("extracted Core package differs from hashed archive")

    def _start(self) -> None:
        if self._process and self._process.poll() is None:
            return
        if not _CORE_WORKER_SLOTS.acquire(timeout=self.worker_timeout_seconds):
            raise TimeoutError("maximum parallel Core workers reached")
        self._slot_acquired = True
        env = {
            "PATH": str(Path(self._node).parent),
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
            "SHASHBESH_CORE_PACKAGE": str(self.core_package_root),
            "SHASHBESH_CORE_SHA256": self.configuration["core_artifact_sha256"],
        }
        try:
            self._process = subprocess.Popen(
                [self._node, *([f"--max-old-space-size={self.node_heap_mb}"] if self.node_heap_mb else []), str(self._worker_path)], cwd=str(self._worker_path.parent.parent), env=env,
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                bufsize=0, close_fds=True,
            )
            self._read_buffer.clear()
            hello = self._request("hello")
            if hello.get("core_version") != self.configuration["core_version"] or hello.get("core_artifact_sha256") != self.configuration["core_artifact_sha256"]:
                raise RuntimeError("Node worker loaded an unexpected Core package")
        except Exception:
            self._stop()
            raise

    def _stop(self) -> None:
        process, self._process = self._process, None
        self._read_buffer.clear()
        if process:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=0.25)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=1)
            for stream in (process.stdin, process.stdout):
                if stream:
                    stream.close()
        if self._slot_acquired:
            self._slot_acquired = False
            _CORE_WORKER_SLOTS.release()

    def _request(self, operation: str, **payload: Any) -> dict[str, Any]:
        if self._process is None or self._process.poll() is not None:
            self._start()
        assert self._process and self._process.stdin and self._process.stdout
        self._request_id += 1
        request_id = self._request_id
        body = json.dumps({"protocol": "lab-node-protocol/1", "request_id": request_id,
                           "operation": operation, **payload}, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + b"\n"
        if len(body) > MAX_REQUEST_BYTES:
            raise ValueError("Core worker request exceeds size limit")
        try:
            self._process.stdin.write(body)
            self._process.stdin.flush()
            # A complete 3/4-seat journal contains substantially more Core search
            # and verified command snapshots. Keep live commands on their normal
            # budget; only full-journal operations receive a bounded larger budget.
            saved = payload.get("state", {})
            players = saved.get("core_state", {}).get("players", []) if isinstance(saved, dict) else []
            multiplier = 3 if operation in {"replay", "replay_timeline", "restore"} and len(players) > 2 else 1
            deadline = time.monotonic() + self.worker_timeout_seconds * multiplier
            while b"\n" not in self._read_buffer:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError(f"Core worker timed out during {operation}")
                ready, _, _ = select.select([self._process.stdout], [], [], remaining)
                if not ready:
                    raise TimeoutError(f"Core worker timed out during {operation}")
                chunk = os.read(self._process.stdout.fileno(), 65536)
                if not chunk:
                    raise RuntimeError("Core worker exited before replying")
                self._read_buffer.extend(chunk)
                if len(self._read_buffer) > MAX_RESPONSE_BYTES:
                    raise RuntimeError("Core worker response exceeds size limit")
            line, _, rest = self._read_buffer.partition(b"\n")
            self._read_buffer = bytearray(rest)
            response = json.loads(line.decode("utf-8"))
            if response.get("protocol") != "lab-node-protocol/1" or response.get("request_id") != request_id:
                raise RuntimeError("Core worker response identity mismatch")
            if not response.get("ok"):
                error = response.get("error", {})
                raise ValueError(f"Core rejected {operation}: {error.get('name', 'Error')}: {error.get('message', 'unknown error')}")
            return response["data"]
        except TimeoutError:
            self._stop()
            raise
        except (RuntimeError, json.JSONDecodeError, OSError):
            self._stop()
            raise

    def reset(self, seed: int, *, manual: bool = False, players: list[int] | None = None) -> dict[str, Any]:
        if isinstance(seed, bool) or not isinstance(seed, int) or not -(1 << 63) <= seed < (1 << 63):
            raise ValueError("seed must fit a signed 64-bit integer")
        return self._request("reset", seed=str(seed), manual=manual, players=[1, 2] if players is None else players)["state"]

    def roll_dice(self, state: dict[str, Any], *, stop_before_player: int | None = None) -> dict[str, Any]:
        return self._request("live_roll", state=state, stop_before_player=stop_before_player)["state"]

    def restore(self, saved: dict[str, Any], *, manual: bool = True) -> dict[str, Any]:
        """Verify Core replay and seed/counter before restoring a live worker context."""
        return self._request("restore", state=saved, manual=manual)["state"]

    def legal_actions(self, state: dict[str, Any]) -> list[dict[str, Any]]:
        return self._request("legal_actions", state=state)["actions"]

    def step(self, state: dict[str, Any], action: Any) -> dict[str, Any]:
        return self._request("step", state=state, action=action)["state"]

    def is_terminal(self, state: dict[str, Any]) -> bool:
        return state.get("winner_player") is not None or state.get("phase") == "game_over"

    def result(self, state: dict[str, Any]) -> dict[str, Any]:
        return self._request("result", state=state)["result"]

    def serialize(self, state: dict[str, Any]) -> dict[str, Any]:
        return {key: state[key] for key in ("environment_id", "environment_version", "core_version",
                "core_artifact_sha256", "active_player", "phase", "winner_player", "current_roll", "pieces")}

    def serialize_replay(self, state: dict[str, Any]) -> dict[str, Any]:
        return self._request("serialize", state=state)["state"]

    def current_player(self, state: dict[str, Any]) -> int:
        player = state["active_player"]
        if type(player) is not int or player not in (0, 1, 2, 3):
            raise ValueError(f"unexpected active player seat: {player}")
        return player

    def verify_replay(self, serialized_state: dict[str, Any]) -> dict[str, Any]:
        return self._request("replay", state=serialized_state)

    def geometry(self) -> dict[str, Any]:
        """Return the board geometry parsed by the pinned Core artifact."""
        return self._request("geometry")

    def replay_timeline(self, serialized_state: dict[str, Any], actions: list[dict[str, Any]]) -> dict[str, Any]:
        """Verify a saved Core journal and materialize event, roll and compatible action frames via Engine.replay."""
        return self._request("replay_timeline", state=serialized_state, actions=actions)

    def release_game(self, seed: int) -> bool:
        """Release worker-held game state after its immutable replay is stored."""
        return bool(self._request("release", seed=str(seed)).get("released"))

    def close(self) -> None:
        if self._process and self._process.poll() is None:
            try:
                self._request("shutdown")
                if self._process.stdin:
                    self._process.stdin.close()
                self._process.wait(timeout=1)
            except Exception:
                pass
        self._stop()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
