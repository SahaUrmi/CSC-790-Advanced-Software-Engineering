# github_crawl.py
"""
GitHub PR crawler for your DevGPT-style dataset.

Usage:
    export GITHUB_TOKEN=ghp_XXXXXXXXXXXXXXXX
    python github_crawl.py repos.txt llm_pr_raw.jsonl

Where repos.txt contains lines like:
    owner1/repo1
    owner2/repo2
"""

import sys
import os
import time
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

import requests

GITHUB_API_BASE = "https://api.github.com"


class GitHubClient:
    def __init__(self, token: Optional[str] = None, sleep_between: float = 0.5) -> None:
        self.token = token or os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise RuntimeError("GitHub token not provided. Set GITHUB_TOKEN env var or pass token.")

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        })
        self.sleep_between = sleep_between

    def get(self, url: str, params: Dict[str, Any] = None) -> Any:
        """Simple GET with basic rate-limit friendly sleep."""
        time.sleep(self.sleep_between)
        resp = self.session.get(url, params=params)
        if resp.status_code == 403 and "rate limit" in resp.text.lower():
            print("Hit rate limit, sleeping 60 seconds...", file=sys.stderr)
            time.sleep(60)
            resp = self.session.get(url, params=params)

        resp.raise_for_status()
        return resp.json()


def fetch_repo_info(client: GitHubClient, owner: str, repo: str) -> Dict[str, Any]:
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"
    return client.get(url)


def fetch_prs_for_repo(
    client: GitHubClient,
    owner: str,
    repo: str,
    since: str = "2023-01-01T00:00:00Z",
    max_prs: int = 150,
) -> List[Dict[str, Any]]:
    """
    Fetch PRs for a repo, state=all, sorted by creation date (desc),
    and stop when created_at < since.
    """
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls"
    per_page = 50
    page = 1
    all_prs: List[Dict[str, Any]] = []

    since_dt = datetime.fromisoformat(since.replace("Z", "+00:00"))

    while True:
        params = {
            "state": "all",
            "sort": "created",
            "direction": "desc",
            "per_page": per_page,
            "page": page,
        }
        print(f"Fetching PR page {page} for {owner}/{repo}...", file=sys.stderr)
        time.sleep(client.sleep_between)
        resp = client.session.get(url, params=params)
        if resp.status_code == 404:
            print(f"Repo not found: {owner}/{repo}", file=sys.stderr)
            break
        resp.raise_for_status()
        prs = resp.json()
        if not prs:
            break

        stop = False
        for pr in prs:
            created_at = pr.get("created_at")
            if not created_at:
                continue
            created_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            if created_dt < since_dt:
                stop = True
                break
            all_prs.append(pr)
            if len(all_prs) >= max_prs:
                stop = True
                break
        if stop:
            break
        page += 1

    return all_prs


def fetch_issue_comments(client: GitHubClient, owner: str, repo: str, pr_number: int) -> List[Dict[str, Any]]:
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/issues/{pr_number}/comments"
    return client.get(url)


def fetch_review_comments(client: GitHubClient, owner: str, repo: str, pr_number: int) -> List[Dict[str, Any]]:
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}/comments"
    return client.get(url)


def fetch_commits_for_pr(client: GitHubClient, owner: str, repo: str, pr_number: int) -> List[Dict[str, Any]]:
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}/commits"
    return client.get(url)


def build_dev_gpt_like_row(
    pr: Dict[str, Any],
    repo_info: Dict[str, Any],
    issue_comments: List[Dict[str, Any]],
    review_comments: List[Dict[str, Any]],
    commits: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Map GitHub API JSON into your DevGPT-like row + extras needed for heuristics.
    """
    repo_full_name = repo_info.get("full_name", "")
    repo_language = repo_info.get("language", None)

    pr_number = pr.get("number")
    pr_url = pr.get("html_url")
    pr_title = pr.get("title")
    pr_body = pr.get("body")
    user = pr.get("user") or {}
    author_login = user.get("login", "")

    created_at = pr.get("created_at")
    closed_at = pr.get("closed_at")
    merged_at = pr.get("merged_at")
    updated_at = pr.get("updated_at")
    state = pr.get("state")

    additions = pr.get("additions")
    deletions = pr.get("deletions")
    changed_files = pr.get("changed_files")

    commits_total_count = pr.get("commits")
    commit_sha = commits[-1]["sha"] if commits else None

    all_comments_texts = []
    for c in issue_comments:
        all_comments_texts.append(c.get("body") or "")
    for c in review_comments:
        all_comments_texts.append(c.get("body") or "")
    comments_text = "\n\n".join(all_comments_texts)

    labels = [lbl.get("name", "") for lbl in (pr.get("labels") or [])]

    commit_messages = []
    commit_authors = []
    for c in commits:
        commit_obj = c.get("commit", {})
        msg = commit_obj.get("message", "")
        commit_messages.append(msg)
        author_obj = c.get("author") or {}
        login = author_obj.get("login")
        if login:
            commit_authors.append(login)
        else:
            raw_author = commit_obj.get("author", {})
            email = raw_author.get("email")
            name = raw_author.get("name")
            if email:
                commit_authors.append(email)
            elif name:
                commit_authors.append(name)

    row: Dict[str, Any] = {
        "Type": "PR",
        "URL": pr_url,
        "Author": author_login,
        "RepoName": repo_full_name,
        "RepoLanguage": repo_language,
        "Number": pr_number,
        "Title": pr_title,
        "Body": pr_body,
        "CreatedAt": created_at,
        "ClosedAt": closed_at,
        "MergedAt": merged_at,
        "UpdatedAt": updated_at,
        "State": state,
        "Additions": additions,
        "Deletions": deletions,
        "ChangedFiles": changed_files,
        "CommitsTotalCount": commits_total_count,
        "CommitSha": commit_sha,
        # LLM flag (to be filled later by LLMUsageDetector)
        "ChatgptSharing": None,
        # Extra fields for detection
        "comments_text": comments_text,
        "labels": labels,
        "commit_messages": commit_messages,
        "commit_authors": commit_authors,
    }

    return row


def read_repo_list(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines()]
    return [ln for ln in lines if ln and not ln.startswith("#")]


def main():
    if len(sys.argv) < 3:
        print("Usage: python github_crawl.py repos.txt output.jsonl", file=sys.stderr)
        sys.exit(1)

    repos_file = sys.argv[1]
    output_path = sys.argv[2]

    client = GitHubClient()
    repos = read_repo_list(repos_file)
    print(f"Found {len(repos)} repos to process.", file=sys.stderr)

    since_iso = "2023-01-01T00:00:00Z"

    with open(output_path, "w", encoding="utf-8") as out_f:
        for full in repos:
            print(f"Processing repo: {full}", file=sys.stderr)
            try:
                owner, repo = full.split("/", 1)
            except ValueError:
                print(f"Invalid repo format: {full}, expected owner/repo", file=sys.stderr)
                continue

            try:
                repo_info = fetch_repo_info(client, owner, repo)
            except Exception as e:
                print(f"Failed to fetch repo info for {full}: {e}", file=sys.stderr)
                continue

            try:
                prs = fetch_prs_for_repo(client, owner, repo, since=since_iso, max_prs=150)
            except Exception as e:
                print(f"Failed to fetch PRs for {full}: {e}", file=sys.stderr)
                continue

            print(f"  Found {len(prs)} PRs since {since_iso}", file=sys.stderr)

            for pr in prs:
                number = pr.get("number")
                if number is None:
                    continue

                try:
                    issue_comments = fetch_issue_comments(client, owner, repo, number)
                    review_comments = fetch_review_comments(client, owner, repo, number)
                    commits = fetch_commits_for_pr(client, owner, repo, number)
                except Exception as e:
                    print(f"    Failed details for PR #{number} in {full}: {e}", file=sys.stderr)
                    continue

                row = build_dev_gpt_like_row(pr, repo_info, issue_comments, review_comments, commits)
                out_f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"Done. Output written to {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
