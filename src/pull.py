from pretty_print import *
from utils import *


def report_pull(git_dir, git_name, silent):

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
            print(pass_print_text + f"{success('N')}ot Behind")
        return 0

    if num_behind == -1:
        fail_print_text += f"{failure('Remote Branch Not Found')}"
        print(fail_print_text)
        return 1

    # num_behind > 0
    successful, output, error = call_pull(git_dir, cur_branch)
    files, merged, failed_merge, summary = handle_pull_output(successful, output, error)

    if len(failed_merge) > 0:
        text = merge_conflict_print_text
    else:
        text = pass_print_text

    if successful:
        if summary:
            text += (
                summary.replace("+", success("+")).replace("-", failure("-")).strip()
            ) + " "
        if failed_merge:
            text += f"{warning('Merge Conflict')}"
        print_text = pass_print_text
    else:
        fail_print_text += f"{failure('Aborting')}"
        print_text = fail_print_text

    print(print_text)

    if not silent:

        if not successful:
            print(f"  {summary}:")
        else:
            for merge in failed_merge:
                print("  -", merge)
            for merge in merged:
                print("  - ", merge)

            if files:
                print(f"  Pulled:")
            for file in files:
                print("  -", file.replace("+", success("+")).replace("-", failure("-")))

    print(int(bool(not successful and len(failed_merge) > 0)))
    return int(bool(not successful and len(failed_merge) > 0))


# return 1 when merge failed
