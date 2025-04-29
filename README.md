# Usage

→ Start both real_project/main.py and real_project/client.py scripts (set the server ip in the client's file)

↳ Click on "Connection"

↳ Then on "New Connection"

↳ Then on "Start Search"

↳ Then on the client you want to connect

↳ Finally on "Submit Connection"

→ You can now communicate through the cmd in the main window !

# Commands

cd --goto to a specified directory

↳ usage : 

    cd folder
    
    cd ..

mkdir --create a new directory with the given name

↳ usage : 

    mkdir new_folder


ls --browse all files and folders in the current path

↳ usage :

    ls


remove --remove the file with the given name

↳ usage :

    remove file


removedir --remove the folder with the given name

↳ usage :

    removedir folder


print --write the specified text in the client's console

↳ usage :

    print hello


getfile --download a file or a zipped folder with the given name

↳ usage :

    getfile myfile.txt
    
    getfile myfolder.zip
    

zip --zip a folder or a file with the given name

↳ usage :

    zip folder
    
    zip text.txt
    

move --move the desired file or folder to the desired location

↳ usage : 

    move thing.txt folder
    
    move something.odt folder/folder2
    

getinfo --get all informations and specifications about the client's pc

↳ usage :

    getinfo

    
screenshot --take a screenshot of the client's pc and save it in the server (at the server.py location)

↳ usage :

    screenshot
    

keylogger --keylogger class

↳ usage :
    
    keylogger on

    keylogger off

    keylogger get


exit --exit the connection

↳ usage :

    exit


help --get help

↳ usage :

    help
