"""Boolean Retrieval Engine using custom Inverted Index.

Supports:
- AND, OR, NOT operators
- Parentheses grouping and operator precedence (NOT > AND > OR)
- Infix-to-Postfix conversion (Shunting-Yard algorithm)
- Postfix evaluation using posting sets
"""

import re
from typing import Set, List, Optional
from backend.app.retrieval.inverted_index import InvertedIndex
from backend.app.preprocessing.tokenizer import stem, preprocess_text


class BooleanRetrievalEngine:
    """Evaluates Boolean search queries against an Inverted Index."""

    OPERATORS = {"AND", "OR", "NOT", "(", ")"}
    PRECEDENCE = {"NOT": 3, "AND": 2, "OR": 1}

    def __init__(self, index: InvertedIndex):
        self.index = index

    def _tokenize_query(self, query: str) -> List[str]:
        """Tokenize boolean query string into terms and boolean operators."""
        # Replace parentheses with spaced versions
        spaced = query.replace("(", " ( ").replace(")", " ) ")
        tokens = spaced.split()
        normalized_tokens: List[str] = []

        for token in tokens:
            upper = token.upper()
            if upper in self.OPERATORS:
                normalized_tokens.append(upper)
            else:
                # Stem query term
                stemmed = stem(token)
                if stemmed:
                    normalized_tokens.append(stemmed)
        return normalized_tokens

    def _infix_to_postfix(self, tokens: List[str]) -> List[str]:
        """Convert infix boolean tokens to postfix (RPN) using Shunting-Yard algorithm."""
        output: List[str] = []
        operator_stack: List[str] = []

        # Insert implicit AND if two terms appear adjacent without operator
        processed: List[str] = []
        for i, token in enumerate(tokens):
            processed.append(token)
            if i + 1 < len(tokens):
                next_tok = tokens[i + 1]
                # If current is term or ')' and next is term, 'NOT', or '('
                is_curr_term = token not in {"AND", "OR", "NOT", "("}
                is_next_term = next_tok not in {"AND", "OR", ")"}
                if is_curr_term and is_next_term:
                    processed.append("AND")

        for token in processed:
            if token not in self.OPERATORS:
                output.append(token)
            elif token == "(":
                operator_stack.append(token)
            elif token == ")":
                while operator_stack and operator_stack[-1] != "(":
                    output.append(operator_stack.pop())
                if operator_stack and operator_stack[-1] == "(":
                    operator_stack.pop()
            else:
                while (
                    operator_stack
                    and operator_stack[-1] != "("
                    and self.PRECEDENCE.get(operator_stack[-1], 0) >= self.PRECEDENCE.get(token, 0)
                ):
                    output.append(operator_stack.pop())
                operator_stack.append(token)

        while operator_stack:
            op = operator_stack.pop()
            if op != "(":
                output.append(op)

        return output

    def search(self, query: str) -> Set[str]:
        """Execute boolean query and return matching set of document IDs."""
        tokens = self._tokenize_query(query)
        if not tokens:
            return set()

        # If query has no operators at all, default to AND intersection of all terms
        has_operator = any(t in self.OPERATORS for t in tokens)
        if not has_operator:
            sets = [set(self.index.get_postings(t).keys()) for t in tokens]
            if not sets:
                return set()
            return set.intersection(*sets)

        postfix = self._infix_to_postfix(tokens)
        stack: List[Set[str]] = []
        universal_set = set(self.index.doc_ids)

        for token in postfix:
            if token not in self.OPERATORS:
                # Term lookup
                matching_docs = set(self.index.get_postings(token).keys())
                stack.append(matching_docs)
            elif token == "NOT":
                if not stack:
                    return set()
                operand = stack.pop()
                stack.append(universal_set - operand)
            elif token == "AND":
                if len(stack) < 2:
                    return set()
                right = stack.pop()
                left = stack.pop()
                stack.append(left & right)
            elif token == "OR":
                if len(stack) < 2:
                    return set()
                right = stack.pop()
                left = stack.pop()
                stack.append(left | right)

        return stack.pop() if stack else set()
