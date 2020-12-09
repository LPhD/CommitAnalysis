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
                
    #3: Potential Donor (as we need a test), also valid in-between-version and Target
    #2: Needed at least once in between Donor and Target, also valid Target
    #1: Valid in-between-version, also valid Target
    #0: Valid Target if it is followed by the above     
    
    # After we analyze the whole commit, decide what to do
    if containsTests and not containsRemovalsInRelevantFiles: #Do we really need the second part? 
        # Current commit must contain tests and not contain removals (potential Donor commit) -> We currently can only backport additions, not removals
        relevantCommitList.append(file)
        return 3
    elif not containsRemovalsInRelevantFiles and containsRelevantFileTypes:
        # Current commit does not contain removals or tests, but contains changes to relevant file types (as it makes no sense to migrate code among identical versions) (valid version between Donor and Target, must occur at least once) -> Same problem as above, if there happen removals in code that is part of the SU, the SU will add them again
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


#3: Potential Donor (as we need a test), also valid in-between-version and Target
#2: Needed at least once in between Donor and Target, also valid Target
#1: Valid in-between-version, also valid Target
#0: Valid Target if it is followed by the above
# [Filename, status (int)]
commitStatusList = []

#Walk the directory (files are sorted ascending by name, we start with the oldest commit)               
for fileName in sorted(os.listdir(inputDir)): 
    with open(os.path.join("Commits/", fileName), 'r') as file: 
        # Use to seperate different commit types 
        state = analyzeFile(file)
        commitStatusList.append([fileName,state])


#Start at the last element    
index = len(commitStatusList) -1
number = 0

#Identifies a history of commits fitting the desired criteria
while index > 0:
    #Take the last possible Donor and then search backwards
    if (commitStatusList[index][1] == 3):
        
            anotherIndex = index - 1
            counter = 0
            #Check previous commits
            while anotherIndex > 0 and not commitStatusList[anotherIndex][1] == 0: 
                #print("We get here "+str(commitStatusList[anotherIndex][1]))
            
                #We need at least one relevant addition
                if commitStatusList[anotherIndex][1] == 2:
                    counter = counter + 1
                    print("Counter: "+str(counter))
                    
                anotherIndex = anotherIndex -1
                
            #If we get here, the status of commit at anotherIndex should be 0
            if counter > 0 and commitStatusList[anotherIndex][1] == 0:
                print("Donor: "+str(commitStatusList[index][0]))
                print("Target: "+str(commitStatusList[anotherIndex][0]))
                #Count number of results
                number = number + 1                
            
    index = index -1
    

    
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
print("Found fitting histories: "+str(number)) 
