import os
import optparse

def find(f, list):
	for item in list:
		if f == item:
			return True
	return False

def paths_with_files_passing_test_at_path(test, path):
	for root, dirs, files in os.walk(path, topdown = True):
		for p in (os.path.join(root, f) for f in files if test(f)):
			yield p

def paths_for_dirs_passing_test_at_path(test, path):
	for root, dirs, files in os.walk(path, topdown = True):
		for d in (os.path.join(root, di) for di in dirs if test(di)):
			yield d

def print_dict_items(input_dict):
	for key, values in input_dict.iteritems():
		if len(values) > 0:
			print(key + ":")
			for s in values:
				print(s)

def categorize_files(paths):
	strings_dict = {}
	for p in paths:
		directory = os.path.basename(os.path.dirname(p))
		if directory in lproj_folder_names:
			if find(directory, strings_dict.keys()) == False:
				strings_dict[directory] = []
			strings_dict[directory].append(p)
	return strings_dict

def paths_for_lproj_folders(project_path):
	lproj_paths = paths_for_dirs_passing_test_at_path(lambda f:f.endswith('.lproj'), project_path)
	lproj_folder_names = []
	for d in lproj_paths:
		tail = os.path.basename(d)
		if find(tail, lproj_folder_names) == False:
			lproj_folder_names.append(tail)

	return lproj_folder_names

def paths_for_strings(project_path):
	strings_paths = paths_with_files_passing_test_at_path(lambda f:f == "Localizable.strings", project_path)

	strings_dict = categorize_files(strings_paths)

	if len(strings_dict.keys()) > 0:
		print("\n**** .strings files ****")

	print_dict_items(strings_dict)

def paths_for_plurals(project_path):
	strings_paths = paths_with_files_passing_test_at_path(lambda f:f == "Localizable.stringsdict", project_path)

	strings_dict = categorize_files(strings_paths)

	if len(strings_dict.keys()) > 0:
		print("\n**** .stringsdict files ****")

	print_dict_items(strings_dict)

def paths_for_arrays():
	print("\n**** Getting arrays strings files ****")

def paths_for_storyboards_strings(project_path):
	storyboards_paths = paths_with_files_passing_test_at_path(lambda f:f.endswith('.storyboard'), project_path)
	storyboards_strings_names = []
	for p in storyboards_paths:
		tail = os.path.basename(p)
		storyboards_strings_names.append(tail.replace(".storyboard",".strings"))

	storyboards_strings = paths_with_files_passing_test_at_path(lambda f:find(f,storyboards_strings_names), project_path)

	strings_dict = categorize_files(storyboards_strings)

	if len(strings_dict.keys()) > 0:
		print("\n**** storyboards strings files ****")

	print_dict_items(strings_dict)

def paths_for_nib_or_xib_strings(project_path):
	nibs_paths = paths_with_files_passing_test_at_path(lambda f:f.endswith('.nib') or f.endswith('.xib'), project_path)
	nibs_strings_names = []
	for p in nibs_paths:
		tail = os.path.basename(p)
		nibs_strings_names.append(tail.replace(p[-4:], ".strings"))

	xibs_strings = paths_with_files_passing_test_at_path(lambda f:find(f,nibs_strings_names), project_path)
			
	strings_dict = categorize_files(xibs_strings)
	
	if len(strings_dict.keys()) > 0:
		print("\n**** nib or xib strings files ****")

	print_dict_items(strings_dict)

def show_localized_strings_files_in_project(project_path):
	global lproj_folder_names
	lproj_folder_names = paths_for_lproj_folders(project_path)
	paths_for_strings(project_path)
	paths_for_plurals(project_path)
	paths_for_storyboards_strings(project_path)
	paths_for_nib_or_xib_strings(project_path)

def main():
	p = optparse.OptionParser()
	p.add_option('--project-path', '-p', dest="project_path")
	options, arguments = p.parse_args()

	project_path = None

	if 'PROJECT_DIR' in os.environ:
		project_path = os.environ['PROJECT_DIR']
	elif options.project_path:
		project_path = options.project_path

	show_localized_strings_files_in_project(project_path)

main()

