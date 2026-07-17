import tensorflow as tf
from transformers import TFAutoModel, AutoTokenizer
import numpy as np
import logging
import re

logger = logging.getLogger(__name__)

class BERTFeatureExtractor:
    """
    Loads 'bert-base-uncased' via TensorFlow and Hugging Face.
    Extracts dense feature embeddings for downstream classification tasks.
    """
    def __init__(self):
        logger.info("Initializing Hugging Face BERT model and tokenizer via TensorFlow.")
        self.tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
        self.model = TFAutoModel.from_pretrained('bert-base-uncased')
        logger.info("BERT model loaded successfully.")

    def extract_embedding(self, text: str) -> np.ndarray:
        """
        Tokenizes text and extracts the [CLS] token hidden state.
        The [CLS] token serves as an aggregate representation of the entire sequence.
        """
        if not text:
            text = "Empty text"
            
        inputs = self.tokenizer(
            text, 
            return_tensors='tf', 
            truncation=True, 
            padding=True, 
            max_length=128
        )
        
        outputs = self.model(inputs)
        # last_hidden_state shape: (batch_size, sequence_length, hidden_size)
        # We take the embedding of the first token ([CLS]) for classification.
        cls_embedding = outputs.last_hidden_state[:, 0, :].numpy()[0]
        return cls_embedding

    def extract_entities(self, text: str) -> dict:
        """
        Performs rule-based Named Entity Recognition (NER) to extract emails and phone numbers.
        Ensures functional entity extraction without requiring a fine-tuned NER head.
        """
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        phones = re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text)
        
        return {
            "emails": list(set(emails)),
            "phones": list(set(phones))
        }