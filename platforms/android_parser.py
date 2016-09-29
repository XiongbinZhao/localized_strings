import os
import xml.etree.ElementTree as etree
from xml.etree.ElementTree import ParseError

"""
Usage

Main Function:
-- def android_parser.start_parsing(strings_path):
    Given a path of a xml file.
    Parse the file and return a dictionary as output.

Sub Function:
-- def get_xml_content(xml_path):
    Given a path of a xml file.
    Open and read the xml file, return the content in xml-tree object
-- def parse_xml(content):
    Given the content of a xml file
    Parse the content and return a dictionary

e.g.
.xml file
 {  
    "file_type": "xml", 
    "content":[ 
    			{   
    			  "string_type": "Could be string, string-array or plurals", 
    		      "name": "This is the name", 
    			  "value": "this is the value"
    			} 
    		  ]
 }
"""
def get_xml_content(xml_path):
    try:
        tree = etree.parse(xml_path)
        root = tree.getroot()
    except ParseError:
        print "---- The format of xml file is not correct: " + xml_path + "\n"
        return

    return root

def parse_xml(content):
    if content is None:
        return

    stringset = []
    for child in content:
        xml_dict = {"string_type": child.tag}
        if child.tag == "string":
            text = child.text or ""
            xml_dict["name"] = child.attrib["name"]
            xml_dict["value"] = text
        elif child.tag == "string-array":
            items = []
            for item in child:
                text = item.text or ""
                items.append(text)
            xml_dict["name"] = child.attrib["name"]
            xml_dict["value"] = items
        elif child.tag == "plurals":
            items = {}
            for item in child:
                text = item.text or ""
                for key in item.attrib.keys():
                    items[item.attrib[key]] = text

            xml_dict["name"] = child.attrib["name"]
            xml_dict["value"] = items
        else:
            return None
        stringset.append(xml_dict)

    return stringset

def start_parsing(strings_path):
    ext = os.path.splitext(strings_path)[1]
    if ext == ".xml":
        content = get_xml_content(strings_path)
        result_stringset = parse_xml(content)

        if result_stringset is not None:
            if len(result_stringset) == 0:
                print "---- xml file has not objects: " + xml_path + "\n"
                return
            else:
                print "---- Parsing xml file: " + strings_path
                return {"file_type": "xml", "file_path":strings_path, "content": result_stringset}



