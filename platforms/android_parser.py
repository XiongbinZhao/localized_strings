import os
import xml.etree.ElementTree as etree
from xml.etree.ElementTree import ParseError

"""

Call def start_parsing(strings_path):

Given a path of a xml file.
Parse the file and return a dictionary as output.

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

def parse_xml(xml_path):
    try:
        tree = etree.parse(xml_path)
        root = tree.getroot()
    except ParseError:
        print "---- The format of xml file is not correct: " + xml_path + "\n"
        return
    strings = {"file_type": "xml", "file_path":xml_path, "content": []}
    for child in root:
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
        strings["content"].append(xml_dict)

    if len(strings["content"]) == 0:
        print "---- xml file has not objects: " + xml_path + "\n"
        return
    else:
        strings["file_path"] = xml_path
        print "---- Parsing xml file: " + xml_path
        return strings

def start_parsing(strings_path):
    ext = os.path.splitext(strings_path)[1]
    if ext == ".xml":
        strings = parse_xml(strings_path)
        return strings