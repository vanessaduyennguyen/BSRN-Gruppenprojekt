import TermTk as ttk
import argparse
import os
import random

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

    felder_matrix = []
    for x in range(felder_Anzahl):
        rows = []
        for y in range(felder_Anzahl):
  
            word = random.choice(words)
            words.remove(word)
            feld = ttk.TTkButton(parent=root, border=True, text=word, checked = False, checkable = True)
            gridLayout.addWidget(feld, row=y, col=x, rowspan=1, colspan=1, direction=3)
            rows.append(feld)

            if felder_Anzahl == 5 and y == 2 and x == 2 or felder_Anzahl == 7 and y == 3 and x == 3:
                neues_Feld = JOKER_ausfüllen(feld)
                last_index = len(rows)-1
                rows[last_index] = neues_Feld
        felder_matrix.append(rows)
        
    root.mainloop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="textdateibefehl.py", add_help=False)
    parser.add_argument('wordfile', nargs='?', help='Der Name der zu öffnenden Datei')
    args = parser.parse_args()

    if args.wordfile is None:
        filename = input("Geben Sie den Namen der Textdatei ein:")
    else:
        filename = args.wordfile

    if os.path.exists(filename):
        words = open_file(filename)
        felder_Anzahl = int(input("Geben Sie die Anzahl der Felder ein: "))
        create_bingo_card(felder_Anzahl, words)
    else:
        print(f"Die Datei {filename} existiert nicht.")

