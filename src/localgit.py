#!/usr/bin/env python3

import os.path

from .list import report_list
from .log import report_log
from .parsers import setup_parser
from .pretty_print import success, warning
from .pull import report_pull
from .push import report_push
from .status import report_status
from .utils import (
    find_dirs_from_repo_names,
    get_excluded_git_dirs,
    get_git_dirs,
    get_valid_git_dirs,
)


def run_log(args, gits: list[tuple[str, str]]) -> int:
    """Runs the `localGits log` command with the input arguments.

    Args:
        args: The parsed CL arguments for the log suparser and their values.
        gits: List of pairs of the folder names and directories of where the local repositories are.

    Returns exit codes 0 (the command was ran successfully in all repos) or 1 (otherwise).
    """
    exit_code = 0
    for git_name, git_dir in gits:
        exit_code |= report_log(
            git_dir,
            git_name,
            args.num_logs,
        )
    return exit_code


def run_status(args, gits: list[tuple[str, str]]):
    """Runs the `localGits status` command with the input arguments.

    Args:
        args: The parsed CL arguments for the status suparser and their values.
        gits: List of pairs of the folder names and directories of where the local repositories are.

    Returns exit codes 0 (all the local repositories are uptodate) or 1 (otherwise).
    """

    all_tags_false = (
        not args.modified and not args.untracked
    )  # the flags are false by default. If all are false, then run all. Better way?
    untracked = all_tags_false or args.untracked
    modified = all_tags_false or args.modified

    exit_code = 0
    for git_name, git_dir in gits:
        exit_code |= report_status(
            git_dir,
            git_name,
            args.silent,
            args.verbose,
            untracked,
            modified,
            args.commit_diffs,
        )

    if exit_code == 0:
        print(success("Repos are uptodate."))

    print()
    return exit_code


def run_pull(args, gits: list[tuple[str, str]]) -> int:
    """Runs the `localGits pull ` command with the input arguments.

    Args:
        args: The parsed CL arguments for the pull suparser and their values.
        gits: List of pairs of the folder names and directories of where the local repositories are.

    Returns exit codes 0 (if the pull call was successful in all repos) or 1 (otherwise).
    """
    exit_code = 0

    for git_name, git_dir in gits:
        exit_code |= report_pull(
            git_dir,
            git_name,
            args.silent,
            args.verbose,
        )

    if exit_code == 0:  # use an enum?
        print(success("Repos are uptodate."))
    print()

    return exit_code


def run_push(args, gits: list[tuple[str, str]]) -> int:
    """Runs the `localGits push` command with the input arguments.

    Args:
        args: The parsed CL arguments for the push suparser and their values.
        gits: List of pairs of the folder names and directories of where the local repositories are.

    Returns exit codes 0 (if the push call was successful in all repos) or 1 (otherwise).
    """

    exit_code = 0
    for git_name, git_dir in gits:
        exit_code |= report_push(
            git_dir, git_name, args.silent, args.verbose, args.push_all, args.message
        )

    if exit_code == 0:
        print(success("Repos are uptodate."))
    print()
    return exit_code


def run_list(gits: list[tuple[str, str]], excluded_gits: list[tuple[str, str]]) -> int:
    if len(gits) == 0 and len(excluded_gits) == 0:
        print(warning("No local github repos found."))
        return 1

    for git_name, git_dir in gits:
        report_list(git_dir, git_name, False)

    if len(excluded_gits) > 0:
        print("\nExcluded: ")

    for git_name, git_dir in excluded_gits:
        report_list(git_dir, git_name, True)
    print()

    return 0


def main():
    """Executes the `localGits` command by finding all the local repos and call status, pull,
    push, or log in each of the repos. Also, setups the approriate argument parser for each of
    the commands. Looks for enviriomental variables `LOCAL_GITS_EXCLUDE_REPO` which is a `;`
    separated string containing the names of the repositories to exlude and `LOCAL_GITS_EXCLUDE_DIR`
    which is also a `;` separated string containing the directories from within no repositories
    should be included (eg '~/.cache/;~/.local/share/nvim/lazy').

    Returns exit code as determined by commands.
    """
    parser = setup_parser(run_push, run_pull, run_status, run_log)
    args = parser.parse_args()

    exclude = [] if args.exclude is None else args.exclude

    if env_exclude := os.environ.get("LOCALGIT_EXCLUDE_REPO"):
        exclude.extend(env_exclude.split(";"))

    exclude_dirs = os.environ.get("LOCALGIT_EXCLUDE_DIR", "").split(";")

    if args.subcommand == "list":
        # hande the `list` command differently because the function parameters are not the same
        valid_git_dirs = get_valid_git_dirs(exclude, exclude_dirs)
        gits = get_git_dirs(valid_git_dirs)
        gits.sort(key=lambda x: x[0])

        if args.all:
            excluded_git_dirs = get_excluded_git_dirs(exclude, exclude_dirs)
            excluded_gits = get_git_dirs(excluded_git_dirs)
            excluded_gits.sort(key=lambda x: x[1])
            # sort by directory string because there are a bunch of .local, .cache directories. Looks better for printing
        else:
            excluded_gits = []

        return run_list(gits, excluded_gits)

    if not args.repo_names and not args.repo_directories:
        valid_git_dirs = get_valid_git_dirs(exclude, exclude_dirs)
        gits = get_git_dirs(valid_git_dirs)
    else:
        gits = []
        if git_dirs := args.repo_directories:
            git_dirs = [
                git_dir[:-1] if git_dir[-1] == "/" else git_dir for git_dir in git_dirs
            ]
            gits = get_git_dirs(git_dirs)
        if repo_names := args.repo_names:
            valid_git_dirs = get_valid_git_dirs(exclude, exclude_dirs)
            gits.extend(find_dirs_from_repo_names(repo_names, valid_git_dirs))
            gits = list(set(gits))  # combine and make unique

    if len(gits) == 0:
        print(warning("No local github repos found."))
        return 1

    gits.sort(key=lambda x: x[0])
    return args.func(args, gits)


if __name__ == "__main__":
    exit(main())
