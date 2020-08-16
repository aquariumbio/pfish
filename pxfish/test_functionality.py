import subprocess
import time
import os 
# Create log file
#log_file = open("test_output.txt", 'w')

# print("Prints Help Text")
# test_results = subprocess.run(["python3", "../pxfish/pyfish.py", "-h"], stdout=log_file)

# Creaet unique names for tests 
timestamp = time.strftime("%y%m%d%H%M%S")

directory = "DirName" + timestamp
category = "Category_name" + timestamp
operation_type = "optype_name" + timestamp 
library = "lib_name" + timestamp
    
# create op_type

path = os.path.normpath(directory)
# create category and operation type 
create_ot_results = subprocess.run(["python3", "pyfish.py", "create", 
                        "-d", directory, 
                        "-c", category, 
                        "-o", operation_type])

print("Create Op Type exit codes: %d" % create_ot_results.returncode )

category_path = os.path.join(path, category)
subdirectory_path = os.path.join(category_path, "operation_types")
file_path = os.path.join(subdirectory_path, operation_type)
protocol_path = os.path.join(file_path, "protocol.rb")

with open(protocol_path, 'w') as file:
    file.write(timestamp)

with open("test.txt", "a") as myfile:
    myfile.write("appended text")

# create category and library  
#create_lib_results = subprocess.run(["python3", "pyfish.py", "create", 
#                        "-d", directory, 
#                        "-c", category,
#                        "-l", library])
#
#print("Create Library exit codes: %d" % create_lib_results.returncode )
#
# change op_type file 

# change library file 

# push op_type file 

# push library file 

# pull op_type file 

# pull library file 

# check for changes 

#test_file = open("/directory_name/category_name/operation_type_name")
#test_results = subprocess.run(["python3", "pyfish.py", "push", "-d", "DirNameTest2", "-c", "ScriptTest", "-o", "OTScript23"])
#test_results = subprocess.run(["python3", "../pxfish/pyfish.py", "pull", "-d", "DirNameTest"])



#log_file.close()

