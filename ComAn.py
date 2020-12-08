#!/usr/bin/env python3

import os, sys

relevantCommitList = []
testCommitList = set()

# Analyze the content of each commit, to exlude commits that remove at least one line from .c or .h files
def analyzeFile(file):  
    global relevantCommitList, testCommitList
    
    relevantFilePart = False
    containsRelevantFileTypes = False
    
    for line in file:
        # Get the changed filetype
        if (line.startswith("diff --git")):
            if ".h " in line or ".c " in line:
                print("Relevant file: "+line)
                relevantFilePart = True
                containsRelevantFileTypes = True
            elif ".t " in line:
                print("Test: "+line)
                relevantFilePart = False
                # Use set to prevent duplicate addition if commit changes several tests
                testCommitList.add(file)                
            else:
                print("Not relevant file: "+line)
                relevantFilePart = False
                
        #Only look at lines from .c and .h files
        if relevantFilePart:
            if (line.startswith("- ")):
                print("Found removal: "+line)
                #Do not analyzeFile any further
                return
    
    # If we get here, the file does not contain removals in relevant files
    if containsRelevantFileTypes: relevantCommitList.append(file)            

#Set input dir
if len(sys.argv) != 2:
    print('No input directory given, using default directory: \"Commits/\"')
    inputDir = "Commits/" 
else:
    inputDir = sys.argv[1]    
            
#Walk the directory                
for filename in os.listdir(inputDir):
    print("Current file: "+filename)

    with open(os.path.join("Commits/", filename), 'r') as file: 
        analyzeFile(file)

#Copy the commits that contain only additions in c./.h files to RelevantChanges/
print("Relevant commits")
for file in relevantCommitList:
    print(file.name)
    os.system("cp -v --parents "+file.name+" RelevantChanges/")     

#Copy the commits that contain tests to Tests/
print("Tests")
for file in testCommitList:
    print(file.name)
    os.system("cp -v --parents "+file.name+" Tests/")  
    
#Print results
print("Found relevant commits: "+str(len(relevantCommitList)))    
print("Found commits with tests: "+str(len(testCommitList))) 
