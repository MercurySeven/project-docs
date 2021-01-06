import re
import os
import typing
from pathlib import Path
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db


START_EXPRESSION = "INIZIO_SEZIONE_GENERATA_AUTOMATICAMENTE"
END_EXPRESSION = "FINE_SEZIONE_GENERATA_AUTOMATICAMENTE"


def findSectionStart(lines: typing.List[str]) -> int:
    matchedIndexes = [
        i for i, line in enumerate(lines) if re.search(START_EXPRESSION, line)
    ]
    assert len(matchedIndexes) == 1, "found too many start expressions"
    assert matchedIndexes[0] != 0, "this matched index does not make sense"

    return matchedIndexes[0]


def findSectionEnd(lines: typing.List[str]) -> int:
    matchedIndexes = [
        i for i, line in enumerate(lines) if re.search(END_EXPRESSION, line)
    ]
    assert len(matchedIndexes) == 1, "found too many end expressions"
    assert matchedIndexes[0] != 0, "this matched index does not make sense"

    return matchedIndexes[0]


def main() -> None:
    # Fetch the service account key JSON file contents
    print(os.environ.get('client_id'))
    secrets = {
        "type": "service_account",
        "project_id": "glossario-765f4",
        "private_key_id": os.environ.get('private_key_id'),
        "private_key": os.environ.get('private_key'),
        "client_email": "firebase-adminsdk-lxanj@glossario-765f4.iam.gserviceaccount.com",
        "client_id": os.environ.get('client_id'),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-lxanj%40glossario-765f4.iam.gserviceaccount.com"
    }

    

    cred = credentials.Certificate(secrets)

    # Initialize the app with a service account, granting admin privileges
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://glossario-765f4-default-rtdb.firebaseio.com/'
    })

    ref = db.reference('/')

    texFilePath = Path(".", "Esterni", "Glossario", "Glossario.tex")

    with texFilePath.open(
        "r", encoding="utf-8", errors="strict", newline="\n"
    ) as texFile:
        wholeContents: typing.List[str] = texFile.readlines()

    sectionStart = findSectionStart(wholeContents)
    sectionEnd = findSectionEnd(wholeContents)

    preamble = wholeContents[: sectionStart + 1]
    # contents = wholeContents[sectionStart + 1 : sectionEnd]
    ending = wholeContents[sectionEnd:]

    contents: typing.List[str] = []

    if ref.get() and len(ref.get().items()) > 0:
        for letter, entries in ref.get().items():
            if len(entries) > 0:
                definitions = []

                for name, description in entries.items():
                    decodedName = decodeFromFirebase(name)
                    if description:
                        definitions.append("  \\item[" + decodedName + "] " + description + "\n")
                        print(f"Inserted {decodedName}")
                    else:
                        print(f"ignored term {decodedName}.")

                if definitions:
                    contents.append("\\section{" + letter + "}\n")
                    contents.append("\\begin{description}\n")

                    contents.extend(definitions)

                    contents.append("\\end{description}\n")
                    contents.append("\\newpage\n")

    with texFilePath.open(
        "w", encoding="utf-8", errors="strict", newline="\n"
    ) as texFile:
        texFile.write("".join(preamble + contents + ending))


def decodeFromFirebase(stringa) -> str :
    stringaPulita = stringa.replace(",", ".")#Firebase non accetta il . come carattere nella chiave
    stringaPulita = stringaPulita.replace("\\", "/")#Doppio slash per evitare di creare figli
    return stringaPulita

if __name__ == "__main__":
    main()
