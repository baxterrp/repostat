import typer

from dotenv import load_dotenv
from typing_extensions import Annotated
from repostat.github import print_repository_stats


def lookup_github_api(
    owner: str, project: str, json: Annotated[bool, typer.Option("--json")] = False
):
    print_repository_stats(owner, project, json)


def cli():
    load_dotenv()
    typer.run(lookup_github_api)
