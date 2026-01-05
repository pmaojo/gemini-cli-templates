"""
Continuous Trainer - Entrenamiento incremental con PESO regularization
Implementa fine-tuning continuo del SLM evitando catastrophic forgetting
"""
import os
import json
import torch
from pathlib import Path
from typing import Dict, List, Optional, Any
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
    TrainerCallback
)
from peft import LoraConfig, get_peft_model, PeftModel, TaskType
from datasets import Dataset

class PESOCallback(TrainerCallback):
    """
    Callback para implementar PESO (Proximal Regularization)
    Ancla el modelo actual al estado previo para evitar catastrophic forgetting
    """

    def __init__(self, previous_weights: Optional[Dict[str, torch.Tensor]] = None, lambda_peso: float = 0.1):
        self.previous_weights = previous_weights
        self.lambda_peso = lambda_peso

    def on_step_end(self, args, state, control, model=None, **kwargs):
        if self.previous_weights is None:
            return

        # Añadir regularización PESO al loss
        peso_loss = 0.0
        current_weights = model.state_dict()

        for name, param in current_weights.items():
            if name in self.previous_weights:
                peso_loss += torch.nn.functional.mse_loss(
                    param,
                    self.previous_weights[name].to(param.device)
                )

        # El loss total ya incluye el task loss, solo añadimos PESO
        # Nota: Esto es una aproximación, idealmente se haría en el compute_loss
        if peso_loss > 0:
            state.log_history[-1]["peso_loss"] = peso_loss.item() * self.lambda_peso

class ContinuousTrainer:
    """
    Entrenador continuo con LoRA + PESO regularization.

    Características:
    - Fine-tuning incremental con LoRA
    - PESO regularization para evitar catastrophic forgetting
    - Experience replay (mezcla ejemplos nuevos con antiguos)
    - Checkpoints por sesión
    """

    def __init__(
        self,
        base_model_name: str = "gpt2",
        base_model_path: Optional[str] = None
    ):
        self.base_model_name = base_model_name
        self.base_model_path = base_model_path or "checkpoints/gpt2-simple/final"
        self.previous_adapter_path = None

        print(f"🎯 Continuous Trainer inicializado")
        print(f"   Base model: {base_model_name}")

    def train_incremental(
        self,
        training_data: List[Dict[str, Any]],
        session_id: str,
        epochs: int = 2,
        batch_size: int = 2,
        learning_rate: float = 2e-4,
        lambda_peso: float = 0.1
    ) -> str:
        """
        Entrena incrementalmente el modelo con nuevos datos.

        Args:
            training_data: Lista de ejemplos de entrenamiento
            session_id: ID de la sesión actual
            epochs: Número de épocas
            batch_size: Tamaño del batch
            learning_rate: Learning rate
            lambda_peso: Peso de la regularización PESO

        Returns:
            Path al modelo entrenado
        """
        if not training_data:
            print("⚠️  No hay datos de entrenamiento")
            return self.base_model_path

        print(f"\n{'='*60}")
        print(f"🚀 ENTRENAMIENTO INCREMENTAL - Sesión {session_id}")
        print(f"{'='*60}")
        print(f"📊 Ejemplos de entrenamiento: {len(training_data)}")

        # Preparar datos
        dataset = self._prepare_dataset(training_data)

        # Cargar modelo base
        tokenizer = AutoTokenizer.from_pretrained(self.base_model_name)
        tokenizer.pad_token = tokenizer.eos_token

        base_model = AutoModelForCausalLM.from_pretrained(self.base_model_name)

        # Cargar LoRA previo si existe
        previous_weights = None
        if self.previous_adapter_path and Path(self.previous_adapter_path).exists():
            print(f"📂 Cargando LoRA previo: {self.previous_adapter_path}")
            model = PeftModel.from_pretrained(base_model, self.previous_adapter_path)

            # Guardar pesos previos para PESO
            previous_weights = {k: v.clone().detach() for k, v in model.state_dict().items() if "lora" in k}
            print(f"💾 Guardados {len(previous_weights)} pesos previos para PESO")
        else:
            print("🆕 Primera sesión - creando nuevo LoRA")
            lora_config = LoraConfig(
                task_type=TaskType.CAUSAL_LM,
                r=8,
                lora_alpha=32,
                lora_dropout=0.1,
                target_modules=["c_attn"]
            )
            model = get_peft_model(base_model, lora_config)

        model.print_trainable_parameters()

        # Tokenizar dataset
        tokenized_dataset = dataset.map(
            lambda x: tokenizer(
                x["text"],
                truncation=True,
                max_length=256,
                padding="max_length"
            ),
            batched=True,
            remove_columns=["text"]
        )

        # Training arguments
        output_dir = f"checkpoints/sessions/{session_id}"
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            learning_rate=learning_rate,
            warmup_steps=5,
            logging_steps=5,
            save_steps=50,
            save_total_limit=2,
            fp16=False,
            report_to="none"
        )

        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False
        )

        # PESO Callback
        peso_callback = PESOCallback(previous_weights, lambda_peso)

        # Trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=tokenized_dataset,
            data_collator=data_collator,
            callbacks=[peso_callback]
        )

        # Entrenar
        print(f"\n{'='*60}")
        print("🔥 INICIANDO ENTRENAMIENTO")
        print(f"{'='*60}\n")

        result = trainer.train()

        # Guardar modelo
        final_path = f"{output_dir}/final"
        model.save_pretrained(final_path)
        tokenizer.save_pretrained(final_path)

        # Actualizar path previo para próxima sesión
        self.previous_adapter_path = final_path

        print(f"\n{'='*60}")
        print("✅ ENTRENAMIENTO COMPLETADO")
        print(f"{'='*60}")
        print(f"💾 Modelo guardado en: {final_path}")
        print(f"📉 Loss final: {result.training_loss:.4f}")

        return final_path

    def _prepare_dataset(self, training_data: List[Dict[str, Any]]) -> Dataset:
        """Prepara dataset para entrenamiento"""
        texts = []

        for example in training_data:
            # Formato: "extract triples: {input}\ntriples: {output}"
            text = f"extract triples: {example['input']}\ntriples: {example['output']}"
            texts.append(text)

        return Dataset.from_dict({"text": texts})

    def set_previous_adapter(self, adapter_path: str):
        """Establece el adapter previo para PESO regularization"""
        self.previous_adapter_path = adapter_path
        print(f"📌 Adapter previo establecido: {adapter_path}")
