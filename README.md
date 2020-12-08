# CommitAnalysis

Makes analysis of git commits easier

Fork of: https://github.com/SSE-LinuxAnalysis/ComAn

# Overview

The [Com]mit [Ex]traction process (realized as ComEx.sh script) creates a "diff file" for each commit of the repository and writes the changes introduced by the respective commit (the "git diff information") to that file. The [Com]mit [An]alysis process (realized as ComAn.py Python script) analyzes these changes for each commit based on given criteria to identify a subset of relevant commits. A detailed description of the tools realizing these processes can be found below. The current versions of these two core tools support:

    ComEx: any git-based software repository
    ComAn: any git-based software repository


# Technical Requirements:

    We suggest to use Ubuntu as operating system; we used Ubuntu 14.04.3 LTS
    For executing the ComEx.sh git has to be installed; we used git version 1.9.1
    

# [Com]mit [Ex]traction

The ComEx.sh script creates a "diff file" for each commit available in a git repository (the set of commits to be extracted can be further restricted by a commit list file; see "-l" option below). Such a "diff file" is named by the committer date (in Unix timestamp format) and the commit hash of the extracted commit. It contains the committer date in the first line and all changes introduced by the commit in the following lines. These changes are obtained by calling the "git show" command with some additional options to retrieve the entire content of each file changed by the respective commit. 

# Usage: 

    bash ComEx.sh [-i DIR] [-o DIR]

    -i <git_dir>       Specify the directory of the git repository
    -o <output_dir>    Specify the directory to save the "diff files" to
    -l <commit_list>   Specify a file containing the commits (SHA) to extract
                       [optional]. Each line of this file has to contain a
                       single commit SHA without leading or trailing
                       whitespaces.
                       
# [Com]mit [An]alysis

The ComAn.py Python script analyzes each "diff file" in the given input directory (see option below) to identify commits based on certain relevancy criteria. Currently, the script isolates commits 
  1. Changing specific test files in the /Tests directory 
  2. Containing only additions in \*.c and \*.h files in the /RelevantChanges directory

# Usage: 
    python3 ComAn.py [DIR]

    -<input_dir>       Optional: specify the directory of the input directory containing the diffs to be analyzed. Default is /Commits.
