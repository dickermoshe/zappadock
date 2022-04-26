# ZappaDock
[![Downloads](https://pepy.tech/badge/zappadock)](https://pepy.tech/project/zappadock)

### Install 
It's dead simple :
```
$ pip install zappadock
```


## Usage 
1. Check that the Docker daemon is running by typing `docker info` command from a terminal.
2. Set your AWS credentials in environmental variables or in the `~/.aws` folder.  See the [Amazon Docs](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html#environment-variables) for more information.
3. Run `zappadock` in the directory you wish to run your Zappa commands.  
Your directory will be loaded in a docker container, and a virtual environment will be created and activated.  

4. To run the built-in servers:
* Django:  
`python manage.py runserver 0.0.0.0:8000`  
* Flask:  
`flask run --host=0.0.0.0 --port=8000`  

If you have any problems, open a issue and we'll figure it out.
  
  
  
## About
This package makes dealing with [Zappa](https://github.com/zappa/Zappa) a walk in the park.
#### How ?
Zappa runs Flask/Django web apps on AWS Lambda.  
We LOVE Zappa. However it's not the MOST user-friendly application ever.
#### Why ?
You see, Zappa builds all your requirements before uploading your app to AWS Lambda. However, pip downloads the packages that are compatible with the computer it is running on, so when Zappa uploads it to AWS Lambda, many packages don't work (notably `psycopg2` among others).
#### What's the solution ?
The solution recommend by the [The Django Guide for Zappa](https://romandc.com/zappa-django-guide/) is to run your Zappa commands in a docker container similar to the one that AWS Lambda uses.  
This will ensure that all the dependencies will be AWS Lambda compatible. 
This ZappaDock streamlines the workflow.
#### What Does ZappaDock Do ?
ZappaDock does 3 things.
1. Run a docker container with your code mounted.
2. Load your AWS Credentials from the `~/.aws` folder and environmental variables into the container.
3. Create and activate a virtual environment inside the container.  

So now you can test and deploy your code confident that it will work once deployed.  


## Contributing
I mostly made this for myself.  If you want to help make this a masterpiece, be a sport and contribute.  
Thanks!

