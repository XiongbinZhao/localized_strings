import os
import argparse
import plistlib

from base import base_seeker
from base import base_parser

def main():
    p = argparse.ArgumentParser(description='Parsing Localized Strings Files for iOS/Android projects')
    p.add_argument('-init', metavar='project-path', dest="project_path", help="Find and parse Localized Strings Files in the project_path")
    arguments = p.parse_args()

    project_path = None

    if 'PROJECT_DIR' in os.environ:
        project_path = os.environ['PROJECT_DIR']
    elif arguments.project_path:
        project_path = arguments.project_path

    strings_list = base_seeker.find_localized_strings_files_in_project(project_path)

    parser = base_parser.StringsParser()
    parser.parse_localized_files(strings_list)

main()