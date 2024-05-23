import TermTk as ttk
import argparse
import os
import random

# Die Methode soll das Feld in der Mitte ersetzen und automatisch markieren.
# Das Feld mit den neuen Eigenschaften wird zurückgegeben.
def JOKER_ausfüllen(feld):
    feld.setText("JOKER")
    feld.setChecked(True)
    return feld


def open_file(filename):
    with open(filename, 'r') as file:
        return file.read().splitlines()

def create_bingo_card(felder_Anzahl, words):
    gridLayout = ttk.TTkGridLayout(columnMinHeight=0,columnMinWidth=0)
    root = ttk.TTk(layout=gridLayout)
    # Eine 2D-Liste (Matrix von den Bingofeldern) wird zur Überprüfung, ob es ein Bingo gibt, erstellt.
    felder_matrix = []
    for x in range(felder_Anzahl):
        # Es wird eine Reihe der Matrix erstellt
        rows = []
        for y in range(felder_Anzahl):
            word = random.choice(words)
            words.remove(word)
            feld = ttk.TTkButton(parent=root, border=True, text=word, checked = False, checkable = True)
            gridLayout.addWidget(feld, row = x, col = y, rowspan=1, colspan=1, direction=3)
            # Zu der Reihe der Matrix werden bei jedem Durchlauf der Schleife TTkButton-Objekte hinzugefügt (insgesamt felder_Anzahl-Objekte).
            rows.append(feld)

            if felder_Anzahl%2 != 0 and x == (felder_Anzahl//2) and y == (felder_Anzahl//2):
                neues_Feld = JOKER_ausfüllen(feld)
                # Der Index von dem altem Feld(der zuletzt genutzte Index) wird durch das neue Feld (mit den "neuen Attributen") ersetzt.
                last_index = len(rows)-1
                rows[last_index] = neues_Feld

        # Die "fertige" Reihe wird nun der Matrix hinzugefügt
        # Bei erneuten Durchlauf der Schleife wird wieder eine neue Reihe erstellt, hinzugefügt, etc....
        felder_matrix.append(rows)
    
        
    root.mainloop()
    #return felder_matrix
    
# Hauptfunktion, die die Kommandozeilenargumente verarbeitet und die Bingo-Karte erstellt    
def main():
    # Kommandozeilenargumente mit dem argparse-Modul hinzufügen
    parser = argparse.ArgumentParser(description="Erstellen einer Bingo-Karte.")
    # Definiert das Kommandozeilenargument 'filename' (Dateiname)
    parser.add_argument("wordfile", nargs='?', help='Der Name der zu öffnenden Datei') 
    # Definiert das Kommandozeilenargument 'felder_Anzahl' (Anzahl der Felder auf der Bingo-Karte)
    parser.add_argument("felder_Anzahl", type=int, help="Die Anzahl der Felder der Bingo-Karte.")
    
    # Parst die Kommandozeilenargumente und speichert sie in 'args'
    args = parser.parse_args()

    # Weist die Argumente 'filename' und 'felder_Anzahl' den entsprechenden Variablen zu
    filename = args.wordfile
    felder_Anzahl = args.felder_Anzahl

    # Überprüft, ob die angegebene Datei existiert
    if os.path.exists(filename):
        # Wenn sie existiert, wird sie geöffnet
        words = open_file(filename)
        # Ruft die Funktion zum Erstellen der Bingo-Karte auf
        create_bingo_card(felder_Anzahl, words)
    else:
        # Wenn die Datei nicht existiert, wird eine Fehlermeldung ausgegeben
        print(f"Die Datei {filename} existiert nicht.")
        
if __name__ == "__main__":
    main()


