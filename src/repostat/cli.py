import typer
from repostat.github import print_repository_stats

def lookup_github_api(owner: str, project: str):
    print(f"Looking up github directory for {owner}/{project}!")
    print_repository_stats(owner, project)


def cli():
    typer.run(lookup_github_api)