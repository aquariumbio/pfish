import subprocess
import time
import os 

# Create log file
#log_file = open("test_output.txt", 'w')

# print("Prints Help Text")
# test_results = subprocess.run(["python3", "../pxfish/pyfish.py", "-h"], stdout=log_file)

def names(*, category, operation_type=None, library=None, timestamp):
    names = {
             "directory" : "DirName" + timestamp,
             "category" : category + timestamp,
             "operation_type" : operation_type + timestamp, 
             "library" : library + timestamp,
             "timestamp" : timestamp,
            }
    
    names["path"] = os.path.normpath(names["directory"])
    return names
    

def paths(*, path, category, subdirectory, item, file_name):
    category_path = os.path.join(path, category)
    subdirectory_path = os.path.join(category_path, subdirectory)
    item_path = os.path.join(subdirectory_path, item)
    file_path = os.path.join(item_path, file_name)
    return file_path


# Test for creating, pushing, and pulling single Operation Types and Libraries
names = names(category="cat_create",
                operation_type="ot_create", 
                library="lib_create", 
                timestamp=time.strftime("%d%H%M%S"))

# create category and operation type 
create_ot_results = subprocess.run(["python3", "pyfish.py", "create", 
                        "-d", names["directory"], 
                        "-c", names["category"], 
                        "-o", names["operation_type"]
                        ])

print("Create Op Type exit codes: %d" % create_ot_results.returncode )

file_path = paths(path=names["path"], 
                    category=names["category"], 
                    subdirectory="operation_types", 
                    item=names["operation_type"],
                    file_name="protocol.rb"
                    )

# edited op type 
with open(file_path, 'w') as file:
    file.write("checking that edited version is pushed")

# push edited op_type
push_ot_results = subprocess.run(
                        ["python3", "pyfish.py", "push", 
                        "-d", names["directory"], 
                        "-c", names["category"], 
                        "-o", names["operation_type"]
                        ])

print("Push Op Type exit codes: %d" % push_ot_results.returncode)


# create second op type in same category 
names["operation_type"] = names["operation_type"] + "test2"
create_ot_results = subprocess.run(["python3", "pyfish.py", "create", 
                        "-d", names["directory"], 
                        "-c", names["category"], 
                        "-o", names["operation_type"]
                        ])

# pull category
create_ot_results = subprocess.run(["python3", "pyfish.py", "pull", 
                        "-d", names["directory"], 
                        "-c", names["category"], 
                        ])

# pull edited  optype
#pull_ot_results = subprocess.run(
#                        ["python3", "pyfish.py", "pull",
#                        "-d", names["directory"],
#                        "-c", names["category"],
#                        "-o", names["operation_type"]
#                        ])
#
#print("Pull Op Type exit codes: %d" % pull_ot_results.returncode )

# create library
create_lib_results = subprocess.run(["python3", "pyfish.py", "create",
                        "-d", names["directory"], 
                        "-c", names["category"],
                        "-l", names["library"]
                        ])

print("Create Library exit codes: %d" % create_lib_results.returncode )

file_path = paths(path=names["path"],
                    category=names["category"],
                    subdirectory="libraries",
                    item=names["library"],
                    file_name="source.rb"
                    )

# edit library file
with open(file_path, 'a') as file:
    file.write("checking that edited version of library is pushed")

# push edited library file
push_lib_results = subprocess.run(
                        ["python3", "pyfish.py", "push",
                        "-d", names["directory"],
                        "-c", names["category"],
                        "-o", names["library"]
                        ])

print("Push library exit codes: %d" % push_lib_results.returncode)

# pull edited library
pull_lib_results = subprocess.run(
                        ["python3", "pyfish.py", "pull",
                        "-d", names["directory"],
                        "-c", names["category"],
                        "-o", names["library"]
                        ])

print("Pull library exit codes: %d" % pull_lib_results.returncode )

# check for changes

#test_file = open("/directory_name/category_name/operation_type_name")
#test_results = subprocess.run(["python3", "pyfish.py", "push", "-d", "DirNameTest2", "-c", "ScriptTest", "-o", "OTScript23"])
#test_results = subprocess.run(["python3", "../pxfish/pyfish.py", "pull", "-d", "DirNameTest"])

#log_file.close()
