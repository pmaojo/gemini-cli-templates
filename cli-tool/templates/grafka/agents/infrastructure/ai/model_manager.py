"""
Model Manager - Gestiona versiones del modelo y persistencia entre sesiones
Implementa rollback automático si el nuevo modelo es peor
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

class ModelManager:
    """
    Gestiona checkpoints del modelo SLM y selecciona el mejor.

    Funcionalidades:
    - Cargar mejor modelo al iniciar
    - Guardar checkpoints con metadata
    - Comparar rendimiento entre versiones
    - Rollback automático si el nuevo modelo empeora
    """

    def __init__(self, base_model_path: str = "checkpoints/gpt2-simple/final"):
        self.base_model_path = base_model_path
        self.sessions_dir = Path("checkpoints/sessions")
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

        self.metadata_file = Path("checkpoints/model_metadata.json")
        self.metadata = self._load_metadata()

        print(f"📊 Model Manager inicializado - {len(self.metadata)} sesiones registradas")

    def load_best_model(self) -> str:
        """
        Carga el mejor modelo basado en métricas.

        Returns:
            Path al mejor modelo
        """
        if not self.metadata:
            print(f"🆕 Primera sesión - usando modelo base: {self.base_model_path}")
            return self.base_model_path

        # Ordenar por tasa de feedback positivo
        sorted_sessions = sorted(
            self.metadata,
            key=lambda x: x.get("feedback_positive_rate", 0.0),
            reverse=True
        )

        best_session = sorted_sessions[0]
        best_path = str(self.sessions_dir / best_session["session_id"])

        print(f"✨ Cargando mejor modelo: {best_session['session_id']}")
        print(f"   📈 Positive rate: {best_session['feedback_positive_rate']:.1%}")
        print(f"   📉 Loss: {best_session.get('loss', 'N/A')}")

        return best_path

    def save_checkpoint(
        self,
        session_id: str,
        model_path: str,
        metrics: Dict[str, Any]
    ):
        """
        Guarda checkpoint con metadata.

        Args:
            session_id: ID de la sesión
            model_path: Path donde se guardó el modelo
            metrics: Métricas del modelo (loss, accuracy, feedback_rate, etc.)
        """
        metadata = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "model_path": model_path,
            "loss": metrics.get("loss", None),
            "feedback_positive_rate": metrics.get("positive_rate", 0.0),
            "total_interactions": metrics.get("total_interactions", 0),
            "training_examples": metrics.get("training_examples", 0)
        }

        self.metadata.append(metadata)
        self._save_metadata()

        print(f"💾 Checkpoint guardado: {session_id}")
        print(f"   Métricas: {metrics}")

    def should_rollback(
        self,
        new_metrics: Dict[str, Any],
        threshold: float = 0.8
    ) -> bool:
        """
        Determina si se debe hacer rollback al modelo anterior.

        Args:
            new_metrics: Métricas del nuevo modelo
            threshold: Umbral de degradación aceptable (0.8 = 20% peor)

        Returns:
            True si se debe hacer rollback
        """
        if not self.metadata:
            return False  # No hay modelo anterior

        # Obtener mejor modelo anterior
        prev_best = max(
            self.metadata,
            key=lambda x: x.get("feedback_positive_rate", 0.0)
        )

        prev_rate = prev_best.get("feedback_positive_rate", 0.0)
        new_rate = new_metrics.get("positive_rate", 0.0)

        # Rollback si el nuevo modelo es significativamente peor
        if new_rate < prev_rate * threshold:
            print(f"⚠️  ROLLBACK RECOMENDADO:")
            print(f"   Modelo anterior: {prev_rate:.1%}")
            print(f"   Modelo nuevo: {new_rate:.1%}")
            print(f"   Degradación: {((prev_rate - new_rate) / prev_rate * 100):.1f}%")
            return True

        return False

    def get_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de todos los modelos"""
        if not self.metadata:
            return {"total_sessions": 0}

        positive_rates = [m.get("feedback_positive_rate", 0.0) for m in self.metadata]

        return {
            "total_sessions": len(self.metadata),
            "best_positive_rate": max(positive_rates),
            "avg_positive_rate": sum(positive_rates) / len(positive_rates),
            "latest_session": self.metadata[-1]["session_id"],
            "improvement_trend": self._calculate_trend(positive_rates)
        }

    def _calculate_trend(self, values: List[float]) -> str:
        """Calcula tendencia de mejora"""
        if len(values) < 2:
            return "insufficient_data"

        recent = values[-3:]  # Últimas 3 sesiones
        if len(recent) < 2:
            return "insufficient_data"

        if all(recent[i] <= recent[i+1] for i in range(len(recent)-1)):
            return "improving"
        elif all(recent[i] >= recent[i+1] for i in range(len(recent)-1)):
            return "degrading"
        else:
            return "stable"

    def _load_metadata(self) -> List[Dict[str, Any]]:
        """Carga metadata de sesiones previas"""
        if not self.metadata_file.exists():
            return []

        with open(self.metadata_file, 'r') as f:
            return json.load(f)

    def _save_metadata(self):
        """Guarda metadata en disco"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
