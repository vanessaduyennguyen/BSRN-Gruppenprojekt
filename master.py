import multiprocessing
import random
import time

buzzwords = [
    "Synergie", "Blockchain", "Big Data", "KI", "IoT", "Machine Learning",
    "Cloud", "Agil", "Disruptiv", "5G", "DevOps", "Künstliche Intelligenz",
    "Microservices", "Deep Learning", "Cybersecurity"
]

def draw_buzzwords(queue, num_buzzwords):
    drawn_words = random.sample(buzzwords, num_buzzwords)
    for word in drawn_words:
        print(f'Gezogenes Buzzword: {word}')
        queue.put(word)
        time.sleep(1)  # Wartezeit simuliert das Ziehen der Buzzwords

if __name__ == "__main__":
    queue = multiprocessing.Queue()
    num_buzzwords = 10

    # Start drawing process
    drawing_process = multiprocessing.Process(target=draw_buzzwords, args=(queue, num_buzzwords))
    drawing_process.start()
    drawing_process.join()  # Wait for the drawing process to finish