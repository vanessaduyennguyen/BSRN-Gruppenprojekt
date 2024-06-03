import multiprocessing
import random

buzzwords = [
    "Synergie", "Blockchain", "Big Data", "KI", "IoT", "Machine Learning",
    "Cloud", "Agil", "Disruptiv", "5G", "DevOps", "Künstliche Intelligenz",
    "Microservices", "Deep Learning", "Cybersecurity"
]

def generate_bingo_card():
    return random.sample(buzzwords, 5)

def check_bingo(card, drawn_words):
    return set(card).issubset(set(drawn_words))

def player_process(queue):
    card = generate_bingo_card()
    print(f'Spieler-Bingokarte: {card}')
    drawn_words = []

    while True:
        word = queue.get()
        if word:
            drawn_words.append(word)
            print(f'Spieler empfängt: {word}')
            if check_bingo(card, drawn_words):
                print('Bingo! Spieler hat gewonnen!')
                break

if __name__ == "__main__":
    queue = multiprocessing.Queue()
    player_process(queue)

    # Start player processes
    #players = [multiprocessing.Process(target=player_process, args=(queue,)) for _ in range(2)]
    #for player in players:
     #   player.start()

    # Start drawing process
     #   draw_buzzwords(queue, 10)

   # for player in players:
   #     player.join()  # Wait for the player processes to finish