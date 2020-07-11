from github import Github
from packaging.version import parse as parse_version

__version_info__ = ("1", "3")
__version__ = ".".join(__version_info__)


class CheckUpdatesError(Exception):

    def __init__(self, reason, message="Couldn't check for the latest version"):
        self.message = message
        self.reason = str(reason)
        super(CheckUpdatesError, self).__init__(self.message)

    def __str__(self):
        return self.message + " | " + self.reason


def check_for_updates():
    try:
        gh = Github()
        repo = gh.get_repo("Nahnahchi/dark-shell-R")
        releases = repo.get_releases()
        releases_versions = [parse_version(release.tag_name) for release in releases]
        available = max(releases_versions)
        current = parse_version(__version__)
        return current >= available, max(current, available).base_version
    except Exception as e:
        raise CheckUpdatesError(e)
