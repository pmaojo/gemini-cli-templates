import logging
import uuid
from typing import Dict, Any, Optional
from enum import Enum
import asyncio

# Setup logging
logger = logging.getLogger(__name__)

class SLMStatus(Enum):
    PENDING = "Pending"
    TRAINING = "Training"
    READY = "Ready"
    FAILED = "Failed"
    STOPPED = "Stopped"

class SLMManager:
    """
    Manages Small Language Model (SLM) instances for tenants.
    Handles lifecycle: Creation, Training, Loading, Deletion.
    """

    def __init__(self, base_model_path: str = "microsoft/phi-2"):
        self.base_model_path = base_model_path
        # In-memory registry of active models (for demo purposes)
        # In production, this would be backed by Redis or similar
        self.active_models: Dict[str, Any] = {}

    async def create_instance(self, tenant_id: str, name: str) -> Dict[str, Any]:
        """
        Register a new SLM instance for a tenant.
        """
        instance_id = f"slm-{uuid.uuid4().hex[:8]}"
        logger.info(f"Creating SLM instance {instance_id} for tenant {tenant_id}")

        # Here we would interact with the Frappe backend to create the SLMInstance record
        # For now, we return the metadata
        return {
            "instance_id": instance_id,
            "tenant_id": tenant_id,
            "name": name,
            "status": SLMStatus.PENDING.value,
            "base_model": self.base_model_path
        }

    async def train_model(self, tenant_id: str, instance_id: str, training_data: list) -> str:
        """
        Trigger training for a tenant's SLM.
        """
        logger.info(f"Starting training for {instance_id} (Tenant: {tenant_id})")

        # Mock training process
        # In reality, this would submit a job to a queue (e.g., RQ/Celery)
        # using the ContinuousTrainer logic

        try:
            # Simulate training delay
            await asyncio.sleep(2)

            # Mock generating a new adapter path
            adapter_path = f"data/models/{tenant_id}/{instance_id}/adapter"

            logger.info(f"Training completed for {instance_id}. Adapter saved at {adapter_path}")
            return adapter_path

        except Exception as e:
            logger.error(f"Training failed for {instance_id}: {e}")
            raise e

    def load_model(self, tenant_id: str, instance_id: str) -> Any:
        """
        Load a specific SLM instance into memory.
        """
        model_key = f"{tenant_id}:{instance_id}"
        if model_key in self.active_models:
            return self.active_models[model_key]

        logger.info(f"Loading SLM {instance_id} for tenant {tenant_id}")

        # Here we would load the model using TrainableSLM or similar
        # For now, return a placeholder
        model = {"id": instance_id, "status": "loaded"}
        self.active_models[model_key] = model
        return model

    def unload_model(self, tenant_id: str, instance_id: str):
        """
        Unload model from memory to free resources.
        """
        model_key = f"{tenant_id}:{instance_id}"
        if model_key in self.active_models:
            del self.active_models[model_key]
            logger.info(f"Unloaded SLM {instance_id}")

    def get_status(self, tenant_id: str, instance_id: str) -> str:
        """
        Get the current status of an SLM instance.
        """
        # In a real system, query the database or job queue
        return SLMStatus.READY.value
