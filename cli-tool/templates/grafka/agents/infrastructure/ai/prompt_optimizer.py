"""
Prompt Optimizer - Optimización automática de prompts basada en feedback
Implementa OPRO (Optimization by PROmpting) para mejorar instrucciones del sistema
"""
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import litellm

class PromptOptimizer:
    """
    Optimiza los prompts del sistema basándose en el historial de errores.
    Usa un meta-prompt para reescribir instrucciones y reducir fallos recurrentes.
    """

    def __init__(self, prompts_dir: str = "prompts", model: str = None):
        self.prompts_dir = Path(prompts_dir)
        self.prompts_dir.mkdir(parents=True, exist_ok=True)
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-3-flash")

        # Cargar prompts actuales o crear defaults
        self.current_prompts = self._load_prompts()

    def optimize_prompt(
        self,
        prompt_name: str,
        negative_examples: List[Dict[str, Any]],
        positive_examples: List[Dict[str, Any]]
    ) -> str:
        """
        Optimiza un prompt específico usando ejemplos de fallos y éxitos.

        Args:
            prompt_name: Nombre del prompt (ej: "extraction_system_prompt")
            negative_examples: Lista de ejemplos donde el modelo falló
            positive_examples: Lista de ejemplos exitosos

        Returns:
            Nuevo prompt optimizado
        """
        current_prompt = self.current_prompts.get(prompt_name, "")

        if not current_prompt:
            print(f"⚠️ Prompt {prompt_name} no encontrado. Saltando optimización.")
            return ""

        print(f"🔄 Optimizando prompt: {prompt_name}...")

        # Construir meta-prompt para el optimizador
        meta_prompt = f"""Eres un experto en ingeniería de prompts (Prompt Engineering).
Tu objetivo es mejorar el siguiente prompt del sistema para reducir errores.

PROMPT ACTUAL:
\"\"\"{current_prompt}\"\"\"

EJEMPLOS DE FALLOS (Feedback Negativo):
{self._format_examples(negative_examples[:5])}

EJEMPLOS DE ÉXITO (Feedback Positivo):
{self._format_examples(positive_examples[:3])}

TAREA:
1. Analiza por qué falló el modelo en los ejemplos negativos.
2. Reescribe el prompt para prevenir estos errores específicos.
3. Mantén las partes que funcionaron bien en los ejemplos positivos.
4. Sé claro, directo y usa técnicas como Chain-of-Thought si ayuda.

Devuelve SOLO el nuevo prompt optimizado, sin explicaciones extra.
"""

        try:
            response = litellm.completion(
                model=self.model,
                messages=[{"role": "user", "content": meta_prompt}],
                temperature=0.4
            )

            new_prompt = response.choices[0].message.content.strip()

            # Limpiar comillas si el LLM las añadió
            if new_prompt.startswith('"') and new_prompt.endswith('"'):
                new_prompt = new_prompt[1:-1]

            # Guardar nueva versión
            self._save_prompt_version(prompt_name, new_prompt)
            self.current_prompts[prompt_name] = new_prompt

            print(f"✨ Prompt optimizado guardado. Longitud: {len(new_prompt)} chars")
            return new_prompt

        except Exception as e:
            print(f"❌ Error optimizando prompt: {e}")
            return current_prompt

    def get_prompt(self, prompt_name: str) -> str:
        """Obtiene el prompt actual"""
        return self.current_prompts.get(prompt_name, "")

    def _format_examples(self, examples: List[Dict[str, Any]]) -> str:
        """Formatea ejemplos para el meta-prompt"""
        formatted = ""
        for i, ex in enumerate(examples, 1):
            formatted += f"Ejemplo {i}:\n"
            formatted += f"Input: {ex.get('input', '')}\n"
            formatted += f"Output Generado: {ex.get('output', '')}\n"
            if 'explanation' in ex:
                formatted += f"Error: {ex['explanation']}\n"
            formatted += "---\n"
        return formatted

    def _load_prompts(self) -> Dict[str, str]:
        """Carga prompts desde disco"""
        prompts = {}
        # Si no hay archivos, crear defaults
        default_extraction = """Eres un experto en agricultura regenerativa y permacultura.
Tu tarea es extraer conocimiento estructurado del texto proporcionado.
Genera triples RDF en formato JSON: [["sujeto", "predicado", "objeto"]].
Usa predicados en inglés (e.g., "improves", "requires", "produces").
Mantén los sujetos y objetos en su idioma original o inglés."""

        extraction_path = self.prompts_dir / "extraction_system_prompt.txt"
        if not extraction_path.exists():
            with open(extraction_path, 'w') as f:
                f.write(default_extraction)
            prompts["extraction_system_prompt"] = default_extraction
        else:
            with open(extraction_path, 'r') as f:
                prompts["extraction_system_prompt"] = f.read()

        return prompts

    def _save_prompt_version(self, name: str, content: str):
        """Guarda una versión del prompt con timestamp"""
        # Guardar actual
        with open(self.prompts_dir / f"{name}.txt", 'w') as f:
            f.write(content)

        # Guardar histórico
        history_dir = self.prompts_dir / "history"
        history_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(history_dir / f"{name}_{timestamp}.txt", 'w') as f:
            f.write(content)
