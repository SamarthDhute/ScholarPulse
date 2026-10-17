"""ScholarPulse Evaluation Module."""

from backend.app.evaluation.retrieval_eval import (
    RetrievalEvaluator,
    EvaluationSummary,
    QueryEvaluationResult,
    compute_precision_at_k,
    compute_recall_at_k,
    compute_average_precision,
    compute_reciprocal_rank,
    compute_dcg_at_k,
    compute_ndcg_at_k,
)

__all__ = [
    "RetrievalEvaluator",
    "EvaluationSummary",
    "QueryEvaluationResult",
    "compute_precision_at_k",
    "compute_recall_at_k",
    "compute_average_precision",
    "compute_reciprocal_rank",
    "compute_dcg_at_k",
    "compute_ndcg_at_k",
]
