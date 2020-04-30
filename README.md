# ParroPyTriFish

Scripts for pulling/pushing protocols/libraries to/from Aquarium.
-- add note that you need to have trident/etc. installed

## Getting started

The example scripts assume a file `resources.py` that defines the values `login`, `password` and `url`.
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

