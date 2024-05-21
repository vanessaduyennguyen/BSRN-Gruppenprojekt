import TermTk as ttk

def ersetze_ButtonText(feld):
    # Methode von TTkButton wird genutzt, um die Mitte des Feldes zu ersetzen (Joker)
    feld.setText("Joker")

felder_Anzahl = int (input("Geben Sie die Anzahl der Felder ein: "))

    # Layout wird verwendet, um die Positionierung der Widgets zu definieren
gridLayout = ttk.TTkGridLayout(columnMinHeight=0,columnMinWidth=0)
    # Hauptwidget wird erstellt (mit dem zuvor erstellten TTkGridLayout-Layout initialisiert): Ein neues TTk-Objekt wird erstellt
root = ttk.TTk(layout=gridLayout)

# Bingokarte wird erstellt 
for x in range(0, felder_Anzahl):
    for y in range(0, felder_Anzahl):
        feld = ttk.TTkButton(parent=root, border=True, text="Button R " + str (x+1), checked = False, checkable = True)
        gridLayout.addWidget(feld, row=y, col=x, rowspan=1, colspan=1, direction=3)
       
        if felder_Anzahl == 5 and y == 2 and x == 2 or felder_Anzahl == 7 and y == 3 and x == 3 :
            ersetze_ButtonText(feld)


root.mainloop()