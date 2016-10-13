
#!/usr/bin/env python

import os
import argparse
import plistlib
import shutil

from base import base_seeker
from base import base_parser
from platforms import ios_seeker
from platforms import android_seeker

def main():
    p = argparse.ArgumentParser(description='Parsing Localized Strings Files for iOS/Android projects')
    p.add_argument('-init', metavar='project-path', dest="project_path", help="Find and parse Localized Strings Files in the project_path")
    arguments = p.parse_args()

    project_path = None

    if 'PROJECT_DIR' in os.environ:
        project_path = os.environ['PROJECT_DIR']
    elif arguments.project_path:
        project_path = arguments.project_path

    ios_strings_list = ios_seeker.find_localized_strings(project_path)
    android_strings_list = android_seeker.find_localized_strings(project_path)

    output_dir = os.path.join(project_path, "script_output")

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    base_parser.set_output_path(output_dir)
    base_parser.set_proj_path(project_path)
    #android_strings_list = base_parser.parse_android_localized_files(android_strings_list)
    #ios_strings_list = base_parser.parse_ios_localized_files(ios_strings_list)

    # if android_strings_list is None and ios_strings_list is None:
    #     print "Error: There is no Localized Strings file in the target project."
    # else:
    #     print "****\n****\n**** Done! Strings have been output to: " + output_dir
    
main()