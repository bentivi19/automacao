# memory.py
import json
import os
import datetime
from typing import Any, Dict, List, Optional

MEMORY_FILE = "memory.json"
BACKUP_FILE = "memory.backup.json"


class Memory:
    def __init__(self, memory_file: str = MEMORY_FILE):
        self.memory_file = memory_file
        self.data = self._load_memory()

    # ----------------------- Carga e Normalização -----------------------

    def _default_structure(self) -> Dict[str, Any]:
        """Estrutura base da memória."""
        return {
            "user_profile": {},
            "preferences": {},
            "tasks": [],   # lista de dicts {task, done, created_at}
            "notes": [],   # lista de dicts {id, text, tags, source, timestamp}
            "system": {}
        }

    def _normalize_notes(self, notes_raw: Any) -> List[Dict[str, Any]]:
        """Garante que as notas estejam no formato estruturado."""
        normalized: List[Dict[str, Any]] = []
        if not isinstance(notes_raw, list):
            return normalized

        for idx, item in enumerate(notes_raw):
            if isinstance(item, str):
                # Compatibilidade com versões antigas: nota simples em texto
                normalized.append({
                    "id": idx + 1,
                    "text": item,
                    "tags": [],
                    "source": "legacy",
                    "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
                })
            elif isinstance(item, dict):
                normalized.append({
                    "id": item.get("id", idx + 1),
                    "text": item.get("text", ""),
                    "tags": item.get("tags", []),
                    "source": item.get("source", "unknown"),
                    "timestamp": item.get(
                        "timestamp",
                        datetime.datetime.now().isoformat(timespec="seconds")
                    ),
                })
        return normalized

    def _normalize_tasks(self, tasks_raw: Any) -> List[Dict[str, Any]]:
        """Garante que as tarefas estejam no formato estruturado."""
        normalized: List[Dict[str, Any]] = []
        if not isinstance(tasks_raw, list):
            return normalized

        for item in tasks_raw:
            if isinstance(item, str):
                normalized.append({
                    "task": item,
                    "done": False,
                    "created_at": datetime.datetime.now().isoformat(timespec="seconds")
                })
            elif isinstance(item, dict):
                normalized.append({
                    "task": item.get("task", ""),
                    "done": bool(item.get("done", False)),
                    "created_at": item.get(
                        "created_at",
                        datetime.datetime.now().isoformat(timespec="seconds")
                    ),
                })
        return normalized

    def _normalize_memory(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """Aplica normalização para garantir que todas as chaves existam e estejam consistentes."""
        base = self._default_structure()

        base["user_profile"] = raw.get("user_profile", {}) or {}
        base["preferences"] = raw.get("preferences", {}) or {}
        base["system"] = raw.get("system", {}) or {}

        base["notes"] = self._normalize_notes(raw.get("notes", []))
        base["tasks"] = self._normalize_tasks(raw.get("tasks", []))

        return base

    def _load_memory(self) -> Dict[str, Any]:
        """Carrega a memória do arquivo JSON ou cria uma nova."""
        if not os.path.exists(self.memory_file):
            return self._default_structure()

        try:
            with open(self.memory_file, "r", encoding="utf-8") as f:
                raw = json.load(f)
            return self._normalize_memory(raw)
        except Exception:
            # evita falhas caso o JSON esteja corrompido
            return self._default_structure()

    # ----------------------- Backup & Salvamento -----------------------

    def _backup_memory(self):
        """Cria um backup simples da memória atual."""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    content = f.read()
                with open(BACKUP_FILE, "w", encoding="utf-8") as bf:
                    bf.write(content)
        except Exception:
            # não quebra o fluxo caso o backup falhe
            pass

    def _save_memory(self):
        """Salva a memória no arquivo JSON."""
        self._backup_memory()
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    # ----------------------- Operações de Notas -----------------------

    def add_note(
        self,
        text: str,
        tags: Optional[List[str]] = None,
        source: Optional[str] = None
    ) -> Dict[str, Any]:
        """Adiciona uma nota estruturada ao histórico."""
        if tags is None:
            tags = []
        if source is None:
            source = "manual"

        next_id = (max((n.get("id", 0) for n in self.data["notes"]), default=0) + 1)
        note = {
            "id": next_id,
            "text": text,
            "tags": tags,
            "source": source,
            "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        }
        self.data["notes"].append(note)
        self._save_memory()
        return note

    def get_notes(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retorna as notas, opcionalmente limitadas."""
        if limit is None or limit >= len(self.data["notes"]):
            return list(self.data["notes"])
        return self.data["notes"][-limit:]

    def search_notes(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Busca notas que contenham o texto ou tag informados."""
        query_lower = query.lower()
        results = []
        for note in self.data["notes"]:
            text_match = query_lower in note.get("text", "").lower()
            tags = [t.lower() for t in note.get("tags", [])]
            tag_match = query_lower in tags
            if text_match or tag_match:
                results.append(note)
                if len(results) >= limit:
                    break
        return results

    def clear_notes(self):
        """Remove todas as notas."""
        self.data["notes"] = []
        self._save_memory()

    # ----------------------- Operações de Preferências -----------------------

    def add_preference(self, key: str, value: Any):
        """Adiciona ou altera uma preferência do usuário."""
        self.data["preferences"][key] = value
        self._save_memory()

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Retorna uma preferência do usuário."""
        return self.data["preferences"].get(key, default)

    # ----------------------- Operações de Tarefas -----------------------

    def add_task(self, task: str) -> Dict[str, Any]:
        """Adiciona uma tarefa à lista."""
        t = {
            "task": task,
            "done": False,
            "created_at": datetime.datetime.now().isoformat(timespec="seconds")
        }
        self.data["tasks"].append(t)
        self._save_memory()
        return t

    def mark_task_done(self, index: int) -> bool:
        """Marca uma tarefa como concluída pelo índice."""
        try:
            self.data["tasks"][index]["done"] = True
            self._save_memory()
            return True
        except Exception:
            return False

    def get_tasks(self, only_pending: bool = False) -> List[Dict[str, Any]]:
        """Retorna todas as tarefas ou apenas as pendentes."""
        if not only_pending:
            return list(self.data["tasks"])
        return [t for t in self.data["tasks"] if not t.get("done", False)]

    def clear_tasks(self):
        """Remove todas as tarefas."""
        self.data["tasks"] = []
        self._save_memory()

    # ----------------------- Perfil do Usuário -----------------------

    def update_user_profile(self, key: str, value: Any):
        """Atualiza parte do perfil do usuário."""
        self.data["user_profile"][key] = value
        self._save_memory()

    def get_user_profile(self) -> Dict[str, Any]:
        """Retorna o perfil completo do usuário."""
        return dict(self.data["user_profile"])

    # ----------------------- Sistema & Geral -----------------------

    def set_system_value(self, key: str, value: Any):
        """Define um valor na seção de sistema (config interna do assistente)."""
        self.data["system"][key] = value
        self._save_memory()

    def get_system_value(self, key: str, default: Any = None) -> Any:
        """Obtém um valor da seção de sistema."""
        return self.data["system"].get(key, default)

    def get_memory(self) -> Dict[str, Any]:
        """Retorna toda a memória."""
        return self.data

    def clear_memory(self):
        """Limpa a memória completamente."""
        self.data = self._default_structure()
        self._save_memory()


# ----------------------- MemoryStore (fachada global) -----------------------


class MemoryStore:
    """
    Fachada simples para reutilizar uma única instância de Memory
    em vários módulos (assistant.py, agentes, etc.).
    """

    _instance: Optional[Memory] = None

    @classmethod
    def get_memory(cls) -> Memory:
        if cls._instance is None:
            cls._instance = Memory()
        return cls._instance

    # Helpers de atalho, opcionais mas práticos:

    @classmethod
    def add_note(
        cls,
        text: str,
        tags: Optional[List[str]] = None,
        source: Optional[str] = None
    ) -> Dict[str, Any]:
        return cls.get_memory().add_note(text, tags=tags, source=source)

    @classmethod
    def get_notes(cls, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        return cls.get_memory().get_notes(limit=limit)

    @classmethod
    def search_notes(cls, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        return cls.get_memory().search_notes(query, limit=limit)

    @classmethod
    def add_task(cls, task: str) -> Dict[str, Any]:
        return cls.get_memory().add_task(task)

    @classmethod
    def get_tasks(cls, only_pending: bool = False) -> List[Dict[str, Any]]:
        return cls.get_memory().get_tasks(only_pending=only_pending)

    @classmethod
    def update_user_profile(cls, key: str, value: Any):
        return cls.get_memory().update_user_profile(key, value)

    @classmethod
    def get_user_profile(cls) -> Dict[str, Any]:
        return cls.get_memory().get_user_profile()

    @classmethod
    def clear_all(cls):
        return cls.get_memory().clear_memory()
