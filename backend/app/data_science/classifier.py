"""Academic Text Classification Engine for ScholarPulse.

Adheres strictly to ScholarPulse SRS v1.0 Section 4 (FR-013, FR-018) & Section 8.7:
- Multinomial Naive Bayes, Logistic Regression, and Linear SVC classifiers
- Strict featurization ordering (split before fitting TF-IDF)
- Full academic evaluation metrics: Accuracy, Precision, Recall, Macro/Weighted F1, Confusion Matrix
- Category inference with probability/confidence scores
- Model comparison suite
- Artifact serialization with joblib and metadata JSON
"""

import os
import json
import time
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
)
import joblib


class PaperClassifier:
    """Supervised text classification pipeline for research paper categorisation."""

    SUPPORTED_MODELS = {"multinomial_nb", "logistic_regression", "linear_svc"}

    def __init__(self, model_version: str = "classifier-v1"):
        self.model_version = model_version
        self.model_type: Optional[str] = None
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.model: Optional[Any] = None
        self.classes: List[str] = []
        self.training_metrics: Dict[str, Any] = {}
        self.is_trained: bool = False

    def _create_estimator(self, model_type: str, random_state: int = 42) -> Any:
        """Instantiate scikit-learn classifier based on model_type."""
        if model_type == "multinomial_nb":
            return MultinomialNB(alpha=1.0)
        elif model_type == "logistic_regression":
            return LogisticRegression(
                max_iter=1000,
                random_state=random_state,
                C=1.0,
                solver="lbfgs",
            )
        elif model_type == "linear_svc":
            return LinearSVC(random_state=random_state, C=1.0, dual="auto")
        else:
            raise ValueError(
                f"Unsupported model_type: '{model_type}'. Supported: {self.SUPPORTED_MODELS}"
            )

    def train(
        self,
        documents: List[Dict[str, Any]],
        model_type: str = "multinomial_nb",
        test_size: float = 0.2,
        random_state: int = 42,
    ) -> Dict[str, Any]:
        """Train classifier with strict featurization ordering.

        Strict featurization rule: train/test split is performed BEFORE fitting
        the TF-IDF vectorizer to prevent target and feature leakage.

        Args:
            documents: List of paper dicts with 'title', optional 'abstract', and 'category'.
            model_type: 'multinomial_nb', 'logistic_regression', or 'linear_svc'.
            test_size: Ratio of documents held out for testing.
            random_state: Random seed for deterministic reproducibility.

        Returns:
            Dictionary containing evaluation metrics and confusion matrix.
        """
        if model_type not in self.SUPPORTED_MODELS:
            raise ValueError(
                f"Invalid model_type: '{model_type}'. Choose from {self.SUPPORTED_MODELS}"
            )

        # Prepare corpus texts and labels
        texts: List[str] = []
        labels: List[str] = []

        for doc in documents:
            category = doc.get("category")
            # Fallback if categories is a list
            if not category and doc.get("categories"):
                cats = doc.get("categories")
                category = cats[0] if isinstance(cats, list) and cats else None

            if not category:
                continue

            title = doc.get("title", "")
            abstract = doc.get("abstract", "") or ""
            combined_text = f"{title} {abstract}".strip()
            if not combined_text:
                continue

            texts.append(combined_text)
            labels.append(str(category))

        if len(texts) < 4:
            raise ValueError("At least 4 labeled documents are required to train a classifier.")

        # Determine if stratification is feasible
        label_counts: Dict[str, int] = {}
        for lbl in labels:
            label_counts[lbl] = label_counts.get(lbl, 0) + 1

        num_classes = len(label_counts)
        min_class_count = min(label_counts.values())

        # Scikit-learn requires test_size >= num_classes and train_size >= num_classes for stratified split
        approx_test_count = int(len(texts) * test_size) if isinstance(test_size, float) else test_size
        approx_train_count = len(texts) - approx_test_count
        stratify = (
            labels
            if min_class_count >= 2
            and approx_test_count >= num_classes
            and approx_train_count >= num_classes
            else None
        )

        # Train/test split performed BEFORE featurization
        X_train_raw, X_test_raw, y_train, y_test = train_test_split(
            texts,
            labels,
            test_size=test_size,
            random_state=random_state,
            stratify=stratify,
        )

        # Fit vectorizer strictly on training data
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=5000,
            sublinear_tf=True,
            stop_words="english",
        )
        X_train = self.vectorizer.fit_transform(X_train_raw)
        X_test = self.vectorizer.transform(X_test_raw)

        # Train estimator
        start_time = time.perf_counter()
        estimator = self._create_estimator(model_type, random_state=random_state)
        estimator.fit(X_train, y_train)
        training_duration = time.perf_counter() - start_time

        # Predict on test split
        y_pred = estimator.predict(X_test)

        # Unique classes
        unique_classes = sorted(list(set(labels)))
        self.classes = unique_classes
        self.model = estimator
        self.model_type = model_type
        self.is_trained = True

        # Calculate metrics
        acc = float(accuracy_score(y_test, y_pred))
        prec_macro = float(precision_score(y_test, y_pred, average="macro", zero_division=0))
        rec_macro = float(recall_score(y_test, y_pred, average="macro", zero_division=0))
        f1_mac = float(f1_score(y_test, y_pred, average="macro", zero_division=0))
        f1_weighted = float(f1_score(y_test, y_pred, average="weighted", zero_division=0))

        # Class-level metrics
        report_dict = classification_report(
            y_test,
            y_pred,
            labels=unique_classes,
            target_names=unique_classes,
            output_dict=True,
            zero_division=0,
        )
        conf_matrix = confusion_matrix(y_test, y_pred, labels=unique_classes).tolist()

        # Check train accuracy to monitor overfitting per ml-best-practices
        y_train_pred = estimator.predict(X_train)
        train_acc = float(accuracy_score(y_train, y_train_pred))

        self.training_metrics = {
            "model_version": self.model_version,
            "model_type": model_type,
            "total_documents": len(texts),
            "train_documents": len(y_train),
            "test_documents": len(y_test),
            "classes": unique_classes,
            "training_time_seconds": round(training_duration, 4),
            "train_accuracy": round(train_acc, 4),
            "test_accuracy": round(acc, 4),
            "precision_macro": round(prec_macro, 4),
            "recall_macro": round(rec_macro, 4),
            "f1_macro": round(f1_mac, 4),
            "f1_weighted": round(f1_weighted, 4),
            "per_class_metrics": {
                cls_name: {
                    "precision": round(report_dict.get(cls_name, {}).get("precision", 0.0), 4),
                    "recall": round(report_dict.get(cls_name, {}).get("recall", 0.0), 4),
                    "f1_score": round(report_dict.get(cls_name, {}).get("f1-score", 0.0), 4),
                    "support": int(report_dict.get(cls_name, {}).get("support", 0)),
                }
                for cls_name in unique_classes
            },
            "confusion_matrix": {
                "labels": unique_classes,
                "matrix": conf_matrix,
            },
        }

        return self.training_metrics

    def compare_models(
        self,
        documents: List[Dict[str, Any]],
        test_size: float = 0.2,
        random_state: int = 42,
    ) -> Dict[str, Any]:
        """Train and evaluate all supported models on identical splits for rigorous comparison."""
        results = {}
        for m_type in self.SUPPORTED_MODELS:
            metrics = self.train(
                documents=documents,
                model_type=m_type,
                test_size=test_size,
                random_state=random_state,
            )
            results[m_type] = {
                "test_accuracy": metrics["test_accuracy"],
                "f1_macro": metrics["f1_macro"],
                "f1_weighted": metrics["f1_weighted"],
                "training_time_seconds": metrics["training_time_seconds"],
            }

        # Select best model based on f1_macro
        best_model = max(results.keys(), key=lambda m: results[m]["f1_macro"])

        # Re-train with the best model to leave pipeline in optimal state
        self.train(
            documents=documents,
            model_type=best_model,
            test_size=test_size,
            random_state=random_state,
        )

        return {
            "comparison": results,
            "recommended_model": best_model,
            "best_f1_macro": results[best_model]["f1_macro"],
        }

    def predict(self, text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Predict top-k categories with probability/confidence scores."""
        if not self.is_trained or self.model is None or self.vectorizer is None:
            raise RuntimeError("Classifier has not been trained yet. Call train() or load() first.")

        cleaned_text = text.strip()
        if not cleaned_text:
            return []

        X = self.vectorizer.transform([cleaned_text])

        # Obtain probability estimates
        if hasattr(self.model, "predict_proba"):
            probs = self.model.predict_proba(X)[0]
        else:
            # Fallback for models without direct probability calibration (e.g. LinearSVC)
            decision = self.model.decision_function(X)
            if decision.ndim == 1 or (decision.ndim == 2 and decision.shape[1] == 1):
                d_val = float(decision[0]) if decision.ndim == 1 else float(decision[0][0])
                prob_pos = 1.0 / (1.0 + np.exp(-d_val))
                probs = np.array([1.0 - prob_pos, prob_pos])
            else:
                d = decision[0]
                exp_d = np.exp(d - np.max(d))
                probs = exp_d / exp_d.sum()

        scored_classes = [
            {"name": cls_name, "score": round(float(prob), 4)}
            for cls_name, prob in zip(self.model.classes_, probs)
        ]
        # Sort descending by score
        scored_classes.sort(key=lambda item: item["score"], reverse=True)
        return scored_classes[:top_k]

    def predict_paper(
        self, paper_id: str, title: str, abstract: Optional[str] = None, top_k: int = 3
    ) -> Dict[str, Any]:
        """Inference endpoint conforming strictly to ScholarPulse SRS v1.0 Section 8.7 contract."""
        combined_text = f"{title} {abstract or ''}".strip()
        predictions = self.predict(combined_text, top_k=top_k)
        return {
            "paper_id": str(paper_id),
            "predicted_categories": predictions,
            "model_version": self.model_version,
            "model_type": self.model_type,
        }

    def save(self, directory: str, filename_prefix: str = "classifier") -> Tuple[str, str]:
        """Serialize trained pipeline and metadata."""
        if not self.is_trained or self.model is None or self.vectorizer is None:
            raise RuntimeError("Cannot save an untrained classifier.")

        os.makedirs(directory, exist_ok=True)
        model_path = os.path.join(directory, f"{filename_prefix}.joblib")
        meta_path = os.path.join(directory, f"{filename_prefix}_metadata.json")

        pipeline_data = {
            "model_version": self.model_version,
            "model_type": self.model_type,
            "vectorizer": self.vectorizer,
            "model": self.model,
            "classes": self.classes,
        }
        joblib.dump(pipeline_data, model_path)

        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(self.training_metrics, f, indent=2)

        return model_path, meta_path

    def load(self, directory: str, filename_prefix: str = "classifier") -> None:
        """Load serialized pipeline from disk."""
        model_path = os.path.join(directory, f"{filename_prefix}.joblib")
        meta_path = os.path.join(directory, f"{filename_prefix}_metadata.json")

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model artifact not found at: {model_path}")

        pipeline_data = joblib.load(model_path)
        self.model_version = pipeline_data["model_version"]
        self.model_type = pipeline_data["model_type"]
        self.vectorizer = pipeline_data["vectorizer"]
        self.model = pipeline_data["model"]
        self.classes = pipeline_data["classes"]
        self.is_trained = True

        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                self.training_metrics = json.load(f)
