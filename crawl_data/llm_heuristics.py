# llm_heuristics.py

import re
from typing import Dict, Any, List, Tuple


class LLMUsageDetector:
    """
    Simple rule-based detector for whether a PR/commit used an LLM.
    You give it a dict with Title, Body, and some extra optional fields,
    and it returns a boolean ChatgptSharing + some debug info.
    """

    def __init__(self) -> None:
        # High-confidence patterns: specific tools, "ChatGPT", "GPT-4", Copilot, etc.
        high_patterns = [
            r"\bchatgpt\b",
            r"\bgpt[- ]?3\.5\b",
            r"\bgpt[- ]?4\b",
            r"\bgithub\s*copilot\b",
            r"\bcopilot\b",
            r"\bclaude\b",
            r"\bcode\s*llama\b",
            r"\bgemini\b",
            r"\bcodewhisperer\b",
            r"\btabnine\b",
            r"\bcursor\b",
            r"\bcodeium\b",
        ]

        # Medium-confidence patterns: generic AI/LLM references
        medium_patterns = [
            r"\bai[- ]assistant\b",
            r"\bai[- ]powered\b",
            r"\bllm\b",
            r"\bai\b.+\bgenerated\b",
            r"\bgenerated\b.+\bby\b.+\bai\b",
        ]

        # Label keywords (for PR labels)
        label_patterns = [
            r"\bai[-_ ]?generated\b",
            r"\bllm\b",
            r"\bchatgpt\b",
            r"\bgpt[- ]?4\b",
            r"\bcopilot\b",
            r"\bai[-_ ]?assisted\b",
        ]

        # Metadata patterns (authors / co-authored-by lines)
        coauthored_pattern = r"co-authored-by:.*(copilot|chatgpt|ai|bot|assistant|cursor|codeium)"
        author_ai_pattern = r"(copilot|chatgpt|ai[-_]?bot|assistant|cursor|codeium)"

        # Compile them (case-insensitive)
        self.high_regex = [re.compile(p, re.IGNORECASE) for p in high_patterns]
        self.medium_regex = [re.compile(p, re.IGNORECASE) for p in medium_patterns]
        self.label_regex = [re.compile(p, re.IGNORECASE) for p in label_patterns]
        self.coauthored_regex = re.compile(coauthored_pattern, re.IGNORECASE)
        self.author_regex = re.compile(author_ai_pattern, re.IGNORECASE)

    def _search_any(self, patterns: List[re.Pattern], text: str) -> List[str]:
        """Return list of matched snippets (for debugging), or empty if none."""
        if not text:
            return []
        snippets: List[str] = []
        for pat in patterns:
            for m in pat.finditer(text):
                start = max(0, m.start() - 40)
                end = min(len(text), m.end() + 40)
                snippets.append(text[start:end].strip())
        return snippets

    def detect(self, pr: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Main API.
        pr: a dict with keys like:
            - 'Title', 'Body'  (DevGPT style)
            - 'comments_text'  (optional)
            - 'labels'         (optional list[str])
            - 'commit_messages'(optional list[str])
            - 'commit_authors' (optional list[str])

        Returns:
            (chatgpt_sharing_bool, debug_dict)
        """
        title = (pr.get("Title") or pr.get("title") or "")[:10000]
        body = (pr.get("Body") or pr.get("body") or "")[:20000]
        comments_text = (pr.get("comments_text") or "")[:20000]
        labels_list = pr.get("labels") or []
        commit_messages = pr.get("commit_messages") or []
        commit_authors = pr.get("commit_authors") or []

        labels_text = " ".join(labels_list)
        commit_messages_text = "\n".join(commit_messages)
        authors_text = " ".join(commit_authors)

        # 1) High-confidence evidence: if any of these hit, we say True
        high_snippets = []
        high_snippets += self._search_any(self.high_regex, title)
        high_snippets += self._search_any(self.high_regex, body)
        high_snippets += self._search_any(self.high_regex, comments_text)
        high_snippets += self._search_any(self.high_regex, commit_messages_text)
        high_snippets += self._search_any(self.label_regex, labels_text)

        coauthored_snippets = self._search_any([self.coauthored_regex], commit_messages_text)
        author_snippets = self._search_any([self.author_regex], authors_text)

        debug_info: Dict[str, Any] = {
            "high_snippets": high_snippets,
            "coauthored_snippets": coauthored_snippets,
            "author_snippets": author_snippets,
            "medium_snippets": [],
        }

        if high_snippets or coauthored_snippets or author_snippets:
            return True, debug_info

        # 2) Medium-confidence: if we see at least one medium pattern
        medium_snippets = []
        medium_snippets += self._search_any(self.medium_regex, title)
        medium_snippets += self._search_any(self.medium_regex, body)
        medium_snippets += self._search_any(self.medium_regex, comments_text)
        medium_snippets += self._search_any(self.medium_regex, commit_messages_text)

        debug_info["medium_snippets"] = medium_snippets

        if medium_snippets:
            # You can decide to be stricter here. For now: one medium hit -> True.
            return True, debug_info

        # 3) Otherwise, no evidence found
        return False, debug_info
