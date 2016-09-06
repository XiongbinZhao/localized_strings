import os, plistlib, codecs, re, chardet

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

def parse_strings(strings_path=None):
    print("---- Parsing strings file: " + strings_path)
    if strings_path is not None:
        content = _get_content(filename=strings_path)
    stringset = []
    resultdict = {"content": stringset, "file_type": "strings"}
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
    strings = {"file_type": "stringsdict", "content": []}
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

def start_parsing(strings_path):
    ext = os.path.splitext(strings_path)[1]
    if ext == ".strings":
        return parse_strings(strings_path)
        pass
    elif ext == ".stringsdict":
        return parse_stringsdict(strings_path)
        pass
