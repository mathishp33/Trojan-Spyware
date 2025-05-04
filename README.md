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


  
