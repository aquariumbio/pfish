# Parrotfish (aka Phoenixfish)

Scripts for pulling/pushing protocols/libraries to/from Aquarium.

## Getting started

You must have Docker installed to run the script this way.

- Ensure you have a directory `~/bin`:

  ```bash
  mkdir -p ~/bin
  ```

- Add `~/bin` to your PATH. How you do this depends on your the shell that you run.

- Clone Parrotfish:

  ```bash
  git clone https://github.com/klavinslab/pfish.git
  ```

- Install the `pfish` script

  ```bash
  cd pfish
  make install
  ```

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

1. Pull all libraries and operation types in the default Aquarium instance:

   ```bash
   pfish pull
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
