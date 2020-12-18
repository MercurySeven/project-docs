import argparse
import json
import re
import sys
from pathlib import Path
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db



ARGUMENT_PARSER = argparse.ArgumentParser()

# TODO define a path argument so as to call this script with
# python ./make-json.py ../path-to-target-folder
ARGUMENT_PARSER.add_argument(
    "-v", "--version", help="show program version and exit", action="store_true"
)

PARSED_ARGS = ARGUMENT_PARSER.parse_args()

if PARSED_ARGS.version:
    print("make-json.py version 1.0.1\nLicensed under the GPLv3.0")
    sys.exit()


def main() -> None:
    # Fetch the service account key JSON file contents
    cred = credentials.Certificate('glossarioChiave.json')

    # Initialize the app with a service account, granting admin privileges
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://glossario-765f4-default-rtdb.firebaseio.com/'
    })

    ref = db.reference('/')

    for file in Path(".").glob("**/*.tex"):
        with file.open(
            "r", encoding="utf-8", errors="strict", newline="\n"
        ) as openedFile:
            for lineNumber, line in enumerate(openedFile):
                for match in re.finditer(r"\\glo\{(?P<entry>.*?)\}", line):
                    entry = match.group("entry")
                    initial = entry[0].upper()


                    if not ref.child(initial).get():#Se non è presente la lettera iniziale come figlio
                        refLocal = ref.child(initial)
                        dictionary = dict()
                    else:
                        refLocal = ref.child(initial)
                        dictionary = dict(refLocal.get().items())

                    if len(entry) < 2:
                        print(f"skipping entry {entry}, too short")
                        continue

                    # cannot use the str.capitalize() function because it lowers every
                    # other letter
                    capitalizedEntry = initial + entry[1:]

                    try:
                        if capitalizedEntry not in dictionary.keys():
                            refLocal.child(capitalizedEntry).set("{scrivere o ignorare questa definizione}")
                            print(f"Aggiungo {capitalizedEntry}")

                    except KeyError:
                        print("This entry is not a suitable dictionary key.")
                        print(f"File: {file}")
                        print(f"Line number: {lineNumber}")
                        print(f"Line: {line}")
                        print(f"Entry: {capitalizedEntry}")

if __name__ == "__main__":
    main()
