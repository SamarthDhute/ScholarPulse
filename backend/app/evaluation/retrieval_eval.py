"""Objective Information Retrieval Evaluation Harness.

Computes academic IR evaluation metrics according to TREC and standard IR methodology:
- Precision at K (P@K)
- Recall at K (Recall@K)
- Average Precision (AP) and Mean Average Precision (MAP)
- Mean Reciprocal Rank (MRR)
- Discounted Cumulative Gain (DCG@K)
- Normalized Discounted Cumulative Gain (NDCG@K)
- Multi-ranker comparative benchmarking
"""

import json
import math
import os
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any

from backend.app.retrieval.search_service import SearchService


def compute_precision_at_k(retrieved_ids: List[str], relevant_ids: Set[str], k: int) -> float:
    """Compute Precision@K = |Retrieved@K ∩ Relevant| / K."""
    if k <= 0:
        return 0.0
    cutoff = retrieved_ids[:k]
    num_relevant_retrieved = sum(1 for doc_id in cutoff if doc_id in relevant_ids)
    return num_relevant_retrieved / float(k)


def compute_recall_at_k(retrieved_ids: List[str], relevant_ids: Set[str], k: int) -> float:
    """Compute Recall@K = |Retrieved@K ∩ Relevant| / |Relevant|."""
    if not relevant_ids or k <= 0:
        return 0.0
    cutoff = retrieved_ids[:k]
    num_relevant_retrieved = sum(1 for doc_id in cutoff if doc_id in relevant_ids)
    return num_relevant_retrieved / float(len(relevant_ids))


def compute_average_precision(retrieved_ids: List[str], relevant_ids: Set[str]) -> float:
    """Compute Average Precision (AP) for a single query."""
    if not relevant_ids or not retrieved_ids:
        return 0.0

    hit_count = 0
    sum_precisions = 0.0

    for rank, doc_id in enumerate(retrieved_ids, start=1):
        if doc_id in relevant_ids:
            hit_count += 1
            sum_precisions += hit_count / float(rank)

    return sum_precisions / float(len(relevant_ids))


def compute_reciprocal_rank(retrieved_ids: List[str], relevant_ids: Set[str]) -> float:
    """Compute Reciprocal Rank (RR) = 1 / rank of first relevant retrieved document."""
    for rank, doc_id in enumerate(retrieved_ids, start=1):
        if doc_id in relevant_ids:
            return 1.0 / float(rank)
    return 0.0


def compute_dcg_at_k(retrieved_ids: List[str], judgments: Dict[str, int], k: int) -> float:
    """Compute DCG@K = sum((2^grade - 1) / log2(i + 1))."""
    if k <= 0:
        return 0.0

    dcg = 0.0
    for i, doc_id in enumerate(retrieved_ids[:k], start=1):
        grade = judgments.get(doc_id, 0)
        gain = (2.0 ** grade) - 1.0
        discount = math.log2(i + 1.0)
        dcg += gain / discount

    return dcg


def compute_ndcg_at_k(retrieved_ids: List[str], judgments: Dict[str, int], k: int) -> float:
    """Compute Normalized Discounted Cumulative Gain (NDCG@K) = DCG@K / IDCG@K."""
    if k <= 0 or not judgments:
        return 0.0

    actual_dcg = compute_dcg_at_k(retrieved_ids, judgments, k)

    # Compute Ideal DCG (IDCG) by sorting ground-truth grades descending
    sorted_grades = sorted(judgments.values(), reverse=True)
    idcg = 0.0
    for i, grade in enumerate(sorted_grades[:k], start=1):
        gain = (2.0 ** grade) - 1.0
        discount = math.log2(i + 1.0)
        idcg += gain / discount

    if idcg == 0.0:
        return 0.0

    return actual_dcg / idcg


@dataclass
class QueryEvaluationResult:
    """Evaluation metrics for a single query."""
    query_id: str
    query: str
    precision_at_k: Dict[int, float]
    recall_at_k: Dict[int, float]
    ndcg_at_k: Dict[int, float]
    average_precision: float
    reciprocal_rank: float
    retrieved_count: int
    relevant_count: int


@dataclass
class EvaluationSummary:
    """Aggregate evaluation summary across all queries for a ranker."""
    method: str
    num_queries: int
    map_score: float
    mrr_score: float
    mean_precision_at_k: Dict[int, float]
    mean_recall_at_k: Dict[int, float]
    mean_ndcg_at_k: Dict[int, float]
    query_results: List[QueryEvaluationResult] = field(default_factory=list)


class RetrievalEvaluator:
    """Evaluates search algorithms against ground-truth relevance judgments."""

    def __init__(self, cutoffs: Optional[List[int]] = None):
        self.cutoffs = cutoffs if cutoffs is not None else [5, 10]

    def load_judgments(self, filepath: str) -> List[Dict[str, Any]]:
        """Load benchmark queries and relevance judgments from JSON file."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Relevance judgments file not found at {filepath}")
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def evaluate_ranker(
        self,
        search_service: SearchService,
        method: str,
        benchmark_queries: List[Dict[str, Any]],
    ) -> EvaluationSummary:
        """Run evaluation for a specified ranking algorithm across all benchmark queries."""
        query_results: List[QueryEvaluationResult] = []
        max_k = max(self.cutoffs) if self.cutoffs else 10

        for item in benchmark_queries:
            q_id = item["query_id"]
            query_str = item["query"]
            judgments: Dict[str, int] = item.get("judgments", {})
            relevant_ids = {doc_id for doc_id, grade in judgments.items() if grade > 0}

            # Retrieve top results
            response = search_service.search(
                query=query_str,
                method=method,
                top_k=max_k,
                include_snippets=False,
            )
            retrieved_ids = [r.doc_id for r in response.results]

            # Compute metrics for this query
            p_at_k = {k: compute_precision_at_k(retrieved_ids, relevant_ids, k) for k in self.cutoffs}
            r_at_k = {k: compute_recall_at_k(retrieved_ids, relevant_ids, k) for k in self.cutoffs}
            ndcg_at_k = {k: compute_ndcg_at_k(retrieved_ids, judgments, k) for k in self.cutoffs}
            ap = compute_average_precision(retrieved_ids, relevant_ids)
            rr = compute_reciprocal_rank(retrieved_ids, relevant_ids)

            query_results.append(
                QueryEvaluationResult(
                    query_id=q_id,
                    query=query_str,
                    precision_at_k=p_at_k,
                    recall_at_k=r_at_k,
                    ndcg_at_k=ndcg_at_k,
                    average_precision=round(ap, 4),
                    reciprocal_rank=round(rr, 4),
                    retrieved_count=len(retrieved_ids),
                    relevant_count=len(relevant_ids),
                )
            )

        n = len(query_results)
        if n == 0:
            return EvaluationSummary(
                method=method,
                num_queries=0,
                map_score=0.0,
                mrr_score=0.0,
                mean_precision_at_k={k: 0.0 for k in self.cutoffs},
                mean_recall_at_k={k: 0.0 for k in self.cutoffs},
                mean_ndcg_at_k={k: 0.0 for k in self.cutoffs},
            )

        map_score = sum(q.average_precision for q in query_results) / float(n)
        mrr_score = sum(q.reciprocal_rank for q in query_results) / float(n)

        mean_p = {
            k: round(sum(q.precision_at_k[k] for q in query_results) / float(n), 4)
            for k in self.cutoffs
        }
        mean_r = {
            k: round(sum(q.recall_at_k[k] for q in query_results) / float(n), 4)
            for k in self.cutoffs
        }
        mean_ndcg = {
            k: round(sum(q.ndcg_at_k[k] for q in query_results) / float(n), 4)
            for k in self.cutoffs
        }

        return EvaluationSummary(
            method=method,
            num_queries=n,
            map_score=round(map_score, 4),
            mrr_score=round(mrr_score, 4),
            mean_precision_at_k=mean_p,
            mean_recall_at_k=mean_r,
            mean_ndcg_at_k=mean_ndcg,
            query_results=query_results,
        )

    def compare_rankers(
        self,
        search_service: SearchService,
        methods: List[str],
        benchmark_queries: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Run comparison across multiple ranking algorithms and return structured benchmark report."""
        comparison_results = {}
        for method in methods:
            summary = self.evaluate_ranker(search_service, method, benchmark_queries)
            comparison_results[method] = {
                "map": summary.map_score,
                "mrr": summary.mrr_score,
                "p@5": summary.mean_precision_at_k.get(5, 0.0),
                "recall@5": summary.mean_recall_at_k.get(5, 0.0),
                "ndcg@5": summary.mean_ndcg_at_k.get(5, 0.0),
                "num_queries": summary.num_queries,
            }

        return {
            "num_evaluated_queries": len(benchmark_queries),
            "ranker_comparison": comparison_results,
        }
