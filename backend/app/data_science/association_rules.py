"""Association Rule Mining Engine for Research Keywords.

Adheres strictly to ScholarPulse SRS v1.0 Section 4 (FR-015) & Section 8.8:
- Frequent itemsets extraction via Apriori algorithm (mlxtend)
- Association rule generation with Support, Confidence, Lift, Leverage, and Conviction
- Parameter bounds validation (min_support in (0, 1], min_confidence in (0, 1], min_lift >= 0)
- Keyword association lookups and query filtering
- Bounded pagination conforming to API contracts
- JSON serialization for artifact persistence
"""

import os
import json
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Sequence, Set
import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules


@dataclass
class FrequentItemset:
    """Represents a frequent set of co-occurring keywords."""
    items: List[str]
    support: float
    item_count: int


@dataclass
class AssociationRule:
    """Represents a directional association rule (antecedents -> consequents)."""
    antecedents: List[str]
    consequents: List[str]
    support: float
    confidence: float
    lift: float
    leverage: float
    conviction: float


@dataclass
class AssociationMiningResult:
    """Complete output of association rule mining execution."""
    total_transactions: int
    min_support: float
    min_confidence: float
    min_lift: float
    frequent_itemsets_count: int
    rules_count: int
    frequent_itemsets: List[FrequentItemset]
    rules: List[AssociationRule]
    model_version: str = "association-v1"


class KeywordAssociationMiner:
    """Mines frequent keyword combinations and association rules across research papers."""

    def __init__(self, model_version: str = "association-v1"):
        self.model_version = model_version
        self.last_result: Optional[AssociationMiningResult] = None

    def validate_parameters(
        self, min_support: float, min_confidence: float, min_lift: float
    ) -> None:
        """Validate mining thresholds per ScholarPulse SRS Section 8.8."""
        if not (0.0 < min_support <= 1.0):
            raise ValueError(
                f"min_support must be in range (0.0, 1.0], received: {min_support}"
            )
        if not (0.0 < min_confidence <= 1.0):
            raise ValueError(
                f"min_confidence must be in range (0.0, 1.0], received: {min_confidence}"
            )
        if min_lift < 0.0:
            raise ValueError(f"min_lift must be >= 0.0, received: {min_lift}")

    def mine(
        self,
        transactions: List[List[str]],
        min_support: float = 0.04,
        min_confidence: float = 0.3,
        min_lift: float = 1.0,
        max_itemset_len: Optional[int] = 4,
    ) -> AssociationMiningResult:
        """Mine frequent itemsets and association rules from keyword transactions.

        Args:
            transactions: List of keyword lists (one list per paper).
            min_support: Minimum fraction of transactions containing the itemset.
            min_confidence: Minimum conditional probability P(consequent|antecedent).
            min_lift: Ratio of observed co-occurrence to expected under independence.
            max_itemset_len: Upper bound on mined itemset length.

        Returns:
            AssociationMiningResult containing itemsets, rules, and parameters.
        """
        self.validate_parameters(min_support, min_confidence, min_lift)

        # Filter empty transactions and clean terms
        cleaned_transactions: List[List[str]] = []
        for kw_list in transactions:
            if not kw_list:
                continue
            cleaned = [k.strip().lower() for k in kw_list if k and k.strip()]
            # Deduplicate within transaction
            unique_kws = list(set(cleaned))
            if unique_kws:
                cleaned_transactions.append(unique_kws)

        total_tx = len(cleaned_transactions)
        if total_tx == 0:
            empty_res = AssociationMiningResult(
                total_transactions=0,
                min_support=min_support,
                min_confidence=min_confidence,
                min_lift=min_lift,
                frequent_itemsets_count=0,
                rules_count=0,
                frequent_itemsets=[],
                rules=[],
                model_version=self.model_version,
            )
            self.last_result = empty_res
            return empty_res

        # One-hot encode transactions
        te = TransactionEncoder()
        te_ary = te.fit(cleaned_transactions).transform(cleaned_transactions)
        df_encoded = pd.DataFrame(te_ary, columns=te.columns_).astype(bool)

        # Generate frequent itemsets via Apriori
        frequent_df = apriori(
            df_encoded,
            min_support=min_support,
            use_colnames=True,
            max_len=max_itemset_len,
        )

        frequent_itemsets_list: List[FrequentItemset] = []
        rules_list: List[AssociationRule] = []

        if not frequent_df.empty:
            for _, row in frequent_df.iterrows():
                items = sorted(list(row["itemsets"]))
                frequent_itemsets_list.append(
                    FrequentItemset(
                        items=items,
                        support=round(float(row["support"]), 4),
                        item_count=len(items),
                    )
                )

            # Generate association rules
            try:
                raw_rules_df = association_rules(
                    frequent_df,
                    metric="confidence",
                    min_threshold=min_confidence,
                )

                if not raw_rules_df.empty:
                    # Filter by min_lift
                    filtered_rules_df = raw_rules_df[raw_rules_df["lift"] >= min_lift]

                    for _, r in filtered_rules_df.iterrows():
                        conviction_val = float(r["conviction"])
                        if math.isinf(conviction_val) or math.isnan(conviction_val):
                            conviction_val = 999.0

                        rules_list.append(
                            AssociationRule(
                                antecedents=sorted(list(r["antecedents"])),
                                consequents=sorted(list(r["consequents"])),
                                support=round(float(r["support"]), 4),
                                confidence=round(float(r["confidence"]), 4),
                                lift=round(float(r["lift"]), 4),
                                leverage=round(float(r["leverage"]), 4),
                                conviction=round(conviction_val, 4),
                            )
                        )
            except Exception:
                # If rule generation produces no rules at given threshold
                rules_list = []

        # Sort itemsets descending by support
        frequent_itemsets_list.sort(key=lambda item: item.support, reverse=True)

        # Sort rules descending by lift, then confidence
        rules_list.sort(key=lambda r: (r.lift, r.confidence), reverse=True)

        self.last_result = AssociationMiningResult(
            total_transactions=total_tx,
            min_support=min_support,
            min_confidence=min_confidence,
            min_lift=min_lift,
            frequent_itemsets_count=len(frequent_itemsets_list),
            rules_count=len(rules_list),
            frequent_itemsets=frequent_itemsets_list,
            rules=rules_list,
            model_version=self.model_version,
        )

        return self.last_result

    def find_rules_for_term(
        self, term: str, position: str = "antecedent", top_n: int = 10
    ) -> List[AssociationRule]:
        """Query rules containing the specified term in antecedents or consequents."""
        if not self.last_result:
            return []

        term_lower = term.strip().lower()
        matched: List[AssociationRule] = []

        for rule in self.last_result.rules:
            if position in ("antecedent", "both"):
                if any(term_lower in ant.lower() for ant in rule.antecedents):
                    matched.append(rule)
                    continue
            if position in ("consequent", "both"):
                if any(term_lower in cons.lower() for cons in rule.consequents):
                    matched.append(rule)

        return matched[:top_n]

    def paginate_rules(
        self, page: int = 1, page_size: int = 20
    ) -> Dict[str, Any]:
        """Return paginated association rules conforming to SRS Section 8.8."""
        if not self.last_result:
            return {
                "page": page,
                "page_size": page_size,
                "total_rules": 0,
                "total_pages": 0,
                "rules": [],
                "model_version": self.model_version,
            }

        total_rules = len(self.last_result.rules)
        total_pages = math.ceil(total_rules / page_size) if total_rules > 0 else 0
        current_page = max(1, page)
        start_idx = (current_page - 1) * page_size
        end_idx = start_idx + page_size

        page_rules = self.last_result.rules[start_idx:end_idx]

        return {
            "page": current_page,
            "page_size": page_size,
            "total_rules": total_rules,
            "total_pages": total_pages,
            "min_support": self.last_result.min_support,
            "min_confidence": self.last_result.min_confidence,
            "min_lift": self.last_result.min_lift,
            "model_version": self.last_result.model_version,
            "rules": [
                {
                    "antecedents": r.antecedents,
                    "consequents": r.consequents,
                    "support": r.support,
                    "confidence": r.confidence,
                    "lift": r.lift,
                    "leverage": r.leverage,
                    "conviction": r.conviction,
                }
                for r in page_rules
            ],
        }

    def to_dict(self, result: Optional[AssociationMiningResult] = None) -> Dict[str, Any]:
        """Convert mining result to JSON-serializable dictionary."""
        res = result or self.last_result
        if res is None:
            return {}

        return {
            "model_version": res.model_version,
            "total_transactions": res.total_transactions,
            "min_support": res.min_support,
            "min_confidence": res.min_confidence,
            "min_lift": res.min_lift,
            "frequent_itemsets_count": res.frequent_itemsets_count,
            "rules_count": res.rules_count,
            "frequent_itemsets": [
                {
                    "items": item.items,
                    "support": item.support,
                    "item_count": item.item_count,
                }
                for item in res.frequent_itemsets
            ],
            "rules": [
                {
                    "antecedents": r.antecedents,
                    "consequents": r.consequents,
                    "support": r.support,
                    "confidence": r.confidence,
                    "lift": r.lift,
                    "leverage": r.leverage,
                    "conviction": r.conviction,
                }
                for r in res.rules
            ],
        }

    def save(self, filepath: str) -> None:
        """Serialize association mining results to JSON file."""
        if self.last_result is None:
            raise RuntimeError("No association rules to save. Call mine() first.")

        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(self.last_result), f, indent=2)

    def load(self, filepath: str) -> AssociationMiningResult:
        """Load association mining results from JSON file."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Association rules file not found: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        itemsets = [
            FrequentItemset(
                items=it["items"],
                support=it["support"],
                item_count=it["item_count"],
            )
            for it in data.get("frequent_itemsets", [])
        ]

        rules = [
            AssociationRule(
                antecedents=r["antecedents"],
                consequents=r["consequents"],
                support=r["support"],
                confidence=r["confidence"],
                lift=r["lift"],
                leverage=r["leverage"],
                conviction=r["conviction"],
            )
            for r in data.get("rules", [])
        ]

        self.last_result = AssociationMiningResult(
            total_transactions=data["total_transactions"],
            min_support=data["min_support"],
            min_confidence=data["min_confidence"],
            min_lift=data["min_lift"],
            frequent_itemsets_count=data["frequent_itemsets_count"],
            rules_count=data["rules_count"],
            frequent_itemsets=itemsets,
            rules=rules,
            model_version=data.get("model_version", self.model_version),
        )

        return self.last_result
