import subprocess

log_file = open("test_output.txt", 'w')

print("Prints Help Text")
test_results = subprocess.run(["python3", "pxfish/pyfish.py", "-h"], stdout=log_file)

print("Pulls Files")

print("The exit code was: %d" % test_results.returncode )

log_file.close()
# presumably I need to set it up to write the commands 
# to standard input and then check the results?

#list_files = subprocess.run(["ls", "-l"], stdout=subprocess.DEVNULL)
#list_files = subprocess.run(["ls", "-l"], stdout=log_file)

