# Gruppenmitglieder:
# Ioana-Carmen Moldovan (1514892), Vanessa Nguyen (1513741), Pantea Dolatabadian (1414653), Aliia Nurbekova (1526039), Thi Song Thu Pham (1413382) 

import TermTk as ttk
import argparse
import os
import sys
import random
import logging
import threading
import time
from datetime import datetime
from TermTk.TTkWidgets.button import TTkButton
from TermTk.TTkWidgets.resizableframe import TTkResizableFrame

# Spielerklasse erstellen
class Spieler:
    def __init__(self, name, pipe_name, pos, size=(50, 20)):
        """
        Initialisiert die Spielerklasse mit Name, Pipe, Position und Größe des Fensters.
        
        name: Name des Spielers
        pipe_name: Name der benannten Pipe zur Kommunikation
        pos: Position des Fensters
        size: Größe des Fensters
        """
        try:
            # Initialisiere Spieler-Attribute
            self.name = name
            self.pipe_name = pipe_name
            self.root = ttk.TTk()
            self.bingoFenster = ttk.TTkWindow(parent=self.root, pos=pos, size=size, title=name, resizable=True)
            self.winLayout = ttk.TTkGridLayout()
            self.bingoFenster.setLayout(self.winLayout)
            self.felder_matrix = []
            self.has_won = False
            
            # Logdatei einrichten
            timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            log_filename = f"{timestamp}-bingo-{self.name}.txt"
            self.logger = logging.getLogger(name)
            
            # Handler für Datei-Logging
            handler = logging.FileHandler(log_filename)
            formatter = logging.Formatter('%(asctime)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.DEBUG)
            
            # Entferne den Standard-StreamHandler, falls vorhanden, 
            # damit es nicht in der Konsole ausgegeben wird
            for handler in logging.root.handlers[:]:
                if isinstance(handler, logging.StreamHandler):
                    logging.root.removeHandler(handler)

            # Start logging
            self.logger.info("Start des Spiels")
            
        except ImportError as e:
            #Fehler beim Importieren des Moduls TermTK ob es existiert
            print(f"ImportError: {e}")
            sys.exit(1)
        except Exception as e:
            #Allgemeiner Fehler
            print(f"Fehler beim Initialisieren des Spielers: {e}")
            sys.exit(1)

    def create_bingo_card(self, felder_Anzahl, words):
        """
        Erstellt die Bingo-Karte mit der angegebenen Anzahl von Feldern und Wörtern
        
        felder_Anzahl: Anzahl der Felder (NxN)
        words: Liste der Wörter für die Bingo-Karte
        """
        try:
            #Eine 2D-Liste (Matrix von den Bingofeldern) wird zur Überprüfung, ob es ein Bingo gibt, erstellt.
            self.felder_Anzahl = felder_Anzahl
            self.logger.info(f"Größe des Spielfelds: {felder_Anzahl} x {felder_Anzahl}")
            self.felder_matrix = []
            for x in range(felder_Anzahl):
                # Es wird eine Reihe der Matrix erstellt
                rows = []
                for y in range(felder_Anzahl):
                    word = random.choice(words)
                    words.remove(word)
                    feld = TTkButton(border=True, text=word, checked=False, checkable=True)
                    # Verbindung der Methode pruefe_Ob_Bingo mit dem Klickereignis des Feldes
                    feld.clicked.connect(self.pruefe_Ob_Bingo)
                    feld.clicked.connect(self.on_button_clicked_wrapper(feld, word, x, y))
                    # Feld zum Layout hinzufügen
                    self.winLayout.addWidget(feld, x, y)
                    # Zu der Reihe der Matrix werden bei jedem Durchlauf der Schleife TTkButton-Objekte hinzugefügt (insgesamt felder_Anzahl-Objekte).
                    rows.append(feld)

                    if felder_Anzahl % 2 != 0 and x == (felder_Anzahl // 2) and y == (felder_Anzahl // 2):
                        # Jokerfeld erstellen
                        feld = self.JOKER_ausfüllen(feld)
                        # Der Index von dem altem Feld (der zuletzt genutzte Index) wird durch das neue Feld (mit den "neuen Attributen") ersetzt.
                        last_index = len(rows) - 1
                        rows[last_index] = feld

                # Die "fertige" Reihe wird nun der Matrix hinzugefügt
                # Bei erneuten Durchlauf der Schleife wird wieder eine neue Reihe erstellt, hinzugefügt, etc....
                self.felder_matrix.append(rows)

            # Bingo- und Spiel Beenden-Buttons hinzufügen
            self.bingo_button = TTkButton(text="Bingo", parent=self.bingoFenster, border=True)
            self.bingo_button.clicked.connect(self.bingo_check)
            self.winLayout.addWidget(self.bingo_button, felder_Anzahl, 0, 1, felder_Anzahl)

            self.exit_button = TTkButton(text="Spiel beenden", parent=self.bingoFenster, border=True)
            self.exit_button.clicked.connect(self.spiel_beenden)
            self.winLayout.addWidget(self.exit_button, felder_Anzahl + 1, 0, 1, felder_Anzahl)

            return self.felder_matrix
        
        except IndexError as e:
            # Fehler bei der Indexierung
            print(f"IndexError: {e}")
        except TypeError as e:
            # Typfehler
            print(f"TypeError: {e}")
        except Exception as e:
            # Allgemeiner Fehler
            print(f"Fehler beim Erstellen der Bingo-Karte: {e}")
    
    # Methode wird aufgerufen, wenn ein Feld angeklickt wird
    def on_button_clicked(self, button, word, x, y):
        if not self.has_won and not button.isChecked():
            # Status: Button ist angeklickt
            button.setChecked(True)
     
    # Wrapper-Methode für das Klickereignis eines Feldes
    def on_button_clicked_wrapper(self, button, word, x, y):
        def wrapper():
            self.on_button_clicked(button, word, x, y)
        return wrapper
    
    # Ancklicken eines Wortes in die Logdatei schreiben
    def on_button_clicked(self, button, word, x, y):
        if not self.has_won and button.isChecked():
            self.logger.info(f"{word} ({x}/{y})")

    @staticmethod
    def JOKER_ausfüllen(feld):
        # Die Methode soll das Feld in der Mitte ersetzen und automatisch markieren.
        # Das Feld mit den neuen Eigenschaften wird zurückgegeben.
        feld.setText("JOKER")
        feld.setChecked(True)
        return feld

    def zeige_gewonnen_nachricht(self):
        # Erstellen eines neuen Fensters, um die Gewinnnachricht anzuzeigen
        gewonnenFenster = ttk.TTkWindow(parent=self.root, title=" Bingo!", size=(30, 5))
        # Positioniere das Fenster in der oberen rechten Ecke des Terminals
        terminal_width = self.root.width()
        gewonnenFenster.move(terminal_width - 50, 0)
        gewonnenLayout = ttk.TTkLayout()
        gewonnenFenster.setLayout(gewonnenLayout)
        gewonnenLabel = ttk.TTkLabel(text=f"{self.name}, du hast gewonnen!!!")
        gewonnenLayout.addWidget(gewonnenLabel)
        gewonnenFenster.show()
        self.logger.info(f"Sieg")

    def zeige_verloren_nachricht(self):
        # Erstellen eines neuen Fensters, um die Verliernachricht anzuzeigen
        verlorenFenster = ttk.TTkWindow(parent=self.root, title=" Bingo! ", size=(30, 5))
        # Positioniere das Fenster in der oberen rechten Ecke des Terminals
        terminal_width = self.root.width()
        verlorenFenster.move(terminal_width - 50, 0)
        verlorenLayout = ttk.TTkLayout()
        verlorenFenster.setLayout(verlorenLayout)
        verlorenLabel = ttk.TTkLabel(text=f"{self.name}, du hast verloren :(")
        verlorenLayout.addWidget(verlorenLabel)
        verlorenFenster.show()
        self.logger.info(f"Verloren ")

    # Methode zum Beenden des Spiels und Schreiben einer Nachricht in die Pipe
    def spiel_beenden(self):
        # Beendet das Spiel
        message = f"Kein Gewinner"
        logging.info(message)
        self.lock_bingo_card()
        # Benannte Pipe im write()-Modus öffnen
        with open(self.pipe_name, 'w') as pipe:
            pipe.write(message + "\n")
            pipe.flush()

    # Überprüft, ob ein Bingo vorliegt und führt entsprechende Aktionen aus
    def bingo_check(self):
        # Überprüft, ob ein Bingo vorliegt
        if self.pruefe_Ob_Bingo():
            TTkButton._checkable = False
            self.exit_button._checkable = False
            self.has_won = True
            self.zeige_gewonnen_nachricht()
            message = f"{self.name} hat gewonnen!!"
            logging.info(message)
            self.logger.info(f"Ende des Spiels")
            self.lock_bingo_card()
            
            with open(self.pipe_name, 'w') as pipe:
                pipe.write(message + "\n")
                pipe.flush()

    def pruefe_Ob_Bingo(self):
        # Überprüft, ob es ein Bingo gibt
        bingo = False
        
        # Diagonale
        if all(self.felder_matrix[i][i].isChecked() for i in range(len(self.felder_matrix))):
            bingo = True

        # Diagonale 
        if all(self.felder_matrix[i][len(self.felder_matrix) - 1 - i].isChecked() for i in range(len(self.felder_matrix))):
            bingo = True

        # Reihe
        for row in self.felder_matrix:
            if all(feld.isChecked() for feld in row):
                bingo = True
                break
        
        # Spalte
        for col in range(len(self.felder_matrix[0])):
            if all(row[col].isChecked() for row in self.felder_matrix):
                bingo = True
                break

        return bingo

    def start(self):
        # Startet das Spiel in der pyTermTk-Mainloop
        self.root.mainloop()

    def lock_bingo_card(self):
        # Felder können nicht mehr angeklickt werden
        for row in self.felder_matrix:
            for button in row:
                button.setDisabled()
        self.bingo_button.setDisabled()
        self.exit_button.setDisabled()

def open_file(filename):
    # Datei öffnen und einlesen der Zeilen in einer Liste
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            logging.info(f"Datei {filename} geöffnet und gelesen")
            return file.read().splitlines()
    except FileNotFoundError as e:
        print(f"FileNotFoundError: {e}")
        sys.exit(1)
    except PermissionError as e:
        print(f"PermissionError: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Fehler beim Öffnen der Datei: {e}")
        sys.exit(1)

def server_process(pipe_name, pos, size):
    """
    Server-Prozess zur Verwaltung des Spiels und der Bingo-Karte des Servers
    
    pipe_name: Name der benannten Pipe zur Kommunikation
    pos: Position des Fensters
    size: Größe des Fensters
    """
    print("Das Bingospiel wurde gestartet.")

    if not os.path.exists(pipe_name):
        # Erstellen mit First in First Out
        os.mkfifo(pipe_name)

    # Spieler in einer Liste speichern
    clients = []
    
     # Benannte Pipe im read()-Modus öffnen
    while True:
        try:
            with open(pipe_name, 'r') as pipe:
                while True:
                    message = pipe.readline().strip()
                    if message:
                        logging.info(f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')} Nachricht empfangen: {message}")
                        print(f"{message}")
                        if "ist beigetreten" in message:
                            client_name = message.split()[0]
                            clients.append(client_name)
                        elif "Kein Gewinner" in message:
                            broadcast_message(clients, message)
                            break
                        elif "hat gewonnen" in message:
                            broadcast_message(clients, message)
                            break
        except Exception as e:
            logging.error(f"Error reading from pipe: {e}")


# Für jeden Client wird eine Pipe erstellt
def broadcast_message(clients, message):
    for client in clients:
        client_pipe_name = f"/tmp/{client}_pipe"
        if not os.path.exists(client_pipe_name):
            os.mkfifo(client_pipe_name)
        with open(client_pipe_name, 'w') as pipe:
            pipe.write(f"{message}\n")
            pipe.flush()

    print("Das Spiel ist beendet.")
    sys.exit()

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
    
    try:
        # Ein Spieler wird erstellt
        spieler = Spieler(name, pipe_name, pos, size)
        # Die Bingo-Karte des Spielers wird erstellt
        spieler.create_bingo_card(felder_Anzahl, words)

        # Die Beitrittsnachricht wird in die Pipe geschrieben
        with open(pipe_name, 'w') as pipe:
            pipe.write(f"{name} ist beigetreten.\n")
            print(name + " ist beigetreten.")
            pipe.flush()

        # Funktion zum Lesen von Nachrichten aus der Pipe
        def lese_pipe():
            # Die Pipe wird nach dem jeweiligen Client benannt
            client_pipe_name = f"/tmp/{name}_pipe"
            # Falls sie nicht existiert, wird sie hiermit erstellt:
            if not os.path.exists(client_pipe_name):
                os.mkfifo(client_pipe_name)
                
            # Die Pipe wird im read()-Modus erstellt und wartet auf Nachrichten
            with open(client_pipe_name, 'r') as pipe:
                message = pipe.readline().strip()
                if message:
                    if "hat gewonnen" in message and name not in message:
                        spieler.zeige_verloren_nachricht()
                        spieler.logger.info(f"Ende des Spiels")
                        spieler.lock_bingo_card()
                    elif "Kein Gewinner" in message:
                        spieler.lock_bingo_card()
                        spieler.logger.info(f"Ende des Spiels")
        
        # Thread, um die lese_pipe-Funktion asynchron auszuführen
        threading.Thread(target=lese_pipe, daemon=True).start()
        
        # Die mainloop von pyTermTk wird aufgerufen, um die Ereignisse dort zu verzeichnen bspw. das Markieren von Feldern
        spieler.root.mainloop()
        
    except Exception as e:
        print(f"Fehler im Client-Prozess: {e}")
        sys.exit(1)

# Hauptfunktion, die die Kommandozeilenargumente verarbeitet und Prozesse erstellt

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

    try:
        args = parser.parse_args()
    except argparse.ArgumentError as e:
        # Fehler beim Verarbeiten der Argumente
        print(f"Fehler beim Verarbeiten der Argumente: {e}")
        parser.print_help()
        sys.exit(1)
    except argparse.ArgumentTypeError as e:
        # Typfehler bei den Argumenten, wenn felder_Anzahl keine gültige Ganzzahl ist
        print(f"argparse.ArgumentTypeError: {e}")
        print("Ursache: Das Argument felder_Anzahl ist keine gültige Ganzzahl.")
        sys.exit(1)
    except Exception as e:
        # Allgemeiner Fehler
        print(f"Allgemeiner Fehler: {e}")
        sys.exit(1)

    filename = args.wordfile
    felder_Anzahl = args.felder_Anzahl

    if not filename:
        parser.error("Bitte geben Sie den Dateinamen der Wortliste an.")

    if felder_Anzahl <= 0:
        parser.error("Die Anzahl der Felder muss größer als Null sein.")

    pipe_name = "/tmp/bingo_pipe"

    if os.path.exists(filename):
        # Wenn die Datei existiert, wird sie geöffnet
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
        sys.exit(1)

if __name__ == "__main__":
    main()
    logging.info("Bingo Programm gestartet.")
    logging.info("Bingo Programm beendet.")