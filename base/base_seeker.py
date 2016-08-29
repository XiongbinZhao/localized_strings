import os

class StringsLocator:
    def find(self, f, list):
		for item in list:
			if f == item:
				return True
		return False

    def error(self, file_path, line_number, message):
	    print "%s:%d: error: %s" % (file_path, line_number, message)

    def paths_with_files_passing_test_at_path(self,test, path):
		for root, dirs, files in os.walk(path, topdown = True):
			for p in (os.path.join(root, f) for f in files if test(f)):
				parentDirs = root.split('/')
				if self.find('Pods', parentDirs) == False:
					yield p

    def paths_for_dirs_passing_test_at_path(self, test, path):
		for root, dirs, files in os.walk(path, topdown = True):
			for d in (os.path.join(root, di) for di in dirs if test(di)):
				yield d

    def print_dict_items(self, input_dict):
		for key, values in input_dict.iteritems():
			if len(values) > 0:
				print(key + ":")
				for s in values:
					print(s)

    def categorize_files(self, paths):
		strings_dict = {}
		for p in paths:
			directory = os.path.basename(os.path.dirname(p))
			if directory in lproj_folder_names:
				if self.find(directory, strings_dict.keys()) == False:
					strings_dict[directory] = []
				strings_dict[directory].append(p)
		return strings_dict

    def paths_for_lproj_folders(self, project_path):
		lproj_paths = self.paths_for_dirs_passing_test_at_path(lambda f:f.endswith('.lproj'), project_path)
		lproj_folder_names = []
		for d in lproj_paths:
			tail = os.path.basename(d)
			if self.find(tail, lproj_folder_names) == False:
				lproj_folder_names.append(tail)

		return lproj_folder_names

    def paths_for_strings(self, project_path):
		strings_paths = self.paths_with_files_passing_test_at_path(lambda f:f == "Localizable.strings", project_path)

		strings_dict = self.categorize_files(strings_paths)

		return ("Strings", strings_dict)

    def paths_for_plurals(self, project_path):
		strings_paths = self.paths_with_files_passing_test_at_path(lambda f:f == "Localizable.stringsdict", project_path)

		strings_dict = self.categorize_files(strings_paths)

		return ("Plurals", strings_dict)

    def paths_for_arrays(self, project_path):
		strings_paths = self.paths_with_files_passing_test_at_path(lambda f:f == "LocalizableArray.strings", project_path)

		strings_dict = self.categorize_files(strings_paths)

		return ("Array", strings_dict)

    def paths_for_storyboards_strings(self, project_path):
		storyboards_paths = self.paths_with_files_passing_test_at_path(lambda f:f.endswith('.storyboard'), project_path)
		storyboards_strings_names = []
		for p in storyboards_paths:
			tail = os.path.basename(p)
			storyboards_strings_names.append(tail.replace(".storyboard",".strings"))

		storyboards_strings = self.paths_with_files_passing_test_at_path(lambda f:self.find(f,storyboards_strings_names), project_path)

		strings_dict = self.categorize_files(storyboards_strings)

		return ("Storyboards_Strings", strings_dict)

    def paths_for_nib_or_xib_strings(self, project_path):
		nibs_paths = self.paths_with_files_passing_test_at_path(lambda f:f.endswith('.nib') or f.endswith('.xib'), project_path)
		nibs_strings_names = []
		for p in nibs_paths:
			tail = os.path.basename(p)
			nibs_strings_names.append(tail.replace(p[-4:], ".strings"))

		xibs_strings = self.paths_with_files_passing_test_at_path(lambda f:self.find(f,nibs_strings_names), project_path)
				
		strings_dict = self.categorize_files(xibs_strings)

		return ("Nib_Xib_Strings", strings_dict)

    def show_localized_strings_files_in_project(self, project_path):

		if not project_path or not os.path.exists(project_path):
			self.error("", 0, "bad project path:%s" % project_path)
			return

		global lproj_folder_names
		lproj_folder_names = self.paths_for_lproj_folders(project_path)

		strings_list = []

		strings = self.paths_for_strings(project_path)
		plurals = self.paths_for_plurals(project_path)
		storyboards = self.paths_for_storyboards_strings(project_path)
		xibs = self.paths_for_nib_or_xib_strings(project_path)
		array = self.paths_for_arrays(project_path)

		for item in [strings, plurals, storyboards, xibs, array]:
			strings_list.append(item)

		return strings_list