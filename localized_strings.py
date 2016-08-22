import os
import optparse

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

		#if len(strings_dict.keys()) > 0:
			#print("\n**** .strings files ****")

		#self.print_dict_items(strings_dict)

		return ("strings", strings_dict)

	def paths_for_plurals(self, project_path):
		strings_paths = self.paths_with_files_passing_test_at_path(lambda f:f == "Localizable.stringsdict", project_path)

		strings_dict = self.categorize_files(strings_paths)

		#if len(strings_dict.keys()) > 0:
			#print("\n**** .stringsdict files ****")

		#self.print_dict_items(strings_dict)

		return ("plurals", strings_dict)

	def paths_for_arrays():
		print("\n**** Getting arrays strings files ****")

	def paths_for_storyboards_strings(self, project_path):
		storyboards_paths = self.paths_with_files_passing_test_at_path(lambda f:f.endswith('.storyboard'), project_path)
		storyboards_strings_names = []
		for p in storyboards_paths:
			tail = os.path.basename(p)
			storyboards_strings_names.append(tail.replace(".storyboard",".strings"))

		storyboards_strings = self.paths_with_files_passing_test_at_path(lambda f:self.find(f,storyboards_strings_names), project_path)

		strings_dict = self.categorize_files(storyboards_strings)

		#if len(strings_dict.keys()) > 0:
			#print("\n**** storyboards strings files ****")

		#self.print_dict_items(strings_dict)

		return ("storyboards_strings", strings_dict)

	def paths_for_nib_or_xib_strings(self, project_path):
		nibs_paths = self.paths_with_files_passing_test_at_path(lambda f:f.endswith('.nib') or f.endswith('.xib'), project_path)
		nibs_strings_names = []
		for p in nibs_paths:
			tail = os.path.basename(p)
			nibs_strings_names.append(tail.replace(p[-4:], ".strings"))

		xibs_strings = self.paths_with_files_passing_test_at_path(lambda f:self.find(f,nibs_strings_names), project_path)
				
		strings_dict = self.categorize_files(xibs_strings)
		
		#if len(strings_dict.keys()) > 0:
			#print("\n**** nib or xib strings files ****")

		#self.print_dict_items(strings_dict)

		return ("nib_xib_strings", strings_dict)

	def show_localized_strings_files_in_project(self, project_path):

		print(project_path)
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

		for item in [strings, plurals, storyboards, xibs]:
			strings_list.append(item)

		return strings_list

class StringsParser:
	def parse_localized_files(self, strings_list):
		# Parse two types of files: .strings & .stringsdict
		for strings_tuple in strings_list:
			print strings_tuple[0]
			for key, values in strings_tuple[1].iteritems():
				if len(values) > 0:
					print(key + ":")
				for s in values: # iterate all the .strings & .stringsdict files
					root,ext = os.path.splitext(s)
					if ext == ".strings":
						self.parse_strings()
					elif ext == ".stringsdict":
						self.parse_stringsdict()
			print "\n"

	def parse_strings(self):
		print("Parsing strings")

	def parse_stringsdict(self):
		print("Parsing stringsdict")

def main():
	p = optparse.OptionParser()
	p.add_option('--project-path', '-p', dest="project_path")
	options, arguments = p.parse_args()

	project_path = None

	if 'PROJECT_DIR' in os.environ:
		project_path = os.environ['PROJECT_DIR']
	elif options.project_path:
		project_path = options.project_path

	locator = StringsLocator()
	# Return a list of tuple list [("Strings Type",StringsFilesLocation Dict)], i.e. ("Strings", {})
	strings_list = locator.show_localized_strings_files_in_project(project_path)

	parser = StringsParser()
	parser.parse_localized_files(strings_list)

main()
