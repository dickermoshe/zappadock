
import os
import platform
import configparser
import traceback

import click
import docker

DOCKERFILE = """
FROM {base_image}

WORKDIR /var/task

# Fancy prompt to remind you are in ZappaDock
RUN echo 'export PS1="\[\e[36m\]ZappaDock>\[\e[m\] "' >> /root/.bashrc

# Additional RUN commands here
RUN yum clean all
RUN yum install -y which clang cmake python-devel python3-devel amazon-linux-extras gcc openssl-devel bzip2-devel libffi-devel wget tar gzip make

RUN echo 'virtualenv -p python3 ./zappa-venv >/dev/null' >> /root/.bashrc
RUN echo 'source ./zappa-venv/bin/activate >/dev/null' >> /root/.bashrc

CMD ["bash"]"""

def get_creds_from_env():
    # Get credentials from environment variables
    key = os.environ.get('AWS_ACCESS_KEY_ID')
    secret = os.environ.get('AWS_SECRET_ACCESS_KEY')
    region = os.environ.get('AWS_DEFAULT_REGION')
    return key, secret, region if not None in (key, secret, region) else False

def get_creds_from_credentials_file():
    # Get credentials from ~/.aws/credentials
    aws_credentials_path = os.path.expanduser('~/.aws/credentials')
    if os.path.isfile(aws_credentials_path):
        config = configparser.ConfigParser()
        config.read(aws_credentials_path)
        
        # If there are no credentials in the file, return False
        if len(config.sections()) == 0:
            return False

        # If there is only one profile, use it
        elif len(config.sections()) == 1:
            profile = config.sections()[0]

        # Otherwise, prompt the user
        else:
            profile = click.prompt(f"Please enter the profile you would like to use: ",type=click.Choice(config.sections()))
        
        key = config[profile].get('aws_access_key_id')
        secret = config[profile].get('aws_secret_access_key')
        region = config[profile].get('region')
        return key, secret, region if not None in (key, secret, region) else False

@click.command()
def zappadock():
    docker_file = '.zappadock-Dockerfile'
    if not os.path.isfile(docker_file):
        click.echo(f"Creating Dockerfile.")
        with open(docker_file, 'w') as f:
            python_version = '.'.join(platform.python_version().split('.')[:2])

            if python_version not in ['3.6', '3.7', '3.8','3.9']:
                click.echo(f"Python version {python_version} is not supported. Please use 3.6, 3.7, 3.8, or 3.9.")
                exit()

            if (platform.machine().lower() in ['aarch64', 'arm64', 'armv7l', 'armv8l']
                and python_version in ['3.6', '3.7']):
                click.echo("AWS Lambda does not support Python 3.6 or 3.7 on ARM64 on devices.")
                exit()
            
            if python_version in ['3.8','3.9']:
                image = f"mlupin/docker-lambda:python{python_version}-build"
            else:
                image = f"lambci/lambda:build-python{python_version}"

            f.write(DOCKERFILE.format(base_image=image))

    # Get credentials
    click.echo("Getting AWS credentials.")
    credentials = get_creds_from_env() 
    if not credentials:
        credentials = get_creds_from_credentials_file()
    if not credentials:
        click.echo("Credentials not found.\nYou can set them in ~/.aws/credentials or by setting environment variables.\nSee https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html#environment-variables for more info.")
        click.echo("Exiting...")
        exit()
    
    # Create Docker client
    try:
        click.echo("Creating Docker client.")
        client = docker.from_env()
    except docker.errors.DockerException:
        click.echo(f"{traceback.format_exc()}\n\nDocker failed to load.\nMake sure its installed and running before continuing.")
        click.echo("Exiting...")
        exit()
    
    # Check if Dockerfile is already built
    with open(docker_file, 'rb') as f:
        try:
            click.echo("Building Docker Image. This may take some time...")
            docker_image = client.images.build(fileobj=f)
        except docker.errors.DockerException:
            click.echo(f"{traceback.format_exc()}\n\nDocker failed to build.\nCheck the Dockerfile for any mistakes.")
            click.echo("Exiting...")
            exit()
    
    # Create command to start ZappaDock
    cmnd1 ="docker run -ti --rm"
    cmnd2 = f"-e AWS_ACCESS_KEY_ID={credentials[0]} -e AWS_SECRET_ACCESS_KEY={credentials[1]} -e AWS_DEFAULT_REGION={credentials[2]}"
    cmnd3 = f'-v "{os.getcwd()}:/var/task" {docker_image[0].id}'

    # Run command
    click.echo("Starting ZappaDock...")
    os.system(f"{cmnd1} {cmnd2} {cmnd3}")




    

