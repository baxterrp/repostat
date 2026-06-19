import logging

import httpx
import pytest
import respx
import typer

import repostat.github as github

expected_github_url = "https://api.github.com/repos/owner/repo"


def test_build_repo_details_maps_fields(sample_repo_response):
    repo = github._build_repo_details(sample_repo_response)

    assert repo.full_name == "owner/repo"
    assert repo.description == "A repo"
    assert repo.stargazers_count == 42
    assert repo.default_branch == "main"
    assert repo.topics == ["python", "github", "api"]


def test_print_repo_details_with_json(sample_repo_response, capsys):
    expected = (
        "{\n"
        '  "full_name": "owner/repo",\n'
        '  "description": "A repo",\n'
        '  "stargazers_count": 42,\n'
        '  "default_branch": "main",\n'
        '  "topics": [\n'
        '    "python",\n'
        '    "github",\n'
        '    "api"\n'
        "  ]\n"
        "}\n"
    )
    github._print_repo_details(sample_repo_response, True)
    captured = capsys.readouterr()
    assert captured.out == expected


def test_print_repo_details_with_class(sample_repo_response, capsys):
    expected = (
        "Repository: owner/repo\n"
        "Description: A repo\n"
        "Stars: 42\n"
        "Default Branch: main\n"
        "Topics: python, github, api\n"
    )

    github._print_repo_details(sample_repo_response, False)
    captured = capsys.readouterr()
    assert captured.out == expected


def test_build_client_includes_auth_header_when_token_set(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv("GITHUB_TOKEN", "test_token")
    client = github._build_client()

    assert "Authorization" in client.headers
    assert client.headers["Authorization"] == "Bearer test_token"


def test_build_client_omits_auth_header_when_no_token_set():
    client = github._build_client()
    assert "Authorization" not in client.headers


def test_fetch_returns_dict_on_success(sample_repo_response):
    with respx.mock:
        respx.get(expected_github_url).mock(
            return_value=httpx.Response(200, json=sample_repo_response)
        )
        with github._build_client() as client:
            result = github.fetch(client, "owner", "repo")

    assert result == sample_repo_response


def test_fetch_raises_repository_not_found_on_404():
    with respx.mock:
        respx.get(expected_github_url).mock(return_value=httpx.Response(404))
        with github._build_client() as client:
            with pytest.raises(github.RepositoryNotFoundError):
                github.fetch(client, "owner", "repo")


def test_fetch_raises_error_on_other_http_errors():
    with respx.mock:
        respx.get(expected_github_url).mock(return_value=httpx.Response(500))
        with github._build_client() as client:
            with pytest.raises(httpx.HTTPStatusError):
                github.fetch(client, "owner", "repo")


@pytest.mark.parametrize("use_json", [True, False])
def test_print_repo_stats_prints_correctly_on_success(
    use_json, caplog, capsys, sample_repo_response
):
    json_message = (
        "{\n"
        '  "full_name": "owner/repo",\n'
        '  "description": "A repo",\n'
        '  "stargazers_count": 42,\n'
        '  "default_branch": "main",\n'
        '  "topics": [\n'
        '    "python",\n'
        '    "github",\n'
        '    "api"\n'
        "  ]\n"
        "}\n"
    )

    structured_message = (
        "Repository: owner/repo\n"
        "Description: A repo\n"
        "Stars: 42\n"
        "Default Branch: main\n"
        "Topics: python, github, api\n"
    )

    expected_message = json_message if use_json else structured_message

    with caplog.at_level(logging.INFO):
        with respx.mock:
            respx.get(expected_github_url).mock(
                return_value=httpx.Response(200, json=sample_repo_response)
            )
            github.print_repository_stats("owner", "repo", use_json)

    assert "Fetching repository info for owner/repo" in caplog.text
    assert expected_message in capsys.readouterr().out


@pytest.mark.parametrize(
    "error_code,message",
    [
        (404, "Repository owner/repo not found"),
        (500, "Error fetching repository info for owner/repo"),
    ],
)
def test_print_repo_stats_logs_error_on_failure(caplog, error_code, message):
    with caplog.at_level(logging.ERROR):
        with respx.mock:
            respx.get(expected_github_url).mock(return_value=httpx.Response(error_code))
            with pytest.raises(typer.Exit):
                github.print_repository_stats("owner", "repo", True)

    assert message in caplog.text


def test_print_repo_stats_logs_error_on_key_error(caplog):
    with respx.mock:
        respx.get(expected_github_url).mock(
            return_value=httpx.Response(200, json={"full_name": "owner/repo"})
        )
        with pytest.raises(typer.Exit):
            with caplog.at_level(logging.ERROR):
                github.print_repository_stats("owner", "repo", False)
    assert "Missing key in repository info for owner/repo" in caplog.text


def test_print_repo_stats_handles_unexpected_exception(
    monkeypatch: pytest.MonkeyPatch, caplog
):
    def explode(*args, **kwargs):
        raise RuntimeError("unexpected")

    monkeypatch.setattr(github, "fetch", explode)
    with pytest.raises(typer.Exit):
        with caplog.at_level(logging.ERROR):
            github.print_repository_stats("owner", "repo", False)

    assert "Unexpected error for owner/repo" in caplog.text
