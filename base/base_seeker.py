import os

def find(f, list):
	for item in list:
		if f == item:
			return True
	return False

def error(file_path, line_number, message):
    print "%s:%d: error: %s" % (file_path, line_number, message)

def paths_with_files_passing_test_at_path(test, path):
	for root, dirs, files in os.walk(path, topdown = True):
		for p in (os.path.join(root, f) for f in files if test(f)):
			parentDirs = root.split('/')
			if find('Pods', parentDirs) == False:
				yield p

def paths_for_dirs_passing_test_at_path(test, path):
	for root, dirs, files in os.walk(path, topdown = True):
		for d in (os.path.join(root, di) for di in dirs if test(di)):
			yield d

def paths_for_values_folders(project_path):
	folder_paths = paths_for_dirs_passing_test_at_path(lambda f:f.startswith('values'), project_path)
	for path in folder_paths:
		dirname = os.path.dirname(path)
		if dirname.endswith('/src/main/res'):
			print path

def find_localized_strings_files_in_project(project_path):
    if not project_path or not os.path.exists(project_path):
    	error("", 0, "bad project path:%s" %project_path)
    	return
    	
    paths_for_values_folders(project_path)