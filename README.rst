.. raw:: html

    <p align="center">
        <a href="#readme">
            <img alt="ConfigMate Logo" src="https://i.imgur.com/7DaKfnc.png" style="height: 60px;">
        </a>
    </p>
    <h1 align="center" style="font-size: 2.5em; margin: 0; padding: 0;">ConfigMate</h1>
    <p align="center" style="font-size: 1.2em; font-weight: 300; color: #555; margin: 0;">
        Practical and versatile configuration parsing in Python
    </p>
    <p align="center">
        <a href="https://pypi.python.org/pypi/configmate"><img alt="Pypi version" src="https://img.shields.io/pypi/v/configmate.svg"></a>
        <a href="https://pypi.python.org/pypi/configmate"><img alt="Python versions" src="https://img.shields.io/badge/python-3.8%5E-blue.svg"></a>
        <a href="https://pypi.python.org/pypi/configmate"><img alt="Downloads" src="https://img.shields.io/pypi/dm/configmate"></a>
        <a href="https://app.codacy.com/gh/ArthurBook/configmate/dashboard"><img alt="Code quality" src="https://img.shields.io/codacy/grade/451b032d35a2452ea05f14d66c30c8f3.svg"></a>
        <a href="https://github.com/ArthurBook/configmate/blob/master/LICENSE"><img alt="License" src="https://img.shields.io/github/license/ArthurBook/configmate"></a>
    </p>

------------------------------------------------------------------------


**ConfigMate** ... <DESC>
Configurate with Confidence

Installation
---------------
.. code-block:: bash

    pip install configmate[all]

    pip install "configmate[json,pydantic]"

If youv've already taken a look at the plugins, you can install only the ones you need:

```bash
pip install "configmate[json,pydantic]"
```

Key Features
---------------
- *Extensible file format support* - Automatic detection & parsing of all standard configuration file formats, customize with only necessary dependencies.
- *Environment variable support* - Automatically parse environment variables into configuration values while managing defaults in your configuration file.
- *CLI support* - Automatically generate a CLI interface & provide overrides with files or values directly from the command line.
- *Type validation* - Custom validation support, and seamless extension for Pydantic's fantastic validation capabilities.


Quick Tour
---------------

Why not...
---------------
- configparser
- json/toml/yaml fileparsers
- argparse pallets/click google/fire
- hydra