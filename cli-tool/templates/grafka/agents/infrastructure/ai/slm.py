"""Trainable SLM wrapper for fine-tuning"""
import torch
import torch.nn as nn
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model

class TrainableSLM(nn.Module):
    """
    Wrapper around a Small Language Model (SLM) for fine-tuning.
    Supports LoRA for efficient training.
    """
    def __init__(self, model_name: str = "microsoft/phi-2", use_lora: bool = True, adapter_path: str = None):
        super().__init__()
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

        # Ensure pad token exists
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float32, # Use float32 for CPU compatibility by default
            device_map="auto",
            trust_remote_code=True
        )

        if adapter_path:
            print(f"📂 Loading LoRA adapter from: {adapter_path}")
            from peft import PeftModel
            self.model = PeftModel.from_pretrained(self.model, adapter_path)
            self.model.print_trainable_parameters()
        elif use_lora:
            self.setup_lora()

    def setup_lora(self):
        """Configure LoRA adapters"""
        # Detectar módulos target según la arquitectura del modelo
        if "phi" in self.model_name.lower():
            target_modules = ["Wqkv", "out_proj"]
        elif "gpt2" in self.model_name.lower() or "gpt-2" in self.model_name.lower():
            target_modules = ["c_attn", "c_proj"]  # GPT-2 usa estos nombres
        elif "llama" in self.model_name.lower() or "mistral" in self.model_name.lower():
            target_modules = ["q_proj", "v_proj", "k_proj", "o_proj"]
        else:
            # Default para modelos tipo Llama/Mistral
            target_modules = ["q_proj", "v_proj"]

        config = LoraConfig(
            r=8,
            lora_alpha=32,
            target_modules=target_modules,
            lora_dropout=0.05,
            bias="none",
            task_type="CAUSAL_LM"
        )
        self.model = get_peft_model(self.model, config)
        self.model.print_trainable_parameters()

    def reload_adapter(self, adapter_path: str):
        """Hot-reload a new LoRA adapter"""
        print(f"🔄 Hot-reloading adapter from: {adapter_path}")
        from peft import PeftModel
        import torch

        # Unload existing adapter if possible or just load over
        # For safety in PEFT, it's often best to reload base model or use set_adapter if multiple
        # But for simple single-adapter replacement:

        # 1. Move to CPU to avoid OOM during swap
        self.model.cpu()

        # 2. Load new adapter
        try:
            # If it's already a PeftModel, we can try load_adapter but simpler to re-wrap
            if isinstance(self.model, PeftModel):
                self.model.load_adapter(adapter_path, adapter_name="default")
            else:
                self.model = PeftModel.from_pretrained(self.model, adapter_path)

            # 3. Move back to device
            if torch.cuda.is_available():
                self.model.cuda()

            print(f"✅ Adapter reloaded successfully")
        except Exception as e:
            print(f"❌ Error reloading adapter: {e}")
            # Fallback: keep current model
            if torch.cuda.is_available():
                self.model.cuda()

    def forward(self, input_ids, attention_mask=None, labels=None):
        """Forward pass for training"""
        return self.model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels
        )

    def generate(self, prompt: str, max_new_tokens: int = 128) -> str:
        """Generate text from prompt"""
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            padding=True,
            truncation=True
        ).to(self.model.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                pad_token_id=self.tokenizer.pad_token_id,
                do_sample=True,
                temperature=0.7
            )

        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
