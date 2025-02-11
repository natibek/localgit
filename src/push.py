import os.path

from .pretty_print import failure, success
from .utils import (
    PushStatus,
    call_add_all,
    call_commit,
    call_push,
    get_cur_branch,
    get_unpushed_files,
    num_commits_ahead,
)


def report_push(
    git_dir: str,
    git_name: str,
    silent: bool,
    verbose: bool,
    push_all: bool,
    message: str,
) -> int:
    """Push all the repositories that are ahead of their origin and report the result of pushing.

    Args:
        git_dir: The directory where the local repo is.
        git_name: The name of the folder containing the github repository.
        silent: Whether to remove details from output.
        verbose: Whether to print for directories unaffected by the command.
        push_all: Whether to commit and push both modified and untracked files.
        message: The commit message. Default is "new updates"

    Returns exit codes 0 (if the push call was successful) or 1 (otherwise).
    """
    cur_branch = get_cur_branch(git_dir)
    if cur_branch is None:
        return 0

    files = get_unpushed_files(git_dir)
    num_ahead = num_commits_ahead(git_dir, cur_branch)
    home_path = os.path.expanduser("~")

    if len(files) == 0 and num_ahead == 0:
        if not silent and verbose:
            print(
                f"{git_dir.replace(home_path, '~')}: "
                + success(f"{git_name}")
                + f"<{cur_branch}>"
            )
        return 0

    if len(files) > 0:
        pass_file_display_text = (
            success(f"{git_name}") + f"<{cur_branch}>{success('->')}"
        )

        has_modified = any(file.startswith("M") for file in files)
        has_untracked = any(file.startswith("?") for file in files)
        has_deleted = any(file.startswith("D") for file in files)

        modified_message = (
            " Updated "
            + ", ".join(file[2:] for file in files if file.startswith("M"))
            + ". "
            if has_modified and not message
            else ""
        )
        added_message = (
            " Added "
            + ", ".join(file[3:] for file in files if file.startswith("?"))
            + ". "
            if has_untracked and not message
            else ""
        )
        deleted_message = (
            " Deleted "
            + ", ".join(file[2:] for file in files if file.startswith("D"))
            + ". "
            if has_deleted and not message
            else ""
        )

        if push_all:
            call_add_all(git_dir)
            commit_output = call_commit(
                git_dir, message or (modified_message + added_message + deleted_message)
            )
        elif has_modified or has_deleted:
            commit_output = call_commit(
                git_dir, message or (modified_message + deleted_message), True
            )
        elif not silent and verbose:
            print(
                f"{git_dir.replace(home_path, '~')}: "
                + success(f"{git_name}")
                + f"<{cur_branch}>"
            )
            return 0
        else:
            return 0

        if commit_output is None:
            print(
                f"{git_dir.replace(home_path, '~')}: "
                + failure(f"{git_name}")
                + f"<{cur_branch}>"
                + failure("-> Commit Failed")
            )
            return 1

    else:
        assert num_ahead > 0
        # cases like merges from other branch into local branch.
        # No file is shown as modified or untracked but there are commits that have not been pushed
        pass_file_display_text = success(f"{git_name}") + f"<{cur_branch}> "
        commit_output = ""

    push_status = call_push(git_dir, cur_branch)

    fail_file_display_text = failure(f"{git_name}") + f"<{cur_branch}>{failure('->')} "

    fail_print_text = f"{git_dir.replace(home_path, '~')}: {fail_file_display_text}"
    pass_print_text = f"{git_dir.replace(home_path, '~')}: {pass_file_display_text}"

    if push_status == PushStatus.SUCCESSFUL:
        if commit_output:
            pass_print_text += (
                commit_output.replace("+", success("+"))
                .replace("-", failure("-"))
                .strip()
            )
        print_text = pass_print_text
    elif push_status == PushStatus.REPO_VIOLATION:
        fail_print_text += failure("Repository Rule Violation")
        print_text = fail_print_text

    else:
        fail_print_text += failure("Aborting")
        print_text = fail_print_text

    print(print_text)

    if not silent and push_status == PushStatus.SUCCESSFUL:
        for file in files:
            if file.startswith("M"):
                print("  -", file)
            if file.startswith("D"):
                print("  -", file)
            if file.startswith("?") and push_all:
                print("  -", file)

    return int(not push_status == PushStatus.SUCCESSFUL)
