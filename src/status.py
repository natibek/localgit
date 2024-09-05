import os

from pretty_print import failure, success
from utils import commits_ahead, commits_behind, get_cur_branch, get_unpushed_files


def report_status(
    git_dir: str,
    git_name: str,
    silent: bool,
    untracked: bool,
    modified: bool,
    check_remote: bool,
    check_ahead: bool,
) -> int:

    files = get_unpushed_files(git_dir)
    cur_branch = get_cur_branch(git_dir)

    if not cur_branch:
        return 0

    num_behind = commits_behind(git_dir, cur_branch) if check_remote else 0
    num_ahead = commits_ahead(git_dir, cur_branch) if not check_remote else 0

    home_path = os.path.expanduser("~")

    if len(files) == 0 and num_behind == 0 and num_ahead == 0:
        if not silent:
            print(
                f"{git_dir.replace(home_path, '~')}: {success(git_name)}<{cur_branch}>"
            )
        return 0

    modified_count = sum(1 for file in files if file.startswith("M"))
    untracked_count = sum(1 for file in files if file.startswith("?"))

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
