import numpy as np
from sklearn.ensemble import RandomForestClassifier
import logging

logger = logging.getLogger(__name__)

class LeadScorer:
    """
    Trains a Scikit-learn Random Forest classifier on BERT embeddings.
    The model is trained on synthetic baseline data on initialization to ensure
    immediate operational capability without an external dataset.
    """
    def __init__(self, embedding_size: int = 768):
        logger.info("Initializing Scikit-learn Lead Scorer.")
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self._train_baseline(embedding_size)
        
    def _train_baseline(self, embedding_size: int):
        """
        Generates synthetic embeddings to train the classifier.
        Simulates a distribution where higher magnitude vectors correlate with higher lead quality.
        """
        logger.info("Training Random Forest classifier with synthetic baseline data.")
        
        # Generate 500 synthetic samples
        X_train = np.random.rand(500, embedding_size)
        
        # Assign labels based on a dummy heuristic (e.g., vector magnitude)
        magnitudes = np.linalg.norm(X_train, axis=1)
        y_train = np.where(
            magnitudes > np.percentile(magnitudes, 66), 'High',
            np.where(magnitudes > np.percentile(magnitudes, 33), 'Medium', 'Low')
        )
        
        self.model.fit(X_train, y_train)
        logger.info("Lead Scorer trained and ready for predictions.")

    def predict_score(self, embedding: np.ndarray) -> str:
        """
        Predicts the lead score based on the provided BERT embedding.
        """
        if embedding.ndim == 1:
            embedding = embedding.reshape(1, -1)
            
        prediction = self.model.predict(embedding)
        return prediction[0]