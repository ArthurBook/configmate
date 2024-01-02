# configmate: universal, practical configuration parser for Python. 
With support for multiple file format backends, this package provides robust validation and allows for configuration overrides. Engineered for straightforward and reliable integration into Python applications.


## Key Features:
- *Support for Multiple File Formats*: ConfigMate supports JSON, YAML, TOML and XML formats.
- *Overrides*: Allows for easy management of multiple config_files.
- *Environment Variable Interpolation* using the syntax `${VAR_NAME:default_value}`.

## Example:
Let's say you have a Python app that needs to be deployed in multiple environments. You want to be able to configure the application using config files, but you also want to be able to override certain settings in the production environment:
```json
// config.json (This is the default configuration file.)
{
    "db": "DEV",
    "port": "${PORT:8080}" // default to 8080 if PORT is not set in env
}

// prod_config.json (overrides certain settings in the prod environment.)
{
    "db": "PROD", // overrides db in prod deployment
}
```

Here's how you use configmate to load and validate these configurations in a Python application:
```python
# app.py
import configmate
import pydantic


class Config(pydantic.BaseModel):
    db: str
    port: int


config = configmate.get_config(
    "config.json",  # main config
    "prod_config.json",  # prod overlay
    validation=lambda kwargs: Config(**kwargs),
)

print(config)
```

Now, when you run the application, the configuration files are parsed in order and you can override the port using an environment variable:
```bash
PORT=9000 python app.py
## db='PROD' port=9000
```
