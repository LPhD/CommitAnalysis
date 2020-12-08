#!/usr/bin/env python3

import os, sys, shutil

relevantCommitList = []
testCommitList = set()

# Analyze the content of each commit, to exlude commits that remove at least one line from .c or .h files
def analyzeFile(file):  
    global relevantCommitList, testCommitList       

    relevantFilePart = False
    containsRelevantFileTypes = False
    containsRemovalsInRelevantFiles = False
    containsTests = False
    
    for line in file:
        # Get the changed filetype
        if (line.startswith("diff --git")):
        
            if ".h " in line or ".c " in line:
                relevantFilePart = True
                containsRelevantFileTypes = True
                
            elif ".t " in line:
                relevantFilePart = False
                # Use set to prevent duplicate addition if commit changes several tests
                testCommitList.add(file) 
                containsTests = True   
                
            else:
                relevantFilePart = False
                
        #Only look at lines from .c and .h files
        if relevantFilePart:
            if (line.startswith("- ")):
                containsRemovalsInRelevantFiles = True
    
    # After we analyze the whole commit, decide what to do
    if containsTests and not containsRemovalsInRelevantFiles: #Do we really need the second part? 
        # Current commit must contain tests and not contain removals (potential Donor commit) -> We currently can only backport additions, not removals
        return 3
    elif not containsRemovalsInRelevantFiles and containsRelevantFileTypes:
        # Current commit does not contain removals or tests, but contains changes to relevant file types (as it makes no sense to migrate code among identical versions) (potential Target commit, or valid version between Donor and Target) -> Same problem as above, if there happen removals in code that is part of the SU, the SU will add them again
        relevantCommitList.append(file) 
        return 2          
    elif not containsRemovalsInRelevantFiles :
        # Current commit does not contain removals (valid version between Donor and Target) -> Same problem as above...
        return 1    
    else:
        # Current commits contains removals in relevant files (currently not supported)
        return 0


#Set input dir
if len(sys.argv) != 2:
    print('No input directory given, using default directory: \"Commits/\"')
    inputDir = "Commits/" 
else:
    inputDir = sys.argv[1]    
            
#Walk the directory                
for filename in os.listdir(inputDir):
    with open(os.path.join("Commits/", filename), 'r') as file: 
        # Use to seperate different commit types (irrelevant 0, no harming changes 1, relevant/Target 2, tests/Donor 2)
        analyzeFile(file)

#Copy the commits that contain only additions in c./.h files to RelevantChanges/
resultFoldername = "RelevantChanges/"
# Delete old results
if os.path.exists(resultFoldername):
    shutil.rmtree(resultFoldername)
os.makedirs(resultFoldername)
for file in relevantCommitList:
    os.system("cp --parents "+file.name+" "+resultFoldername)     

#Copy the commits that contain tests to Tests/
resultFoldername = "Tests/"
# Delete old results
if os.path.exists(resultFoldername):
    shutil.rmtree(resultFoldername)
os.makedirs(resultFoldername)
for file in testCommitList:
    os.system("cp --parents "+file.name+" "+resultFoldername)  
    
#Print results
print("Found relevant commits: "+str(len(relevantCommitList)))    
print("Found commits with tests: "+str(len(testCommitList))) 
