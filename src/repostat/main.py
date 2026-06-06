from typing import Any

import httpx


def get_repo(owner: str, repo_name: str) -> dict[str, Any]:
    url = f"https://api.github.com/repos/{owner}/{repo_name}"
    response = httpx.get(url)
    response.raise_for_status()
    return response.json()


def main():
    owner = "baxterrp"
    repo_name = "repostat"
    repo_info = get_repo(owner, repo_name)
    print_repo_info(repo_info)


def print_repo_info(repo_info: dict[str, Any]) -> None:
    delimiter = ", "
    print(f"repository: {repo_info['full_name']}")
    print(f"description: {repo_info['description']}")
    print(f"stars: {repo_info['stargazers_count']}")
    print(f"default branch: {repo_info['default_branch']}")
    print(f"topics: {delimiter.join(repo_info.get('topics') or [])}")


if __name__ == "__main__":
    main()
