import argparse # für Kommandozeilenargumente
import os # Interaktion mit Betriebssystem
    
# Funktion zum Öffnen der Textdatei
def open_file(filename):
    with open(filename, 'r') as file: # im Lesemodus 
        print(file.read()) # ausgeben -> wird später geändert

# Überprüfung ob Skript direkt ausgeführt wird
if __name__ == "__main__": 
    # Erstellen von parser für Kommandozeilenbefehle
    parser = argparse.ArgumentParser(prog="textdateibefehl.py", add_help=False)
    # Argument definieren für Dateiname
    parser.add_argument('wordfile', nargs='?', help='Der Name der zu öffnenden Datei')

    # Methode, um Argument zurückzugeben
    args = parser.parse_args()
    
    # Aufforderung, um den Namen der Datei einzugeben nur wenn es nicht direkt eingegeben wurde
    if args.wordfile is None:
        filename = input("Geben Sie den Namen der Textdatei ein:")
    else:
        filename = args.wordfile
        
    # Wenn die Textdatei mit diesem Namen existiert, wird diese geöffnet
    if os.path.exists(filename):  
        open_file(filename)
    else:
        print(f"Die Datei {filename} existiert nicht.")