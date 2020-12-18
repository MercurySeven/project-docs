# Documentazione del capitolato C7 SWE 2020/2021

## Composizione del gruppo
- Daniele Giachetto
- Davide Albiero
- Francesco De Marchi
- Giosuè Calgaro
- Lucrezia Gradi
- Matteo Pagotto
- Tommaso Poppi

## Come usare il Glossario

Per usare gli script è necessario Python 3.6+ e installare firebase-admin con il seguente comando `pip install firebase-admin`.  
Assicurarsi che nella root principale ci sia il file `glossarioChiave.json` (disponibile su Slack#documenti-vari)

1. Per aggiungere una parola al glossario, la parola deve essere racchiusa da `\glo{PAROLA}`
2. Il passo successivo è `python3 upload-glossario.py` per caricare le parole su Firebase.
3. Per modificare la descrizione bisogna collegarsi a [Firebase](https://console.firebase.google.com/project/glossario-765f4/database/glossario-765f4-default-rtdb/data) con l'account gmail del gruppo.  
Una volta collegati si potrà modificare la descrizione delle parole aggiunte.
4. Per creare il glossario bisogna eseguire lo script `python3 make-glossario.py`.
5. Per cercare tutte le parole che non sono racchiuse in `\glo{ }` lanciate lo script `python3 check-glossario.py`  
CONSIGLIO DI EFFETTUARE UN COMMIT PRIMA DI QUESTO COMANDO, COSÌ DA VEDERE QUALI PAROLE SONO STATE CAMBIATE.
