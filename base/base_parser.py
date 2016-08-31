
from __future__ import absolute_import
import os
import plistlib
import codecs, re, chardet

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

class StringsParser:

    def parse_localized_files(self, strings_list):
		# Parse two types of files: .strings & .stringsdict
        if not strings_list:
			return

        for strings_tuple in strings_list:
            print "******** " + strings_tuple[0] + " ********"
            for key, values in strings_tuple[1].iteritems():
                if len(values) > 0:
                    print "**** " + key + ":"
                for s in values: # iterate all the .strings & .stringsdict files
                    root,ext = os.path.splitext(s)
                    if ext == ".strings":
                        self.parse_strings(s)
                        pass
                    elif ext == ".stringsdict":
                        self.parse_stringsdict(s)
                        pass
            print "\n"

    def parse_strings(content="", strings_path=None):
    	print("---- Parsing strings file: " + strings_path)
        if strings_path is not None:
            content = _get_content(filename=strings_path)
        stringset = []
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
        for s in stringset:
            print "\n"
            for key, value in s.iteritems():
                print "**" + key + ": " + value

    def parse_stringsdict(self, strings_path):
		print("---- Parsing stringsdict file: " + strings_path)
		plist_object = plistlib.readPlist(strings_path)
		for key, value in plist_object.iteritems():
			print "**NSLocalizedString: " + key
			for sub_key, sub_value in value.iteritems():
				variable = ""
				if sub_key == "NSStringLocalizedFormatKey":
					variable = sub_value[3: -1]
					print "**" + sub_key + ": " + sub_value
					print "**Variable: " + variable

					if variable in value.keys():
						plurals_rule_dict = value[variable]
						spec_type_key = "NSStringFormatSpecTypeKey"
						value_type_key = "NSStringFormatValueTypeKey"

						for type_key in [spec_type_key, value_type_key]:
							if type_key in plurals_rule_dict.keys():
								print "**" + type_key + ": " + plurals_rule_dict[type_key]
							else:
								print "(** " + type_key + " is Missing **)"

						for plural_rule_key in ["zero", "one", "two", "few", "many", "other"]:
							if plural_rule_key in plurals_rule_dict.keys():
								print "**" + plural_rule_key + ": " + plurals_rule_dict[plural_rule_key]

			print "\n"