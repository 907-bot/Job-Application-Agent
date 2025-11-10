"""
MAYINI Framework Model
Transformer-based Language Model implementation
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import List, Dict, Optional
import numpy as np


class MAYINIVocabulary:
    """Vocabulary management for MAYINI model"""
    
    def __init__(self, vocab_size: int = 5000):
        """
        Initialize vocabulary
        
        Args:
            vocab_size: Maximum vocabulary size
        """
        self.vocab_size = vocab_size
        
        # Special tokens
        self.word_to_id = {
            '<PAD>': 0,
            '<UNK>': 1,
            '<START>': 2,
            '<END>': 3,
            '<MASK>': 4,
        }
        
        # Add common resume/job terms
        common_terms = [
            # Programming languages
            'python', 'java', 'javascript', 'typescript', 'c++', 'go', 'rust', 'swift',
            # Frameworks & Libraries
            'react', 'angular', 'vue', 'django', 'flask', 'spring', 'nodejs', 'express',
            # DevOps & Cloud
            'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'jenkins', 'gitlab', 'terraform',
            # Databases
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
            # Actions
            'developed', 'implemented', 'designed', 'engineered', 'architected',
            'led', 'managed', 'coordinated', 'optimized', 'improved', 'accelerated',
            'launched', 'delivered', 'built', 'created', 'maintained', 'scaled',
            # Nouns
            'team', 'project', 'feature', 'product', 'system', 'application',
            'service', 'platform', 'infrastructure', 'api', 'microservice', 'database',
            # Adjectives
            'senior', 'junior', 'lead', 'principal', 'staff', 'full-stack', 'back-end', 'front-end',
            # General
            'experience', 'years', 'skills', 'proficiency', 'expertise', 'knowledge',
            'requirements', 'responsibilities', 'qualifications', 'benefits',
        ]
        
        idx = 5
        for term in common_terms:
            if idx < vocab_size:
                self.word_to_id[term] = idx
                idx += 1
        
        # Reverse mapping
        self.id_to_word = {v: k for k, v in self.word_to_id.items()}
        
        # Ensure vocab size is set
        self.current_vocab_size = len(self.word_to_id)
    
    def encode(self, text: str, max_len: int = 512) -> torch.Tensor:
        """
        Encode text to token IDs
        
        Args:
            text: Input text
            max_len: Maximum sequence length
            
        Returns:
            Tensor of token IDs
        """
        tokens = text.lower().split()
        token_ids = []
        
        for token in tokens[:max_len]:
            token_id = self.word_to_id.get(token, self.word_to_id['<UNK>'])
            token_ids.append(token_id)
        
        # Pad to max_len
        while len(token_ids) < max_len:
            token_ids.append(self.word_to_id['<PAD>'])
        
        return torch.tensor(token_ids[:max_len], dtype=torch.long)
    
    def decode(self, token_ids: torch.Tensor) -> str:
        """
        Decode token IDs to text
        
        Args:
            token_ids: Tensor of token IDs
            
        Returns:
            Decoded text string
        """
        if isinstance(token_ids, torch.Tensor):
            token_ids = token_ids.cpu().numpy().tolist()
        
        words = []
        for token in token_ids:
            word = self.id_to_word.get(int(token), '<UNK>')
            if not word.startswith('<'):
                words.append(word)
        
        return ' '.join(words)
    
    def batch_encode(self, texts: List[str], max_len: int = 512) -> torch.Tensor:
        """
        Encode batch of texts
        
        Args:
            texts: List of text strings
            max_len: Maximum sequence length
            
        Returns:
            Batch tensor of token IDs
        """
        encoded = [self.encode(text, max_len) for text in texts]
        return torch.stack(encoded)
    
    def batch_decode(self, token_ids_batch: torch.Tensor) -> List[str]:
        """
        Decode batch of token IDs
        
        Args:
            token_ids_batch: Batch tensor of token IDs
            
        Returns:
            List of decoded text strings
        """
        return [self.decode(ids) for ids in token_ids_batch]


class MAYINITransformerBlock(nn.Module):
    """Single transformer block for MAYINI model"""
    
    def __init__(self, hidden_dim: int, num_heads: int = 8, ff_dim: int = 1024, dropout: float = 0.1):
        """
        Initialize transformer block
        
        Args:
            hidden_dim: Hidden dimension size
            num_heads: Number of attention heads
            ff_dim: Feed-forward dimension
            dropout: Dropout rate
        """
        super().__init__()
        
        self.attention = nn.MultiheadAttention(
            embed_dim=hidden_dim,
            num_heads=num_heads,
            batch_first=True,
            dropout=dropout
        )
        
        self.feed_forward = nn.Sequential(
            nn.Linear(hidden_dim, ff_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(ff_dim, hidden_dim),
            nn.Dropout(dropout)
        )
        
        self.norm1 = nn.LayerNorm(hidden_dim)
        self.norm2 = nn.LayerNorm(hidden_dim)
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Forward pass through transformer block
        
        Args:
            x: Input tensor [batch, seq_len, hidden_dim]
            mask: Optional attention mask
            
        Returns:
            Output tensor [batch, seq_len, hidden_dim]
        """
        # Multi-head attention with residual
        attn_out, _ = self.attention(x, x, x, key_padding_mask=mask)
        x = self.norm1(x + self.dropout(attn_out))
        
        # Feed-forward with residual
        ff_out = self.feed_forward(x)
        x = self.norm2(x + ff_out)
        
        return x


class MAYINIModel(nn.Module):
    """Complete MAYINI Framework Transformer Model"""
    
    def __init__(
        self,
        vocab_size: int = 5000,
        hidden_dim: int = 256,
        num_heads: int = 8,
        num_layers: int = 4,
        max_seq_len: int = 512,
        dropout: float = 0.1
    ):
        """
        Initialize MAYINI model
        
        Args:
            vocab_size: Vocabulary size
            hidden_dim: Hidden dimension
            num_heads: Number of attention heads
            num_layers: Number of transformer layers
            max_seq_len: Maximum sequence length
            dropout: Dropout rate
        """
        super().__init__()
        
        self.vocab_size = vocab_size
        self.hidden_dim = hidden_dim
        self.num_heads = num_heads
        self.num_layers = num_layers
        self.max_seq_len = max_seq_len
        
        # Token embedding
        self.embedding = nn.Embedding(vocab_size, hidden_dim, padding_idx=0)
        
        # Positional encoding
        self.pos_embedding = nn.Embedding(max_seq_len, hidden_dim)
        
        # Transformer blocks
        self.transformer_layers = nn.ModuleList([
            MAYINITransformerBlock(hidden_dim, num_heads, hidden_dim * 4, dropout)
            for _ in range(num_layers)
        ])
        
        # Output projection
        self.output_layer = nn.Linear(hidden_dim, vocab_size)
        
        self.dropout = nn.Dropout(dropout)
        
        # Initialize weights
        self._init_weights()
    
    def _init_weights(self):
        """Initialize model weights"""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
            elif isinstance(module, nn.Embedding):
                nn.init.normal_(module.weight, mean=0.0, std=0.02)
    
    def forward(self, input_ids: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Forward pass through MAYINI model
        
        Args:
            input_ids: Input token IDs [batch, seq_len]
            mask: Optional padding mask
            
        Returns:
            Logits [batch, seq_len, vocab_size]
        """
        batch_size, seq_len = input_ids.shape
        
        # Token embeddings
        x = self.embedding(input_ids)
        
        # Positional embeddings
        positions = torch.arange(seq_len, device=input_ids.device).unsqueeze(0).expand(batch_size, -1)
        pos_emb = self.pos_embedding(positions)
        
        # Combine embeddings
        x = x + pos_emb
        x = self.dropout(x)
        
        # Pass through transformer layers
        for layer in self.transformer_layers:
            x = layer(x, mask)
        
        # Output projection
        logits = self.output_layer(x)
        
        return logits
    
    def generate(
        self,
        prompt: torch.Tensor,
        max_length: int = 50,
        temperature: float = 1.0,
        top_k: int = 50
    ) -> torch.Tensor:
        """
        Generate text continuation
        
        Args:
            prompt: Input prompt token IDs
            max_length: Maximum generation length
            temperature: Sampling temperature
            top_k: Top-k sampling parameter
            
        Returns:
            Generated token IDs
        """
        self.eval()
        generated = prompt.clone()
        
        with torch.no_grad():
            for _ in range(max_length):
                logits = self.forward(generated)
                next_token_logits = logits[:, -1, :] / temperature
                
                # Top-k sampling
                if top_k > 0:
                    indices_to_remove = next_token_logits < torch.topk(next_token_logits, top_k)[0][..., -1, None]
                    next_token_logits[indices_to_remove] = -float('Inf')
                
                # Sample from distribution
                probs = F.softmax(next_token_logits, dim=-1)
                next_token = torch.multinomial(probs, num_samples=1)
                
                # Append to generated sequence
                generated = torch.cat([generated, next_token], dim=1)
                
                # Stop if max length reached
                if generated.shape[1] >= self.max_seq_len:
                    break
        
        return generated
    
    def get_embeddings(self, input_ids: torch.Tensor) -> torch.Tensor:
        """
        Get contextual embeddings
        
        Args:
            input_ids: Input token IDs
            
        Returns:
            Embeddings [batch, seq_len, hidden_dim]
        """
        batch_size, seq_len = input_ids.shape
        
        # Token + positional embeddings
        x = self.embedding(input_ids)
        positions = torch.arange(seq_len, device=input_ids.device).unsqueeze(0).expand(batch_size, -1)
        pos_emb = self.pos_embedding(positions)
        x = x + pos_emb
        
        # Pass through transformer
        for layer in self.transformer_layers:
            x = layer(x)
        
        return x
    
    def count_parameters(self) -> int:
        """Count trainable parameters"""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)
    
    def save_model(self, path: str):
        """Save model state"""
        torch.save({
            'model_state_dict': self.state_dict(),
            'vocab_size': self.vocab_size,
            'hidden_dim': self.hidden_dim,
            'num_heads': self.num_heads,
            'num_layers': self.num_layers,
        }, path)
    
    def load_model(self, path: str):
        """Load model state"""
        checkpoint = torch.load(path, map_location='cpu')
        self.load_state_dict(checkpoint['model_state_dict'])
    
    def __repr__(self) -> str:
        """String representation"""
        return f"MAYINIModel(vocab={self.vocab_size}, hidden={self.hidden_dim}, layers={self.num_layers}, params={self.count_parameters():,})"
