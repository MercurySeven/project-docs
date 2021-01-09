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
            parole.append(decodeFromFirebase(name))

    newfile: typing.List[str] = []

    filepaths = Path(".").glob("**/*.tex")

    blacklist = ["informazioni.tex","registro_modifiche.tex","Glossario.tex","LetteraDiPresentazione.tex","verbale.tex"]

    result = [file for file in filepaths if os.path.basename(file) not in blacklist]

    for file in result:
        with file.open(
            "r", encoding="utf-8", errors="strict", newline="\n"
         ) as openedFile:
            for lineNumber, line in enumerate(openedFile):
                curr_line = line
                if((re.search("section{",line) is None) and 
                (re.search("paragraph{",line) is None) and 
                (re.search(r"paragraph\*{",line) is None) and 
                (re.search("input{",line) is None) and 
                (re.search("includegraphics",line) is None) and 
                (re.search("http",line) is None) and 
                (re.search("label{",line) is None) and 
                (re.search("caption{",line) is None)):
                    for name in parole:
                        #regex = r"(?<!\\glo{)\b" + name +r"\b(?=[},\W])"
                        #https://stackoverflow.com/questions/4213800/is-there-something-like-a-counter-variable-in-regular-expression-replace/4214173#4214173
                        regex = r"(?=(?=\w)(?<!\w)(?<!\\glo{)(?<!\\))" + sistemaCaratteriSpeciali(name) +r"(?=(?<=\w)(?!\w)|(?=[},\W]))"

                        for match in re.finditer(regex, line):
                            curr_line = re.sub(regex, r"\\glo{" + name +"}", curr_line)
                        lowerCaseName = name[0].lower() + name[1:]
                        regex = r"(?=(?=\w)(?<!\w)(?<!\\glo{)(?<!\\))" + sistemaCaratteriSpeciali(lowerCaseName) +r"(?=(?<=\w)(?!\w)|(?=[},\W]))"
                        for match in re.finditer(regex, line):
                            curr_line = re.sub(regex, r"\\glo{" + lowerCaseName +"}", curr_line)

                newfile.append(curr_line)

        with file.open(
            "w", encoding="utf-8", errors="strict", newline="\n"
        ) as openedFile:
            openedFile.write("".join(newfile))
        newfile: typing.List[str] = []
        print("Checked " + str(file))

def decodeFromFirebase(stringa) -> str :
    stringaPulita = stringa.replace(",", ".")#Firebase non accetta il . come carattere nella chiave
    stringaPulita = stringaPulita.replace("\\", "/")#Doppio slash per evitare di creare figli
    return stringaPulita

def sistemaCaratteriSpeciali(stringa) -> str:
    stringaPulita = stringa.replace("+","\+")
    return stringaPulita

if __name__ == "__main__":
    main()
