"""Dependency injection providers for ScholarPulse API routes.

Provides:
- Database sessions (get_db)
- Initialized SearchService singleton with automatic offline dataset hydration
- Initialized DataScienceService singleton with automatic artifact hydration
- Repository and domain service factories
"""

import os
import json
from typing import Optional
from fastapi import Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.core.logging import logger
from backend.app.retrieval.search_service import SearchService
from backend.app.data_science.service import DataScienceService
from backend.app.evaluation.retrieval_eval import RetrievalEvaluator
from backend.app.repositories.paper_repository import PaperRepository
from backend.app.repositories.category_repository import CategoryRepository
from backend.app.repositories.keyword_repository import KeywordRepository
from backend.app.ingestion.service import IngestionService

# Global singletons for fast in-memory query processing
_SEARCH_SERVICE_INSTANCE: Optional[SearchService] = None
_DS_SERVICE_INSTANCE: Optional[DataScienceService] = None


def get_search_service() -> SearchService:
    """Provide singleton SearchService, hydrating from artifacts or sample dataset."""
    global _SEARCH_SERVICE_INSTANCE
    if _SEARCH_SERVICE_INSTANCE is not None:
        return _SEARCH_SERVICE_INSTANCE

    indexes_dir = os.path.join("artifacts", "indexes")
    index_file = os.path.join(indexes_dir, "inverted_index.json")

    if os.path.exists(index_file):
        try:
            logger.info("Loading SearchService from persisted artifacts in %s", indexes_dir)
            _SEARCH_SERVICE_INSTANCE = SearchService.load(indexes_dir)
            return _SEARCH_SERVICE_INSTANCE
        except Exception as e:
            logger.warning("Failed to load existing index artifact (%s). Rebuilding...", e)

    service = SearchService()
    sample_dataset = os.path.join("datasets", "raw", "sample_papers.json")
    if os.path.exists(sample_dataset):
        logger.info("Hydrating SearchService from %s", sample_dataset)
        service.build_from_dataset(sample_dataset)
        try:
            service.save(indexes_dir)
        except Exception as e:
            logger.warning("Could not persist index to %s: %s", indexes_dir, e)

    _SEARCH_SERVICE_INSTANCE = service
    return _SEARCH_SERVICE_INSTANCE


def get_ds_service() -> DataScienceService:
    """Provide singleton DataScienceService, training models on sample data if needed."""
    global _DS_SERVICE_INSTANCE
    if _DS_SERVICE_INSTANCE is not None:
        return _DS_SERVICE_INSTANCE

    artifacts_dir = os.path.join("artifacts", "models")
    ds_service = DataScienceService(artifacts_dir=artifacts_dir)

    # Check if sample papers exist for initial fit
    sample_dataset = os.path.join("datasets", "raw", "sample_papers.json")
    if os.path.exists(sample_dataset):
        try:
            with open(sample_dataset, "r", encoding="utf-8") as f:
                papers = json.load(f)

            # 1. Fit recommender (populates papers_data for analytics and recommendations)
            try:
                ds_service.fit_recommender(papers)
            except Exception as e:
                logger.warning("Failed to fit recommender: %s", e)

            # 2. Train classifier
            try:
                ds_service.train_classifier(papers, model_type="multinomial_nb", test_size=0.2)
            except Exception as e:
                logger.warning("Failed to train classifier: %s", e)

            # 3. Fit clustering
            try:
                ds_service.cluster_corpus(papers, n_clusters=4, method="kmeans")
            except Exception as e:
                logger.warning("Failed to fit clustering: %s", e)

            # 4. Mine association rules
            try:
                ds_service.mine_association_rules(papers, min_support=0.08, min_confidence=0.3, min_lift=1.0)
            except Exception as e:
                logger.warning("Failed to mine association rules: %s", e)
        except Exception as e:
            logger.warning("Failed initial fit of DataScienceService: %s", e)

    _DS_SERVICE_INSTANCE = ds_service
    return _DS_SERVICE_INSTANCE


def get_evaluator() -> RetrievalEvaluator:
    """Provide RetrievalEvaluator configured with benchmark relevance judgments."""
    eval_file = os.path.join("datasets", "eval", "relevance_judgments.json")
    if os.path.exists(eval_file):
        return RetrievalEvaluator.from_json_file(eval_file)
    return RetrievalEvaluator(judgments=[], dataset_version="sample-v1")


def get_paper_repository(db: Session = Depends(get_db)) -> PaperRepository:
    """Provide PaperRepository for database access."""
    return PaperRepository(db)


def get_category_repository(db: Session = Depends(get_db)) -> CategoryRepository:
    """Provide CategoryRepository for database access."""
    return CategoryRepository(db)


def get_keyword_repository(db: Session = Depends(get_db)) -> KeywordRepository:
    """Provide KeywordRepository for database access."""
    return KeywordRepository(db)


def get_ingestion_service(db: Session = Depends(get_db)) -> IngestionService:
    """Provide IngestionService for batch imports."""
    return IngestionService(db)
