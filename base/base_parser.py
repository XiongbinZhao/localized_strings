
from __future__ import absolute_import
from platforms import ios_parser
from platforms import android_parser
import os, plistlib, codecs, re, chardet
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

def parse_localized_files(strings_list):
    if not strings_list:
        return

    global development_lan_dict
    development_lan_dict = {}
    get_development_dict(strings_list)

    for strings_tuple in strings_list:
        if len(strings_tuple[1].keys()) > 0 and strings_tuple[0] != "Plist":
            print "******** " + strings_tuple[0] + " ********"
            for key, values in strings_tuple[1].iteritems():
                if len(values) > 0:
                    print "**** " + key + ":"
                    pass

                for s in values:
                    ios_strings = ios_parser.start_parsing(s)
                    android_strings = android_parser.start_parsing(s)
                    output_strings(ios_strings)
                    output_strings(android_strings)
            print "\n"

def output_strings(strings):
    if strings == None:
        return
    strings_type = strings["file_type"]

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

def print_development_dict():
    if development_lan_dict.keys() > 0:
        for key, value in development_lan_dict.iteritems():
            print "**Development_Language: " + key + " - " + value

def get_development_dict(strings_list):
    for strings_tuple in strings_list:
        if strings_tuple[0] == "Plist":
            paths = strings_tuple[1]['Plist']
            for p in paths:
                lan = parse_plist(p)
                if lan:
                    dirname = os.path.basename(os.path.dirname(p))
                    basename = os.path.basename(p)
                    info_file = dirname + "/" + basename
                    global development_lan_dict
                    development_lan_dict[info_file] = lan

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
