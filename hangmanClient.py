#Author: Collyn Miller
#for use with hangmanServer.py

import socket
import argparse
import json

def hm_Client():

    #parsing input flags
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--portNumber", help="Port number of server to use.")
    parser.add_argument("-i", "--serverIP", help="IP or DNS of server to connect to.")
    
    args = parser.parse_args()
    host = args.serverIP
    port = int(args.portNumber)  

    player_id = 0

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))
        print("Connected to the server!")

        try:
            while True:
                response = client_socket.recv(1024)
                if not response:
                    print("Disconnected from server.")
                    break

                data = json.loads(response.decode())
                if "id" in data:
                    player_id = data["id"]
                if "message" in data:
                    print(data["message"])
                    
                if "game_state" in data:
                    game_state = data["game_state"]
                    
                    if game_state["turn"] == player_id:
                        print(game_state["display"])
                        lives = game_state["lives"]
                        print(f"Lives remaining: {lives}")
                        wordsize = len(game_state["display"])
                        
                        while True:
                            letter = str(input(f"Your turn! Guess a letter or the word of length {wordsize}: "))
                            if (len(letter) == 1 or len(letter) == wordsize) and letter.isalpha():
                                valid = True
                            else:
                                valid = False

                            #checks for input validity, then checks to see if the letter has already been guessed
                            if game_state["letters"].count(letter) > 0:
                                print(f"{letter} has already been guessed, try again!")
                            else:    
                                if valid:
                                    break
                                else:
                                    print(f"Please try again and enter a single alphabet character or guess a word of correct length.")

                        letter = letter.lower()
                        client_socket.sendall(json.dumps({"letter": letter}).encode())
                    else:
                        print("Waiting for your turn...")
                
                #checks for a game over flag, to terminate gracefully
                if "gameOver" in data:
                    client_socket.sendall(json.dumps({"gameOver": "gameOver"}).encode())
                    print("Exiting the game.")
                    break
        except KeyboardInterrupt:
            print("Exiting the game.")





if __name__ == '__main__':
    hm_Client()