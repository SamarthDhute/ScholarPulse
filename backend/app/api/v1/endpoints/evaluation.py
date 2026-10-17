import os
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, status

from backend.app.schemas.evaluation import EvaluationResponse, EvaluationReportItem
from backend.app.retrieval.search_service import SearchService
from backend.app.evaluation.retrieval_eval import RetrievalEvaluator
from backend.app.api.deps import get_search_service, get_evaluator

router = APIRouter()


@router.get(
    "/evaluation/retrieval",
    response_model=EvaluationResponse,
    status_code=status.HTTP_200_OK,
    summary="Benchmark and compare Information Retrieval algorithms",
)
def evaluate_retrieval_models(
    search_service: SearchService = Depends(get_search_service),
    evaluator: RetrievalEvaluator = Depends(get_evaluator),
) -> EvaluationResponse:
    """Benchmark BM25, TF-IDF, and Language Model against ground-truth judgments."""
    judgments = evaluator.get_evaluated_queries()
    if not judgments:
        eval_file = os.path.join("datasets", "eval", "relevance_judgments.json")
        if os.path.exists(eval_file):
            judgments = evaluator.load_judgments(eval_file)

    reports = []
    for method in ["bm25", "tfidf", "language_model"]:
        summary = evaluator.evaluate_ranker(
            search_service=search_service,
            method=method,
            benchmark_queries=judgments,
        )
        reports.append(
            EvaluationReportItem(
                ranker_name=summary.method,
                num_queries=summary.num_queries,
                mean_average_precision=summary.map_score,
                mean_reciprocal_rank=summary.mrr_score,
                precision_at_k={str(k): v for k, v in summary.mean_precision_at_k.items()},
                recall_at_k={str(k): v for k, v in summary.mean_recall_at_k.items()},
                ndcg_at_k={str(k): v for k, v in summary.mean_ndcg_at_k.items()},
            )
        )

    return EvaluationResponse(
        dataset_version=evaluator.dataset_version or "v1.0",
        query_count=len(judgments),
        reports=reports,
    )
