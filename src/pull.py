import os

from pretty_print import failure, success, warning
from utils import (
    call_pull,
    commits_behind,
    get_cur_branch,
    get_unpushed_files,
    handle_pull_output,
)


def report_pull(git_dir: str, git_name: str, silent: bool) -> int:

    cur_branch = get_cur_branch(git_dir)
    if not cur_branch:
        return 0
    num_behind = commits_behind(git_dir, cur_branch)

    home_path = os.path.expanduser("~")

    files = get_unpushed_files(git_dir)

    fail_file_display_text = failure(f"{git_name}") + f"<{cur_branch}>{failure('->')} "
    pass_file_display_text = success(f"{git_name}") + f"<{cur_branch}>{success('->')} "
    merge_conflict_display_text = (
        warning(f"{git_name}") + f"<{cur_branch}>{warning('->')} "
    )

    fail_print_text = f"{git_dir.replace(home_path, '~')}: {fail_file_display_text}"
    pass_print_text = f"{git_dir.replace(home_path, '~')}: {pass_file_display_text}"
    merge_conflict_print_text = (
        f"{git_dir.replace(home_path, '~')}: {merge_conflict_display_text}"
    )

    if num_behind == 0:
        if not silent:
            print(
                f"{git_dir.replace(home_path, '~')}: {success(git_name)}<{cur_branch}>"
            )
        return 0

    if num_behind == -1:
        fail_print_text += f"{failure('Remote Branch Not Found')}"
        print(fail_print_text)
        return 1

    output, error = call_pull(git_dir, cur_branch)
    successful, files, merged, failed_merge, summary = handle_pull_output(output, error)

    text = merge_conflict_print_text if len(failed_merge) > 0 else pass_print_text

    if successful:
        if len(summary) > 0:
            text += summary + " "
        if len(failed_merge) > 0:
            text += warning("Merge Conflict")
    else:
        fail_print_text += failure("Error")

    print(text)

    if not silent:

        if not successful:
            print(f"  {summary}")
        else:
            for merge in failed_merge:
                print("  -", merge)
            for merge in merged:
                print("  - ", merge)

            if files:
                print(f"  Pulled:")
        for file in files:
            print("  -", file.replace("+", success("+")).replace("-", failure("-")))

    return int(bool(not successful or len(failed_merge) > 0))


# return 1 when merge failed
