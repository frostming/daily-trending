import os
import re
from typing import Dict, Iterable, Tuple

from .gh import Developer, GitHub, Repository, TrendingSince, BASE_URL
from .tg import Telegram


def format_message(
    repos: Dict[TrendingSince, Iterable[Tuple[Repository, Iterable[str]]]],
    developers: Dict[TrendingSince, Iterable[Developer]],
) -> str:
    def escape(text):
        return re.sub(r"([_*\[\]()~`>#+=|{}.!-])", r"\\\1", text)

    lines = []
    if any(repos.values()):
        lines.append("*Trending Repos*")
        for since, items in repos.items():
            if items:
                lines.append(f"_{since.value.capitalize()}_")
                for repo, users in items:
                    lines.append(
                        f"\\- [{escape(repo.url)}]({BASE_URL}/{repo.url}) "
                        f"\\| {', '.join(users)}"
                    )
                lines.append("")
    if any(developers.values()):
        lines.append("*Trending Developers*")
        for since, items in developers.items():
            if items:
                lines.append(f"_{since.value.capitalize()}_")
                for developer in items:
                    lines.append(
                        f"\\- [{escape(developer.name)}]({BASE_URL}/{developer.username}) "
                        f"\\| [{escape(developer.repo)}]({BASE_URL}/{developer.repo})"
                    )
                lines.append("")
    return "\n".join(lines)


def run_main(gh_token: str, tg_token: str, tg_chat: str):

    github = GitHub(gh_token)
    telegram = Telegram(tg_token)
    repos = github.get_trending_repos()
    developers = github.get_trending_developers()
    message = format_message(repos, developers)
    telegram.send_message(tg_chat, message)


if __name__ == "__main__":
    gh_token = os.getenv("GH_TOKEN")
    tg_token = os.getenv("TG_TOKEN")
    tg_chat = int(os.getenv("TG_CHAT"))

    run_main(gh_token, tg_token, tg_chat)
