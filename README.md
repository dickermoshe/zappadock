# ZappaDock
## About
This package makes dealing with Zappa a walk in the park.
### How ?
Zappa runs Flask/Django web apps on AWS Lambda.  
We LOVE Zappa. However it's not the MOST user-friendly application ever.
### Why ?
You see, Zappa builds all your requirements before uploading your app to AWS Lambda. The problem is that your OS looks nothing like the environment that AWS Lambda looks like.
### So What's the problem ?
Simply, pip downloads the packages that are compatible with the computer it is running on, so when Zappa uploads it to AWS Lambda, many packages don't work (notably `psycopg2` among others).
### What Does ZappaDock Do ?
ZappaDock runs a docker container that mimics the AWS Lambda environment.  
All your code is mounted and inside of a virtual environment.  
Your AWS credentials are also automatically loaded from your environmental variables or your aws credential file.  
So now yor code is running in a Python virtual environment inside of a docker container.  
From here you can test your app and run the Zappa commands you need.  
## Install 
It's dead simple :
```
$ pip install zappadock
```
## Uninstall 
Duh. Just :
```
$ pip uninstall zappadock
```
## Contributing
I mostly made this for myself. Just threw it together. If you want to make this a masterpiece, be a sport and contribute.  
Thanks!

