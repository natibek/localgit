import os.path

from .pretty_print import failure, success
from .utils import get_cur_branch


def report_list(
    git_dir: str,
    git_name: str,
    excluded: bool,
):
    """List all the local repo clones found on the device.

    Args:
        git_dir: The directory where the local repo is.
        git_name: The name of the folder containing the github repository.
        excluded: Whether the repo will be excluded by other commands given the configuration.
    """

    cur_branch = get_cur_branch(git_dir)
    if cur_branch is None:
        return 0

    branch_text = f"<{cur_branch}>" if cur_branch else ""
    home_path = os.path.expanduser("~")

    if excluded:
        print(f"{git_dir.replace(home_path, '~')}: {failure(git_name)}{branch_text}")
    else:
        print(f"{git_dir.replace(home_path, '~')}: {success(git_name)}{branch_text}")
    return 0
