#!/usr/bin/env python3

import argparse
import os

from pretty_print import *

from .pull import *
from .push import *
from .status import *


class readable_dir(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        prospective_dir = values
        if not os.path.isdir(prospective_dir) or not os.path.isdir(
            os.path.expanduser(prospective_dir)
        ):
            raise argparse.ArgumentTypeError(
                "readable_dir:{0} is not a valid path".format(prospective_dir)
            )
        if os.access(prospective_dir, os.R_OK):
            setattr(namespace, self.dest, prospective_dir)
        else:
            raise argparse.ArgumentTypeError(
                "readable_dir:{0} is not a readable dir".format(prospective_dir)
            )


def run_status(args, untracked, modified, gits):
    exit_code = 0
    for git_name, git_dir in gits:
        exit_code |= report_git_status(
            git_dir,
            git_name,
            args.verbose,
            args.all,
            untracked,
            modified,
            args.check_remote,
        )

    if exit_code == 0:
        print(success("All repos are pushed."))
    else:
        print()
    return exit_code


def run_pull(args, untracked, modified, gits):
    exit_code = 0
    for git_name, git_dir in gits:
        cur_branch = get_cur_branch(git_dir)
        if not cur_branch:
            return 0
        num_behind = commits_behind(git_dir, cur_branch)

    print("Pull")
    print(gits)
    return exit_code


def run_push(args, untracked, modified, gits):
    print("Push")


def main():
    parser = argparse.ArgumentParser(
        prog="local_gits",
        description="local_gits helps manage all the local git repos.",
        epilog=(
            "Use the status, pull, push commands to easily get an"
            "overview of the local repo and update them accordingly."
        ),
    )

    subparsers = parser.add_subparsers(required=True, help="Sub-commands")

    status_parser = subparsers.add_parser("status", help="Show the status")
    status_parser.add_argument(
        "--check-remote",
        action="store_true",
        help="Whether to also show how many commits a local repo is behind the origin.",
    )
    status_parser.set_defaults(func=run_status)

    pull_parser = subparsers.add_parser("pull", help="Show the status")
    pull_parser.set_defaults(func=run_pull)

    push_parser = subparsers.add_parser("push", help="Show the status")
    push_parser.set_defaults(func=run_push)

    for subparser in [status_parser, pull_parser, push_parser]:
        subparser.add_argument(
            "--exclude",
            "-x",
            type=str,
            nargs="*",
            help="The names of the github repos you don't want to check.",
        )
        subparser.add_argument(
            "--all",
            "-a",
            action="store_true",
            help="Whether to show all the github repos. Default shows ones with unpushed changes.",
        )

        subparser.add_argument(
            "--verbose",
            "-v",
            action="store_true",
            help="Whether the unpushed files should be shown.",
        )
        subparser.add_argument(
            "--root",
            "-r",
            action=readable_dir,
            default=os.path.expanduser("~"),
            help="The root dir from which github repos should be searched for. ~ by default.",
        )
        behind_type = subparser.add_mutually_exclusive_group()
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

    args = parser.parse_args()

    untracked = (not args.modified and not args.untracked) or args.untracked
    modified = (not args.untracked and not args.modified) or args.modified
    exclude = [] if args.exclude is None else args.exclude

    if env_exclude := os.environ.get("LOCAL_GITS_EXCLUDE_REPO"):
        exclude.extend(env_exclude.split(";"))

    exclude_dirs = os.environ.get("LOCAL_GITS_EXCLUDE_DIR", "").split(";")

    gits = get_git_dirs(args.root, exclude, exclude_dirs)

    if len(gits) == 0:
        print("No local github repos found")
        return 0

    gits.sort(key=lambda x: x[0])

    args.func(args, untracked, modified, gits)
    return 0


if __name__ == "__main__":
    exit(main())
