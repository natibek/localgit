import os.path

from pretty_print import success
from utils import get_commit_logs, get_cur_branch


def report_log(git_dir: str, git_name: str, num_logs: int) -> int:
    """Reports the last `num_logs` outputs of the `git log --oneline` command for each repository.

    Args:
        git_dir: The repository containing the local clone of the repository.
        git_name: The name of the folder containing the github repository.
        num_logs: The last n logs of the `--oneline` log that will be shown. Maximum is 10.

    Returns exit codes 0 or 1.
    """
    logs = get_commit_logs(git_dir, num_logs)
    cur_branch = get_cur_branch(git_dir)

    home_path = os.path.expanduser("~")

    print(f"{git_dir.replace(home_path, '~')}: {success(git_name)}<{cur_branch}>")

    for log in logs:
        if log:
            print("  -", log)
    return 0
