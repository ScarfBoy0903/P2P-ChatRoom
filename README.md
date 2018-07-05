 # Objectives
 The objective of the project is to build a desktop app that could connect users to one another. Users can see each others from their front camera, also they could type in words to communicate with each other.
 This project is called **skyscraper meeting** is because it can be used only in **same subnet** by far. We are still trying to acheive TCP hole punching.
 # Features
   - Kivy GUI
   - TCP based image transmission
   - RC4 image encoded
   - MD5 account/password encoded
   - SQLite server storing salted account/password
 
 # Environment
   - python 3.5 or above
   - Window 8/10

# Python packages installation
As in requirments.txt. You can also download all of the using 
```sh
pip install -r requirements.txt
```

# Usage
### start programs
  - Start both account_server.py and P2P_server.py. 
    - Account_server is for verifying users' identity. 
    - Once an user has login successfully, he/she will connect to P2P_server waiting for a match.
  ```sh
  python account_server.py
  python P2P_server.py
  ```
  Note that these two server should be executed in different python kernel (or different command line). They have to be executed concurrently.
  - Modify the IP address in line 32 of GUI.py
  ```python
  ipAddress = "192.168.*.*"
  ```
  - Execute GUI.py in any computer under the same subnet
  ```sh
  python GUI.py
  ```
 ### how to use
  - The user can now login/register in GUI
  ![Login GUI](pics/Login.png?raw=True)
  ![Account collision](pics/LoginFailed.png?raw=True)
  - There are two option you can choose in setting
    - **mood_detection** is for face detection (we are still working on the mood detection part), it use opencv to detect your face and label it
    - **security_transmission(RC4)** is for transferring your images after RC4 encoding. Therefore, sniffers can't know what exactly you're transmitting.
    - Both end user should have the same **key.txt** in order to use **security_transmission(RC4)**
     ![Setting GUI](pics/Setting.png?raw=True)
  - Once every thing is done, press "**Connect**" at the lower left and wait for another user to connect
   ![main GUI](pics/Main.png?raw=True)
   ![connection failed](pics/ConnectionFailed.png?raw=True)

