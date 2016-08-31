import os

def find(f, list):
	for item in list:
		if f == item:
			return True
	return False

def error(file_path, line_number, message):
	print "%s:%d: error: %s" % (file_path, line_number, message)

# Function for finding paths for files
def paths_with_files_passing_test_at_path(test, path):
	for root, dirs, files in os.walk(path, topdown = True):
		for p in (os.path.join(root, f) for f in files if test(f)):
			yield p

# Function for finding dirs for files
def paths_for_dirs_passing_test_at_path(test, path):
	for root, dirs, files in os.walk(path, topdown = True):
		for d in (os.path.join(root, di) for di in dirs if test(di)):
			yield d

def find_values_folders(project_path):
	folder_paths = paths_for_dirs_passing_test_at_path(lambda f:f.startswith('values'), project_path)
	for path in folder_paths:
		dirname = os.path.dirname(path)
		if dirname.endswith('/res'):
			yield path

def find_localized_strings(project_path):

	if not project_path or not os.path.exists(project_path):
		error("", 0, "bad project path:%s" % project_path)
		return

	global values_folders
	values_folders = find_values_folders(project_path)

	for p in values_folders:
		print p

	print values_folders