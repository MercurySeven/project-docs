import argparse
import json
import sys
import re
import typing
import os
from pathlib import Path
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db


def main() -> None:
    # Fetch the service account key JSON file contents
    cred = credentials.Certificate('glossarioChiave.json')

    # Initialize the app with a service account, granting admin privileges
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://glossario-765f4-default-rtdb.firebaseio.com/'
    })

    ref = db.reference('/')
    dbitems = ref.get().items()
    parole = []
    for letter, entries in dbitems:
        for name, description in entries.items():
            parole.append(name)

    newfile: typing.List[str] = []

    filepaths = Path(".").glob("**/*.tex")

    blacklist = ["informazioni.tex","registro_modifiche.tex","Glossario.tex"]

    result = [file for file in filepaths if os.path.basename(file) not in blacklist]

    for file in result:
        with file.open(
            "r", encoding="utf-8", errors="strict", newline="\n"
         ) as openedFile:
            for lineNumber, line in enumerate(openedFile):
                curr_line = line
                #if((re.search("section{",line) is None) and (re.search("paragraph{",line) is None)):
                for name in parole:
                    for match in re.finditer(r"(?<!\\glo{)\b" + name + r"\b(?![\w\s]*[}])", line):
                        curr_line = re.sub(r"(?<!\\glo{)\b" + name + r"\b(?![\w\s]*[}])", r"\\glo{" + name +r"}", curr_line)
                    lowerCaseName = name[0].lower() + name[1:]
                    for match in re.finditer(r"(?<!\\glo{)\b" + lowerCaseName + r"\b(?![\w\s]*[}])", line):
                        curr_line = re.sub(r"(?<!\\glo{)\b" + lowerCaseName + r"\b(?![\w\s]*[}])", r"\\glo{" + lowerCaseName +r"}", curr_line)

                newfile.append(curr_line)

        with file.open(
            "w", encoding="utf-8", errors="strict", newline="\n"
        ) as openedFile:
            openedFile.write("".join(newfile))
        newfile: typing.List[str] = []
        print("Checked " + str(file))

if __name__ == "__main__":
    main()