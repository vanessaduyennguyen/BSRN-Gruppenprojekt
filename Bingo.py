import TermTk as ttk
import argparse
import os
import sys
import random
import asyncio
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
            handler = logging.FileHandler(log_filename)
            formatter = logging.Formatter('%(asctime)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.DEBUG)
            # Start logging
            self.logger.info(f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')} Start des Spiels")
            self.logger.info(f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')} Größe des Spielfelds: {size}")

        except ImportError as e:
            # Fehler beim Importieren des Moduls
            print(f"ImportError: {e}")
            sys.exit(1)
        except Exception as e:
            # Allgemeiner Fehler
            print(f"Fehler beim Initialisieren des Spielers: {e}")
            sys.exit(1)

    def create_bingo_card(self, felder_Anzahl, words):
        """
        Erstellt die Bingo-Karte mit der angegebenen Anzahl von Feldern und Wörtern
        
        felder_Anzahl: Anzahl der Felder (NxN)
        words: Liste der Wörter für die Bingo-Karte
        """
        try:
            # Eine 2D-Liste (Matrix von den Bingofeldern) wird zur Überprüfung, ob es ein Bingo gibt, erstellt.
            self.felder_Anzahl = felder_Anzahl
            self.logger.info(f"Größe des Spielfelds: {felder_Anzahl} / {felder_Anzahl}")
            self.felder_matrix = []
            for x in range(felder_Anzahl):
                # Es wird eine Reihe der Matrix erstellt
                rows = []
                for y in range(felder_Anzahl):
                    word = random.choice(words)
                    words.remove(word)
                    feld = TTkButton(border=True, text=word, checked=False, checkable=True)
                    feld.clicked.connect(self.pruefe_Ob_Bingo)
                    feld.clicked.connect(self.on_button_clicked_wrapper(feld, word, x, y))
                    self.winLayout.addWidget(feld, x, y)
                    # Zu der Reihe der Matrix werden bei jedem Durchlauf der Schleife TTkButton-Objekte hinzugefügt (insgesamt felder_Anzahl-Objekte).
                    rows.append(feld)

                    if felder_Anzahl % 2 != 0 and x == (felder_Anzahl // 2) and y == (felder_Anzahl // 2):
                        feld = self.JOKER_ausfüllen(feld)
                        # Der Index von dem altem Feld (der zuletzt genutzte Index) wird durch das neue Feld (mit den "neuen Attributen") ersetzt.
                        last_index = len(rows) - 1
                        rows[last_index] = feld

                # Die "fertige" Reihe wird nun der Matrix hinzugefügt
                # Bei erneuten Durchlauf der Schleife wird wieder eine neue Reihe erstellt, hinzugefügt, etc....
                self.felder_matrix.append(rows)

            # Bingo- und Beenden-Buttons hinzufügen
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

    def on_button_clicked_wrapper(self, button, word, x, y):
        def wrapper():
            self.on_button_clicked(button, word, x, y)
        return wrapper

    def on_button_clicked(self, button, word, x, y):
        if not self.has_won and not button.isChecked():
            button.setChecked(True)
            self.logger.info(f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')} {word} ({x}/{y})")

    @staticmethod
    def JOKER_ausfüllen(feld):
        # Die Methode soll das Feld in der Mitte ersetzen und automatisch markieren.
        # Das Feld mit den neuen Eigenschaften wird zurückgegeben.
        feld.setText("JOKER")
        feld.setChecked(True)
        return feld

    def zeige_gewonnen_nachricht(self):
        # Erstellen eines neuen Fensters, um die Gewinnnachricht anzuzeigen
        gewonnenFenster = ttk.TTkWindow(parent=self.root, title="Bingo!", size=(30, 5))
        # Positioniere das Fenster in der oberen rechten Ecke des Terminals
        terminal_width = self.root.width()
        gewonnenFenster.move(terminal_width - 50, 0)
        gewonnenLayout = ttk.TTkLayout()
        gewonnenFenster.setLayout(gewonnenLayout)
        gewonnenLabel = ttk.TTkLabel(text=f"{self.name} hat gewonnen!!!")
        gewonnenLayout.addWidget(gewonnenLabel)
        gewonnenFenster.show()
        self.logger.info(f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')} Sieg")
        print("Du hast gewonnen!!!")

    def zeige_verloren_nachricht(self):
        # Erstellen eines neuen Fensters, um die Verliernachricht anzuzeigen
        verlorenFenster = ttk.TTkWindow(parent=self.root, title="Verloren", size=(30, 5))
        # Positioniere das Fenster in der oberen rechten Ecke des Terminals
        terminal_width = self.root.width()
        verlorenFenster.move(terminal_width - 50, 0)
        verlorenLayout = ttk.TTkLayout()
        verlorenFenster.setLayout(verlorenLayout)
        verlorenLabel = ttk.TTkLabel(text=f"{self.name} hat verloren :(")
        verlorenLayout.addWidget(verlorenLabel)
        verlorenFenster.show()
        self.logger.info(f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')} Verloren")
        print("Du hast verloren :(")

    # Methode zum Beenden des Spiels und Schreiben einer Nachricht in die Pipe
    def spiel_beenden(self):
        # Beendet das Spiel
        message = f"Kein Gewinner"
        logging.info(message)
        self.logger.info(f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')} Ende des Spiels")
        self.lock_bingo_card()
        # self.root.quit()
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
            self.exit_button.setDisabled()
            self.bingo_button.setDisabled()
            self.has_won = True
            self.zeige_gewonnen_nachricht()
            message = f"{self.name} hat gewonnen!!!"
            logging.info(message)
            self.logger.info(f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')} Ende des Spiels")
            self.lock_bingo_card()
            with open(self.pipe_name, 'w') as pipe:
                pipe.write(message + "\n")
                pipe.flush()

    def pruefe_Ob_Bingo(self):
        # Überprüft, ob es ein Bingo gibt
        bingo = False
        if all(self.felder_matrix[i][i].isChecked() for i in range(len(self.felder_matrix))):
            bingo = True

        if all(self.felder_matrix[i][len(self.felder_matrix) - 1 - i].isChecked() for i in range(len(self.felder_matrix))):
            bingo = True

        for row in self.felder_matrix:
            if all(feld.isChecked() for feld in row):
                bingo = True
                break

        for col in range(len(self.felder_matrix[0])):
            if all(row[col].isChecked() for row in self.felder_matrix):
                bingo = True
                break

        return bingo

    def start(self):
        # Startet das Spiel
        self.root.mainloop()

    def lock_bingo_card(self):
        # Disable all buttons on the bingo card
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

    
clients = []
async def server_process(pipe_name, pos, size):
    print("Das Bingospiel wurde gestartet.")
    if not os.path.exists(pipe_name):
        os.mkfifo(pipe_name)
    await read_pipe(pipe_name)
    
async def read_pipe(pipe_name):
    while True:
        try:
            with open(pipe_name, 'r') as pipe:
                while True:
                    message = pipe.readline().strip()
                    if message:
                        logging.info(f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')} Nachricht empfangen: {message}")
                        print(f"Nachricht empfangen: {message}")
                        if "ist beigetreten" in message:
                            client_name = message.split()[0]
                            clients.append(client_name)
                        elif "Kein Gewinner" in message:
                            broadcast_message(clients,pipe_name, message)
                            break
                        elif "hat gewonnen" in message:
                            broadcast_message(clients,pipe_name, message)
                            break
                    await asyncio.sleep(0.1)
        except Exception as e:
            logging.error(f"Error reading from pipe: {e}")
        await asyncio.sleep(1)

def broadcast_message(clients,pipe_name, message):
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
    try:
        spieler = Spieler(name, pipe_name, pos, size)
        spieler.create_bingo_card(felder_Anzahl, words)

        with open(pipe_name, 'w') as pipe:
            pipe.write(f"{name} ist beigetreten.\n")
            print(name + " ist beigetreten.")
            pipe.flush()

        def lese_pipe():
            client_pipe_name = f"/tmp/{name}_pipe"
            if not os.path.exists(client_pipe_name):
                os.mkfifo(client_pipe_name)
            with open(client_pipe_name, 'r') as pipe:
                message = pipe.readline().strip()
                if message:
                    if "hat gewonnen" in message and name not in message:
                        spieler.zeige_verloren_nachricht()
                        spieler.logger.info(f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')} Ende des Spiels")
                        spieler.lock_bingo_card()
                    elif "Kein Gewinner" in message:
                        spieler.lock_bingo_card()
                        spieler.logger.info(f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')} Ende des Spiels")


        threading.Thread(target=lese_pipe, daemon=True).start()
        spieler.root.mainloop()
    except Exception as e:
        print(f"Fehler im Client-Prozess: {e}")
        sys.exit(1)

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
    filename = args.wordfile
    felder_Anzahl = args.felder_Anzahl

    if not filename:
        parser.error("Bitte geben Sie den Dateinamen der Wortliste an.")

    if felder_Anzahl <= 0:
        parser.error("Die Anzahl der Felder muss größer als Null sein.")

    pipe_name = "/tmp/bingo_pipe"

    if os.path.exists(filename):
        words = open_file(filename)

        if args.server:
            asyncio.run(server_process(pipe_name, (0, 0), (50, 20)))
        else:
            if args.name:
                name = args.name
            else:
                name = input("Geben Sie Ihren Namen ein:")

            client_process(name, pipe_name, (0, 0), (50, 20), felder_Anzahl, words)
    else:
        logging.error(f"Die Datei {filename} existiert nicht.")
        print(f"Die Datei {filename} existiert nicht.")
        sys.exit(1)

if __name__ == "__main__":
    main()
    logging.info("Bingo Programm gestartet.")
    logging.info("Bingo Programm beendet.")