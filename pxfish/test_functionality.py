import subprocess
import time

log_file = open("test_output.txt", 'w')

# print("Prints Help Text")
# test_results = subprocess.run(["python3", "../pxfish/pyfish.py", "-h"], stdout=log_file)

# List files and check if they are there 
# add time marker or random number to these 
timestamp = time.strftime("%y%m%d%H%M%S")
directory_name = "DirNameTest" + timestamp
category_name = "New Category" + timestamp
operation_type_name = "new op type name" + timestamp 


print("creates op type")
#test_results = subprocess.run(["python3", "pyfish.py", "create", "-d", "DirNameTest2", "-c", "ScriptTest", "-o", "OTScript23"])
# Pushes files 
#test_file = open("/directory_name/category_name/operation_type_name")
# Open File and add lines 
#test_results = subprocess.run(["python3", "pyfish.py", "push", "-d", "DirNameTest2", "-c", "ScriptTest", "-o", "OTScript23"])
# print("Pulls Files")
# test_results = subprocess.run(["python3", "../pxfish/pyfish.py", "pull", "-d", "DirNameTest"])


print("The exit code was: %d" % test_results.returncode )

log_file.close()

