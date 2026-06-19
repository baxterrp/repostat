from typing import Any
from repostat.exceptions import RepositoryNotFoundError
from repostat.models import Repository

import os
import json as json_lib
import httpx
import typer
import logging

logger = logging.getLogger(__name__)


def fetch(client: httpx.Client, owner: str, repo_name: str) -> dict[str, Any]:
    logger.info("Fetching repository info for %s/%s", owner, repo_name)
    url = f"https://api.github.com/repos/{owner}/{repo_name}"

    try:
        return client.get(url).raise_for_status().json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise RepositoryNotFoundError(owner, repo_name) from e
        raise


def print_repository_stats(owner: str, repo_name: str, json: bool) -> None:
    token = os.getenv("GITHUB_TOKEN")
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    try:
        with httpx.Client(headers=headers) as client:
            repo_info = fetch(client, owner, repo_name)

        rep = Repository(
            full_name=repo_info["full_name"],
            description=repo_info["description"],
            stargazers_count=repo_info["stargazers_count"],
            default_branch=repo_info["default_branch"],
            topics=repo_info.get("topics", []),
        )

        response = repo_info if json else rep.summarize()
        logger.debug("Repository info for %s/%s: %s", owner, repo_name, response)
        print(response)
    except RepositoryNotFoundError as e:
        logger.error(e)
        raise typer.Exit(1)
    except httpx.HTTPError as e:
        logger.error(
            "Error fetching repository info for %s/%s: %s", owner, repo_name, e
        )
        raise typer.Exit(1)
    except (KeyError, json_lib.JSONDecodeError) as e:
        logger.error(
            "Missing key in repository info for %s/%s: %s", owner, repo_name, e
        )
        raise typer.Exit(1)
    except Exception as e:
        logger.error("Unexpected error for %s/%s: %s", owner, repo_name, e)
        raise typer.Exit(1)
