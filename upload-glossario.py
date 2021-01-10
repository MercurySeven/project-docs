import re
import os
from pathlib import Path
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db


def main() -> None:

    if os.path.isfile('glossarioChiave.json'):
        secrets = 'glossarioChiave.json'
    else:
        secrets = {
            "type": "service_account",
            "project_id": "glossario-765f4",
            "private_key_id": os.environ.get('private_key_id'),
            "private_key": os.environ.get('private_key').replace("\\n", "\n"),
            "client_email": "firebase-adminsdk-lxanj@glossario-765f4.iam.gserviceaccount.com",
            "client_id": os.environ.get('client_id'),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.environ.get('client_x509_cert_url')
        }

    # Fetch the service account key JSON file contents
    cred = credentials.Certificate(secrets)

    # Initialize the app with a service account, granting admin privileges
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://glossario-765f4-default-rtdb.firebaseio.com/'
    })

    ref = db.reference('/')

    cache = []

    for file in Path(".").glob("**/*.tex"):
        with file.open(
            "r", encoding="utf-8", errors="strict", newline="\n"
        ) as openedFile:
            print(f"Checking: {str(file)}")
            for lineNumber, line in enumerate(openedFile):
                for match in re.finditer(r"\\glo\{(?P<entry>.*?)\}", line):
                    entry = match.group("entry")
                    initial = entry[0].upper()

                    # cannot use the str.capitalize() function because it lowers every
                    # other letter
                    capitalizedEntry = initial + entry[1:]

                    if capitalizedEntry not in cache :
                        if not ref.child(initial).get():#Se non è presente la lettera iniziale come figlio
                            refLocal = ref.child(initial)
                            dictionary = dict()
                        else:
                            refLocal = ref.child(initial)
                            dictionary = dict(refLocal.get().items())

                        if len(entry) < 2:
                            print(f"skipping entry {entry}, too short")
                            continue

                        cache.append(capitalizedEntry)
                        #print(cache)
                        #print(f"Lunghezza: {len(cache)}")
                        try:
                            if checkIfValid(capitalizedEntry) :
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
    #stringaPulita = re.sub(r"\\ignore{(.*?)\}", r"\1", stringa)
    stringaPulita = stringa.replace(r"\ignore{", "")
    stringaPulita = stringaPulita.replace("  ", " ")
    stringaPulita = stringaPulita.replace(".", ",")#Firebase non accetta il . come carattere nella chiave
    stringaPulita = stringaPulita.replace("/", "\\")#Doppio slash per evitare di creare figli
    return stringaPulita

def checkIfValid(stringa) -> bool :
    return (r"\glo" not in stringa)

if __name__ == "__main__":
    main()
