import os.path

from .pretty_print import failure, success
from .utils import get_commit_diffs, get_cur_branch, get_unpushed_files


def report_status(
    git_dir: str,
    git_name: str,
    silent: bool,
    untracked: bool,
    modified: bool,
    commit_diffs: bool,
) -> int:
    """Report the status of local repositories.

    Args:
        git_dir: The directory where the local repo is.
        git_name: The name of the folder containing the github repository.
        silent: Whether to remove details from output.
        untracked: Whether to only report untracked files.
        modified: Whether to only report modified files.
        commit_diffs: Whether to check how many commits a local repo is ahead and behind the origin.

    Returns exit codes 0 (the local repository is uptodate) or 1 (otherwise).
    """

    cur_branch = get_cur_branch(git_dir)

    if not cur_branch:
        return 0

    num_ahead, num_behind = (
        get_commit_diffs(git_dir, cur_branch) if commit_diffs else (0, 0)
    )

    files = get_unpushed_files(git_dir)
    home_path = os.path.expanduser("~")

    modified_count = sum(1 for file in files if file.startswith("M")) if modified else 0
    untracked_count = (
        sum(1 for file in files if file.startswith("?")) if untracked else 0
    )

    no_files = (
        len(files) == 0
        or (modified_count == 0 and modified and not untracked)
        or (untracked_count == 0 and untracked and not modified)
    )
    if (num_ahead, num_behind) == (0, 0) and no_files:
        if not silent:
            print(
                f"{git_dir.replace(home_path, '~')}: {success(git_name)}<{cur_branch}>"
            )
        return 0

    # cases that are considered a failure.
    if (
        (modified_count and modified)
        or (untracked_count and untracked)
        or num_ahead > 0
        or num_ahead == -1
        or num_behind > 0
        or num_behind == -1
    ):
        file_display_text = failure(f"{git_name}") + f"<{cur_branch}>" + failure("-> ")
        print_text = f"{git_dir.replace(home_path, '~')}: {file_display_text}"
    else:
        return 0

    if modified_count > 0 and modified:
        print_text += f"{failure('M')}odified:{failure(str(modified_count))} "
    if untracked_count > 0 and untracked:
        print_text += f"{failure('U')}ntracked:{failure(str(untracked_count))} "

    if num_behind == -1 or num_ahead == -1:
        print_text += f"{failure('Remote Branch Not Found')}"
    else:
        if num_ahead > 0:
            print_text += f"{failure('A')}head:{failure(str(num_ahead))} "
        if num_behind > 0:
            print_text += f"{failure('B')}ehind:{failure(str(num_behind))}"

    print(print_text)

    if not silent:
        for file in files:
            if modified and file.startswith("M"):
                print("  -", file)
            if untracked and file.startswith("?"):
                print("  -", file)
    return 1
