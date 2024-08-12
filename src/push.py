from pretty_print import *
from utils import *


def report_push(
    git_dir: str, git_name: str, silent: bool, push_all: bool, message: str
) -> int:

    files = get_unpushed_files(git_dir)
    cur_branch = get_cur_branch(git_dir)

    if not cur_branch:
        return 0

    home_path = os.path.expanduser("~")

    if len(files) == 0:
        if not silent:
            print(
                f"{git_dir.replace(home_path, '~')} :"
                + success(f"{git_name}")
                + f"<{cur_branch}>"
            )
        return 0

    fail_file_display_text = failure(f"{git_name}") + f"<{cur_branch}>{failure('->')} "
    pass_file_display_text = success(f"{git_name}") + f"<{cur_branch}>{success('->')} "

    fail_print_text = f"{git_dir.replace(home_path, '~')}: {fail_file_display_text}"
    pass_print_text = f"{git_dir.replace(home_path, '~')}: {pass_file_display_text}"

    if push_all:
        call_add_all(git_dir)
        commit_output = call_commit(git_dir, message)
    else:
        commit_output = call_commit_modified(git_dir, message)

    successful = call_push(git_dir, cur_branch)

    if successful:
        pass_print_text += (
            commit_output.replace("+", success("+")).replace("-", failure("-")).strip()
        )
        print_text = pass_print_text
    else:
        fail_print_text += f"{failure('A')}borting"
        print_text = fail_print_text

    print(print_text)

    if not silent and successful:
        for file in files:
            if file.startswith("M"):
                print("  -", file)
            if file.startswith("?") and push_all:
                print("  -", file)

    return int(not successful)
