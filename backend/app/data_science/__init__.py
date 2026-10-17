"""Data science modules package (classification, clustering, association rules, analytics)."""

from backend.app.data_science.classifier import PaperClassifier
from backend.app.data_science.clustering import PaperClustering, ClusteringResult, ClusterSummary
from backend.app.data_science.association_rules import (
    KeywordAssociationMiner,
    AssociationMiningResult,
    AssociationRule,
    FrequentItemset,
)
from backend.app.data_science.analytics import ResearchAnalyticsService
from backend.app.data_science.service import DataScienceService

__all__ = [
    "PaperClassifier",
    "PaperClustering",
    "ClusteringResult",
    "ClusterSummary",
    "KeywordAssociationMiner",
    "AssociationMiningResult",
    "AssociationRule",
    "FrequentItemset",
    "ResearchAnalyticsService",
    "DataScienceService",
]
