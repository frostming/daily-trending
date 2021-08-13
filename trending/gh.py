import enum
import os
from typing import Dict, Iterable, Sequence, Tuple

import requests
from lxml import html
from typing import NamedTuple

BASE_URL = "https://github.com"


class TrendingSince(enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class Repository(NamedTuple):
    url: str
    description: str
    language: str
    stars: int
    forks: int
    author: str
    contributors: Sequence[str]


class Developer(NamedTuple):
    name: str
    username: str
    repo: str
    repo_desc: str


class GitHub:
    def __init__(self, token: str) -> None:
        self._headers = {
            "Authorization": f"token {token}",
            "accept": "application/vnd.github.v3+json",
        }
        self.users = set(self._get_following())
        self.users.add(self._get_me())

    @staticmethod
    def _get_trending_repos(since: TrendingSince) -> Iterable[Repository]:
        resp = requests.get(f"https://github.com/trending?since={since.value}")
        tree = html.fromstring(resp.content)
        for box in tree.xpath('//article[@class="Box-row"]'):
            print(box)
            yield Repository(
                url=(temp := next(iter(box.xpath("./h1/a/@href")), "").strip("/")),
                author=temp.split("/")[0],
                description=next(iter(box.xpath("./p/text()")), "").strip(),
                language=next(
                    iter(box.xpath('.//span[@itemprop="programmingLanguage"]/text()')),
                    "",
                ).strip(),
                stars=int(
                    (box.xpath('.//svg[@aria-label="star"]/../text()') + ["0", "0"])[1]
                    .strip()
                    .replace(",", "_")
                ),
                forks=int(
                    (box.xpath('.//svg[@aria-label="fork"]/../text()') + ["0", "0"])[1]
                    .strip()
                    .replace(",", "_")
                ),
                contributors=[
                    item.lstrip("/") for item in box.xpath(".//div[2]/span[2]/a/@href")
                ],
            )

    @staticmethod
    def _get_trending_developers(since: TrendingSince) -> Iterable[Developer]:
        resp = requests.get(
            f"https://github.com/trending/developers?since={since.value}"
        )
        tree = html.fromstring(resp.content)
        for box in tree.xpath('//article[@class="Box-row d-flex"]'):
            yield Developer(
                name=(temp := box.xpath(".//div[2]/div/div/h1/a/text()")[0].strip()),
                username=next(
                    iter(box.xpath(".//div[2]/div/div/p/a/@href")), temp
                ).strip("/"),
                repo=next(
                    iter(box.xpath('.//h1[@class="h4 lh-condensed"]/a/@href')), ""
                ).strip("/"),
                repo_desc=" ".join(
                    text.strip()
                    for text in box.xpath(
                        './/h1[@class="h4 lh-condensed"]/following-sibling::div/text()'
                    )
                ),
            )

    def _get_following(self) -> Iterable[str]:
        page = 1
        while True:
            resp = requests.get(
                "https://api.github.com/user/following",
                headers=self._headers,
                params={"per_page": 100, "page": page},
            )
            data = resp.json()
            if not data:
                break
            for user in data:
                yield user["login"]
            page += 1

    def _get_me(self) -> str:
        if os.getenv("GITHUB_USER"):
            return os.getenv("GITHUB_USER")
        resp = requests.get("https://api.github.com/user", headers=self._headers)
        return resp.json()["login"]

    def get_trending_repos(
        self,
    ) -> Dict[TrendingSince, Iterable[Tuple[Repository, Iterable[str]]]]:
        result: Dict[TrendingSince, Iterable[Tuple[Repository, Iterable[str]]]] = {}
        print("Fetching trending repos")
        for since in TrendingSince:
            result[since] = []
            for repo in self._get_trending_repos(since):
                users = set(repo.contributors + [repo.author]) & self.users
                if users:
                    result[since].append((repo, users))
        return result

    def get_trending_developers(self) -> Dict[TrendingSince, Iterable[Developer]]:
        result: Dict[TrendingSince, Iterable[Developer]] = {}
        print("Fetching trending developers")
        for since in TrendingSince:
            result[since] = []
            for dev in self._get_trending_developers(since):
                if dev.username in self.users:
                    result[since].append(dev)
        return result


if __name__ == "__main__":
    print(*GitHub._get_trending_repos(TrendingSince.DAILY), sep="\n")
