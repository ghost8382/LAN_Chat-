import socket
import threading

clients = {}  # Słownik przechowujący połączenia i nazwy użytkowników
lock = threading.Lock()


def broadcast_message(message, sender_socket=None):
    """Wysyłanie wiadomości do wszystkich klientów (poza nadawcą)"""
    with lock:
        for username, client_socket in clients.items():
            if client_socket != sender_socket:
                client_socket.send(message.encode('utf-8'))


def handle_client(client_socket, username):
    """Funkcja obsługująca połączenie klienta"""
    with lock:
        clients[username] = client_socket
    print(f"Użytkownik {username} połączony.")

    # Informowanie wszystkich użytkowników o dołączeniu nowego użytkownika
    broadcast_message(f"{username} dołączył do czatu.")

    try:
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break  # Połączenie zakończone, jeśli brak danych

            # Wiadomość publiczna
            if message.startswith("PUBLIC:"):
                msg_to_send = f"{username}: {message[7:]}"
                broadcast_message(msg_to_send, client_socket)

            # Wiadomość prywatna
            elif message.startswith("PRIVATE:"):
                target_user, msg = message[9:].split(' ', 1)
                if target_user in clients:
                    target_sock = clients[target_user]
                    private_msg = f"Private from {username}: {msg}"
                    target_sock.send(private_msg.encode('utf-8'))
                else:
                    client_socket.send("Użytkownik nie istnieje.".encode('utf-8'))

    except Exception as e:
        print(f"Błąd połączenia z {username}: {e}")
    finally:
        with lock:
            del clients[username]
        client_socket.close()
        # Informowanie innych klientów o rozłączeniu
        broadcast_message(f"{username} opuścił czat.")


def start_server():
    """Uruchomienie serwera"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 5008))
    server_socket.listen(5)
    print("Serwer gotowy i czeka na połączenia...")

    while True:
        client_socket, client_address = server_socket.accept()
        username = client_socket.recv(1024).decode('utf-8')
        print(f"{username} połączony z {client_address}")
        threading.Thread(target=handle_client, args=(client_socket, username), daemon=True).start()


if __name__ == "__main__":
    start_server()
