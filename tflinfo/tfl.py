#!/usr/bin/env python
#pylint: disable=wrong-import-position,wrong-import-order,try-except-raise
"""
Query and display TFL bike information in tabular form
"""
import os
import pickle
import sys
import getpass
from .data import Bikes

def get_auth():
    """
    Attempt to retrieve credentials from saved pickle file.  If not found, prompt for details and
    save for future use.
    """
    home = os.getenv("HOME")
    storage = home + "/.tflcreds"
    try:
        credentials = pickle.load(open(storage, "rb"))
    except (EOFError, IOError):
        credentials = None

    if credentials is None:
        credentials = get_credentials_input()
        pickle.dump(credentials, open(storage, "wb"))
        sys.stderr.write("File saved as {}\n\n".format(storage))
    return credentials

def get_credentials_input():
    """
    Prompt for API credentials and return as a tupple
    """
    sys.stderr.write("TFL credentials, keep empty for public API\n"
                     "You only need to enter this once\n\n")
    app_id = input("Enter TFL App ID: ")
    app_key = getpass.getpass("Enter TFL App Key: ")
    return (app_id, app_key)

def main():
    """Main function"""

    arguments = sys.argv.copy()[1:]  # Use slice to remove filename from arguments list
    app_id, app_key = get_auth()
    print(app_id, app_key)
    try:
        command = arguments.pop(0)  # separate command from args
    except IndexError:
        usage()
        sys.exit(1)

    if command == "search" and len(arguments) == 1:
        bikes = Bikes(app_id, app_key)
        output = bikes.search(*arguments)
        print(output)
    elif command == "search" and not arguments:
        sys.stderr.write("Please specify a search term\n")
        sys.exit(10)
    elif command == "search" and len(arguments) == 3:
        bikes = Bikes(app_id, app_key)
        output = bikes.distance_search(*arguments)
        if not output:
            sys.stderr.write("The search request is not valid\n")
            sys.exit(11)
        print(output)
    elif command == "id" and len(arguments) == 1:
        bikes = Bikes(app_id, app_key)
        output = bikes.get_id(*arguments)
        if not output:
            sys.stderr.write("Bike Point {0} not recognised\n".format(arguments[0]))
            sys.exit(13)
        print(output)
    elif command == "id" and not arguments:
        sys.stderr.write("Please specify a bike point\n")
        sys.exit(12)
    else:
        usage()
        sys.exit(1)

def usage():
    """
    Print script usage to stderr and exit
    """
    sys.stderr.write("Usage:\n"
                     "{0} search <search string>\n"
                     "{0} search <latitude> <longitude> <radius_in_metres>\n"
                     "{0} id <bike_point_id>\n".format(sys.argv[0].split('/')[-1]))
if __name__ == "__main__":
    main()
