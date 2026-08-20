import datetime as dt
import os
import time
import xml.etree.ElementTree as ET

import requests

USERNAME = os.getenv("GITHUB_USERNAME", "RohanGottipati")
TOKEN = os.environ["GITHUB_TOKEN"]
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


def get_json(url, params=None):
    response = requests.get(url, headers=HEADERS, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def graphql(query, variables):
    response = requests.post(
        "https://api.github.com/graphql",
        headers=HEADERS,
        json={"query": query, "variables": variables},
        timeout=30,
    )
    response.raise_for_status()
    body = response.json()
    if body.get("errors"):
        raise RuntimeError(body["errors"])
    return body["data"]


def user_and_repos():
    user = get_json(f"https://api.github.com/users/{USERNAME}")
    repos = []
    page = 1
    while True:
        batch = get_json(
            f"https://api.github.com/users/{USERNAME}/repos",
            {"per_page": 100, "page": page, "type": "owner", "sort": "updated"},
        )
        if not batch:
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return user, repos


def total_commits(created_at):
    query = """
    query($login: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $login) {
        contributionsCollection(from: $from, to: $to) {
          totalCommitContributions
        }
      }
    }
    """
    start = dt.datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    now = dt.datetime.now(dt.timezone.utc)
    total = 0
    while start < now:
        end = min(start + dt.timedelta(days=364, hours=23), now)
        data = graphql(
            query,
            {
                "login": USERNAME,
                "from": start.isoformat().replace("+00:00", "Z"),
                "to": end.isoformat().replace("+00:00", "Z"),
            },
        )
        total += data["user"]["contributionsCollection"]["totalCommitContributions"]
        start = end + dt.timedelta(seconds=1)
    return total


def code_stats(repos):
    additions = deletions = 0
    for repo in repos:
        if repo.get("fork"):
            continue
        url = f"https://api.github.com/repos/{USERNAME}/{repo['name']}/stats/contributors"
        data = None
        for _ in range(4):
            response = requests.get(url, headers=HEADERS, timeout=30)
            if response.status_code == 202:
                time.sleep(2)
                continue
            if response.status_code in (204, 404):
                break
            response.raise_for_status()
            data = response.json()
            break
        if not data:
            continue
        for contributor in data:
            author = contributor.get("author") or {}
            if (author.get("login") or "").lower() != USERNAME.lower():
                continue
            for week in contributor.get("weeks", []):
                additions += int(week.get("a", 0))
                deletions += int(week.get("d", 0))
    return additions, deletions


def replace_svg_values(path, values):
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    tree = ET.parse(path)
    root = tree.getroot()
    for element in root.iter():
        element_id = element.attrib.get("id")
        if element_id in values:
            element.text = f"{values[element_id]:,}"
    tree.write(path, encoding="utf-8", xml_declaration=True)


def main():
    user, repos = user_and_repos()
    stars = sum(
        int(repo.get("stargazers_count", 0)) for repo in repos if not repo.get("fork")
    )
    commits = total_commits(user["created_at"])
    additions, deletions = code_stats(repos)
    values = {
        "repo_data": int(user["public_repos"]),
        "star_data": stars,
        "follower_data": int(user["followers"]),
        "commit_data": commits,
        "loc_data": additions - deletions,
        "loc_add": additions,
        "loc_del": deletions,
    }
    for svg in ("light_mode.svg", "dark_mode.svg"):
        replace_svg_values(svg, values)


if __name__ == "__main__":
    main()
