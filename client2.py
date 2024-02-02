import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('localhost', 1291))

def generate_welcome_message():

    welcome_message = """
    ---------------------------------------------------------------------------------------
                                 Witaj w grze w statki
    ---------------------------------------------------------------------------------------

    Zasady gry:
    1. Gra jest przeznaczona dla dwóch graczy, którzy na przemian wykonują ruchy.
    2. Gracze wprowadzają swoje ruchy, wybierając pozycję na planszy od 1 do 16.
    3. Jeśli jest twoja tura, wprowadź numer pozycji, do której chcesz strzelić:

    Plansza:
    | 1| 2| 3| 4|
    | 5| 6| 7| 8|
    | 9|10|11|12|
    |13|14|15|16|

    Oczekiwanie na przeciwnika...
    """

    return welcome_message

#wiadomość powitalna jako string.
welcome_message_str = generate_welcome_message()
print(welcome_message_str)

while True:
    response = client.recv(2048).decode()
    print(response)
    if "Twoja tura!" in response or "Niepoprawny ruch!" in response:
        while True:
            inp = input("Podaj pozycję do strzału (1-16): ")
            if inp.isdigit() and 1 <= int(inp) <= 16:
                client.send(str.encode(inp))
                response = client.recv(2048).decode()
                print(response)
                if "Niepoprawny ruch!" not in response:
                    break
            else:
                print("Niepoprawna wartość! Podaj liczbę od 1 do 16.")
    if "disconnect" in response:
        client.close()
        exit()