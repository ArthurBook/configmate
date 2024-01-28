<!---
Copyright 2023 Arthur Book. All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->
<div style="text-align: center; max-width: 800px; margin: auto;">
    <div style="display: inline-block; text-align: center;">
        <div style="display: flex; align-items: center; justify-content: center; gap: 20px; margin-bottom: 10px;">
            <h1 style="margin: 0; padding: 0; font-size: 2.5em;">ConfigMate</h1>
            <img src="https://i.imgur.com/7DaKfnc.png" alt="Logo" style="height: 60px;">
        </div>
        <p style="margin: 0; font-size: 1.2em; font-weight: 300; color: #555">
            Practical yet versatile configuration parsing in Python
        </p>
        <p>
            <a href="https://pypi.org/project/configmate/" style="text-decoration: none;">
                <img alt="PyPI" src="https://img.shields.io/pypi/v/configmate.svg?style=flat&label=PyPI&color=blue">
            </a>
            <a href="https://pypi.org/project/configmate/" style="text-decoration: none;">
                <img alt="Python Versions" src="https://img.shields.io/pypi/pyversions/configmate.svg?style=flat&color=lightblue">
            </a>
            <a href="https://pypi.org/project/configmate/" style="text-decoration: none;">
                <img alt="Downloads" src="https://img.shields.io/pypi/dm/configmate.svg?style=flat">
            </a>
            <a href="https://opensource.org/licenses/Apache" style="text-decoration: none;">
                <img alt="License" src="https://img.shields.io/pypi/l/configmate.svg?style=flat&color=green">
            </a>
        </p>
    </div>
</div>

--------------------------------------------------------------------------------
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
