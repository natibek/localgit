import os
import subprocess


def pull(git_dir, cur_branch) -> tuple[bool, list[str], str]:
    pull_output = subprocess.Popen(
        f"git pull origin {cur_branch}".split(" "),
        cwd=git_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    output, error = pull_output.communicate()
    output = output.decode("utf-8").split("\n")
    error = error.decode("utf-8")

    pulled = []
    summary = ""

    for idx, line in enumerate(output):
        if "Fast-forward" in line:
            for file in output[idx + 1 :]:
                if any(
                    text in file for text in ["file changed", "insertions", "deletions"]
                ):
                    summary = file
                    break
                pulled.append(file)
            break

    return True, pulled, summary


def commits_behind(git_dir: str, cur_branch: str) -> int:
    """Check how many commits you are behind."""

    fetch = subprocess.Popen(
        f"git fetch origin {cur_branch}".split(" "),
        cwd=git_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    _, error = fetch.communicate()
    if "couldn't find remote ref" in error.decode("utf-8"):
        return -1

    commits_count = subprocess.check_output(
        f"git rev-list --left-right --count {cur_branch}...origin/{cur_branch}".split(
            " "
        ),
        text=True,
        cwd=git_dir,
    )[:-1].split("\t")
    return int(commits_count[1])


def get_unpushed_files(git_dir: str) -> list[str]:
    files = subprocess.check_output(
        ["git", "status", "--porcelain"],
        text=True,
        cwd=git_dir,
    ).split("\n")

    return [file.strip() for file in files if file]


def get_cur_branch(git_dir):
    cur_branch = subprocess.check_output(
        ["git", "branch", "--show-current"],
        text=True,
        cwd=git_dir,
    )[:-1]
    return cur_branch


def get_git_dirs(
    home_dir: str, exclude: list[str], exclude_dirs: list[str]
) -> list[tuple[str, str]]:
    home_dir = os.path.expanduser(home_dir)
    git_dirs = subprocess.check_output(
        ["find", ".", "-name", ".git"],
        text=True,
        cwd=home_dir,
    ).split("\n")

    git_dirs = [
        os.path.abspath(os.path.dirname(home_dir + git_dir[1:]))
        for git_dir in git_dirs
        if git_dir
    ]
    git_dirs = [
        git_dir
        for direc in exclude_dirs
        for git_dir in git_dirs
        if not direc
        or direc not in git_dir.replace(os.path.expanduser("~"), "~")
        and os.path.basename(git_dir) not in exclude
    ]

    git_names = [os.path.basename(git_dir) for git_dir in git_dirs]
    return list(zip(git_names, git_dirs))
