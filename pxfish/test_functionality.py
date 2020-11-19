"""Functions to create Test Files"""

import subprocess
import time
import os

# Create log file
# log_file = open("test_output.txt", 'w')

# print("Prints Help Text")
# test_results = subprocess.run(["python3", "../pxfish/pyfish.py", "-h"], stdout=log_file)


def names(*, category, operation_type=None, library=None, timestamp):
    """Creates names for test files. Returns a dict"""
    file_names = {
        "directory": "DirName" + timestamp,
        "category": category + timestamp,
        "operation_type": operation_type + timestamp,
        "library": library + timestamp,
        "timestamp": timestamp,
    }

    file_names["path"] = os.path.normpath(file_names["directory"])
    return file_names


def paths(*, path, category, subdirectory, item, file_name):
    """Creates paths for test files."""
    category_path = os.path.join(path, category)
    subdirectory_path = os.path.join(category_path, subdirectory)
    item_path = os.path.join(subdirectory_path, item)
    file_name_path = os.path.join(item_path, file_name)
    print(file_name_path)
    return file_name_path


print("Check Create Operation type")

# Create names to test creation of op type and library
names = names(
    category="cat_cr",
    operation_type="ot_cr",
    library="lib_cr",
    timestamp=time.strftime("%S%d%H%M"))


# create category and operation type with pfish
create_ot_results = subprocess.run(
    ["python3", "pyfish.py", "create",
     "-d", names["directory"],
     "-c", names["category"],
     "-o", names["operation_type"]]
)

print("Create Op Type exit codes: %d" % create_ot_results.returncode)


file_path = paths(
    path=names["path"],
    category=names["category"],
    subdirectory="operation_types",
    item=names["operation_type"],
    file_name="protocol.rb"
)

# Edit operation type file
with open(file_path, 'w') as file:
    file.write("Op type {} edited and pushed".format(names["operation_type"]))


print("Editing and pushing Op Type {} ".format(names["operation_type"]))

# push edited op_type
push_ot_results = subprocess.run(
    ["python3", "pyfish.py", "push",
     "-d", names["directory"],
     "-c", names["category"],
     "-o", names["operation_type"]]
)

print("Push Edited Op Type exit codes: %d" % push_ot_results.returncode)


# create a second op type in the same category
names["operation_type"] = names["operation_type"] + "test2"


create_ot_results = subprocess.run(
    ["python3", "pyfish.py", "create",
     "-d", names["directory"],
     "-c", names["category"],
     "-o", names["operation_type"]]
)

# pull the entire category
print("pull category {}".format(names["category"]))

create_ot_results = subprocess.run(
    ["python3", "pyfish.py", "pull",
     "-d", names["directory"],
     "-c", names["category"]]
)

# pull edited  optype
# pull_ot_results = subprocess.run(
#                        ["python3", "pyfish.py", "pull",
#                        "-d", names["directory"],
#                        "-c", names["category"],
#                        "-o", names["operation_type"]
#                        ])
#
#print("Pull Op Type exit codes: %d" % pull_ot_results.returncode )

# create new library
print("test create new library")

create_lib_results = subprocess.run(["python3", "pyfish.py", "create",
                                     "-d", names["directory"],
                                     "-c", names["category"],
                                     "-l", names["library"]
                                     ])

print("Create Library exit codes: %d" % create_lib_results.returncode)

file_path = paths(
    path=names["path"],
    category=names["category"],
    subdirectory="libraries",
    item=names["library"],
    file_name="source.rb"
)

# edit library file
with open(file_path, 'a') as file:
    file.write("Edited and pushed library {}".format(names["library"]))

# push edited library file
push_lib_results = subprocess.run(
    ["python3", "pyfish.py", "push",
     "-d", names["directory"],
     "-c", names["category"],
     "-l", names["library"]]
)

print("Push library exit codes: %d" % push_lib_results.returncode)

# pull newly edited library
pull_lib_results = subprocess.run(
    ["python3", "pyfish.py", "pull",
     "-d", names["directory"],
     "-c", names["category"],
     "-o", names["library"]]
)

print("Pull library exit codes: %d" % pull_lib_results.returncode)


#test_file = open("/directory_name/category_name/operation_type_name")
#test_results = subprocess.run(["python3", "pyfish.py", "push", "-d", "DirNameTest2", "-c", "ScriptTest", "-o", "OTScript23"])
#test_results = subprocess.run(["python3", "../pxfish/pyfish.py", "pull", "-d", "DirNameTest"])

# log_file.close()
