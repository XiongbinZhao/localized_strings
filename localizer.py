
#!/usr/bin/env python

import os
import argparse
import plistlib
import shutil

from base import base_seeker
from base import base_parser
from platforms import ios_seeker
from platforms import android_seeker
from platforms import ios_parser


def main():
    p = argparse.ArgumentParser(description='Parsing Localized Strings Files for iOS/Android projects')
    p.add_argument('-init', metavar='project-path', dest="project_path", help="Find and parse Localized Strings Files in the project_path")
    arguments = p.parse_args()

    project_path = None

    if 'PROJECT_DIR' in os.environ:
        project_path = os.environ['PROJECT_DIR']
    elif arguments.project_path:
        project_path = arguments.project_path

    android_strings_list = android_seeker.find_localized_strings(project_path)
    ios_strings_list = ios_seeker.find_sets(project_path)
    pbxproj_list = ios_seeker.find_all_pbxproj(project_path)

    base_parser.parser_setup(project_path, None, pbxproj_list)
    base_parser.parse_ios_localized_files_set(ios_strings_list)
    android_strings_list = base_parser.parse_android_localized_files(android_strings_list)

    if android_strings_list is None and ios_strings_list is None:
        print "Error: There is no Localized Strings file in the target project."
    else:
        print "****\n****\n**** Done! Strings have been output to: " + base_parser.get_output_path()
    
main()

