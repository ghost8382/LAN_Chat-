import tkinter as tk
from tkinter import messagebox
import socket
import threading
import time


class ChatClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Client")
        self.client_socket = None
        self.username = ""

        self.create_widgets()

    def create_widgets(self):
        """Tworzenie widgetów w GUI"""
        # Okno wiadomości
        self.chat_display = tk.Text(self.root, state=tk.DISABLED, width=50, height=20)
        self.chat_display.pack(padx=10, pady=10)

        # Wybór odbiorcy wiadomości prywatnej
        self.target_label = tk.Label(self.root, text="Wybierz odbiorcę wiadomości prywatnej:")
        self.target_label.pack(padx=10, pady=5)

        self.target_user = tk.Entry(self.root, width=20)
        self.target_user.pack(padx=10, pady=5)

        # Wpisywanie wiadomości
        self.entry_message = tk.Entry(self.root, width=40)
        self.entry_message.pack(side=tk.LEFT, padx=5, pady=5)

        # Przycisk "Wyślij"
        self.send_button = tk.Button(self.root, text="Wyślij", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT, padx=5, pady=5)

        # Okno logowania
        self.username_window = tk.Toplevel(self.root)
        self.username_window.title("Wprowadź nazwę użytkownika")
        self.username_window.geometry("300x150")

        self.username_label = tk.Label(self.username_window, text="Nazwa użytkownika:")
        self.username_label.pack(pady=5)

        self.username_entry = tk.Entry(self.username_window)
        self.username_entry.pack(pady=5)

        self.connect_button = tk.Button(self.username_window, text="Połącz", command=self.connect_to_server)
        self.connect_button.pack(pady=5)

    def connect_to_server(self):
        """Połączenie z serwerem"""
        self.username = self.username_entry.get()
        if not self.username:
            messagebox.showerror("Błąd", "Proszę wprowadzić nazwę użytkownika!")
            return
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('localhost', 5008))
        self.client_socket.send(self.username.encode('utf-8'))
        self.username_window.destroy()

        threading.Thread(target=self.receive_messages, daemon=True).start()

    def send_message(self):
        """Wysyłanie wiadomości"""
        message = self.entry_message.get()
        target = self.target_user.get()

        if not message:
            messagebox.showerror("Błąd", "Proszę wpisać wiadomość!")
            return

        # Jeśli wiadomość jest kierowana do konkretnego użytkownika
        if target:
            message = f"PRIVATE:{target} {message}"

        # Jeśli wiadomość jest publiczna
        else:
            message = f"PUBLIC:{message}"

        # Wysyłanie wiadomości do serwera
        self.client_socket.send(message.encode('utf-8'))

        # Wyświetlanie wiadomości lokalnie z czasem
        current_time = time.strftime('%H:%M:%S', time.localtime())
        if target:
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.insert(tk.END, f"[{current_time}] You (Private): {message[9:]}\n")
        else:
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.insert(tk.END, f"[{current_time}] You: {message[7:]}\n")
        self.chat_display.config(state=tk.DISABLED)

        self.entry_message.delete(0, tk.END)
        self.save_to_history(f"[{current_time}] You: {message[7:]}" if not target else f"[{current_time}] You (Private): {message[9:]}")

    def receive_messages(self):
        """Odbieranie wiadomości z serwera"""
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                current_time = time.strftime('%H:%M:%S', time.localtime())

                # Wyświetlanie wiadomości z czasem
                self.chat_display.config(state=tk.NORMAL)
                self.chat_display.insert(tk.END, f"[{current_time}] {message}\n")
                self.chat_display.config(state=tk.DISABLED)
                self.chat_display.yview(tk.END)

                # Zapis wiadomości do historii
                self.save_to_history(f"[{current_time}] {message}")
            except:
                break

    def save_to_history(self, message):
        """Zapisuje wiadomość do pliku chat_history.txt"""
        with open("chat_history.txt", "a") as log_file:
            log_file.write(message + "\n")


# Uruchomienie aplikacji
root = tk.Tk()
chat_client = ChatClient(root)
root.mainloop()
