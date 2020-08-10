# Parrotfish (aka Phoenixfish)

Scripts for pulling/pushing protocols/libraries to/from Aquarium.

## Getting started

> Previous versions of these instructions had you clone this repository, which is no longer necessary.

Make sure you have Docker installed.

Download the pfish script with the command

  ```bash
  wget -vO- https://raw.githubusercontent.com/aquariumbio/pfish/master/pfish-install.sh | sh
  ```

This script will download the pfish script and install it in `~/bin`.
So, once the script is done, you'll need to [add `~/bin` to your PATH](https://opensource.com/article/17/6/set-path-linux). 

If you don't have `wget` installed, you can clone this repository and run `make install`.

## Updating

Pfish doesn't currently track updates itself.

Pfish has two parts: the wrapper script, and the pfish Docker image.

1. Update the wrapper script by running the install script describe above.
2. Update the pfish image by running

   ```bash
   pfish update
   ```

Note that the image is updated more frequently than the wrapper script.

## Configuring

Initially, pfish is configured to connect to a [local Aquarium instance](https://aquariumbio.github.io/aquarium-local/) using the default user login (`neptune`) and password (`aquarium`) at URL (`http://localhost/`).
So, if you are using that Aquarium user, you don't need to do anything to start with.

To use a different login with the local instance, run the command

```bash
pfish configure add -l <user-login> -p <user-password>
```

with the new login name and password.

To add another login configuration, use the command

```bash
pfish configure add -n <configuration-name> -l <user-login> -p <user-password> -u <instance-url>
```

where you specify the configuration-name, user-login, password and instance URL.
A configuration name is simply a key to keep track of the login information for a particular Aquarium instance.
(Each of these arguments have defaults that correspond to the local configuration.)

*Note*: The `configure add` command will overwrite an existing login configuration.

The most common use of `configure add` is to set up login configurations for different Aquarium instances.
For instance, a user might have a `production` configuration in addition to the `local` configuration.
In this case, the `local` configuration is still used by default, but the `production` configuration can be specified when transferring protocols.

To change the default configuration, use the command

```bash
pfish configure set-default -n <config-name>
```

with the name of the login configuration that you want to be the default.
You might want to do this if you do development on a staging instance rather than a local one.

## Commands

All commands other than `configure` by default use the current working directory using the Aquarium instance in the default login configuration.
These defaults can be overridden with the following options

- `-d <directory-name>` - use the named subdirectory of the current working directory.
- `-n <config-name>` - use the named login configuration instead of the default.

### Create

The available create commands are:

1. Create an operation type

   ```bash
   pfish create -c <category-name> -o <operation-type-name>
   ```

2. [Creating a library is not currently supported. The work-around is to create the library in Aquarium and use pull.]

### Pull

The available pull commands are:

1. Pull all libraries and operation types in the default Aquarium instance. If you do not specify a directory name, files will be pulled into your current working directory.:

   ```bash
   pfish pull -d <directory_name>
   ```

2. Pull all operations and libraries from a category

   ```bash
   pfish pull -c <category_name>
   ```

3. Pull an operation type

   ```bash
   pfish pull -c <category_name> -o <operation_type_name>
   ```

4. Pull a library

   ```bash
   pfish pull -c <category_name> -l <library_name>
   ```

### Push

_Note_: You must create protocols and libraries using the `create` command before pushing them to Aquarium.

The available push commands are:

1. Push a category:

   ```bash
   pfish push -c <category_name>
   ```

2. Push a library:

   ```bash
   pfish push -c <category_name> -l <library_name>
   ```

3. Push an operation type

   ```bash
   pfish push -c <category_name> -o <operation_type_name>
   ```

## Developing protocols

The strategy for working with protocols with pfish and git is to create the git repo and then use pfish from within the directory for the repository.

The first step is to create a git repository.
So, assuming you first initialize a `myprotocols` repo on GitHub, the commands would be

```bash
git clone <github-path-for-myprotocols>
cd myprotocols
```

You can then either create new protocols or pull existing ones from your Aquarium instance.

To create a new protocol, use the `create` command

```bash
pfish create -c MyCategory -o MyProtocol
```

which will create the protocol both in Aquarium and in the current directory.
The local files will be in the directory `mycategory`:

```bash
.
`-- mycategory
    `-- operation_types
        `-- myprotocol
            |-- cost_model.rb
            |-- definition.json
            |-- documentation.rb
            |-- precondition.rb
            `-- protocol.rb
```

One the protocol is created, make an initial git commit of the new files with the commands

```bash
git add mycategory/operation_types/myprotocol
git commit -m "Add new definition for MyProtocol"
```

and then you can edit the files.

> Notice that pfish uses filenames that are the Aquarium names changed to all lowercase, and spaces changed to underscores.
> The original names are captured in the `definition.json` file and used when protocols and libraries are pushed.
> You do need to use the Aquarium names for libraries in your protocol or library code.

To add protocol code already in Aquarium, use the pull command and add the files to the repository.
For example, consider a `Cloning` category with the following structure

- Libraries:
  - Stripwell Methods
  - Gradient PCR
- Operation Types:
  - Run Gel
  - Order Primer

You can pull this category by running

```bash
pfish pull -c Cloning
```

which will create the following directory structure

```bash
cloning
|-- libraries
|   |-- stripwell_methods
|   `-- gradient_pcr
`-- operation_types
    |-- run_gel
    `-- order_primer
```

with each subdirectory containing the code for the components of each library or operation type.
To add this code to the repository add the `cloning` directory and commit using git.

When you change files and you can push the changes to Aquarium with the `push` command.
For instance, if you changed the `Run Gel` protocol, you would run the command

```bash
pfish push -c Cloning -o "Run Gel"
```

to push only that operation type.

## Developer

This repository is setup with a VS Code devcontainer.
To use it make sure that you have the VS Code Remote extension installed and use it to open the repository in the container.

> If you change the `requirements.txt` file, you will need to rebuild the devcontainer.

This container uses the Dockerfile in the `.devcontainer` directory, which is configured with development tools – unlike the pfish Dockerfile.
To allow the pyfish.py script to be run, the devcontainer minimally mounts the config directory and installs the packages using the `requirements.txt` file.

The GitHub repository is configured to run a CI workflow that publishes a Docker image to aquariumbio/pfish. 
See the files in the `.github` directory for details.

A Makefile is provided to replicate the installation process locally, but is not needed for development.
Use `make build` to create the pfish Docker image locally, and you can then run a shell within the container by typing

```bash
docker run -it --entrypoint /bin/bash aquariumbio/pfish
```
