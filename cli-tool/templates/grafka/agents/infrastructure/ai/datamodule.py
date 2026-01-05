"""DataModule for training data"""
import json
from pathlib import Path
from typing import List, Dict, Any
import lightning as L
from torch.utils.data import Dataset, DataLoader

class TripleExtractionDataset(Dataset):
    """Dataset for triple extraction training"""

    def __init__(self, data_path: str):
        self.data = []
        with open(data_path, 'r', encoding='utf-8') as f:
            for line in f:
                self.data.append(json.loads(line))

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx]

class SemanticDataModule(L.LightningDataModule):
    """Lightning DataModule for semantic system training"""

    def __init__(
        self,
        train_path: str = "data/train.jsonl",
        val_path: str = "data/val.jsonl",
        batch_size: int = 4
    ):
        super().__init__()
        self.train_path = train_path
        self.val_path = val_path
        self.batch_size = batch_size

    def setup(self, stage: str = None):
        if stage == "fit" or stage is None:
            self.train_dataset = TripleExtractionDataset(self.train_path)
            self.val_dataset = TripleExtractionDataset(self.val_path)

    def train_dataloader(self):
        return DataLoader(
            self.train_dataset,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=0,  # 0 para evitar problemas con multiprocessing
            collate_fn=self.collate_fn
        )

    def val_dataloader(self):
        return DataLoader(
            self.val_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=0,
            collate_fn=self.collate_fn
        )

    @staticmethod
    def collate_fn(batch):
        """Custom collate function to handle variable length data"""
        return batch  # Return as list of dicts
