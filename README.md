# Hangman
Simple web game of hangman, with command line interface. When the server is run, choose a word between 3 and 10 characters(inclusive). Then players take
turns guessing letters, or the word itself to win. Players have 6 lives between them, which get lost on incorrect guesses.

# To Use
Run the hangmanServer.py on the command line with python3, using -p to select a port number. Using -n will allow you to specify number of players, it defaults to 2.
The server is listening on 0.0.0.0

Example:
```
python3 hangmanServer.py -p 5000
```
Then run the hangmanClient.py, also on the command line with python3. This is either on a different terminal window, or different system. This takes -p for port number, as well as -i for the server IP or DNS. 

Example on same computer:
```
python3 hangmanClient.py -p 5000 -i 127.0.0.1
```

## **Project Title:**
Hangman

## **Team:**
Collyn Miller

## **Project Objective:**
The goal is to make a functional multiplayer game of hangman in a commmand line interface.

## **Scope:**
### **Inclusions:**
Ability to choose custom word to guess.
Back and forth responses with feedback on right or wrong guesses.

### **Exclusions:**
Graphical functionality beyond simple ASCII rendering.

## **Deliverables:**
A working python script that sets up the game, and allows someone else to connect to it with an address and password.

## **Technical Requirements:**
### **Hardware:**
No specific hardware requried, other than an internet connected device and CLI.

### **Software:**
Python
Socket and networking libraries

## **Assumptions:**
I will assume a consistantly available internet connection.
