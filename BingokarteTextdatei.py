import TermTk as ttk
import argparse
import os
import random
import logging
import threading
import time
from datetime import datetime
from TermTk.TTkWidgets.button import TTkButton
from TermTk.TTkWidgets.resizableframe import TTkResizableFrame

# Spielerklasse erstellen
class Spieler:
    def __init__(self, name, pipe_name, pos, size=(50,20)):
        """
        Initialisiert die Spielerklasse mit Name, Pipe, Position und Größe des Fensters.
        
        name: Name des Spielers
        pipe_name: Name der benannten Pipe zur Kommunikation
        pos: Position des Fensters
        size: Größe des Fensters
        """
        self.name = name
        self.pipe_name = pipe_name
        self.root = ttk.TTk()
        self.bingoFenster = ttk.TTkWindow(parent=self.root, pos=pos, size=size, title=name, resizable = True)
        self.winLayout = ttk.TTkGridLayout()
        self.bingoFenster.setLayout(self.winLayout)
        self.felder_matrix = []
        self.has_won = False

        # Log file setup
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        log_filename = f"{timestamp}-bingo-{self.name}.txt"
        
        # Konfiguration des Loggers
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        
        # Handler für Datei hinzufügen
        handler = logging.FileHandler(log_filename)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        # Entfernen des Standard-Stream-Handlers (Terminalausgabe) damit es nicht im Terminal angezeigt wird
        root_logger = logging.getLogger()
        if root_logger.hasHandlers():
            for h in root_logger.handlers:
                root_logger.removeHandler(h)
        
        # Start logging
        self.logger.info("Start des Spiels")
    
    def create_bingo_card(self, felder_Anzahl, words):
        """
        Erstellt die Bingo-Karte mit der angegebenen Anzahl von Feldern und Wörtern
        
        felder_Anzahl: Anzahl der Felder (NxN)
        words: Liste der Wörter für die Bingo-Karte
        """
        self.felder_Anzahl = felder_Anzahl
        self.logger.info(f"Größe des Spielfelds: {felder_Anzahl} / {felder_Anzahl}")
        
        # Eine 2D-Liste (Matrix von den Bingofeldern) wird zur Überprüfung, ob es ein Bingo gibt, erstellt.
        self.felder_matrix = []
        for x in range(felder_Anzahl):
            # Es wird eine Reihe der Matrix erstellt
            rows = []
            for y in range(felder_Anzahl):
                word = random.choice(words)
                words.remove(word)
                feld = ttk.TTkButton(border=True, text=word, checked = False, checkable = True)
                # Verbindung der Methode pruefe_Ob_Bingo mit dem Klickereignis des Feldes
                feld.clicked.connect(self.pruefe_Ob_Bingo)
                feld.clicked.connect(self.on_button_clicked_wrapper(feld, word, x, y))
                # Feld zum Layout hinzufügen
                self.winLayout.addWidget(feld, x, y)
                # Zu der Reihe der Matrix werden bei jedem Durchlauf der Schleife TTkButton-Objekte hinzugefügt (insgesamt felder_Anzahl-Objekte).
                rows.append(feld)

                if felder_Anzahl %2 != 0 and x == (felder_Anzahl//2) and y == (felder_Anzahl//2):
                    # Jokerfeld erstellen
                    feld = self.JOKER_ausfüllen(feld)
                    # Der Index von dem altem Feld(der zuletzt genutzte Index) wird durch das neue Feld (mit den "neuen Attributen") ersetzt.
                    last_index = len(rows)-1
                    rows[last_index] = feld

            # Die "fertige" Reihe wird nun der Matrix hinzugefügt
            # Bei erneuten Durchlauf der Schleife wird wieder eine neue Reihe erstellt, hinzugefügt, etc....
            self.felder_matrix.append(rows)
    
        # Bingo- und Exit-Buttons zum Layout hinzufügen
        self.bingo_button = TTkButton(text="Bingo", parent=self.bingoFenster, border=True)
        self.bingo_button.clicked.connect(self.bingo_check)
        self.winLayout.addWidget(self.bingo_button, felder_Anzahl, 0, 1, felder_Anzahl)

        self.exit_button = TTkButton(text="Spiel beenden", parent=self.bingoFenster, border=True)
        self.exit_button.clicked.connect(self.spiel_beenden)
        self.winLayout.addWidget(self.exit_button, felder_Anzahl+1, 0, 1, felder_Anzahl)

        return self.felder_matrix
    
    # Die Methode soll das Feld in der Mitte ersetzen und automatisch markieren.
    # Das Feld mit den neuen Eigenschaften wird zurückgegeben.
    @staticmethod
    def JOKER_ausfüllen(feld):
        feld.setText("JOKER")
        feld.setChecked(True)
        return feld
    
    def zeige_gewonnen_nachricht(self):
        # Erstellen eines neuen Fensters, um die Gewinnnachricht anzuzeigen
        gewonnenFenster = ttk.TTkWindow(parent=self.root, title="Bingo!", size=(20, 5))
        gewonnenLayout = ttk.TTkGridLayout()
        gewonnenFenster.setLayout(gewonnenLayout)
        gewonnenLabel = ttk.TTkLabel(text=f"{self.name} hat gewonnen!!!")
        gewonnenLayout.addWidget(gewonnenLabel, 0, 0)
        gewonnenFenster.show()
        self.logger.info("Sieg")
        print("Du hast gewonnen!!!")
        
    def zeige_verloren_nachricht(self):
        # Erstellen eines neuen Fensters, um die Verliernachricht anzuzeigen
        verlorenFenster = ttk.TTkWindow(parent=self.root, title="Verloren", size=(20, 5))
        verlorenLayout = ttk.TTkGridLayout()
        verlorenFenster.setLayout(verlorenLayout)
        verlorenLabel = ttk.TTkLabel(text=f"{self.name} hat verloren :(")
        verlorenLayout.addWidget(verlorenLabel, 0, 0)
        verlorenFenster.show()
        self.logger.info("Verloren")
        print("Du hast verloren :(")

    # Wrapper-Methode für das Klickereignis eines Feldes
    def on_button_clicked_wrapper(self, button, word, x, y):
        def wrapper():
            self.on_button_clicked(button, word, x, y)
        return wrapper

    # Ancklicken eines Wortes in die Logdatei schreiben
    def on_button_clicked(self, button, word, x, y):
        if not self.has_won and button.isChecked():
            #button.setChecked(True)
            self.logger.info(f"{word} ({x}/{y})")

    # Methode zum Beenden des Spiels und Schreiben einer Nachricht in die Pipe
    def spiel_beenden(self):
        message = f"Kein Gewinner"
        logging.info(message)
        self.logger.info("Das Spiel wurde beendet")
        self.root.quit()
        # Benannte Pipe im write()-Modus öffnen
        with open(self.pipe_name, 'w') as pipe:
            pipe.write(message + "\n")
            pipe.flush()

    # Überprüft, ob ein Bingo vorliegt und führt entsprechende Aktionen aus
    def bingo_check(self):
        if self.pruefe_Ob_Bingo():
            TTkButton._checkable = False
            self.exit_button._checkable = False
            self.has_won = True
            self.zeige_gewonnen_nachricht()
            message = f"{self.name} hat gewonnen!!!"
            logging.info(message)
            self.logger.info("Ende des Spiels")
            # Benannte Pipe im write()-Modus öffnen
            with open(self.pipe_name, 'w') as pipe:
                pipe.write(message + "\n")
                pipe.flush()
            #self.root.quit()
    
    def pruefe_Ob_Bingo(self):
        bingo = False
        # Überprüfung, ob es ein Bingo diagonal von oben links nach unten rechts gibt
        if all(self.felder_matrix[i][i].isChecked() for i in range(len(self.felder_matrix))):
            bingo = True

        # Überprüfung, ob es ein Bingo diagonal von oben rechts nach unten links gibt
        if all(self.felder_matrix[i][len(self.felder_matrix) - 1 - i].isChecked() for i in range(len(self.felder_matrix))):
            bingo = True   

        # Überprüfung, ob es ein Bingo in einer Reihe gibt
        for row in self.felder_matrix:
            if all(feld.isChecked() for feld in row):
                bingo = True
                break
         
        # Überprüfung, ob es ein Bingo in einer Spalte gibt
        for col in range(len(self.felder_matrix[0])):
            if all(row[col].isChecked() for row in self.felder_matrix):
                bingo = True
                break 
    
        if bingo:
            return True
        else:
            return False
        
    def start(self):
        self.root.mainloop()

# Datei (wordfile.txt) öffnen und einlesen der Zeilen in einer liste
def open_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        logging.info(f"Datei {filename} geöffnet und gelesen") 
        return file.read().splitlines()

def server_process(pipe_name, pos, size):
    """
    Server-Prozess zur Verwaltung des Spiels und der Bingo-Karte des Servers
    
    pipe_name: Name der benannten Pipe zur Kommunikation
    pos: Position des Fensters
    size: Größe des Fensters
    felder_Anzahl: Anzahl der Felder (NxN)
    words: Liste der Wörter für die Bingo-Karte
    """
    print("Das Bingospiel wurde gestartet.")
    
    # Erstellen der benannten Pipe (wenn sie nicht schon existiert)
    if not os.path.exists(pipe_name):
        # Erstellen mit First In First Out
        os.mkfifo(pipe_name)
    
    # Spieler in einer Liste speichern
    clients = []
    
    # Benannte Pipe im read()-Modus öffnen
    while True:
        with open(pipe_name, 'r') as pipe:
            # Jede Zeile wird einzeln gelesen - daher "\n" wichtig
            message = pipe.readline().strip() 
            if message:
                print(message)
                logging.info(message)
                if "ist beigetreten" in message:
                    client_name = message.split()[0]
                    clients.append(client_name)
                elif "Kein Gewinner" in message:
                    break
                elif "hat gewonnen" in message:
                    for client in clients:
                        if client not in message:
                            with open(pipe_name, 'w') as pipe:
                                pipe.write(f"{client}, Du hast verloren!\n")
                                pipe.flush()
                                
                    break

    print("Das Spiel ist beendet.")
    
def client_process(name, pipe_name, pos, size, felder_Anzahl, words):
    """
    Client-Prozess zur Erstellung eines Spielers und dessen Bingo-Karte.
    
    name: Name des Spielers
    pipe_name: Name der benannten Pipe zur Kommunikation
    pos: Position des Fensters
    size: Größe des Fensters
    felder_Anzahl: Anzahl der Felder (NxN)
    words: Liste der Wörter für die Bingo-Karte
    """
    spieler = Spieler(name, pipe_name, pos, size)
    spieler.create_bingo_card(felder_Anzahl, words)
    
    # Öffnen der Pipe zum Senden der Beitrittsnachricht (write-Modus)
    with open(pipe_name, 'w') as pipe:
        pipe.write(f"{name} ist beigetreten.\n")
        print(name + " ist beigetreten.")
        pipe.flush()
    
    # Lesen der Nachrichten in der Pipe
    def lese_pipe():
        with open(pipe_name, 'r') as pipe:
            message = pipe.readline().strip()
            if message:
                # Überprüfen, ob ein Gewinner gemeldet wurde und ob es nicht der aktuelle Spieler ist
                if "hat gewonnen" in message and name not in message:
                    # Setze den Check-Zustand der Buttons auf False
                    TTkButton._checkable = False
                    # Zeige eine Nachricht über die Niederlage des Spielers an
                    spieler.zeige_verloren_nachricht()
                    # Logge das Ende des Spiels
                    spieler.logger.info("Ende des Spiels")
                    
    # Thread-Funktion, um regelmäßig die Pipe auf Nachrichten zu überprüfen.
    def timer_thread():
        while True:
            lese_pipe()
            time.sleep(1)
    
    # Starte den Thread als Daemon       
    threading.Thread(target=timer_thread, daemon=True).start() 
    
    # Starte die Hauptfenster-Schleife      
    spieler.root.mainloop()
  
# Hauptfunktion, die die Kommandozeilenargumente verarbeitet und die Bingo-Karte erstellt    
def main():
    # Kommandozeilenargumente mit dem argparse-Modul hinzufügen
    parser = argparse.ArgumentParser(description="Erstellen einer Bingo-Karte.")
    # Definiert das Kommandozeilenargument 'filename' (Dateiname)
    parser.add_argument("wordfile", nargs='?', help='Der Name der zu öffnenden Datei') 
    # Definiert das Kommandozeilenargument 'felder_Anzahl' (Anzahl der Felder auf der Bingo-Karte)
    parser.add_argument("felder_Anzahl", type=int, help="Die Anzahl der Felder der Bingo-Karte.")
    # Server wird gestartet, um die Kommunikation zwischen den Prozessen zu gewährleisten
    parser.add_argument("--server", action='store_true', help="Starte als Server") 
    # Hiermit wird jeder Spieler (Client) - Prozess gestartet
    parser.add_argument("--name", type=str, help="Name des Spielers") 
    # Parst die Kommandozeilenargumente und speichert sie in 'args'
    args = parser.parse_args()

    # Weist die Argumente 'filename' und 'felder_Anzahl' den entsprechenden Variablen zu
    filename = args.wordfile
    felder_Anzahl = args.felder_Anzahl
    
    # Name der Pipe festlegen
    pipe_name = "/tmp/bingo_pipe"

    # Überprüft, ob die angegebene Datei existiert
    if os.path.exists(filename):
        # Wenn sie existiert, wird sie geöffnet
        words = open_file(filename)
        
        if args.server:
            # Startet den Server-Prozess wenn --server eingegeben wird
            server_process(pipe_name, (0, 0), (50, 20))
        else:
            # Startet den Client-Prozess wenn --name eingegeben wird
            if args.name:
                name = args.name
            else:
                # Falls kein Name beim Starten des Prozesses eingegeben wurde
                name = input("Geben Sie Ihren Namen ein:")
            
            client_process(name, pipe_name, (0, 0), (50, 20), felder_Anzahl, words)
        
    else:
        # Wenn die Datei nicht existiert, wird eine Fehlermeldung ausgegeben
        logging.error(f"Die Datei {filename} existiert nicht.")
        print(f"Die Datei {filename} existiert nicht.")
        return
        
if __name__ == "__main__":
    main()


