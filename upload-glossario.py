import re
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
                        if encodeForFirebase(capitalizedEntry) not in dictionary.keys():
                            refLocal.child(encodeForFirebase(capitalizedEntry)).set("{scrivere o ignorare questa definizione}")
                            print(f"Uploaded {capitalizedEntry}")

                    except KeyError:
                        print("This entry is not a suitable dictionary key.")
                        print(f"File: {file}")
                        print(f"Line number: {lineNumber}")
                        print(f"Line: {line}")
                        print(f"Entry: {capitalizedEntry}")

def encodeForFirebase(stringa) -> str :
    stringaPulita = stringa.replace(".", ",")#Firebase non accetta il . come carattere nella chiave
    stringaPulita = stringaPulita.replace("/", "\\")#Doppio slash per evitare di creare figli
    return stringaPulita

if __name__ == "__main__":
    main()
