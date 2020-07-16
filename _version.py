from github import Github
from packaging.version import parse as parse_version
from anyascii import anyascii
from colorama import Fore

__app_name__ = "DarkShell-R"
__version_info__ = ("1", "3")
__version__ = ".".join(__version_info__)
__author__ = "Nahnahchi"
__email__ = "nahnahchi@gmail.com"
__description__ = "A command line interface for DARK SOULS REMASTERED"
__github__ = "https://github.com/Nahnahchi/dark-shell-R"


class MetaInfoError(Exception):

    def __init__(self, reason, message="Error retrieving information"):
        self.message = message
        self.reason = str(reason)
        super(MetaInfoError, self).__init__(self.message)

    def __str__(self):
        return self.message + " | " + self.reason


def _get_releases():
    gh = Github()
    repo = gh.get_repo("Nahnahchi/dark-shell-R")
    return repo.get_releases()


def print_app_info():
    print(Fore.LIGHTCYAN_EX + ("\n\t%s v%s — %s\n" % (__app_name__, __version__, __description__)))
    print(Fore.LIGHTBLUE_EX + "\tAuthor:" + Fore.LIGHTYELLOW_EX + ("\t%s" % __author__))
    print(Fore.LIGHTBLUE_EX + "\temail:" + Fore.LIGHTYELLOW_EX + ("\t%s" % __email__))
    print(Fore.LIGHTBLUE_EX + "\tGitHub:" + Fore.LIGHTYELLOW_EX + ("\t%s\n" % __github__))


def print_changelog():
    try:
        releases = _get_releases().reversed
        for release in releases:
            print(Fore.LIGHTCYAN_EX + "v" + release.tag_name +
                  Fore.LIGHTYELLOW_EX + anyascii(release.body).replace("- ", "\t"))
    except Exception as e:
        raise MetaInfoError(e, message="Error retrieving changelog")


def check_for_updates():
    try:
        releases = _get_releases()
        releases_versions = [parse_version(release.tag_name) for release in releases]
        available = max(releases_versions)
        current = parse_version(__version__)
        return current >= available, max(current, available).base_version
    except Exception as e:
        raise MetaInfoError(e, message="Couldn't check for the latest version")