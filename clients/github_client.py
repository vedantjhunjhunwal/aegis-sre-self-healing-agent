from pathlib import Path
from typing import Dict, Any
from github import Github
from git import Repo
import time


class GitHubPRClient:
    def __init__(
        self,
        token: str,
        owner: str,
        repo_name: str,
        base_branch: str,
        create_real_pr: bool,
        local_pr_dir: str = "workspace/prs",
    ):
        self.token = token
        self.owner = owner
        self.repo_name = repo_name
        self.base_branch = base_branch
        self.create_real_pr = create_real_pr
        self.local_pr_dir = Path(local_pr_dir)
        self.local_pr_dir.mkdir(parents=True, exist_ok=True)

    def create_pr(self, title: str, body: str, branch_name: str, repo_path: str) -> Dict[str, Any]:
        if not self.create_real_pr or not self.token or not self.owner or not self.repo_name:
            artifact = self.local_pr_dir / f"{branch_name.replace('/', '_')}.md"
            artifact.write_text(f"# {title}\n\n{body}", encoding="utf-8")
            return {
                "mode": "local_artifact",
                "status": "created",
                "path": str(artifact),
                "title": title,
            }

        repo = Repo(repo_path)
        repo.git.checkout("-B", branch_name)
        repo.git.add(A=True)
        if repo.is_dirty(untracked_files=True):
            repo.index.commit(title)

        origin = repo.remote(name="origin")
        origin.push(refspec=f"{branch_name}:{branch_name}")

        gh = Github(self.token)
        gh_repo = gh.get_repo(f"{self.owner}/{self.repo_name}")
        pr = gh_repo.create_pull(
            title=title,
            body=body,
            head=branch_name,
            base=self.base_branch,
        )
        return {
            "mode": "github",
            "status": "created",
            "url": pr.html_url,
            "number": pr.number,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
