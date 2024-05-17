import TermTk as ttk

FelderAnzahl = input ("Geben Sie die Anzahl der Felder ein: ")

    # Layout wird verwendet, um die Positionierung der Widgets zu definieren
gridLayout = ttk.TTkGridLayout(columnMinHeight=0,columnMinWidth=0)
    # Hauptwidget wird erstellt (mit dem zuvor erstellten TTkGridLayout-Layout initialisiert): Ein neues TTk-Objekt wird erstellt
root = ttk.TTk(layout=gridLayout)

for x in range(0, int(FelderAnzahl)):
    ttk.TTkButton(parent=root, border=True, text="Button R1 " + str (x+1))
    
    for y in range(1, int(FelderAnzahl)):
        gridLayout.addWidget(ttk.TTkButton(parent=root, border=True, text="Button R2 " + str (x+1)),y,x)

    

root.mainloop()