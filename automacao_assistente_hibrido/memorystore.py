# -*- coding: utf-8 -*-
# memorystore.py
import json
import os
from datetime import datetime

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "data", "memory.json")


class MemoryStore:
    def __init__(self, memory_file: str = MEMORY_FILE):
        self.memory_file = memory_file
        self.data = self._load_memory()

    # ----------------------- Carregar memória -----------------------

    def _load_memory(self):
        """Carrega a memória do arquivo JSON ou cria uma nova."""
        default_structure = {
            "user_profile": {},
            "preferences": {},
            "tasks": [],
            "notes": [],
            "interactions": [],
            "system": {}
        }
        
        if not os.path.exists(self.memory_file):
            return default_structure

        try:
            with open(self.memory_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Garantir que todas as chaves existem
                for key in default_structure:
                    if key not in data:
                        data[key] = default_structure[key]
                return data
        except Exception:
            # evita falhas caso o JSON esteja corrompido
            return default_structure

    # ----------------------- Salvar memória -----------------------

    def _save_memory(self):
        """Salva a memória no arquivo JSON."""
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    # ----------------------- Operações de Notas -----------------------

    def add_note(self, text: str, tags: list = None, source: str = None, question: str = None, answer: str = None):
        """Adiciona uma nota ao histórico com tags e fonte. Pode incluir pergunta e resposta."""
        note = {
            "text": text,
            "tags": tags or [],
            "source": source,
            "question": question,
            "answer": answer,
            "timestamp": datetime.now().isoformat()
        }
        self.data["notes"].append(note)
        self._save_memory()

    def get_notes(self, tag: str = None):
        """Retorna notas filtradas por tag se fornecido."""
        if tag:
            return [note for note in self.data["notes"] if tag in note.get("tags", [])]
        return self.data["notes"]

    def search_notes(self, keywords: str, limit: int = 3):
        """Busca notas relevantes baseado em palavras-chave."""
        keywords_lower = keywords.lower().split()
        relevant_notes = []
        
        for note in self.data["notes"]:
            # Busca em question e answer se existirem
            search_text = ""
            if note.get("question"):
                search_text += note.get("question", "").lower()
            if note.get("answer"):
                search_text += " " + note.get("answer", "").lower()
            if note.get("text"):
                search_text += " " + note.get("text", "").lower()
            
            # Contar quantas palavras-chave aparecem
            match_count = sum(1 for keyword in keywords_lower if keyword in search_text)
            
            if match_count > 0:
                relevant_notes.append({
                    "note": note,
                    "match_score": match_count
                })
        
        # Ordenar por relevância e retornar os melhores
        relevant_notes.sort(key=lambda x: x["match_score"], reverse=True)
        return [item["note"] for item in relevant_notes[:limit]]

    def delete_note(self, index: int):
        """Deleta uma nota pelo índice."""
        try:
            if 0 <= index < len(self.data["notes"]):
                self.data["notes"].pop(index)
                self._save_memory()
                return True
        except Exception:
            pass
        return False

    # ----------------------- Operações de Preferências -----------------------

    def add_preference(self, key: str, value):
        """Adiciona ou altera uma preferência do usuário."""
        self.data["preferences"][key] = value
        self._save_memory()

    def get_preference(self, key: str, default=None):
        """Retorna uma preferência específica."""
        return self.data["preferences"].get(key, default)

    # ----------------------- Operações de Tarefas -----------------------

    def add_task(self, task: str, alert_enabled: bool = False, alert_time: str = None, alert_type: str = None):
        """Adiciona uma tarefa à lista com opção de alerta.
        
        Args:
            task: Descrição da tarefa
            alert_enabled: Se deve enviar alerta
            alert_time: Hora do alerta (formato HH:MM)
            alert_type: Tipo de alerta ('email', 'whatsapp', 'ambos')
        """
        self.data["tasks"].append({
            "task": task,
            "done": False,
            "created_at": datetime.now().isoformat(),
            "alert_enabled": alert_enabled,
            "alert_time": alert_time,
            "alert_type": alert_type or "email"
        })
        self._save_memory()

    def mark_task_done(self, index: int):
        """Marca uma tarefa como concluída."""
        try:
            self.data["tasks"][index]["done"] = True
            self.data["tasks"][index]["completed_at"] = datetime.now().isoformat()
            self._save_memory()
            return True
        except Exception:
            return False

    def get_tasks(self, done: bool = None):
        """Retorna tarefas filtradas por status se fornecido."""
        if done is None:
            return self.data["tasks"]
        return [task for task in self.data["tasks"] if task["done"] == done]

    def delete_task(self, index: int):
        """Remove uma tarefa pelo índice."""
        try:
            del self.data["tasks"][index]
            self._save_memory()
            return True
        except Exception:
            return False

    def clear_completed_tasks(self):
        """Remove todas as tarefas concluídas."""
        self.data["tasks"] = [task for task in self.data["tasks"] if not task["done"]]
        self._save_memory()

    # ----------------------- Operações de Interações -----------------------

    def add_interaction(self, question: str, response: str, source: str = "assistant"):
        """Registra uma interação (pergunta e resposta)."""
        interaction = {
            "question": question,
            "response": response,
            "source": source,
            "timestamp": datetime.now().isoformat()
        }
        self.data["interactions"].append(interaction)
        self._save_memory()

    def get_interactions(self, limit: int = None):
        """Retorna interações, opcionalmente limitadas."""
        if limit:
            return self.data["interactions"][-limit:]
        return self.data["interactions"]

    # ----------------------- Operações de Perfil -----------------------

    def update_user_profile(self, key: str, value):
        """Atualiza parte do perfil do usuário."""
        self.data["user_profile"][key] = value
        self._save_memory()

    def get_user_profile(self):
        """Retorna o perfil completo do usuário."""
        return self.data["user_profile"]

    # ----------------------- Operações Gerais -----------------------

    def get_memory(self):
        """Retorna toda a memória."""
        return self.data

    def clear_memory(self):
        """Limpa a memória completamente."""
        self.data = {
            "user_profile": {},
            "preferences": {},
            "tasks": [],
            "notes": [],
            "interactions": [],
            "system": {}
        }
        self._save_memory()

    def get_summary(self):
        """Retorna um resumo da memória."""
        return {
            "total_notes": len(self.data["notes"]),
            "total_tasks": len(self.data["tasks"]),
            "tasks_done": len([t for t in self.data["tasks"] if t["done"]]),
            "total_interactions": len(self.data["interactions"]),
            "preferences_count": len(self.data["preferences"])
        }
