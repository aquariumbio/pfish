# PFish (formerly known as ParroPyTriFish, commonly known as Parrotfish or PhoenixFish)

Scripts for pulling/pushing protocols/libraries to/from Aquarium.

## Getting started

* You will need to have Trident/Pydent installed. It is available [here](https://github.com/klavinslab/trident)

* The example scripts assume a file `resources.py` that defines the values `login`, `password` and `url`.
This file can be constructed by first running the command

```bash
cp resources.py-temp resources.py
```

and then changing the values to match your Aquarium account.

The import

```python
from resources import resources
```

should be included at the top of each script.

The command

```python
session = AqSession(
        resources['aquarium']['login'],
        resources['aquarium']['password'],
        resources['aquarium']['aquarium_url']
    )
```

creates the session object to make queries to Aquarium.

Note that `resources.py` contains secrets that should not be checked into your version control.

## Pulling Files from Aquarium
  * If you would like to pull ALL files from you Aquarium Instance. 
  `pyfish.py pull -d <my_directory_name>`

  * If you would like to pull everything from one category/folder.
  `pyfish.py pull -d <my_directory_name> -c <category_name>`

  * If you would like to pull just one operation type or library. 
  `pyfish.py pull -d <my_directory_name> -c <category_name> -o <operation_type_name>`
  `pyfish.py pull -d <my_directory_name> -c <category_name> -l <library_name>`

### Pulling Example
  * Category: Cloning
    * Libraries:
      * Stripwell Methods
      * Gradiant PCR
    * OperationTypes:
      * Run Gel
      * Order Primer

`pyfish.py pull -d MyDirectoryName -c Cloning`
will pull everything listed under cloning -- all operation types and libraries.

`pyfish.py pull -d MyDirectoryName -c Cloning -l "Stripwell Methods"`
will pull just the Stripwell Methods Library.

`pyfish.py push -d MyDirectoryName -c Cloning -o "Run Gel"`
will pull just the Run Gel operation type. 

## Pushing files to Aquarium

* At the moment, an OperationType or Library must already exist in Aquarium for you to be able to push to it. 
* You can create a blank type or library in Aquarium, then pull it, add whatever you'd like, and then push to it.

* You can push either one library or one operation type at a time. 
* Pushing an operation type will include all parts of that that type (protocol text, cost model, documentatation etc.)

* For a library:
`pyfish.py push -d <directory_name> -c <category_name> -l <library_name>`
    
* For an OperationType 
`pyfish.py push -d <directory_name> -c <category_name> -o <operation_type_name>`

* You may need to refresh Aquarium to see the new version
