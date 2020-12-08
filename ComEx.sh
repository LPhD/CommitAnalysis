#!/bin/bash

#bash ComEx.sh -i /home/lea/Downloads/CommitAnalysis/Repo/the_silver_searcher -o /home/lea/Downloads/CommitAnalysis/Commits

showHelp() {
    echo -e "\n\t[Com]mit [Ex]tractor\n\n"
    echo "The ComEx.sh script creates a \"diff file\" for each commit available in a git"
    echo "repository (the set of commits to be extracted can be further restricted by a"
    echo "commit list file; see \"-l\" option below). Such a \"diff file\" is named by the"
    echo "SHA of the extracted commit and contains the committer date in the first line"
    echo "and all changes introduced by the commit in the following lines. These changes"
    echo "are obtained by calling the \"git show\" command with some additional options to"
    echo "retrieve the entire content of each file changed by the respective commit. The"
    echo "entire content is required to unambiguously differentiate changes to artifact-"
    echo -e "specific and variability information during the commit analysis process.\n"
    echo "Usage: ${0##*/} [-i DIR] [-o DIR]"
            echo " -i <git_dir>       specify the directory of the git repository"
            echo " -o <output_dir>    specify the directory to save the \"diff files\" to"
            echo " -l <commit_list>   specify a file containing the commits (SHA) to extract"
            echo "                    [optional]. Each line of this file has to contain a"
            echo "                    single commit SHA without leading or trailing"
            echo "                    whitespaces."
}

while getopts :l:i:o:h OPT; do
    case $OPT in
        l)
            COMMIT_FILE="$OPTARG" # Optional file containing a list of commits to extract from repository
            ;;
        i)
            REPOSITORY_HOME="$OPTARG" # Path to repository
            ;;
        o)
            OUTPUT_DIRECTORY="$OPTARG" # Path to output directory
            ;;
        h)
            showHelp
            exit
            ;;
    esac
done

showProgress() {
    # Parameter $1 is number of extracted commits
    # Parameter $2 is number of available commits
    if [ "$1" -eq 1 ]; then
        echo -ne "    Stay a while and listen...\r"
    elif [ "$1" -eq -1 ]; then
        echo -ne "    Stay a while and listen... done    \r"
    else
        doUpdate=$(($1 % 100))
        if [ "$doUpdate" -eq 0 ]; then
            percentage=$(bc <<< "scale=2;($1/$2)*100")
            echo -ne "    Stay a while and listen... $percentage%\r"
        fi
    fi
}

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
# Check if path to repository is specified and git is available #
if [ -z "$REPOSITORY_HOME" ]; then
    echo -e "\n[Error] No git repository specified\n"
    showHelp
    exit
else
    if [ ! -d "$REPOSITORY_HOME/.git" ]; then
        echo -e "\n[Error] '$REPOSITORY_HOME' does not specify a git repository\n"
        showHelp
        exit
    fi
fi
# Check if path to repository is specified and git is available #
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #


# ++++++++++++++++++++++++++++++++++++++++++++++++++++ #
# Check if output directory is specified and available #
if [ -z "$OUTPUT_DIRECTORY" ]; then
    echo -e "\n[Error] No output directory specified\n"
    showHelp
    exit
else
    if [ ! -d "$OUTPUT_DIRECTORY" ]; then
        echo "Creating output directory $OUTPUT_DIRECTORY"
        mkdir -p $OUTPUT_DIRECTORY
    else
        echo "Recreating output directory $OUTPUT_DIRECTORY"
        rm -r $OUTPUT_DIRECTORY
        mkdir -p $OUTPUT_DIRECTORY
    fi
fi
# Check if output directory is specified and available #
# ++++++++++++++++++++++++++++++++++++++++++++++++++++ #


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
# Check if commit file is specified and exists (optional) #
if [ ! -z "$COMMIT_FILE" ]; then
    if [ ! -f "$COMMIT_FILE" ]; then
        echo -e "\n[Error] '$COMMIT_FILE' is not a file or does not exist\n"
        showHelp
        exit
    fi
fi
# Check if commit file is specified and exists (optional) #
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++ #


# ++++++++++++++++++++++++++ #
# Go to repository directory #
echo "Switching to repository $REPOSITORY_HOME"
cd $REPOSITORY_HOME
# Go to repository directory #
# ++++++++++++++++++++++++++ #


# ++++++++++++++++++++++++++++++++++++++++++++++++++++ #
# Get all commits from repository or commits from file #
if [ -z "$COMMIT_FILE" ]; then
    echo "Retrieving commits from repository $REPOSITORY_HOME"
    commitList=$(git log --oneline | cut -d' ' -f1)
    availableCommitsCounter=$(echo $commitList | wc -w)
    echo -e "$availableCommitsCounter commits found\n"
else
    echo "Retrieving commits from file $COMMIT_FILE"
    commitList="$(<$COMMIT_FILE)"
    availableCommitsCounter=$(echo $commitList | wc -w)
    echo -e "$availableCommitsCounter commits found\n"
fi
# Get all commits from repository or commits from file #
# ++++++++++++++++++++++++++++++++++++++++++++++++++++ #


# ++++++++++++++++++++ #
# Extract commit diffs #
echo -e "Extracting commit diffs\n"
extractedCommitsCounter=0
for commit in $commitList; do

    # Set filename to commiterDateAsUnixTimestamp_commitHash
    filename=$(git show --format=%ct_%H%n $commit | head -n 1)
    outFile="$OUTPUT_DIRECTORY/$filename.txt"
    
    # Save data and time of commit to outFile first 
    git show -s --format=%ci $commit >> $outFile
    
    # Save full commit diff to outFile
    #git show -U100000 $commit >> $outFile
    git show $commit >> $outFile
    extractedCommitsCounter=$((extractedCommitsCounter + 1))
    showProgress $extractedCommitsCounter $availableCommitsCounter
done
# Extract commit diffs #
# ++++++++++++++++++++ #

showProgress -1
echo -ne "\n\n" # Required to advance the line showing progress
