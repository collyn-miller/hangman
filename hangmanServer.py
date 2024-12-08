import socket
import argparse
import json
import threading
import random

MAX_PLAYERS = 2
TARGET_SCORE = 20

game_state = {
    "players": [],
    "turn": 0,
    "lives": 6,
    "letters": [],
    "display": ""
}
players = []

lock = threading.Lock()  # To ensure thread-safe operations

def broadcast(message):
    for player in players:
        player.sendall(message)

def hmServer():

    #parsing input flags
    parser = argparse.ArgumentParser()

    parser.add_argument("-p", "--portNumber")
    args = parser.parse_args()

    host = socket.gethostname()
    port = int(args.portNumber)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    server_socket.bind((host, port)) 

    while True:
        word = str(input(f"Welcome to Hangman! Please input a word between 3 and 10 characters for the players to guess.\n"))
        if word.isalpha() and len(word) >= 3 and len(word) <=10:
            break
        else:
            print(f"Please enter another word. Either you used a non alphabet character or input the wrong length.")

    blank = "_"
    for i in range(len(word)):
        game_state["display"] += blank

    #print(game_state["display"])
    server_socket.listen(2)
    print(f"Server started. Waiting for {MAX_PLAYERS} players...")

    for i in range(1,(MAX_PLAYERS+1)):
        conn, addr = server_socket.accept()
        player_id = i
        game_state["players"].append(player_id)
        players.append(conn)
        threading.Thread(target=gameClient, args=(conn, addr, player_id, word)).start()
    
    game_state["turn"] = 1
    broadcast(json.dumps({"game_state": game_state}).encode())

        

    

def gameClient(conn, addr, player_id, word):
    print(f"Player {player_id} connected from {addr}")
    conn.sendall(json.dumps({"id": player_id,"message": f"Welcome Player {player_id}! Once all players have joined, the game will begin.", "game_state": game_state}).encode())
    running = True

    try:
        while running:
            data = conn.recv(1024)
            if not data:
                print(f"Player {player_id} disconnected")
                break

            
            request = json.loads(data.decode())
            if "gameOver" in request:
                break

            if game_state["turn"] == player_id:
                lock.acquire()
                broadcast(json.dumps({"message":game_state["display"]}).encode())
                letter = request.get("letter")
                count = word.count(letter)
                if count == 0:
                    game_state["lives"] = game_state["lives"] - 1
                    message =f"Player {player_id} guessed {letter}. Unfortunately, there is no {letter} in the word. -1 lives."
                    broadcast(json.dumps({"message":message}).encode())

                elif count == 1:
                    position = word.find(letter)
                    message =f"Player {player_id} guessed {letter}. There is a {letter} at position {position}!"
                    broadcast(json.dumps({"message":message}).encode())
                    game_state["display"][position] = letter
                
                else:
                    for i in range(len(word)):
                        if word[i] == letter:
                            game_state["display"][i] = letter
                    message =f"Player {player_id} guessed {letter}. There are multiple {letter}'s!"
                    broadcast(json.dumps({"message":message}).encode())



                    # Check for game end condition
                if game_state["display"].count("_") == 0:
                    message = f"Players win! The word was {word}, and you had {game_state['lives']} remaining."
                    print(message)
                    broadcast(json.dumps({"message":message}).encode())
                    broadcast(json.dumps({"gameOver":"over"}).encode())
                    lock.release()
                    break
                elif game_state["lives"] == 0:
                    message = f"Players lose! The word was {word}, better luck next time."
                    print(message)
                    broadcast(json.dumps({"message":message}).encode())
                    broadcast(json.dumps({"gameOver":"over"}).encode())
                    lock.release()
                    break



                # Switch turn
                game_state["turn"] = (game_state["turn"] + 1)
                if game_state["turn"] > MAX_PLAYERS:
                    game_state["turn"] = 1
                lock.release()
                broadcast(json.dumps({"game_state": game_state}).encode())

                         
    finally:
        conn.close()
    
      

if __name__ == '__main__':
    hmServer()