import socket

class App:
    def __init__(self):
        self.port = 5554
        self.socket = None
        
    def run(self):
        try:
            self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0, fileno=None)
            self.socket.bind(("0.0.0.0", self.port))
            self.socket.listen(10)
            print("server now online")
            print("send a command to the connected client : ")
        except Exception as e:
            print("error while creating server : ", e)
        while True:
            try:
                client, client_addr = self.socket.accept()
                
                msg_out = ""
                msg_out = input("[" + client_addr[0] + "/" + str(client_addr[1]) + "] >")
                client.send(msg_out.encode())
                msg = client.recv(1024).decode()
                print("reveiced : ")
                print(msg)
                client.close()
                
            except Exception as e:
                print("error while trying to connect to a client : ", e)

if __name__ == "__main__":
    app = App()
    app.run()