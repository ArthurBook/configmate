# configmate-pydantic-validator
Extends `configmate` to levarage Pydantic for config validation.

## Installation
```bash
pip install configmate-pydanticvalidator
```
OR directly with the extras of `configmate`:
```bash
pip install configmate[pydantic]
```

## Usage
By loading this plugin, `configmate` will use Pydantic to validate the config. 
Under the hood, a new validator is registered to `configmate.components.validators.TypeValidatorFactory`.
This validator will be used for any non-function passed to `validation` in configmate.get_config.

```python
from typing import Dict
import dataclasses

import configmate

@dataclasses.dataclass
class Config:
    host: str
    port: int

config = configmate.get_config(
    "config.json",  # main config
    validation=Dict[str, str], # pydantic will handle validation
)
## >> {'host': 'localhost', 'port': '8080'} # note that port is a string due to pydantic

config = configmate.get_config(
    "config.json",  # main config
    validation=Config, # pydantic will handle validation
) 
## >> Config(host='localhost', port=8080) # port is an int as expected

config = configmate.get_config(
    "config.json",  # main config
    validation=lambda config_dict: ..., # callables will be called with the config dict (as without this plugin)
)
## >> ... # whatever the callable returns
```