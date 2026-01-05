"""
LLM Teacher - Usa Gemini/GPT para generar datos de entrenamiento de alta calidad
Corrige errores y genera variaciones de ejemplos exitosos
"""
import json
import os
from typing import List, Dict, Tuple, Optional, Any
import litellm

class LLMTeacher:
    """
    Usa un LLM grande (Gemini/GPT) para:
    1. Corregir salidas incorrectas (feedback negativo)
    2. Generar variaciones de ejemplos exitosos (feedback positivo)
    3. Aumentar datos de entrenamiento
    """

    def __init__(self, model: str = None):
        self.model = model or os.getenv("GEMINI_MODEL", "gemini/gemini-2.5-flash")
        print(f"🎓 LLM Teacher inicializado con modelo: {self.model}")

    def correct_negative_feedback(
        self,
        input_text: str,
        wrong_output: str
    ) -> Optional[Dict[str, Any]]:
        """
        Corrige una salida incorrecta usando el LLM

        Args:
            input_text: Texto de entrada original
            wrong_output: Salida incorrecta del modelo

        Returns:
            Dict con la versión corregida o None si falla
        """
        prompt = f"""Eres un experto en extracción de triples RDF del dominio de agricultura y permacultura.

Un modelo pequeño generó esta salida INCORRECTA:

Input: {input_text}
Output Incorrecto: {wrong_output}

Por favor, genera la versión CORRECTA de los triples extraídos.

Formato de respuesta (JSON):
{{
    "triples": [["subject", "predicate", "object"], ...],
    "explanation": "breve explicación de la corrección"
}}

Reglas:
- Usa términos del dominio de agricultura/permacultura
- Predicados en inglés (e.g., "improves", "captures", "produces")
- Sujetos y objetos pueden estar en español o inglés
"""

        try:
            response = litellm.completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )

            content = response.choices[0].message.content

            # Limpiar markdown si existe
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            corrected = json.loads(content)

            print(f"✅ LLM Teacher corrigió: {corrected['triples']}")

            return {
                "input": input_text,
                "output": str(corrected["triples"]),
                "explanation": corrected.get("explanation", ""),
                "source": "llm_teacher_correction"
            }

        except Exception as e:
            print(f"❌ Error en corrección LLM: {e}")
            return None

    def generate_variations(
        self,
        input_text: str,
        correct_output: str,
        num_variations: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Genera variaciones de un ejemplo exitoso

        Args:
            input_text: Texto de entrada exitoso
            correct_output: Salida correcta del modelo
            num_variations: Número de variaciones a generar

        Returns:
            Lista de variaciones generadas
        """
        prompt = f"""Eres un experto en agricultura y permacultura.

Este es un ejemplo EXITOSO de extracción de triples:

Input: {input_text}
Output: {correct_output}

Genera {num_variations} variaciones SIMILARES del mismo dominio (agricultura, permacultura, compost, swales, etc.).

Formato de respuesta (JSON):
{{
    "variations": [
        {{
            "input": "nuevo texto en español",
            "triples": [["subject", "predicate", "object"], ...]
        }},
        ...
    ]
}}

Reglas:
- Mantén el mismo estilo y complejidad
- Usa conceptos del dominio de permacultura
- Variedad en los temas (compost, agua, suelo, plantas, etc.)
"""

        try:
            response = litellm.completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7  # Más creatividad para variaciones
            )

            content = response.choices[0].message.content

            # Limpiar markdown
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            result = json.loads(content)
            variations = result.get("variations", [])

            # Formatear para entrenamiento
            formatted = []
            for var in variations:
                formatted.append({
                    "input": var["input"],
                    "output": str(var["triples"]),
                    "source": "llm_teacher_variation"
                })

            print(f"✨ LLM Teacher generó {len(formatted)} variaciones")

            return formatted

        except Exception as e:
            print(f"❌ Error generando variaciones: {e}")
            return []

    def augment_training_data(
        self,
        positive_examples: List[Dict[str, Any]],
        negative_examples: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Aumenta datos de entrenamiento usando ejemplos positivos y negativos

        Args:
            positive_examples: Ejemplos con feedback positivo
            negative_examples: Ejemplos con feedback negativo

        Returns:
            Lista de ejemplos aumentados listos para entrenamiento
        """
        augmented_data = []

        # Corregir ejemplos negativos
        print(f"\n🔧 Corrigiendo {len(negative_examples)} ejemplos negativos...")
        for i, neg_ex in enumerate(negative_examples[:10]):  # Limitar a 10 para no gastar muchos tokens
            corrected = self.correct_negative_feedback(
                neg_ex["input"],
                neg_ex["output"]
            )
            if corrected:
                augmented_data.append(corrected)

            if (i + 1) % 5 == 0:
                print(f"  Procesados {i + 1}/{min(10, len(negative_examples))}")

        # Generar variaciones de ejemplos positivos
        print(f"\n✨ Generando variaciones de {len(positive_examples)} ejemplos positivos...")
        for i, pos_ex in enumerate(positive_examples[:5]):  # Limitar a 5
            variations = self.generate_variations(
                pos_ex["input"],
                pos_ex["output"],
                num_variations=2
            )
            augmented_data.extend(variations)

            if (i + 1) % 3 == 0:
                print(f"  Procesados {i + 1}/{min(5, len(positive_examples))}")

        print(f"\n📊 Total de ejemplos aumentados: {len(augmented_data)}")

        return augmented_data
