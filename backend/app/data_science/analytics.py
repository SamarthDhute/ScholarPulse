"""Bibliometric and Research Analytics Service.

Adheres strictly to ScholarPulse SRS v1.0 Section 4 (FR-016) & Section 8.6:
- Publication volume over time with year-over-year trends
- Research category distribution and share
- Keyword frequency distributions
- Co-authorship collaboration network graph (nodes, edges, weights)
- Top productive authors and top collaborating author pairs
- Bounded time-range filtering (year_min, year_max)
"""

from collections import Counter, defaultdict
from itertools import combinations
from typing import Dict, List, Optional, Any, Tuple, Set


class ResearchAnalyticsService:
    """Computes bibliometric analytics, trends, and collaboration network graphs."""

    @staticmethod
    def filter_by_year(
        papers: List[Dict[str, Any]],
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Filter a list of papers by publication year bounds."""
        filtered = []
        for p in papers:
            year = p.get("publication_year")
            if year is None:
                continue
            if year_min is not None and year < year_min:
                continue
            if year_max is not None and year > year_max:
                continue
            filtered.append(p)
        return filtered

    def get_overview_summary(
        self,
        papers: List[Dict[str, Any]],
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Generate high-level collection overview metrics."""
        filtered = self.filter_by_year(papers, year_min, year_max)
        total_papers = len(filtered)

        if total_papers == 0:
            return {
                "total_papers": 0,
                "total_authors": 0,
                "total_categories": 0,
                "total_keywords": 0,
                "year_min": None,
                "year_max": None,
                "avg_authors_per_paper": 0.0,
            }

        authors_set: Set[str] = set()
        categories_set: Set[str] = set()
        keywords_set: Set[str] = set()
        years: List[int] = []
        total_authorships = 0

        for p in filtered:
            # Authors
            paper_authors = p.get("authors", [])
            total_authorships += len(paper_authors)
            for a in paper_authors:
                name = a if isinstance(a, str) else a.get("display_name", "")
                if name:
                    authors_set.add(name)

            # Categories
            cats = p.get("categories", [])
            for c in cats:
                name = c if isinstance(c, str) else c.get("name", "")
                if name:
                    categories_set.add(name)

            # Keywords
            kws = p.get("keywords", [])
            for k in kws:
                term = k if isinstance(k, str) else k.get("display_term", "")
                if term:
                    keywords_set.add(term.lower())

            # Year
            y = p.get("publication_year")
            if y is not None:
                years.append(y)

        avg_authors = round(total_authorships / total_papers, 2) if total_papers > 0 else 0.0

        return {
            "total_papers": total_papers,
            "total_authors": len(authors_set),
            "total_categories": len(categories_set),
            "total_keywords": len(keywords_set),
            "year_min": min(years) if years else None,
            "year_max": max(years) if years else None,
            "avg_authors_per_paper": avg_authors,
        }

    def get_publication_trends(
        self,
        papers: List[Dict[str, Any]],
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Compute chronological publication volume and year-over-year growth."""
        filtered = self.filter_by_year(papers, year_min, year_max)
        year_counts: Counter = Counter()

        for p in filtered:
            year = p.get("publication_year")
            if year is not None:
                year_counts[year] += 1

        sorted_years = sorted(year_counts.keys())
        trends = []
        cumulative = 0
        prev_count: Optional[int] = None

        for yr in sorted_years:
            count = year_counts[yr]
            cumulative += count

            growth_rate: Optional[float] = None
            if prev_count is not None and prev_count > 0:
                growth_rate = round(((count - prev_count) / prev_count) * 100.0, 2)

            trends.append({
                "year": yr,
                "count": count,
                "cumulative_count": cumulative,
                "growth_percentage": growth_rate,
            })
            prev_count = count

        return trends

    def get_category_distribution(
        self,
        papers: List[Dict[str, Any]],
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Compute paper counts and percentage share across academic categories."""
        filtered = self.filter_by_year(papers, year_min, year_max)
        category_counts: Counter = Counter()
        total_assignments = 0

        for p in filtered:
            cats = p.get("categories", [])
            for c in cats:
                name = c if isinstance(c, str) else c.get("name", "")
                if name:
                    category_counts[name] += 1
                    total_assignments += 1

        distribution = []
        for cat_name, count in category_counts.most_common():
            share = round((count / total_assignments) * 100.0, 2) if total_assignments > 0 else 0.0
            distribution.append({
                "category": cat_name,
                "count": count,
                "percentage_share": share,
            })

        return distribution

    def get_keyword_distribution(
        self,
        papers: List[Dict[str, Any]],
        top_n: int = 20,
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Extract top recurring keywords with frequency and percentage."""
        filtered = self.filter_by_year(papers, year_min, year_max)
        keyword_counts: Counter = Counter()
        total_keywords = 0

        for p in filtered:
            kws = p.get("keywords", [])
            for k in kws:
                term = k if isinstance(k, str) else k.get("display_term", "")
                if term and term.strip():
                    normalized = term.strip().lower()
                    keyword_counts[normalized] += 1
                    total_keywords += 1

        top_keywords = []
        for kw, count in keyword_counts.most_common(top_n):
            share = round((count / total_keywords) * 100.0, 2) if total_keywords > 0 else 0.0
            top_keywords.append({
                "keyword": kw,
                "count": count,
                "percentage_share": share,
            })

        return top_keywords

    def get_top_authors(
        self,
        papers: List[Dict[str, Any]],
        top_n: int = 15,
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Identify most productive authors based on paper counts."""
        filtered = self.filter_by_year(papers, year_min, year_max)
        author_counts: Counter = Counter()

        for p in filtered:
            authors = p.get("authors", [])
            for a in authors:
                name = a if isinstance(a, str) else a.get("display_name", "")
                if name:
                    author_counts[name] += 1

        top_authors = []
        for author_name, count in author_counts.most_common(top_n):
            top_authors.append({
                "author": author_name,
                "paper_count": count,
            })

        return top_authors

    def get_coauthorship_network(
        self,
        papers: List[Dict[str, Any]],
        min_collaborations: int = 1,
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Construct co-authorship collaboration network graph.

        Returns:
            Dictionary with:
            - nodes: list of authors with paper counts
            - edges: list of co-authorship links with weights and paper titles
            - top_collaborators: most frequent collaboration pairs
        """
        filtered = self.filter_by_year(papers, year_min, year_max)
        author_papers: Dict[str, List[str]] = defaultdict(list)
        collaboration_counts: Dict[Tuple[str, str], int] = defaultdict(int)
        collaboration_titles: Dict[Tuple[str, str], List[str]] = defaultdict(list)

        for p in filtered:
            title = p.get("title", "Untitled")
            raw_authors = p.get("authors", [])
            # Extract author names
            names = []
            for a in raw_authors:
                n = a if isinstance(a, str) else a.get("display_name", "")
                if n and n.strip():
                    names.append(n.strip())

            # Unique authors for this paper
            unique_authors = sorted(list(set(names)))
            for author in unique_authors:
                author_papers[author].append(title)

            # Pairwise combinations
            for a1, a2 in combinations(unique_authors, 2):
                pair = (a1, a2) if a1 < a2 else (a2, a1)
                collaboration_counts[pair] += 1
                collaboration_titles[pair].append(title)

        # Build nodes (only authors who have at least one paper)
        nodes = [
            {
                "id": author,
                "name": author,
                "paper_count": len(titles),
            }
            for author, titles in sorted(author_papers.items(), key=lambda x: len(x[1]), reverse=True)
        ]

        # Build edges filtered by min_collaborations
        edges = []
        for (a1, a2), count in sorted(
            collaboration_counts.items(), key=lambda x: x[1], reverse=True
        ):
            if count >= min_collaborations:
                edges.append({
                    "source": a1,
                    "target": a2,
                    "weight": count,
                    "paper_titles": collaboration_titles[(a1, a2)],
                })

        # Top collaborating pairs
        top_collaborators = [
            {
                "author_1": edge["source"],
                "author_2": edge["target"],
                "joint_papers": edge["weight"],
            }
            for edge in edges[:10]
        ]

        return {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "nodes": nodes,
            "edges": edges,
            "top_collaborators": top_collaborators,
        }
