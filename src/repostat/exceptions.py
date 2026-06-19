class RepositoryNotFoundError(Exception):
    def __init__(self, owner: str, repo_name: str):
        self.owner = owner
        self.repo_name = repo_name
        super().__init__(f"Repository {owner}/{repo_name} not found")
