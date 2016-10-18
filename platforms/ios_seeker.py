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
        if directory in lproj_folders:
            if find(directory, strings_dict.keys()) == False:
                strings_dict[directory] = []
            parentDirs = p.split('/')
            if find('Pods', parentDirs) == False:
                strings_dict[directory].append(p)
    return strings_dict

def paths_for_strings(project_path):
    strings_paths = paths_with_files_passing_test_at_path(lambda f:f == "Localizable.strings", project_path)

    strings_dict = categorize_files(strings_paths)

    return ("Strings", strings_dict)

def paths_for_plurals(project_path):

    strings_paths = paths_with_files_passing_test_at_path(lambda f:f.endswith('.stringsdict'), project_path)
    strings_dict = categorize_files(strings_paths)

    return ("Plurals", strings_dict)

def paths_for_arrays(project_path):
    strings_paths = paths_with_files_passing_test_at_path(lambda f:f == "LocalizableArray.strings", project_path)

    strings_dict = categorize_files(strings_paths)

    return ("Array", strings_dict)

def paths_for_storyboards_strings(project_path):
    storyboards_paths = paths_with_files_passing_test_at_path(lambda f:f.endswith('.storyboard'), project_path)
    storyboards_strings_names = []
    for p in storyboards_paths:
        tail = os.path.basename(p)
        storyboards_strings_names.append(tail.replace(".storyboard",".strings"))

    storyboards_strings = paths_with_files_passing_test_at_path(lambda f:find(f,storyboards_strings_names), project_path)

    strings_dict = categorize_files(storyboards_strings)

    return ("Storyboards_Strings", strings_dict)

def paths_for_nib_or_xib_strings(project_path):
    nibs_paths = paths_with_files_passing_test_at_path(lambda f:f.endswith('.nib') or f.endswith('.xib'), project_path)
    nibs_strings_names = []
    for p in nibs_paths:
        tail = os.path.basename(p)
        nibs_strings_names.append(tail.replace(p[-4:], ".strings"))

    xibs_strings = paths_with_files_passing_test_at_path(lambda f:find(f,nibs_strings_names), project_path)
            
    strings_dict = categorize_files(xibs_strings)

    return ("Nib_Xib_Strings", strings_dict)

def paths_for_plist_files(project_path):
    plist_paths = paths_with_files_passing_test_at_path(lambda f:f.endswith('.plist'), project_path)
    paths = []
    paths_dict = {}
    for p in plist_paths:
        parentDirs = p.split('/')
        if find('Pods', parentDirs) == False:
            shouldAddToList = True
            for d in parentDirs:
                if d.endswith(".framework") or d.endswith(".xcodeproj"):
                    shouldAddToList = False
                    break
            if shouldAddToList:
                paths.append(p)
    paths_dict["Plist"] = paths
    return ("Plist", paths_dict)

def find_lproj_folders(project_path):
    lproj_paths = paths_for_dirs_passing_test_at_path(lambda f:f.endswith('.lproj'), project_path)
    folders = []
    for p in lproj_paths:
        tail = os.path.basename(p)
        if find(tail, folders) == False:
            folders.append(tail)
    return folders

def find_localized_strings(project_path):

    if not project_path or not os.path.exists(project_path):
        error("", 0, "bad project path:%s" % project_path)
        return

    global lproj_folders
    lproj_folders = find_lproj_folders(project_path)

    find_sets(project_path)

    strings = paths_for_strings(project_path)
    plurals = paths_for_plurals(project_path)
    storyboards = paths_for_storyboards_strings(project_path)
    xibs = paths_for_nib_or_xib_strings(project_path)
    array = paths_for_arrays(project_path)
    plist = paths_for_plist_files(project_path)

    strings_list = [strings, plurals, storyboards, xibs, array, plist]

    return strings_list

def find_sets(project_path):
    '''
    [ 
     {
       "Dir": "path/to/the/set", 
       "lproj": {
                 "en.lproj": ["path/to/A.strings","path/to/B.stringsdict","path/to/C.strings"],
                 "lproj/folder": ["path/to/A.strings","path/to/B.stringsdict"]
                }
     }
    ]
    '''
    lrpoj_folders = find_lproj_path(project_path)
    sets_list = []
    for p in lrpoj_folders:

        files_list = []
        for file_name in os.listdir(p):
            if file_name.endswith(".strings") or file_name.endswith(".stringsdict"):
                file_path = os.path.join(p, file_name)
                files_list.append(file_path)

        basename = os.path.basename(p)
        dirname = os.path.dirname(p)
        if_dir_exists = False
        for l in sets_list:
            if l["Dir"] == dirname:
                l["lproj"][basename] = files_list
                if_dir_exists = True

        if if_dir_exists == False:
            set_dic = {"Dir": dirname, "lproj": {basename: files_list}}
            sets_list.append(set_dic)

    return sets_list

def find_lproj_path(project_path):
    lproj_paths = paths_for_dirs_passing_test_at_path(lambda f:f.endswith('.lproj'), project_path)
    folders_paths = []
    for p in lproj_paths:
        parentDirs = p.split('/')
        if find('Pods', parentDirs) == False:
            shouldAddToList = True
            for d in parentDirs:
                if d.endswith(".framework") or d.endswith(".xcodeproj"):
                    shouldAddToList = False
                    break
            if shouldAddToList:
                folders_paths.append(p)
    return folders_paths

def find_all_pbxproj(project_path):
    pbxproj_paths = paths_with_files_passing_test_at_path(lambda f:f.endswith('.pbxproj'), project_path)
    result_paths = []
    parse_pods = False
    for p in pbxproj_paths:
        if not parse_pods:
            # Don't include Pods pbxproj
            parentDirs = p.split('/')
            if find('Pods', parentDirs) == True:
                continue

        result_paths.append(p)

    return result_paths