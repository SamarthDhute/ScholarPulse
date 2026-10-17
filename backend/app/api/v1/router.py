"""API Version 1 main router.

Aggregates all version 1 endpoint controllers:
- Health & Readiness
- Search papers (BM25, TF-IDF, Language Model, Boolean)
- Paper details & content-based recommendations
- Categories and Keywords taxonomy
- Data Science analysis (classification, clustering, association rules)
- Research analytics (publication trends, distributions, collaboration network)
- Information Retrieval evaluation benchmarking
- Ingestion administration
- User saved library
"""

from fastapi import APIRouter
from backend.app.api.v1.endpoints import (
    health,
    search,
    papers,
    taxonomy,
    analysis,
    analytics,
    evaluation,
    admin,
    library,
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(search.router, tags=["Search"])
api_router.include_router(papers.router, tags=["Papers"])
api_router.include_router(taxonomy.router, tags=["Taxonomy"])
api_router.include_router(analysis.router, tags=["Data Science Analysis"])
api_router.include_router(analytics.router, tags=["Research Analytics"])
api_router.include_router(evaluation.router, tags=["Evaluation"])
api_router.include_router(admin.router, tags=["Administration"])
api_router.include_router(library.router, tags=["Saved Library"])
