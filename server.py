import socket
import threading
import random
import time

server = "127.0.0.1"
port = 1291

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    print(str(e))

s.listen(2)
print("Oczekiwanie na połączenie, Serwer uruchomiony")

board_size = 4
board1 = [[' ' for _ in range(board_size)] for _ in range(board_size)]
board2 = [[' ' for _ in range(board_size)] for _ in range(board_size)]
empty_board1 = [[' ' for _ in range(board_size)] for _ in range(board_size)]
empty_board2 = [[' ' for _ in range(board_size)] for _ in range(board_size)]
currentPlayer = 0
players = [None, None]
first_turn = True

# Losowe umiejscowienie statków na planszy dla każdego gracza
for _ in range(2):
    ship_row = random.randint(0, board_size - 1)
    ship_col = random.randint(0, board_size - 1)
    while board1[ship_row][ship_col] == 'S':
        ship_row = random.randint(0, board_size - 1)
        ship_col = random.randint(0, board_size - 1)
    board1[ship_row][ship_col] = 'S'

    ship_row2 = random.randint(0, board_size - 1)
    ship_col2 = random.randint(0, board_size - 1)
    while board2[ship_row2][ship_col2] == 'S' or (ship_row2 == ship_row and ship_col2 == ship_col):
        ship_row2 = random.randint(0, board_size - 1)
        ship_col2 = random.randint(0, board_size - 1)
    board2[ship_row2][ship_col2] = 'S'

def reset_game():
    global board1, board2, empty_board1, empty_board2, currentPlayer, first_turn
    board1 = [[' ' for _ in range(board_size)] for _ in range(board_size)]
    board2 = [[' ' for _ in range(board_size)] for _ in range(board_size)]
    empty_board1 = [[' ' for _ in range(board_size)] for _ in range(board_size)]
    empty_board2 = [[' ' for _ in range(board_size)] for _ in range(board_size)]
    for _ in range(2):
        ship_row = random.randint(0, board_size - 1)
        ship_col = random.randint(0, board_size - 1)
        while board1[ship_row][ship_col] == 'S':
            ship_row = random.randint(0, board_size - 1)
            ship_col = random.randint(0, board_size - 1)
        board1[ship_row][ship_col] = 'S'

        ship_row2 = random.randint(0, board_size - 1)
        ship_col2 = random.randint(0, board_size - 1)
        while board2[ship_row2][ship_col2] == 'S' or (ship_row2 == ship_row and ship_col2 == ship_col):
            ship_row2 = random.randint(0, board_size - 1)
            ship_col2 = random.randint(0, board_size - 1)
        board2[ship_row2][ship_col2] = 'S'
    currentPlayer = 0
    first_turn = True

def print_board(board):
    return '\n'.join(['|' + '|'.join(row) + '|' for row in board])

def check_winner(board):
    return all(all(cell != 'S' for cell in row) for row in board)

def send_game_result(player, reply):
    if players[0] is not None and players[1] is not None:
        players[0].send(str.encode("\nGame Over!\n" + reply))
        players[1].send(str.encode("\nGame Over!\n" + reply))

        print("Gra zakończona, za 5 sekund rozłączę klientów")
        time.sleep(5)
        players[0].send(str.encode("disconnect"))
        players[1].send(str.encode("disconnect"))
        players[0] = None
        players[1] = None
        reset_game()
        print("Oczekiwanie na nowych graczy:")

def threaded_client(conn, player):
    global currentPlayer, first_turn
    players[player] = conn
    if players[0] is not None and players[1] is not None:
        if player == 0:
            players[0].send(str.encode("Drugi gracz dołączył do gry! Twoja tura!\n" + print_board(board1)))
            players[1].send(str.encode("Dołączyłeś do gry! Gracz 1 zaczyna.\n" + print_board(board2)))
        else:
            players[0].send(str.encode("Dołączyłeś do gry! Gracz 1 zaczyna.\n" + print_board(board1)))
            players[1].send(str.encode("Drugi gracz dołączył do gry! Twoja tura!\n" + print_board(board2)))

    while True:
        try:
            if player == 0:
                board = board1
                empty_board = empty_board1
                opponent_board = board2
            else:
                board = board2
                empty_board = empty_board2
                opponent_board = board1

            valid_move = False
            while not valid_move:
                data = conn.recv(2048).decode()
                if not data:
                    break
                elif data.lower() == 'statki':
                    conn.sendall(str.encode(print_board(board)))
                    continue
                else:
                    move = int(data) - 1
                    row = move // board_size
                    col = move % board_size
                    if empty_board[row][col] != ' ':
                        reply = "\nPudło, tutaj już strzelałeś, Tura przepada! \n"
                        valid_move = True
                        if check_winner(opponent_board):
                            reply += "Gracz " + str(player + 1) + " wygrywa!\n"
                            send_game_result(player, reply)
                            break
                        else:
                            if currentPlayer == 0:
                                currentPlayer = 1
                            else:
                                currentPlayer = 0
                            players[0].send(str.encode("\nTwoja tura!\n" + print_board(empty_board1)))
                            players[1].send(str.encode("\nTwoja tura!\n" + print_board(empty_board2)))
                    else:
                        if opponent_board[row][col] == 'S':
                            opponent_board[row][col] = 'X'  # Hit
                            empty_board[row][col] = 'X'
                            reply = "Trafiłeś statek!\n"
                        else:
                            opponent_board[row][col] = 'O'  # Miss
                            empty_board[row][col] = 'O'
                            reply = "\nPudło!\n"
                        valid_move = True
                        if check_winner(opponent_board):
                            reply = ""
                            reply += "Gracz " + str(player + 1) + " wygrywa!\n"
                            send_game_result(player, reply)
                            break
                        else:
                            if currentPlayer == 0:
                                currentPlayer = 1
                            else:
                                currentPlayer = 0
                            players[0].send(str.encode("Twoja tura!\n" + print_board(empty_board1)))
                            players[1].send(str.encode("Twoja tura!\n" + print_board(empty_board2)))
                conn.sendall(str.encode("Twoja plansza\n" + print_board(board)))
                conn.sendall(str.encode(reply + print_board(empty_board)))
        except Exception as e:
            print(f"Error {e}")
            players[currentPlayer] = None
            reset_game()
            break

    conn.close()

while True:
    if players[0] is None or players[1] is None:
        conn, addr = s.accept()
        print("Połączono do:", addr)
        threading.Thread(target=threaded_client, args=(conn, currentPlayer)).start()
        if currentPlayer == 0:
            currentPlayer = 1
        else:
            currentPlayer = 0
