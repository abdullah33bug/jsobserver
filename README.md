# JSObserver

JSObserver tool is specifically created for **Bug Bounty Hunters** & **Penteteration Testers**. 
JSObserver monitors JavaScript files of target applications for new or changed endpoints and sends real-time notifications to an integrated Slack channel.

# How It Works

Whenever jsobserver runs, it takes JS file URL from **target.txt** file located in directory named **target** and processes it. During this procedure, it fetches all the endpoints from JS file and saves within a txt file in directory named **result** - creates sepearate txt result file for each JS file and creates the result files with the sequential numeric names for example, 1.txt, 2.txt, & 3.txt etc.
The tool compares the current fetched endpoints result with the previously created JS file result txt file and concludes, if there any changes or not. For this to keep the record of each scan, it creates a changes tracking history file named **jsobserver.json**. Within that file it has the JS file URL with the latest file name created for that specific JS file within the result directory. This helps to make understanding for the tool that, which is the latest result file to compare the current fetched endpoints with to draw a comparsion. On basis of which it decides, whether there are any changes to be notified about.
If there are any changes, it sends the message to slack channel added within the script. Message includes; **new endpoints, result file name, JS file URL, previous & new file size**. 

# Installation & Setup

Clone this repository: 
```
git clone https://github.com/abdullah33bug/JSObserver.git
cd jsobserver
pip3 install -r requirements.txt #requests #jsbeautifier #slack-sdk
```

Add you Slack Bot Token and Slack Channel ID
```
cd jsobserver 
nano jsobserver.py
At start of script replace token and channel id in following
SLACK_TOKEN = "xoxb-100xxxxx-xxxxxx-xxxxxxx"
SLACK_CHANNEL_ID = "C0A1xxxxx"
After replacing save the script
```
<img width="1148" height="378" alt="image" src="https://github.com/user-attachments/assets/8762aa2c-abb8-41f1-90e1-85d66c0b3a9d" />
<p style="line-height: 1;"></p>

Create Target directory
```
In jsobserver tool folder, create target directory and target.txt file and paste js file URLs in target.txt
cd jsobserver
mkdir target
cd target
nano target.txt # in this add target application js file urls and save it
```
<img width="767" height="123" alt="image" src="https://github.com/user-attachments/assets/94ce3377-87a8-4f16-bb21-394eb6313bea" />
<img width="1457" height="157" alt="image" src="https://github.com/user-attachments/assets/b8e7840c-4c52-4b97-9d40-be83b983fd5e" />  
<p style="line-height: 1;"></p>

Create Result directory
```
For results, create a result folder and leave it as is. The tool will create the result files on its own, leave it empty.
cd jsobserver
mkdir result
```
<img width="935" height="132" alt="image" src="https://github.com/user-attachments/assets/0afbd492-a2f0-486c-9029-c53116a7c94b" />
