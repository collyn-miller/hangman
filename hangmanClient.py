import socket
import argparse
import json
import threading

def hm_Client():

    #parsing input flags
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--portNumber")
    parser.add_argument("-i", "--serverIP")
    
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
                        
                        letter = str(input("Your turn! Enter a letter to guess: "))
                        letter = letter.lower()
                        client_socket.sendall(json.dumps({"letter": letter}).encode())
                    else:
                        print("Waiting for your turn...")
                if "gameOver" in data:
                    client_socket.sendall(json.dumps({"gameOver": "gameOver"}).encode())
                    print("Exiting the game.")
                    break
        except KeyboardInterrupt:
            print("Exiting the game.")





if __name__ == '__main__':
    hm_Client()