#!/usr/bin/env python3
"""
Train Model Script
Trains and validates the MAYINI model
Usage: python scripts/train_model.py [options]
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, Any

import torch
import torch.nn as nn
from torch.optim import Adam
from torch.utils.data import DataLoader

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Configuration
from src.mayini_model import MAYINIModel, MAYINIVocabulary


class ModelTrainer:
    """Trainer for MAYINI model"""
    
    def __init__(self, config: Configuration):
        """Initialize trainer"""
        self.config = config
        self.device = config.device
        self.logger = self._setup_logging()
        
        # Create model
        model_config = config.get_model_config()
        self.model = MAYINIModel(
            vocab_size=model_config['vocab_size'],
            hidden_dim=model_config['hidden_dim'],
            num_heads=model_config['num_heads'],
            num_layers=model_config['num_layers'],
            max_seq_len=model_config['max_seq_length'],
            dropout=model_config['dropout_rate']
        ).to(self.device)
        
        # Optimizer
        training_config = config.get_training_config()
        self.optimizer = Adam(
            self.model.parameters(),
            lr=training_config['learning_rate'],
            weight_decay=training_config['weight_decay']
        )
        
        # Loss function
        self.criterion = nn.CrossEntropyLoss()
        
        self.logger.info(f"Model initialized with {self.model.count_parameters():,} parameters")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger('train_model')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def train_epoch(self, train_loader: DataLoader, epoch: int) -> float:
        """Train for one epoch"""
        self.model.train()
        total_loss = 0.0
        
        for batch_idx, (inputs, targets) in enumerate(train_loader):
            inputs = inputs.to(self.device)
            targets = targets.to(self.device)
            
            # Forward pass
            self.optimizer.zero_grad()
            outputs = self.model(inputs)
            
            # Calculate loss
            loss = self.criterion(outputs.view(-1, self.config.model_config['vocab_size']), targets.view(-1))
            
            # Backward pass
            loss.backward()
            
            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(
                self.model.parameters(),
                self.config.training_config['gradient_clip']
            )
            
            # Optimization step
            self.optimizer.step()
            
            total_loss += loss.item()
            
            if (batch_idx + 1) % 10 == 0:
                avg_loss = total_loss / (batch_idx + 1)
                self.logger.info(
                    f"Epoch {epoch} | Batch {batch_idx + 1} | "
                    f"Loss: {avg_loss:.4f}"
                )
        
        return total_loss / len(train_loader)
    
    def validate(self, val_loader: DataLoader) -> float:
        """Validate model"""
        self.model.eval()
        total_loss = 0.0
        
        with torch.no_grad():
            for inputs, targets in val_loader:
                inputs = inputs.to(self.device)
                targets = targets.to(self.device)
                
                outputs = self.model(inputs)
                loss = self.criterion(
                    outputs.view(-1, self.config.model_config['vocab_size']),
                    targets.view(-1)
                )
                total_loss += loss.item()
        
        return total_loss / len(val_loader)
    
    def save_checkpoint(self, filepath: str, epoch: int, loss: float):
        """Save model checkpoint"""
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'loss': loss,
            'config': self.config.to_dict(),
        }
        
        torch.save(checkpoint, filepath)
        self.logger.info(f"Checkpoint saved: {filepath}")
    
    def load_checkpoint(self, filepath: str):
        """Load model checkpoint"""
        checkpoint = torch.load(filepath, map_location=self.device)
        
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        
        self.logger.info(f"Checkpoint loaded: {filepath}")
        return checkpoint['epoch'], checkpoint['loss']
    
    def train(self, train_loader: DataLoader, val_loader: DataLoader, num_epochs: int):
        """Train model for specified epochs"""
        self.logger.info(f"Starting training for {num_epochs} epochs")
        
        best_val_loss = float('inf')
        checkpoint_dir = Path(self.config.paths['checkpoint_dir'])
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        for epoch in range(1, num_epochs + 1):
            self.logger.info(f"\n{'='*50}")
            self.logger.info(f"Epoch {epoch}/{num_epochs}")
            self.logger.info(f"{'='*50}")
            
            # Train
            train_loss = self.train_epoch(train_loader, epoch)
            self.logger.info(f"Training Loss: {train_loss:.4f}")
            
            # Validate
            val_loss = self.validate(val_loader)
            self.logger.info(f"Validation Loss: {val_loss:.4f}")
            
            # Save checkpoint
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                checkpoint_path = checkpoint_dir / f"best_model_epoch_{epoch}.pt"
                self.save_checkpoint(str(checkpoint_path), epoch, val_loss)
                self.logger.info(f"New best model saved!")
        
        self.logger.info(f"\nTraining completed!")
        self.logger.info(f"Best validation loss: {best_val_loss:.4f}")


def main():
    """Main training function"""
    parser = argparse.ArgumentParser(description='Train MAYINI model')
    parser.add_argument(
        '--epochs',
        type=int,
        default=10,
        help='Number of training epochs (default: 10)'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=32,
        help='Batch size (default: 32)'
    )
    parser.add_argument(
        '--learning-rate',
        type=float,
        default=0.0001,
        help='Learning rate (default: 0.0001)'
    )
    parser.add_argument(
        '--checkpoint',
        type=str,
        help='Load checkpoint to resume training'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config/config.yaml',
        help='Configuration file path'
    )
    
    args = parser.parse_args()
    
    # Setup
    config = Configuration()
    trainer = ModelTrainer(config)
    
    # Log training configuration
    trainer.logger.info("Training Configuration:")
    trainer.logger.info(f"  Device: {trainer.device}")
    trainer.logger.info(f"  Epochs: {args.epochs}")
    trainer.logger.info(f"  Batch Size: {args.batch_size}")
    trainer.logger.info(f"  Learning Rate: {args.learning_rate}")
    
    # Create dummy data loaders for demonstration
    trainer.logger.info("\nCreating dummy data loaders for demonstration...")
    
    # Dummy training data
    train_data = [(torch.randint(0, 5000, (512,)), torch.randint(0, 5000, (512,))) 
                  for _ in range(100)]
    train_loader = DataLoader(train_data, batch_size=args.batch_size, shuffle=True)
    
    # Dummy validation data
    val_data = [(torch.randint(0, 5000, (512,)), torch.randint(0, 5000, (512,))) 
                for _ in range(20)]
    val_loader = DataLoader(val_data, batch_size=args.batch_size)
    
    trainer.logger.info(f"Training samples: {len(train_data)}")
    trainer.logger.info(f"Validation samples: {len(val_data)}")
    
    # Train
    try:
        trainer.train(train_loader, val_loader, args.epochs)
        trainer.logger.info("\n✅ Training completed successfully!")
        return 0
    except KeyboardInterrupt:
        trainer.logger.info("\n⚠️  Training interrupted by user")
        return 1
    except Exception as e:
        trainer.logger.error(f"\n❌ Training failed with error: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
