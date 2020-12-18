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

    newfile: typing.List[str] = []

    dbitems = ref.get().items()

    filepaths = Path(".").glob("**/*.tex")

    blacklist = ["informazioni.tex","registro_modifiche.tex","Glossario.tex"]

    result = [file for file in filepaths if os.path.basename(file) not in blacklist]

    for file in result:
        with file.open(
            "r", encoding="utf-8", errors="strict", newline="\n"
         ) as openedFile:
            for lineNumber, line in enumerate(openedFile):
                curr_line = ""
                for letter, entries in dbitems:
                    for name, description in entries.items():
                        for match in re.finditer(r"(?<!\\glo{)\b" + name + r"\b(?![\w\s]*[}])", line):
                            if(len(curr_line)>0):
                                curr_line = re.sub(r"(?<!\\glo{)\b" + name + r"\b(?![\w\s]*[}])", r"\\glo{" + name +r"}", curr_line)
                            else:
                                curr_line = re.sub(r"(?<!\\glo{)\b" + name + r"\b(?![\w\s]*[}])", r"\\glo{" + name +r"}", line)
                        lowerCaseName = name[0].lower() + name[1:]
                        for match in re.finditer(r"(?<!\\glo{)\b" + lowerCaseName + r"\b(?![\w\s]*[}])", line):
                            if(len(curr_line)>0):
                                curr_line = re.sub(r"(?<!\\glo{)\b" + lowerCaseName + r"\b(?![\w\s]*[}])", r"\\glo{" + lowerCaseName +r"}", curr_line)
                            else:
                                curr_line = re.sub(r"(?<!\\glo{)\b" + lowerCaseName + r"\b(?![\w\s]*[}])", r"\\glo{" + lowerCaseName +r"}", line)
                if(len(curr_line)>0):
                    if(curr_line != line):
                        newfile.append(curr_line)
                else:
                    newfile.append(line)

        with file.open(
            "w", encoding="utf-8", errors="strict", newline="\n"
        ) as openedFile:
            openedFile.write("".join(newfile))
        newfile: typing.List[str] = []
        print("Checked " + str(file))

if __name__ == "__main__":
    main()
