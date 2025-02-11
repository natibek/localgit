import os.path
import subprocess
from enum import Enum

from .pretty_print import failure, success, warning


class PushStatus(Enum):
    """Enum for storing the status of the attemped push."""

    SUCCESSFUL = 0
    REPO_VIOLATION = 1
    OTHER_FAILURE = 2


def get_commit_logs(git_dir: str, num_logs: int) -> list[str]:
    """Get the last min(`num_logs`, number of commit logs) logs of a github repository.

    Args:
        git_dir: The directory where the local repo is.
        num_logs: Maximum number of logs to get from the repositories.

    Returns a list of the last `num_logs` logs.
    """
    logs_output = subprocess.Popen(
        ["git", "log", "--oneline"],
        cwd=git_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    output, error = logs_output.communicate()

    if error.decode("utf-8"):
        return []
    # print(error.decode("utf-8"))
    logs = output.decode("utf-8").split("\n")
    return logs[: min(len(logs), num_logs)]


def call_commit(git_dir: str, message: str, tracked: bool = False) -> str | None:
    """Call `git commit -m ` with a message.

    Args:
        git_dir: The github directory where the command will be run.
        message: The commit message.

    Returns:
        The text output from the command or None if commit failed.
    """
    if tracked: option = "-am"
    else: option = "-m"

    output = subprocess.Popen(
        ["git", "commit", option, message],
        cwd=git_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    commit_output, error = output.communicate()

    if error:
        return None

    commit_output = commit_output.decode().split("\n")[1].strip()
    return commit_output


def call_add_all(git_dir: str) -> None:
    """Call `git add -A`.

    Args:
        git_dir: The github directory where the command will be run.
    """
    subprocess.call(
        f"git add -A".split(" "),
        cwd=git_dir,
    )


def call_push(git_dir: str, cur_branch: str) -> PushStatus:
    """Call `git push` or `git push -u origin cur_branch`.

    Args:
        git_dir: The github directory where the command will be run.
        cur_branch: The branch that the user has checkout.

    Returns:
        Whether the command was successful.
    """
    push_output = subprocess.Popen(
        "git push".split(" "),
        cwd=git_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    _, error = push_output.communicate()

    # print(f"{output=}")
    # print(f"{error=}")
    error = error.decode("utf-8")
    if "push declined due to repository rule violations" in error:
        return PushStatus.REPO_VIOLATION

    if "git push --set-upstream origin" in error:
        push_output = subprocess.Popen(
            f"git push -u origin {cur_branch}".split(" "),
            cwd=git_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        _, error = push_output.communicate()
        # print(f"{output=}")
        # print(f"{error=}")
    return PushStatus.SUCCESSFUL


def call_pull(git_dir, cur_branch) -> tuple[str, str]:
    """Call `git pull origin cur_branch`.

    Args:
        git_dir: The github directory where the command will be run.
        cur_branch: The branch that the user has checkout.

    Returns:
        Tuple reporting whether the stdout, and stderr.
    """
    pull_output = subprocess.Popen(
        f"git pull origin {cur_branch}".split(" "),
        cwd=git_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    output, error = pull_output.communicate()
    output = output.decode("utf-8")
    error = error.decode("utf-8")

    # print(f"{output=}")
    # print(f"{error=}")
    return output, error


def handle_pull_output(
    output: str, error: str
) -> tuple[bool, list[str], list[str], list[str], str]:
    """Handles the output of `call_pull` to report what files were pull, merged, and failed to
    merge.

    Args:
        output: The text in the stdout after `git pull origin ...` was called.
        error: The text in the stderr after `git pull origin ...` was called.

    Returns:
        Tuple reporting whether the call was successful, the files that were pulled,
        successfully merged, filed to merge, and summary of the pull.
    """
    pulled = []
    merged = []
    failed_merge = []
    summary = ""
    successful = True

    if "Aborting" in error:  # git pull aborted because commits haven't been pushed
        successful = False
        error_lst = error.split("\n")
        for idx, line in enumerate(error_lst):
            if "overwritten by merge" in line:
                summary = line.split(":")[1].strip() + ": "
                for file in error_lst[idx + 1 :]:
                    if "Please commit your changes" in file:
                        break
                    pulled.append(file.strip())
                break
    elif "fatal: Exiting because of an unresolved conflict" in error:  # merge conflict
        successful = False
        summary = failure("Unresolved Conflict")
    else:
        output_lst = output.split("\n")
        for idx, line in enumerate(output_lst):

            if line.startswith("Auto-merging"):  # Merge conflict exists
                if output_lst[idx + 1].startswith(
                    "CONFLICT (content): Merge conflict in "
                ):
                    message = output_lst[idx + 1].split(": ")[1].strip().split(" ")
                    message = " ".join(message[0:2]) + ": " + " ".join(message[3:])
                    failed_merge.append(
                        message.replace("Merge conflict", warning("Merge conflict"))
                    )
                else:
                    merged.append(
                        line.replace("Auto-merging", success("Auto-merging") + ":")
                    )
            elif any(text in line for text in ["Fast-forward", "Merge made by"]):
                # No conflicts
                for file in output_lst[idx + 1 :]:
                    if any(
                        text in file
                        for text in ["file changed", "insertion", "deletion"]
                    ):
                        summary = file.replace("+", success("+")).replace(
                            "-", failure("-")
                        )
                        break
                    pulled.append(file)
                break

    return successful, pulled, merged, failed_merge, summary


def get_commit_diffs(git_dir: str, cur_branch: str) -> tuple[int, ...]:
    """Get the commit difference between the local repo and the origin.

    Args:
        git_dir: The github directory where the command will be run.
        cur_branch: The branch that the user has checkout.

    Returns:
        The number of commits the local repo is ahead and behind the origin.
    """
    fetch = subprocess.Popen(
        f"git fetch origin {cur_branch}".split(" "),
        cwd=git_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    _, error = fetch.communicate()
    if "couldn't find remote ref" in error.decode("utf-8"):
        return -1, -1

    commits_count = subprocess.Popen(
        f"git rev-list --left-right --count {cur_branch}...origin/{cur_branch}".split(
            " "
        ),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=git_dir,
    )
    output, error = commits_count.communicate()

    if "unknown revision or path not in the working tree" in error.decode("utf-8"):
        return -1, -1

    return tuple(int(diff) for diff in output.decode("utf-8")[:-1].split("\t"))


def num_commits_ahead(git_dir: str, cur_branch: str) -> int:
    """Check how many commits you are ahead of the origin.

    Args:
        git_dir: The github directory where the command will be run.
        cur_branch: The branch that the user has checkout.

    Returns:
        The number of commits the local repo is behind the origin.
    """
    return get_commit_diffs(git_dir, cur_branch)[0]


def num_commits_behind(git_dir: str, cur_branch: str) -> int:
    """Check how many commits you are behind the origin.

    Args:
        git_dir: The github directory where the command will be run.
        cur_branch: The branch that the user has checkout.

    Returns:
        The number of commits the local repo is behind the origin.
    """
    return get_commit_diffs(git_dir, cur_branch)[1]


def get_unpushed_files(git_dir: str) -> list[str]:
    """Gets the files in the local branch that are modified or untracked.

    Args:
        git_dir: The github directory where the command will be run.

    Returns:
        The modified files (starting with 'M') and untracked files (starting with '??').
    """
    files = subprocess.check_output(
        ["git", "status", "--porcelain"],
        text=True,
        cwd=git_dir,
    ).split("\n")

    return [file.strip() for file in files if file]


def get_cur_branch(git_dir) -> str | None:
    """Gets the current branch the local repo is checkout into.

    Args:
        git_dir: The github directory where the command will be run.

    Returns:
        The name of the current branch or None if there was an error.
    """
    fetch = subprocess.Popen(
        ["git", "branch", "--show-current"],
        cwd=git_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    output, error = fetch.communicate()
    if error.decode("utf-8"):
        return None

    return output.decode()[:-1]


def get_git_names(git_dirs: list[str]) -> list[str]:
    """Gets the names of the folders containing the local clone of github repositories.

    Args:
        git_dirs: List of the valid directories containing github repositories.

    Returns a list of the folder names containing the github repositories.
    """
    return [os.path.basename(git_dir) for git_dir in git_dirs]


def find_dirs_from_repo_names(
    repo_names: list[str], valid_git_dirs: list[str]
) -> list[tuple[str, str]]:
    """Finds the directories for each of the specified repo names with binary search.

    Args:
        repo_names: The user provided list of repo names.
        valid_git_dirs: All the valid git dirs found locally.

    Returns a list of pairs of folder names and directories of where the repositories are.
    """
    dirs_map = {os.path.basename(git_dir): git_dir for git_dir in valid_git_dirs}
    # gits = [(name, dirs_map[name]) for name in set(repo_names) if name in dirs_map]
    gits = []

    for name in set(repo_names):
        if name in dirs_map:
            gits.append((name, dirs_map[name]))
        else:
            print(
                warning(
                    f"No folder with name <{name}> containing a git repo was found."
                )
            )

    return gits


def get_all_git_dirs() -> list[str]:
    """Gets all the local git repo clones found on the device. Uses `file . -name .git` ran on the
    /home/$USER/ directory.

    Returns all the git repo clones found on the device.
    """

    root_dir = os.path.expanduser("~")
    git_dirs = subprocess.check_output(
        ["find", ".", "-name", ".git"],
        text=True,
        cwd=root_dir,
    ).split("\n")

    return [
        os.path.abspath(os.path.dirname(root_dir + git_dir[1:]))
        for git_dir in git_dirs
        if git_dir
    ]


def get_valid_git_dirs(exclude: list[str], exclude_dirs: list[str]) -> list[str]:
    """Gets all the valid directories containing github repositories excluding directories and
    folders specified in --exclude-dirs flag or environment variables.

    Args:
        exclude: List of the github repo names to exclude.
        exclude_dirs: List of the directories containing github repositories to ignore.

    Returns all the directories containing git repositories after applying exclusion.
    """

    all_git_dirs = get_all_git_dirs()

    return [
        git_dir
        for git_dir in all_git_dirs
        if os.path.basename(git_dir) not in exclude
        and not any(
            direc in git_dir.replace(os.path.expanduser("~"), "~")
            for direc in exclude_dirs
        )
    ]


def get_excluded_git_dirs(exclude: list[str], exclude_dirs: list[str]) -> list[str]:
    """Gets all the directories containing github repositories that would be excluded with the
    --exclude-dirs flag or environment variables.

    Args:
        exclude: List of the github repo names to exclude.
        exclude_dirs: List of the directories containing github repositories to ignore.

    Returns all the directories containing git repositories after applying exclusion.
    """
    all_git_dirs = get_all_git_dirs()

    return [
        git_dir
        for git_dir in all_git_dirs
        if os.path.basename(git_dir) in exclude
        or any(
            direc in git_dir.replace(os.path.expanduser("~"), "~")
            for direc in exclude_dirs
        )
    ]


def get_git_dirs(valid_git_dirs: list[str]) -> list[tuple[str, str]]:
    """Gets the directories and foldernames containing the local clone of the github
    repositories.

    Returns a list of pairs of folder names and directories of where the repositories are.
    """
    return list(zip(get_git_names(valid_git_dirs), valid_git_dirs))
