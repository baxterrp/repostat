from typing import Any
from repostat.models import Repository

import httpx


def fetch(owner: str, repo_name: str) -> dict[str, Any]:
    url = f"https://api.github.com/repos/{owner}/{repo_name}"
    response = httpx.get(url)
    response.raise_for_status()
    return response.json()


def print_repository_stats(owner: str, repo_name: str, json: bool) -> None:
    repo_info = fetch(owner, repo_name)
    rep = Repository(
        full_name=repo_info["full_name"],
        description=repo_info["description"],
        stargazers_count=repo_info["stargazers_count"],
        default_branch=repo_info["default_branch"],
        topics=repo_info.get("topics", []),
    )

    response = repo_info if json else rep.summarize()
    print(response)
