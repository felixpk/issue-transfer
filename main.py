import argparse
import configparser
import json
from typing import Dict, List

import requests as requests
import logging
from requests.auth import HTTPBasicAuth


def get_gitlab_issues() -> List:
    """Download GitLab issues"""
    return requests.get(
        f"{GITLAB_BASE_URL}/projects/{GITLAB_PROJECT_ID}/issues?labels={GITLAB_LABELS}&state=opened",
        headers={"PRIVATE-TOKEN": GITLAB_PAT},
    ).json()


def get_github_issues() -> List:
    return requests.get(
        f"{GITHUB_BASE_URL}/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/issues",
        headers={"Accept": "application/vnd.github.v3+json"},
        auth=HTTPBasicAuth(GITHUB_REPO_OWNER, GITHUB_PAT),
    ).json()


def post_issue(issue_data: Dict):
    """Upload issue to Github"""
    return requests.post(
        f"{GITHUB_BASE_URL}/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/issues",
        headers={"Accept": "application/vnd.github.v3+json"},
        data=json.dumps(issue_data),
        auth=HTTPBasicAuth(GITHUB_REPO_OWNER, GITHUB_PAT),
    )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dry-run", action="store_true")
    return parser.parse_args()


def transfer_issues():
    gitlab_issues = get_gitlab_issues()
    github_issue_titles = [issue["title"] for issue in get_github_issues()]

    for gitlab_issue in gitlab_issues:
        issue_title = gitlab_issue["title"]

        if issue_title in github_issue_titles:
            LOGGER.warning(f"Skipped '{issue_title}' (Duplicate Title)")
            continue

        if not ARGS.dry_run:
            resp = post_issue({"title": issue_title, "body": gitlab_issue["description"]})
            if resp.status_code == 201:
                LOGGER.info(f"Transfered '{issue_title}'")
        else:
            LOGGER.info(f"[SIM] Transfered '{issue_title}'")


if __name__ == "__main__":
    LOGGER = logging.getLogger(__name__)

    config = configparser.ConfigParser()
    config.read("settings.ini")

    try:
        GITLAB_BASE_URL = config["GITLAB"]["base-url"]
        GITLAB_PROJECT_ID = config["GITLAB"]["project-id"]
        GITLAB_LABELS = config["GITLAB"]["labels"]
        GITLAB_PAT = config["GITLAB"]["access-token"]

        GITHUB_BASE_URL = config["GITHUB"]["base-url"]
        GITHUB_REPO_NAME = config["GITHUB"]["repo-name"]
        GITHUB_REPO_OWNER = config["GITHUB"]["repo-owner"]
        GITHUB_PAT = config["GITHUB"]["access-token"]
    except KeyError as e:
        LOGGER.error(f"Please make sure {str(e)} is defined in settings.ini")
        exit(1)

    ARGS = parse_arguments()
    transfer_issues()
