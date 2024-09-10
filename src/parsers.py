import argparse
import os.path
from typing import Any, Callable


class readable_dir(argparse.Action):
    """From stackoverflow and modified
    https://stackoverflow.com/questions/11415570/directory-path-types-with-argparse
    """

    def __call__(self, parser, namespace, values: list[str], option_string=None):
        git_dirs = []
        for prospective_dir in values:
            dir_name = os.path.expanduser(prospective_dir)
            if not os.path.isdir(prospective_dir) or not os.path.isdir(dir_name):
                raise argparse.ArgumentTypeError(
                    f"{prospective_dir} is not a valid directory."
                )
            if os.access(prospective_dir, os.R_OK):
                if ".git" in os.listdir(dir_name):
                    git_dirs.append(prospective_dir)
                else:
                    raise argparse.ArgumentTypeError(
                        f"{prospective_dir} is not a github directory."
                    )
            else:
                raise argparse.ArgumentTypeError(
                    f"{prospective_dir} is not a readable directory."
                )

        setattr(namespace, self.dest, git_dirs)


def add_common_args(subparser):
    """Adds all the common arguments that status, pull, and push have to their respective
    parsers.

    Args:
        subparser: The subparser belonging to status, pull, log, or push commands.
    """
    subparser.add_argument(
        "repo_names",
        type=str,
        nargs="*",
        help="The names of the git repo folders to affect.",  # root dir from which github repos should be searched for. ~ by default.",
    )
    subparser.add_argument(
        "--repo-directories",
        "-r",
        nargs="*",
        action=readable_dir,
        help="The directories with git repos to affect.",  # root dir from which github repos should be searched for. ~ by default.",
    )
    subparser.add_argument(
        "--exclude",
        "-x",
        type=str,
        nargs="*",
        help="The names of the git repo folders you don't want to check.",
    )
    subparser.add_argument(
        "--silent",
        "-s",
        action="store_true",
        help="Do not print repo specific outputs. Only print holistic details.",
    )


def setup_status_subparser(
    subparsers: argparse._SubParsersAction, run_status: Callable[[Any], int]
):
    """Setups up the status subparser with the common arguments and status specific arguments
    including --modified, --untracked, --check-behind, --check-ahead."""
    status_parser = subparsers.add_parser(
        "status", help="Show the status of local repos."
    )
    add_common_args(status_parser)
    status_parser.set_defaults(func=run_status)
    behind_type = status_parser.add_mutually_exclusive_group()
    behind_type.add_argument(
        "--modified",
        action="store_true",
        help="Whether to only check for modified files.",
    )
    behind_type.add_argument(
        "--untracked",
        action="store_true",
        help="Whether to only check for untracked files.",
    )
    behind_type.add_argument(
        "--commits-behind",
        action="store_true",
        help="Whether to also show how many commits a local repo is behind the origin.",
    )
    behind_type.add_argument(
        "--commits-ahead",
        action="store_true",
        help="Whether to also show how many commits a local repo is ahead of the origin.",
    )


def setup_push_subparser(
    subparsers: argparse._SubParsersAction, run_push: Callable[[Any], int]
):
    """Setups up the push subparser with the common arguments and status specific arguments
    including --push-all, --message."""
    push_parser = subparsers.add_parser(
        "push", help="Push all the commited changes in the local repos."
    )
    push_parser.set_defaults(func=run_push)
    add_common_args(push_parser)
    push_parser.add_argument(
        "--push-all",
        "-A",
        action="store_true",
        help="Whether to push all the changes (ie including untracked changes).",
    )
    push_parser.add_argument(
        "--message",
        "-m",
        type=str,
        default="new updates",
        help="The commit message. (Default 'new updates')",
    )
    push_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print summary for all repos (including those unaffected by command).",
    )


def setup_pull_subparser(
    subparsers: argparse._SubParsersAction, run_pull: Callable[[Any], int]
):
    """Setups up the pull subparser with the common arguments."""
    pull_parser = subparsers.add_parser(
        "pull", help="Pull from origin for all local repos that are behind."
    )
    pull_parser.set_defaults(func=run_pull)
    add_common_args(pull_parser)
    pull_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print summary for all repos (including those unaffected by command).",
    )


def setup_log_subparser(
    subparsers: argparse._SubParsersAction, run_log: Callable[[Any], int]
):
    """Setups up the log subparser with common arguments excluding --silent and add new
    --num-logs argument."""

    log_parser = subparsers.add_parser(
        "log", help="Get the last n oneline commit logs of local repositories."
    )
    log_parser.add_argument(
        "repo_names",
        type=str,
        nargs="*",
        help="The names of the folders with github repos to affect.",  # root dir from which github repos should be searched for. ~ by default.",
    )
    log_parser.add_argument(
        "--repo-directories",
        "-r",
        nargs="*",
        action=readable_dir,
        help="The directories with github repos to affect.",  # root dir from which github repos should be searched for. ~ by default.",
    )
    log_parser.add_argument(
        "--exclude",
        "-x",
        type=str,
        nargs="*",
        help="The names of the github repos you don't want to check.",
    )
    log_parser.add_argument(
        "--num-logs",
        "-n",
        type=int,
        default=3,
        help="The number of logs to show for each local repo. Default if 3.",
    )
    log_parser.set_defaults(func=run_log)


def setup_parser(run_push, run_pull, run_status, run_log) -> argparse.ArgumentParser:
    """Setups up the argumental parser for `localgit` with subparsers for each of the its
    commangs (status, log, pull, push)."""

    parser = argparse.ArgumentParser(
        prog="localgit",
        description="localgit helps manage all the local git repos.",
        epilog=(
            "Use the status, pull, push, log commands to easily get an"
            " overview of the local repo and update them accordingly."
        ),
    )

    subparsers = parser.add_subparsers(required=True, help="Commands")
    setup_status_subparser(subparsers, run_status)
    setup_pull_subparser(subparsers, run_pull)
    setup_push_subparser(subparsers, run_push)
    setup_log_subparser(subparsers, run_log)

    return parser
