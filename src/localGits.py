#!/usr/bin/env python3

import os

from parsers import setup_parser
from pretty_print import *
from pull import *
from push import *
from status import *


def run_status(args, gits: list[tuple[str, str]]):
    all_tags_false = (
        not args.modified
        and not args.untracked
        and not args.check_remote
        and not args.check_ahead
    )
    untracked = all_tags_false or (args.untracked)
    modified = all_tags_false or args.modified
    check_ahead = all_tags_false or args.check_ahead

    exit_code = 0
    for git_name, git_dir in gits:
        exit_code |= report_status(
            git_dir,
            git_name,
            args.silent,
            untracked,
            modified,
            args.check_remote,
            check_ahead,
        )

    if exit_code == 0 and args.check_remote:
        print(success("No repos are behind their origin."))
    elif exit_code == 0:
        print(success("All repos are pushed."))

    print()
    return exit_code


def run_pull(args, gits: list[tuple[str, str]]) -> int:
    exit_code = 0

    for git_name, git_dir in gits:
        exit_code |= report_pull(
            git_dir,
            git_name,
            args.silent,
        )

    if exit_code == 0:  # use an enum?
        print(success("All repos are uptodate."))
    print()

    return exit_code


def run_push(args, gits: list[tuple[str, str]]) -> int:

    exit_code = 0
    for git_name, git_dir in gits:
        exit_code |= report_push(
            git_dir, git_name, args.silent, args.push_all, args.message
        )

    if exit_code == 0:
        print(success("All repos are uptodate."))
    print()
    return exit_code


def main():
    parser = setup_parser(run_push, run_pull, run_status)
    args = parser.parse_args()

    exclude = [] if args.exclude is None else args.exclude

    if env_exclude := os.environ.get("LOCAL_GITS_EXCLUDE_REPO"):
        exclude.extend(env_exclude.split(";"))

    exclude_dirs = os.environ.get("LOCAL_GITS_EXCLUDE_DIR", "").split(";")

    if git_dirs := args.repo_directories:
        git_dirs = [
            git_dir[:-1] if git_dir[-1] == "/" else git_dir for git_dir in git_dirs
        ]
        gits = list(zip(get_git_names(git_dirs), git_dirs))
        args.all = True
    else:
        gits = get_git_dirs(exclude, exclude_dirs)

    if len(gits) == 0:
        print("No local github repos found")
        return 0

    gits.sort(key=lambda x: x[0])

    args.func(args, gits)
    return 0


if __name__ == "__main__":
    exit(main())
