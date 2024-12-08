#Author: Collyn Miller
#for use with hangmanClient.py

import socket
import argparse
import json
import threading

#game state will hold the state information between the client and server threads
game_state = {
    "players": [],
    "turn": 0,
    "lives": 6,
    "letters": [],
    "display": ""
}

players = []

lock = threading.Lock()  # To enable turn taking

#enables us to send updates for all players to see
def broadcast(message):
    for player in players:
        player.sendall(message)

def hmServer():

    #parsing input flags
    parser = argparse.ArgumentParser()

    parser.add_argument("-p", "--portNumber", help="Desired port number to use.")
    parser.add_argument("-n", "--numPlayers", help="Desired number of client players.")
    args = parser.parse_args()

    host = "0.0.0.0"
    port = int(args.portNumber)

    #defaults to 2 players, can set higher with -n flag
    max_players = 2
    if args.numPlayers is not None:
        max_players = int(args.numPlayers)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    server_socket.bind((host, port)) 

    while True:
        word = str(input(f"Welcome to Hangman! Please input a word between 3 and 10 characters for the players to guess.\n"))
        if word.isalpha() and len(word) >= 3 and len(word) <=10:
            break
        else:
            print(f"Please enter another word. Either you used a non alphabet character or input the wrong length.")

    #constructs the initial blank display
    blank = "_"
    for i in range(len(word)):
        game_state["display"] += blank

    server_socket.listen(2)
    print(f"Server started. Waiting for {max_players} players...")

    #constructs and starts the appropriate threads, one per player
    for i in range(1,(max_players+1)):
        conn, addr = server_socket.accept()
        player_id = i
        game_state["players"].append(player_id)
        players.append(conn)
        threading.Thread(target=gameClient, args=(conn, addr, player_id, word, max_players)).start()
    
    #sets the turn to 1, once everyone is connected
    game_state["turn"] = 1
    broadcast(json.dumps({"message": "All players connected, Game Starting!","game_state": game_state}).encode())
    

def gameClient(conn, addr, player_id, word, max_players):
    print(f"Player {player_id} connected from {addr}")
    message = f"Welcome Player {player_id}! Once all players have joined, the game will begin."
    if player_id == max_players:
        message = f"Welcome Player {player_id}! You are the the last to connect, Game Starting Now!"
    conn.sendall(json.dumps({"id": player_id,"message": message, "game_state": game_state}).encode())
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
                letter = request.get("letter")
                #check for correct word
                if len(letter) == len(word):
                    if letter == word:
                        message = f"Players win! The word was {word}, and you had {game_state['lives']} lives remaining."
                        print(message)
                        broadcast(json.dumps({"message":message}).encode())
                        broadcast(json.dumps({"gameOver":"over"}).encode())
                        lock.release()
                        break
                    else:
                        game_state["lives"] = game_state["lives"] - 1
                        message =f"Player {player_id} guessed {letter}. Unfortunately, {letter} wasn't the word. -1 lives."
                
                #check for letter appearance in the word
                else:
                    game_state["letters"].append(letter)
                    count = word.count(letter)
                    if count == 0:
                        game_state["lives"] = game_state["lives"] - 1
                        message =f"Player {player_id} guessed {letter}. Unfortunately, there is no {letter} in the word. -1 lives."

                    elif count == 1:
                        position = word.find(letter)
                        message =f"Player {player_id} guessed {letter}. There is a {letter} at position {position}!"
                        displayList = list(game_state["display"])
                        displayList[position] = letter
                        game_state["display"] = "".join(displayList)
                    
                    else:
                        displayList = list(game_state["display"])
                        for i in range(len(displayList)):
                            if word[i] == letter:
                                displayList[i] = letter
                        game_state["display"] = "".join(displayList)
                        message =f"Player {player_id} guessed {letter}. There are {count} {letter}'s!"

                # Check for game end condition
                if game_state["display"].count("_") == 0:
                    message = f"Players win! The word was {word}, and you had {game_state['lives']} lives remaining."
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
                if game_state["turn"] > max_players:
                    game_state["turn"] = 1
                lock.release()
                broadcast(json.dumps({"message":message + game_state["display"] , "game_state": game_state}).encode())

                         
    finally:
        conn.close()
    
      

if __name__ == '__main__':
    hmServer()