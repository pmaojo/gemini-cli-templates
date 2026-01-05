"""
Experience Buffer - Almacena interacciones y feedback de usuario
Parte del sistema Agent Lightning para aprendizaje continuo
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path

class ExperienceBuffer:
    """
    Almacena experiencias de usuario para entrenamiento continuo.
    Cada experiencia incluye input, output, feedback (👍/👎), y recompensas AIR.
    """

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.experiences: List[Dict[str, Any]] = []

        # Crear directorio de sesiones si no existe
        self.sessions_dir = Path("data/sessions")
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

        self.session_file = self.sessions_dir / f"{session_id}.jsonl"

        # Cargar experiencias previas si existen
        self._load_from_disk()

    def record_interaction(
        self,
        input_text: str,
        output_text: str,
        feedback: Optional[str] = None,  # "positive", "negative", None
        air_reward: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Registra una interacción usuario-modelo"""
        experience = {
            "timestamp": datetime.now().isoformat(),
            "input": input_text,
            "output": output_text,
            "feedback": feedback,
            "air_reward": air_reward,
            "metadata": metadata or {}
        }

        self.experiences.append(experience)
        self._save_to_disk()

        print(f"📝 Experiencia registrada: {feedback or 'sin feedback'}, reward: {air_reward:.2f}")

    def get_training_data(self) -> List[Dict[str, Any]]:
        """Obtiene solo experiencias con feedback para entrenamiento"""
        return [e for e in self.experiences if e["feedback"] is not None]

    def get_positive_examples(self) -> List[Dict[str, Any]]:
        """Obtiene solo ejemplos con feedback positivo"""
        return [e for e in self.experiences if e["feedback"] == "positive"]

    def get_negative_examples(self) -> List[Dict[str, Any]]:
        """Obtiene solo ejemplos con feedback negativo"""
        return [e for e in self.experiences if e["feedback"] == "negative"]

    def should_train(self, min_feedback: int = 50) -> bool:
        """Determina si hay suficientes datos para entrenar"""
        feedback_count = len(self.get_training_data())
        return feedback_count >= min_feedback

    def get_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de la sesión"""
        training_data = self.get_training_data()
        positive = len(self.get_positive_examples())
        negative = len(self.get_negative_examples())

        return {
            "total_interactions": len(self.experiences),
            "with_feedback": len(training_data),
            "positive_feedback": positive,
            "negative_feedback": negative,
            "positive_rate": positive / len(training_data) if training_data else 0.0,
            "avg_air_reward": sum(e["air_reward"] for e in self.experiences) / len(self.experiences) if self.experiences else 0.0
        }

    def _save_to_disk(self):
        """Persiste experiencias en disco"""
        with open(self.session_file, 'w') as f:
            for exp in self.experiences:
                f.write(json.dumps(exp) + '\n')

    def _load_from_disk(self):
        """Carga experiencias previas si existen"""
        if self.session_file.exists():
            with open(self.session_file, 'r') as f:
                self.experiences = [json.loads(line) for line in f if line.strip()]
            print(f"📂 Cargadas {len(self.experiences)} experiencias previas")

    def export_for_training(self, output_file: str):
        """Exporta datos en formato JSONL para entrenamiento"""
        training_data = self.get_training_data()

        with open(output_file, 'w') as f:
            for exp in training_data:
                # Formato para fine-tuning
                training_example = {
                    "text": exp["input"],
                    "output": exp["output"],
                    "feedback": exp["feedback"],
                    "reward": exp["air_reward"]
                }
                f.write(json.dumps(training_example) + '\n')

        print(f"💾 Exportados {len(training_data)} ejemplos a {output_file}")
        return len(training_data)
