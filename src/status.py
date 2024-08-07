from pretty_print import *
from utils import *


def report_git_status(
    git_dir, git_name, verbose, all, untracked, modified, check_remote
):

    files = get_unpushed_files(git_dir)
    cur_branch = get_cur_branch(git_dir)

    if not cur_branch:
        return 0

    num_behind = commits_behind(git_dir, cur_branch) if check_remote else 0

    home_path = os.path.expanduser("~")

    if len(files) == 0 and num_behind == 0:
        if all:
            print(
                f"{git_dir.replace(home_path, '~')}: {success(git_name)}<{cur_branch}>"
            )
        return 0

    modified_count = sum(1 for file in files if file.startswith("M"))
    untracked_count = sum(1 for file in files if file.startswith("?"))

    if (
        (modified_count and modified)
        or (untracked_count and untracked)
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
    if num_behind > 0:
        print_text += f"{failure('B')}ehind:{failure(str(num_behind))}"
    elif num_behind == -1:
        print_text += f"{failure('Remote Branch Deleted')}"

    print(print_text)

    if verbose:
        for file in files:
            if modified and file.startswith("M"):
                print("  -", file)
            if untracked and file.startswith("?"):
                print("  -", file)
    return 1
