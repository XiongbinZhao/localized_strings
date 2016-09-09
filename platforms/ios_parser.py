
import os, plistlib, codecs, re, chardet
import xml.etree.ElementTree as etree

format_encoding = 'UTF-16'

"""

Call def start_parsing(strings_path):

Given a path of a .strings or .stringsdict file.
Parse the file and return a dictionary as output.

e.g.
.strings file
 {  
    "file_type": "strings", 
    "content":[ {"comment": "This is comment", "key": "this is key", "value": "this is value"} ]
 }

.stringsdict file
{
    "file_type": "stringsdict", 
    "content":[ 
                { "NSLocalizedStringsdict": "This is the key of the stringsdict",
                  "NSStringLocalizedFormatKey": "this is format key", 
                  "NSStringFormatValueTypeKey": "this is the value type key",
                  "NSStringFormatSpecTypeKey": "this is the spec type key", 
                  "Variable": "this is the variable", 
                  "zero": "if any rule for zero", 
                  "one": "if any rule for one", 
                  "two": "if any rule for two", 
                  "few": "if any rule for few", 
                  "many": "if any rule for many", 
                  "other": "if any rule for other"
                } 
              ]
}

.plist file
{
    "file_type": "plist",
    "file_path": "path/to/plist/file",
    "CFBundleDevelopmentRegion": "language_code"
}
"""

def _unescape_key(s):
    return s.replace('\\\n', '')

def _unescape(s):
    s = s.replace('\\\n', '')
    return s.replace('\\"', '"').replace(r'\n', '\n').replace(r'\r', '\r')

def _get_content(filename=None, content=None):
    if content is not None:
        if chardet.detect(content)['encoding'].startswith(format_encoding):
            encoding = format_encoding
        else:
            encoding = 'UTF-8'
        if isinstance(content, str):
            content.decode(encoding)
        else:
            return content
    if filename is None:
        return None
    return _get_content_from_file(filename, format_encoding)

def _get_content_from_file(filename, encoding):
    f = open(filename, 'r')
    try:
        content = f.read()
        if chardet.detect(content)['encoding'].startswith(format_encoding):
            encoding = format_encoding
        else:
            encoding = 'utf-8'

        f.close()
        f = codecs.open(filename, 'r', encoding=encoding)
        return f.read()
    except IOError, e:
        print "Error opening file %s with encoding %s: %s" %\
            (filename, format_encoding, e.message)
    except Exception, e:
        print "Unhandled exception: %s" % e.message
    finally:
        f.close()

def paths_with_files_passing_test_at_path(test, path):
    for root, dirs, files in os.walk(path, topdown = True):
        for p in (os.path.join(root, f) for f in files if test(f)):
            yield p

#parsing project_pbxproj file

def path_for_project_pbxprojs(project_path):
    project_pbxprojs = paths_with_files_passing_test_at_path(lambda f:f == "project.pbxproj", project_path)
    result = []
    for p in project_pbxprojs:
        dirname = os.path.dirname(p)
        dir_list = dirname.split('/')
        if not dirname.endswith('Pods.xcodeproj') and "Pods" not in dir_list:
            result.append(p)

    if len(result) == 0:
        return None
    else:
        return result

def get_info_plist_from_pbxproj(pbxproj_plist):
    tree = etree.parse(pbxproj_plist)
    root = tree.getroot()
    root_object_key = None
    objects_idx = None
    for idx, item in enumerate(root[0]):
        if item.text == "rootObject":
            root_object_key = root[0][idx + 1].text
        if item.text == "objects":
            objects_idx = idx + 1

    targets_keys = []
    if objects_idx is not None and root_object_key is not None:
        objects_dict_items = root[0][objects_idx]

        #enumerate through and find Targets keys
        for idx, item in enumerate(objects_dict_items):

            if item.text == root_object_key:
                root_object_dict = objects_dict_items[idx + 1]
                for sub_idx, sub_item in enumerate(root_object_dict):
                    if sub_item.text == "targets":
                        targets_dict = root_object_dict[sub_idx + 1]
                        for sub_sub_item in targets_dict:
                            targets_keys.append(sub_sub_item.text)
                        break
                break

        #enumerate and find Target_Name and Target_Config_List_Key
        target_name_configkey_list = [] # [("name", "config_key")]
        for idx, item in enumerate(objects_dict_items):
            if item.text in targets_keys:
                target_item = objects_dict_items[idx + 1]
                name = None
                config_key = None
                for idx, item in enumerate(target_item):
                    if item.text == "name":
                        name = target_item[idx + 1].text
                    if item.text == "buildConfigurationList":
                        config_key = target_item[idx + 1].text

                    if name and config_key is not None:
                        target_name_configkey_list.append((name, config_key))
                        name = None
                        config_key = None
                        break

        buildConfig_key_dic = {}
        for name_and_configkey in target_name_configkey_list:
            config_key = name_and_configkey[1]
            name = name_and_configkey[0]
            buildConfig_key_dic[name] = []
            for idx,item in enumerate(objects_dict_items):
                if item.text == config_key:
                    config_list_item = objects_dict_items[idx + 1]

                    for sub_idx, sub_item in enumerate(config_list_item):
                        if sub_item.text == "buildConfigurations":
                            buildConfig_array_item = config_list_item[sub_idx + 1]
                            for sub_sub_item in buildConfig_array_item:
                                buildConfig_key_dic[name].append(sub_sub_item.text)

        #Find schemes and configuration
        schemes_dir = os.path.dirname(pbxproj_plist) + "/xcshareddata/xcschemes"
        schemes_list = []
        for l in paths_with_files_passing_test_at_path(lambda f:f.endswith(".xcscheme"), schemes_dir):
            schemes_list.append(l)

        schemes_dict = get_config_from_scheme(schemes_list)

        info_plist_dic = {}
        for target_name, config_keys in buildConfig_key_dic.iteritems():
            info_plist_dic[target_name] = {}

            for config_key in config_keys: 

                # Enumerate and find all Build Config
                for idx, item in enumerate(objects_dict_items):
                    if item.text == config_key:
                        build_config_item = objects_dict_items[idx + 1]
                        info_plist_path = None
                        build_config_name = None

                        # Enumerate and find build setting & build config name
                        for sub_idx, sub_item in enumerate(build_config_item): 
                            if sub_item.text == "buildSettings":
                                build_setting_item = build_config_item[sub_idx + 1]

                                #Enumerate and find info plist in build setting
                                for sub_sub_idx, sub_sub_item in enumerate(build_setting_item): 
                                    if sub_sub_item.text == "INFOPLIST_FILE":
                                        info_plist_path = build_setting_item[sub_sub_idx + 1].text
                                        break
                            
                            if sub_item.text == "name":
                                build_config_name = build_config_item[sub_idx + 1].text

                            # Break after getting both config_name and plist_path in build_config item
                            if build_config_name and info_plist_path is not None:
                                if target_name in schemes_dict.keys():
                                    if build_config_name == schemes_dict[target_name]:
                                        lan_code = get_lan_code(info_plist_path)
                                        info_plist_dic[target_name] = {"build_config": build_config_name, "info_file":info_plist_path, "lan": lan_code}
                                elif target_name in info_plist_dic.keys():
                                    info_plist_dic.pop(target_name, None)
                                
                                info_plist_path = None
                                build_config_name = None
                                break
                        break

        return info_plist_dic

def get_config_from_scheme(scheme_list):
    if len(scheme_list) == 0:
        return
    scheme_dict = {}
    for scheme_path in scheme_list:
        scheme_name = os.path.basename(scheme_path)
        scheme_name = scheme_name[0:-9]
        tree = etree.parse(scheme_path)
        root = tree.getroot()
        for child in root:
            if child.tag == "TestAction":
                if "buildConfiguration" in child.attrib:
                    scheme_dict[scheme_name] = child.attrib["buildConfiguration"]
                    break

    return scheme_dict

def get_schemes_info_plist(project_path):

    project_pbxprojs = path_for_project_pbxprojs(project_path)
    if project_pbxprojs is None:
        return

    p = project_pbxprojs[0]
    global project_src_dir
    project_src_dir = os.path.dirname(os.path.dirname(p))

    temp_plist_path = os.path.dirname(p) + "/temp.plist"
    command_line = "plutil -convert xml1 -o - " + p + " > " + temp_plist_path
    os.system(command_line)
    
    info_plist_dic =  get_info_plist_from_pbxproj(temp_plist_path)

    return info_plist_dic

def get_lan_code(plist_relative_path):
    plist_path = project_src_dir + "/" + plist_relative_path
    lan = parse_plist(plist_path)
    lan_code = lan["CFBundleDevelopmentRegion"]

    return lan_code
            
def parse_plist(plist_path):

    tree = etree.parse(plist_path)
    root = tree.getroot()
    language_key = "CFBundleDevelopmentRegion"
    for child in root:
        plist_dict = {}
        for idx, item in enumerate(child):
            if item.tag == "key":
                value_item = child[idx+1]
                plist_dict[item.text] = value_item.text
                pass
        if language_key in plist_dict.keys():
            return plist_dict[language_key]
# Parsing strings file

def parse_strings(strings_path=None):
    print("---- Parsing strings file: " + strings_path)
    if strings_path is not None:
        content = _get_content(filename=strings_path)
    stringset = []
    resultdict = {"file_type": "strings", "file_path": strings_path, "content": stringset}
    f = content
    if f.startswith(u'\ufeff'):
        f = f.lstrip(u'\ufeff')
    cp = r'(?:/\*(?P<comment>(?:[^*]|(?:\*+[^*/]))*\**)\*/)'
    kv = r'\s*(?P<line>(?:"(?P<key>[^"\\]*)")\s*=\s*(?:"(?P<value>[^"\\]*)"\s*;))'
    arrays_kv = r'(?:(?P<array_line>"(?P<array_key>[^"\\]*)"\s*=\s*(?P<array_value>\((?:\s*"[^"\\]*",)*\s*\);)))'

    strings = r'(?:%s[ \t]*[\n]|[\r\n]|[\r]){0,1}%s|%s'%(cp, kv, arrays_kv)
    p = re.compile(strings)
    for r in p.finditer(f):
        key = r.group('key') or r.group('array_key')
        value = r.group('value') or r.group('array_value') or ''
        comment = r.group('comment') or ''
        key = _unescape_key(key)
        value = _unescape(value)
        stringset.append({'value': value, 'key': key, 'comment': comment})
    return resultdict

def parse_stringsdict(strings_path):
    print("---- Parsing stringsdict file: " + strings_path)
    plist_object = plistlib.readPlist(strings_path)
    strings = {"file_type": "stringsdict","file_path": strings_path, "content": []}
    for key, value in plist_object.iteritems():
        resultdict = {}
        resultdict['NSLocalizedStringsdict'] = key
        for sub_key, sub_value in value.iteritems():
            variable = ""
            if sub_key == "NSStringLocalizedFormatKey":
                variable = sub_value[3: -1]
                resultdict['NSStringLocalizedFormatKey'] = sub_value
                resultdict['Variable'] = variable
                if variable in value.keys():
                    plurals_rule_dict = value[variable]
                    spec_type_key = "NSStringFormatSpecTypeKey"
                    value_type_key = "NSStringFormatValueTypeKey"

                    for type_key in [spec_type_key, value_type_key]:
                        if type_key in plurals_rule_dict.keys():
                            resultdict[type_key] = plurals_rule_dict[type_key]

                    for plural_rule_key in ["zero", "one", "two", "few", "many", "other"]:
                        if plural_rule_key in plurals_rule_dict.keys():
                            resultdict[plural_rule_key] = plurals_rule_dict[plural_rule_key]
        strings["content"].append(resultdict)
    return strings

def parse_plist(plist_path):
    tree = etree.parse(plist_path)
    root = tree.getroot()
    language_key = "CFBundleDevelopmentRegion"
    for child in root:
        plist_dict = {}
        for idx, item in enumerate(child):
            if item.tag == "key":
                value_item = child[idx+1]
                plist_dict[item.text] = value_item.text
                pass
        if language_key in plist_dict.keys():
            result = {"file_type": "plist", "file_path": plist_path, language_key: plist_dict[language_key]}
            return result

def start_parsing(strings_path):
    ext = os.path.splitext(strings_path)[1]

    if ext == ".strings":
        return parse_strings(strings_path)
        pass
    elif ext == ".stringsdict":
        return parse_stringsdict(strings_path)
        pass
    elif ext == ".plist":
        return parse_plist(strings_path)
        pass
