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
    result = []
    for path in folder_paths:
        if "/build/intermediates/" not in path and not path.endswith("dp"):
            dirname = os.path.dirname(path)
            if dirname.endswith('/res'):
                result.append(path)
    return result

def paths_for_localized_xmls(paths):
    xml_dict = {}

    for p in paths:
        dirname = os.path.basename(p)
        xml_in_path = paths_with_files_passing_test_at_path(lambda f:f.endswith('xml'), p)

        for xml in xml_in_path:
            if not dirname in xml_dict.keys():
                xml_dict[dirname] = []
            xml_dict[dirname].append(xml)

    return [("xml",xml_dict)]

def find_localized_strings(project_path):

    if not project_path or not os.path.exists(project_path):
        error("", 0, "bad project path:%s" % project_path)
        return

    global values_folders_paths
    values_folders_paths = find_values_folders(project_path)
    xml_tuple = paths_for_localized_xmls(values_folders_paths)

    return xml_tuple
