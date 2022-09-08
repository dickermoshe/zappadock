import os
import json
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
RUN yum install -y which clang cmake python-devel python3-devel amazon-linux-extras gcc openssl-devel bzip2-devel libffi-devel wget tar gzip make postgresql-devel

# Commands to Create/Activate python Virtual Environment on launch
RUN echo 'virtualenv -p python3 ./zappa-venv >/dev/null' >> /root/.bashrc
RUN echo 'source ./zappa-venv/bin/activate >/dev/null' >> /root/.bashrc
ENV VIRTUAL_ENV=/var/task/zappa-venv

CMD ["bash"]"""

@click.command()
def zappadock():
    """This is a tool for running Zappa commands in a Lambda-like environment.
    
    Make sure the Docker daemon is installed and running before using this tool.

    Your AWS credentials must be setup to use this tool.
    See https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html#environment-variables for more information.
    """

    # Set Zappadock Docker Filename
    docker_file = '.zappadock-Dockerfile'

    click.echo(f"Creating Dockerfile.")
    with open(docker_file, 'w') as f:

        # Find the current running Python version
        python_version = '.'.join(platform.python_version().split('.')[:2])

        # Check if the current Python version is supported
        if python_version not in ['3.6', '3.7', '3.8','3.9']:
            click.echo(f"Python version {python_version} is not supported. Please use 3.6, 3.7, 3.8, or 3.9.")
            exit()

        # Check the current architecture
        if (platform.machine().lower() in ['aarch64', 'arm64', 'armv7l', 'armv8l']
            and python_version in ['3.6', '3.7']):
            click.echo("AWS Lambda does not support Python 3.6 or 3.7 on ARM64 on devices.")
            exit()

        # Get the base image
        if python_version in ['3.8','3.9']:
            image = f"mlupin/docker-lambda:python{python_version}-build"
        else:
            image = f"lambci/lambda:build-python{python_version}"

        # Write the Dockerfile
        f.write(DOCKERFILE.format(base_image=image))

    docker_run_command = ["docker run -ti --rm"]

    # Add mount command to .aws folder if it exists
    if os.path.isdir(os.path.expanduser('~/.aws')):
        docker_run_command.append(f'-v ~/.aws/:/root/.aws')


    # Add AWS Environment Variables to Docker Command if they exist
    for i in ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_DEFAULT_REGION','AWS_PROFILE']:
        if i in os.environ:
            docker_run_command.append(f'-e {i}={os.environ[i]}')

    try:
        # Create Docker client
        click.echo("Creating Docker client.")
        client = docker.from_env()

    except docker.errors.DockerException as e:

        if 'Permission denied' in str(e):
            # If the user doesn't have permission to run docker, let them know
            click.echo("Your user is not in the docker group.\nSee https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user for more information.")
        else:
            # Docker isn't installed / running
            click.echo(f"{traceback.format_exc()}\n\nDocker failed to load.\nMake sure its installed and running before continuing.")
        click.echo("Exiting...")
        exit()
    
    # Build Docker Image
    with open(docker_file, 'rb') as f:
        try:
            click.echo("Building Docker Image. This may take some time...")
            docker_image = client.images.build(fileobj=f)
        except docker.errors.DockerException as e:
            click.echo(f"{traceback.format_exc()}\n\nDocker failed to build.\nCheck the Dockerfile for any mistakes.")
            click.echo("Exiting...")
            exit()
    
    # Create command to start ZappaDock
    docker_run_command.append(f'-v "{os.getcwd()}:/var/task" -p 8000:8000 {docker_image[0].id}')

    # Run Docker Command
    click.echo("Starting ZappaDock...")
    os.system(' '.join(docker_run_command))
