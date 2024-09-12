# localgit

Command line tool for managing all local git repository clones simultaneously. It includes `status`, `pull`, `push`, and `log` commands which have similar functionalities as their `git` counterparts but affect all/specified local repositories.

To always ignore specific repositories or whole directories when using localgits, you can add them to environmental variables `LOCALGIT_EXCLUDE_REPO` and `LOCALGIT_EXCLUDE_DIR`. These environmental variables are `;` separated strings. Any local repository clone with a name matching one found in `LOCALGIT_EXCLUDE_REPO` and any local repository clone found within any of the directories in `LOCALGIT_EXCLUDE_DIR` will not be affected/checked by `localgit`.

## Installing

If using a Linux Distro, use [`pipx`](https://github.com/pypa/pipx) to install globally. Then:

```bash
pipx install localgit
```

Otherwise, install globally like usual for Windows and Mac.

## Common arguments

For all commands in localgit, the following CL optional arguments are available:

1. `repo_names`: The names of the folders with git repos to check/affect. This is case insensitive.
1. `--repo-directories`, `-r`: Directories with git repos to affect. Their validity is checked by the parser.
1. `--exclude`, `-x`: The names of the git repo folders you don't want to check/affect.
1. `--silent`, `-s`: Do not print repo specific outputs. Only print holistic details. (not available for `localgit log`)

## `localgit status`

Calls `git status` in each git repository clone.

Has the following arguments:

1. `--modified`: Only check for modified files. \~
1. `--untracked`: Only check for untracked files. \~
1. `--commit-diffs`: Check how many commits ahead and behind the origin the local repo clone is. \*

_\~ Arguments are mutually exclusive._

_\* Uses `git rev-list --left-right --count <branch>...origin/<branch>`._

## `localgit pull`

Calls `git pull` in each git repository clone. It reports cases where there are merge conflicts, successful merges, and any errors that occur when pulling from the origin.

Has the following argument:

1. `--verbose`, `-v`: Print summary for all repos (including those unaffected by command).

## `localgit push`

Calls `git commit -am "new updates" ; git push` in each git repository clone (therefore only commits and pushes modified files). Ensures that the local clone is not behind the origin.

Has the following arguments:

1. `--push-all`, `-A`: Push all the changes including untracked ones.
1. `--message`, `-m`: The commit message. Default is 'modified <comma separated list of modified files>. added <comma separated list of untracked files>.
1. `--verbose`, `-v`: Print summary for all repos (including those unaffected by command).

## `localgit log`

Calls `git log --oneline` in each git reposotiry clone and reports the last 3 commit logs or less (if there are fewer) by default.

Has the following argument:

1. `--num-logs`, `-n`: The number of logs to show for each local repo. Default if 3.
