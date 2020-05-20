# Parrotfish (aka Phoenixfish)

Scripts for pulling/pushing protocols/libraries to/from Aquarium.

## Getting started

- You must have Docker installed to run the script this way.

- Ensure you have a directory `~/bin`:

```bash
mkdir -p ~/bin
```

- Install the `pfish` script

```bash
make install
```

Check that you can run `pfish`

```bash
which pfish
```

If you get an error `pfish not found`, then you need to add `~/bin` to your PATH.
How you do this depends on your the shell that you run.

## For each project

[TODO: change this to running `pfish init`]

Copy the file `resources-template.py` in this repository to the directory a new project.

```bash
cp resources-template.py /project/directory/resources.py
```

and then change the values to match your Aquarium instance and account.
It is currently set for the default Aquarium user `neptune`.

Be sure to put `resources.py` into the `.gitignore` file for the project.

## Pulling Files from Aquarium

- If you would like to pull ALL files from you Aquarium Instance.

  ```bash
  pfish pull -d <my_directory_name>
  ```

- If you would like to pull everything from one category/folder.

  ```bash
  pfish pull -d <my_directory_name> -c <category_name>
  ```

- If you would like to pull just one operation type or library.
  ```bash
  pfish pull -d <my_directory_name> -c <category_name> -o <operation_type_name>
  ```
  ```bash
  pfish pull -d <my_directory_name> -c <category_name> -l <library_name>
  ```

### Pulling Example

- Category: Cloning
  - Libraries:
    - Stripwell Methods
    - Gradiant PCR
  - OperationTypes:
    - Run Gel
    - Order Primer

```bash
pfish pull -d MyDirectoryName -c Cloning
```

will pull everything listed under cloning -- all operation types and libraries.

```bash
pfish pull -d MyDirectoryName -c Cloning -l "Stripwell Methods"
```

will pull just the Stripwell Methods Library.

```bash
pfish push -d MyDirectoryName -c Cloning -o "Run Gel"
```

will pull just the Run Gel operation type.

## Pushing files to Aquarium

_Note_: At the moment, an operation type or library must already exist in Aquarium for you to be able to push to it.
If you are adding a new operation type or library, create a blank operation type or library with the name in Aquarium, pull it, add whatever you'd like, and then push.

You can push either one library or one operation type at a time.
Pushing an operation type will include all parts of that that type (protocol test, cost model, documentation etc.)

For a library:

  ```bash
  pfish push -d <directory_name> -c <category_name> -l <library_name>
  ```

For an operation type

  ```bash
  pfish push -d <directory_name> -c <category_name> -o <operation_type_name>
  ```

You may need to refresh Aquarium to see the new version
