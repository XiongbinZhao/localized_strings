
from __future__ import absolute_import
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

class StringsParser:

    def parse_localized_files(self, strings_list):
		# Parse two types of files: .strings & .stringsdict
        if not strings_list:
			return

        global development_lan_dict
        development_lan_dict = {}
        self.get_development_dict(strings_list)

        for strings_tuple in strings_list:
            if len(strings_tuple[1].keys()) > 0 and strings_tuple[0] != "Plist":
                print "******** " + strings_tuple[0] + " ********"
                for key, values in strings_tuple[1].iteritems():
                    if len(values) > 0:
                        print "**** " + key + ":"
                        pass
                    for s in values: # iterate all the .strings & .stringsdict files & .xml files
                        root,ext = os.path.splitext(s)
                        if ext == ".strings":
                            self.parse_strings(s)
                            pass
                        elif ext == ".stringsdict":
                            self.parse_stringsdict(s)
                            pass
                        elif ext == ".xml":
                            self.parse_xml(s)
                            pass

                print "\n"

    def print_development_dict(self):
        if development_lan_dict.keys() > 0:
            for key, value in development_lan_dict.iteritems():
                print "**Development_Language: " + key + " - " + value

    def get_development_dict(self, strings_list):
        for strings_tuple in strings_list:
            if strings_tuple[0] == "Plist":
                paths = strings_tuple[1]['Plist']
                for p in paths:
                    lan = self.parse_plist(p)
                    if lan:
                        dirname = os.path.basename(os.path.dirname(p))
                        basename = os.path.basename(p)
                        info_file = dirname + "/" + basename
                        global development_lan_dict
                        development_lan_dict[info_file] = lan

    def parse_plist(self, plist_path):
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

    def parse_xml(self, xml_path):
        print("---- Parsing xml file: " + xml_path)
        tree = etree.parse(xml_path)
        root = tree.getroot()
        for child in root:
            print child.tag
            if child.tag == "string":
                text = child.text or ""
                print "**Name: " + child.attrib["name"]
                print "**Value: " + text
            elif child.tag == "string-array":
                print "**Name: " + child.attrib["name"]
                for item in child:
                    text = item.text or ""
                    print "*Item: " + text
            elif child.tag == "plurals":
                print "**Name: " + child.attrib["name"]
                for item in child:
                    text = item.text or ""
                    for key in item.attrib.keys():
                        print "*" + item.attrib[key] + ": " + text
            print "\t"

    def parse_strings(self, strings_path=None):
        print "\t"
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
            for key, value in s.iteritems():
                print "**" + key + ": " + value
            self.print_development_dict()
            print "\t"

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
                        self.print_development_dict()

			print "\t"