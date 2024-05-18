def Spieler():
    name=str(input("bitte geben Sie ihren Namen ein"))
    alter=int(input("Bitte geben Sie ihr alter ein"))
    runde=1
   # Spielfeld=randomspielfeld()

#ob es ein bingo ist
    def bingo(bingoKarte):
        #bingo in der zeile
        for row in bingoKarte:
            if all(cell=="X" for cell in row):
                return True
            
            #bingo in der reihe
        for col in range(len(bingoKarte[0])):
            if all(row[col]=="X" for row in bingoKarte):
                return True
            
            #diagonal bingo oben links unten rechts
        if all(bingoKarte[i][i]=="X" for i in range(len(bingoKarte))):
            return True
            #diagonal bingo oben rechts unten links 
        if all(bingoKarte[i][len(bingoKarte)-1-i]=="X" for i in range(len(bingoKarte))):
            return True

        return False        
        

Spieler()
        
        
