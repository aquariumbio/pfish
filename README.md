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

The initial settings for pfish are to connect to a [local Aquarium instance](https://aquariumbio.github.io/aquarium-local/) using the default user login (`neptune`) and password (`aquarium`) at URL (`http://localhost/`).
So, if you are using that Aquarium user, you don't need to do anything to start with.

However, if you use a different login, you'll want to change the login and password for this local instance.
To do this, use the command

```bash
pfish configure add -l <user-login> -p <user-password>
```

with the new login name and password.

The full `configure add` command is

```bash
pfish configure add -n <configuration-name> -l <user-login> -p <user-password> -u <instance-url>
```

where you specify the configuration-name, user-login, password and instance URL.
A configuration name is simply a key to keep track of the login information for a particular Aquarium instance.
Each of these arguments have defaults that correspond to the local configuration:

- the default configuration name is `local`,
- the login is `neptune`,
- the password is `aquarium`, and
- the URL is `http://localhost/`.

So, the command for changing the local user from above

```bash
pfish configure add -l <user-login> -p <user-password>
```

uses the configuration name `local` and the URL `http://localhost/`.

**Note**: the `configure add` command will overwrite an existing login configuration, as shown in this example.

If you also want to be able to push/pull from your production instance, you should create a different login configuration with

The most common use of `configure add` is to set up logins for different Aquarium instances.
For instance, a user might have a `production` configuration in addition to the `local` configuration.
The `local` configuration is used by default, and the other commands allow specifying the configuration that should be used.

You can set the default configuration with the command

```bash
pfish configure set-default -n <config-name>
```

which you might want to do if you do development on a staging server.

## Commands

The following commands work with files in the current working directory using the Aquarium instance in the default login configuration.

- To work in a subdirectory of the current working directory, use the option `-d <directory-name>`.
- To use a different instance, specify the login configuration with the option `-n <config-name>`.

### Create

The available create commands are:

1. Create an operation type

   ```bash
   pfish create -c <category-name> -o <operation-type-name>
   ```

2. [creating a library is not currently supported]

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

3. Pull just one operation type

   ```bash
   pfish pull -c <category_name> -o <operation_type_name>
   ```

4. Pull one library

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
Let's first create a protocol using the `create` command

```bash
pfish create -c MyCategory -o MyProtocol
```

which will create a protocol both in Aquarium and in the current directory.
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

Now make an initial git commit

```bash
git add mycategory
git commit -m "Add new definition for MyProtocol"
```

and then you can edit the files.

> Pfish mangles names to be lowercase with spaces changed to underscores.
> The original names are captured in the `definition.json` file and used when protocols and libraries are pushed.
> You do need to use the Aquarium names for libraries that you use.

In the situation where you have protocol code already in Aquarium that you want to work with on disk, you can pull that code and add it to your git repository.

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
