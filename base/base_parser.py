
from __future__ import absolute_import
from platforms import ios_parser
from platforms import android_parser
import os, plistlib, codecs, re, chardet, shutil
import xml.etree.ElementTree as etree

format_encoding = 'UTF-16'

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

def set_output_path(output_path):
    global target_dir
    target_dir = output_path

def set_proj_path(project_path):
    global proj_path
    proj_path = project_path

def parse_ios_localized_files(strings_list):
    if not strings_list:
        return

    global development_lan_dict

    development_lan_dict = {}
    development_lan_dict = ios_parser.get_schemes_info_plist(proj_path)

    ios_strings_list = []
    for strings_tuple in strings_list:
        if len(strings_tuple[1].keys()) > 0:
            for key, values in strings_tuple[1].iteritems():

                for s in values:
                    ios_strings = ios_parser.start_parsing(s)
                    if ios_strings is not None:
                        if not s.endswith(".plist"):
                            ios_strings_list.append(ios_strings)

                    output_strings(ios_strings)
    if len(ios_strings_list) == 0:
        return None
    else:
        return ios_strings_list

def parse_android_localized_files(strings_list):
    if not strings_list:
        return

    android_strings_list = []
    for strings_tuple in strings_list:
        if len(strings_tuple[1].keys()) > 0:
            for key, values in strings_tuple[1].iteritems():

                for s in values:
                    android_strings = android_parser.start_parsing(s)

                    if android_strings is not None:
                        android_strings_list.append(android_strings)

                    output_strings(android_strings)
    if len(android_strings_list) == 0:
        return None
    else:
        return android_strings_list

def output_txt_file(strings):
    output_file = os.path.basename(strings["file_path"]) + ".txt"
    output_dir = os.path.basename(os.path.dirname(strings["file_path"]))

    output_file_path = os.path.join(output_dir, output_file)
    path_to_output = os.path.join(target_dir, output_file_path)

    if not os.path.exists(os.path.split(path_to_output)[0]):
        os.makedirs(os.path.split(path_to_output)[0])

    if os.path.isfile(path_to_output):
        text_file = open(path_to_output, "a")
    else:
        text_file = open(path_to_output, "w+")

    strings_type = strings["file_type"]

    if strings_type == "strings":
        for dic in strings["content"]:
            text_file.write("**comment: " + dic["comment"].encode("utf-8") + "\n")
            text_file.write("**key: " + dic["key"].encode("utf-8") + "\n")
            text_file.write("**value: " + dic["value"].encode("utf-8") + "\n")
            write_development_dict(text_file)
            text_file.write("\n")

    elif strings_type == "stringsdict":
        for dic in strings["content"]:
            title_key = "NSLocalizedStringsdict"
            localized_format_key = "NSStringLocalizedFormatKey"
            value_type_key = "NSStringFormatValueTypeKey"
            spec_type_key = "NSStringFormatSpecTypeKey"
            variable_key = "Variable"

            plural_rule_keys = ["zero", "one", "two", "few", "many", "other"]
            available_keys = dic.keys()
            for key in [title_key, localized_format_key, value_type_key, spec_type_key, variable_key]:
                if key in available_keys:
                    text_file.write("**" + key + ": " + dic[key].encode("utf-8") + "\n")
            for key in plural_rule_keys:
                if key in available_keys:
                    text_file.write("**" + key + ": " + dic[key].encode("utf-8") + "\n")
            write_development_dict(text_file)
            text_file.write("\n")

    elif strings_type == "xml":
        for dic in strings["content"]:
            keys = dic.keys()
            if "string_type" in keys:
                if "name" in keys:
                    if "value" in keys:
                        string_type = dic["string_type"].encode("utf-8")
                        name = dic["name"].encode("utf-8")
                        value = dic["value"]

                        if string_type == "string":
                            text_file.write("**string_type: " + string_type + "\n")
                            text_file.write("**name: " + name + "\n")
                            text_file.write("**value: " + value.encode("utf-8") + "\n")
                            pass
                        elif string_type == "plurals":
                            text_file.write("**string_type: " + string_type + "\n")
                            text_file.write("**name: " + name + "\n")
                            text_file.write("**value: " + str(value) + "\n")
                            pass
                        elif string_type == "string-array":
                            text_file.write("**string_type: " + string_type + "\n")
                            text_file.write("**name: " + name + "\n")
                            value_output = ""
                            for v in value:
                                value_output = value_output + v.encode("utf-8") + ", "
                            text_file.write("**value: " + value_output + "\n")
                            pass

            text_file.write("\n")

    text_file.close()


def output_strings(strings):
    if strings == None:
        return

    strings_type = strings["file_type"]
    output_txt_file(strings)
'''
    if strings_type == "strings":
        for dic in strings["content"]:
            print "**comment: " + dic["comment"]
            print "**key: " + dic["key"]
            print "**value: " + dic["value"]
            print_development_dict()
            print "\n"

    elif strings_type == "stringsdict":
        for dic in strings["content"]:
            title_key = "NSLocalizedStringsdict"
            localized_format_key = "NSStringLocalizedFormatKey"
            value_type_key = "NSStringFormatValueTypeKey"
            spec_type_key = "NSStringFormatSpecTypeKey"
            variable_key = "Variable"

            plural_rule_keys = ["zero", "one", "two", "few", "many", "other"]
            available_keys = dic.keys()
            for key in [title_key, localized_format_key, value_type_key, spec_type_key, variable_key]:
                if key in available_keys:
                    print "**" + key + ": " + dic[key]
            for key in plural_rule_keys:
                if key in available_keys:
                    print "**" + key + ": " + dic[key]
            print_development_dict()
            print "\t"

    elif strings_type == "xml":
        for dic in strings["content"]:
            keys = dic.keys()
            if "string_type" in keys:
                if "name" in keys:
                    if "value" in keys:
                        string_type = dic["string_type"]
                        name = dic["name"]
                        value = dic["value"]

                        if string_type == "string":
                            print "**string_type: " + string_type
                            print "**name: " + name
                            print "**value: " + value
                            pass
                        elif string_type == "plurals":
                            print "**string_type: " + string_type
                            print "**name: " + name
                            print "**value: " + str(value)
                            pass
                        elif string_type == "string-array":
                            print "**string_type: " + string_type
                            print "**name: " + name
                            value_output = ""
                            for v in value:
                                value_output = value_output + v + ", "
                            print "**value: " + value_output
                            pass
            
            print "\t"
'''

def write_development_dict(text_file):
    for key, value in development_lan_dict.iteritems():
        text_file.write("**Development_Language: " + key + " - " +  value['info_file'] + " - " + value["lan"] + "\n")

def print_development_dict():
    for key, value in development_lan_dict.iteritems():
        print "**Development_Language: " + key + " - " +  value['info_file'] + " - " + value["lan"]
        pass
