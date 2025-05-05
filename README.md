# Remote Administration Tool (RAT)

This software is intended for authorized use only. Unauthorized access or surveillance without consent is illegal and unethical under most jurisdictions.

# Usage


→ Start both main.py and client.py scripts (set the server ip in the client's file)

↳ Click on "Connection"

↳ Then on "New Connection"

↳ Then on "Start Search"

↳ Then on the client you want to connect

↳ Finally on "Submit Connection"

→ You can now communicate through the cmd in the main window !


# Requirements

before running main.py and client.py, you need to make sure you installed : 

- mss
- pynput
- opencv-python
- numpy
- pyautogui
- requests

you can do it using pip : 

        pip install mss pynput psutil opencv-python numpy pyautogui requests


# Features

🛠️ CMD commands

🗑️ Remove files/folders

📂 Move files/folders

🌐 File upload/download

⚙️ Execute files

🧾 Logs

🗃️ Zipping/Unzipping files/folders remotely

🖥️ Get system info (OS, IP, CPU, RAM)

📸 Screenshot capture

👁️ Screen monitoring

⌨️ Keylogger

🔒 Encrypted communication with ssl

🧬 Basic authentication between client/server

⛔ Prevent duplicate clients

📁 File explorer GUI

📅 Task scheduling


# Commands

comments :

    #this a comment
    //this is also a command

change directory : 

    cd ..
    cd my_folder
    cd "my folder"

get current path :

    cwd

get all files/folder in the current path/desired directory :

    dir
    dir my_folder
    dir "my folder"

rename a file/folder :

    rename my_file.txt "my file.txt"
    rename C:/folder C:/folder2

create a new directory :

    mkdir "my folder"
    mkdir myfolder
    mkdir C:/myfolder2

create multiple directories :

    makedirs "folder/folder2/folder 3"

remove the desired file :

    removefile "my file.odt"
    removefile mymusic.mp3

remove the desired directory :

    removedir "my folder"
    removedir myfolder

return if the provided path exists : 

    ispath C:/folder/folder2
    ispath "C:/folder 3"

return if the provided path is a directory : 

    isdir "folder 1/file.txt"
    isdir folder2/my_folder

download a file from the client in the directory /ressources/received_files/ : 

    getfile "myfile 2.txt"
    getfile zipped_folder.zip

upload a file to the client to the current directory : 

    sendfile C:/folder/folder2/file.txt

zip a file/folder :

    zip "folder 1"
    zip file.odt

unzip a zipped file/folder :

    unzip "folder 1"
    unzip file.odt

move the desired file/folder to the desired location : 

    move "folder/file 3.txt" folder/folder2
    move folder2/myfolder folder/myfolder2

copy and paste the desired file :

    copyfile "folder 1/file.txt" "C:/folder 3"
    copyfile my_folder/file2.txt "folder 3/my folder"

copy and paste the desired folder :

    copydir "folder 1" "C:/folder 3"
    copydir my_folder "my folder"

take a screenshot of all screens or desired screen, then saves it in the directory : /ressources/received_screenshots/ :

    screenshot
    screenshot 0
    screenshot 1

invoke a new cmd and enter the desired command : 

    cmd dir /s
    cmd ping www.google.com
    cmd cd "my folder"
    cmd del my_file.txt

turn on/off, get and clear keylooger :

    keylogger on
    keylogger off
    keylogger get
    keylogger clear

get all connection, current disk and pc informations of the client (OS, CPU, RAM, Disk, location) :

    info

run the desired file :

    execute myfile.txt
    execute "my file2.doc"

print the desired text :

    print

get the mouse position :

    mousepos

click on the desired pixel with desired button :

    mouseclick left 100 400
    mouseclick
    mouseclick right 400 800 1 0.0
    # args are : button(left, right, middle)=left, x(int)=None, y(int)=None, clicks(int)=1, interval(float)=0.0

hold click down :

    mousedown right 400 600
    mousedown
    # args are : button(left, right, middle)=left, x(int)=None, y(int)=None

release click:

    mouseup right 400 600
    mouseup
    # args are : button(left, right, middle)=left, x(int)=None, y(int)=None
  
hold click and click while to offset :

    mousedrag 100 400 1 right
    mousedrag 200 500
    # args are : x(int), y(int), duration(float)=0.0, button(left, right, middle)=left

hold click and click while to position :

    mousedragto 100 400 1 right
    mousedragto 200 500
    # args are : x(int), y(int), duration(float)=0.0, button(left, right, middle)=left

move mouse to the desired offset of the position :

    mousemove 100 400 2
    mousemove 200 500
    # args are : x(int), y(int), duration(float)=0.0

move mouse to the desired position :

    mousemoveto 100 400 2
    mousemoveto 200 500
    # args are : x(int), y(int), duration(float)=0.0

write something using the client's keyboard :

    write "hello world !"
    write "['h', 'backspace', 'e']" 0.2
    write ["h","backspace","e"]
    # args are : keys(str, str(list)), interval(float)=0.0

list of all the usable keys : 

    ['\t', '\n', '\r', ' ', '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 
    'k', 
    'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '{', '|', '}', '~', 'accept', 'add', 'alt', 'altleft', 'altright', 'apps', 'backspace', 'browserback', 'browserfavorites', 'browserforward', 'browserhome', 'browserrefresh', 'browsersearch', 
    'browserstop', 'capslock', 'clear', 'convert', 'ctrl', 'ctrlleft', 'ctrlright', 'decimal', 'del', 'delete', 'divide', 'down', 'end', 'enter', 'esc', 'escape', 'execute', 'f1', 'f10', 'f11', 'f12', 'f13', 'f14', 'f15', 'f16', 'f17', 'f18', 'f19', 'f2', 'f20', 'f21', 
    'f22', 'f23', 'f24', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'final', 'fn', 'hanguel', 'hangul', 'hanja', 'help', 'home', 'insert', 'junja', 'kana', 'kanji', 'launchapp1', 'launchapp2', 'launchmail', 'launchmediaselect', 'left', 'modechange', 'multiply', 
    'nexttrack', 
    'nonconvert', 'num0', 'num1', 'num2', 'num3', 'num4', 'num5', 'num6', 'num7', 'num8', 'num9', 'numlock', 'pagedown', 'pageup', 'pause', 'pgdn', 'pgup', 'playpause', 'prevtrack', 'print', 'printscreen', 'prntscrn', 'prtsc', 'prtscr', 'return', 'right', 'scrolllock', 
    'select', 'separator', 'shift', 'shiftleft', 'shiftright', 'sleep', 'space', 'stop', 'subtract', 'tab', 'up', 'volumedown', 'volumemute', 'volumeup', 'win', 'winleft', 'winright', 'yen', 'command', 'option', 'optionleft', 'optionright']


press the desired keys :

    press g
    press "['h', 'backspace', 'd']"
    press ["h","backspace","e"]
    # args are : keys(str, str(list)), interval(float)=0.0

press desired keys in order and then release them in reverse order :

    hotkey g
    hotkey "['h', 'backspace', 'd']"
    hotkey ["h","backspace","e"]
    # args are : keys(str, str(list))

hold the desired key down :

    keydown h
    keydown "alt"

release the desired key :

    keyup h
    keyup "alt"

display a popup with a timeout of 100 sec :

    alert "you are being watched !" "Warning !"
    alert :) HELLO
    # args are : text(str), title(str)

get the current screen size :

    screensize

shutdown the client :

    close
