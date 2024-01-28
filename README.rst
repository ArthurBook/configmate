.. raw:: html

    <p align="center">
        <a href="#readme">
            <img alt="ConfigMate Logo" src="https://i.imgur.com/7DaKfnc.png" style="height: 172px;">
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

**ConfigMate** streamlines heavyweight config parsing into a sleek, zero-boilerplate experience that lets you configure with confidence.

Key Features
---------------
- *Extensible file format support*: - Automatic detection & parsing of all standard config file formats.
- *Environment variable interpolation*: - Parse environment variables while keeping defaults in your configuration file.
- *Override files*: Segregate base configuration management and DEV/STAG/PROD overrides in separate files.
- *CLI support*: Override configuration values with files or values dirctly from an automatically generated command line interface.
- *Type validation*: - Custom validation support, and seamless extension for Pydantic's fantastic validation capabilities.

Get Started with ConfigMate
-------------------------------

ConfigMate simplifies your configuration management. Get started with these easy steps:

**Installation**

Install ConfigMate with all standard features:

.. code-block:: bash

    pip install "configmate[standard]"

Alternatively, install with specific features (e.g., Pydantic):

.. code-block:: bash

    pip install "configmate[pydantic]"

**Set Up Configuration**

1. **Create a Configuration File:**

   Define your database configuration in `config.yaml`:

   .. code-block:: yaml

        # config.yaml
        Database configuration:
            host: localhost
            port: ${DB_PORT:8000}

2. **Integrate with Your Script:**

   Use ConfigMate to load and validate configuration in your script:

   .. code-block:: python

        # example.py
        import configmate
        import dataclasses

        @dataclasses.dataclass
        class DatabaseConfig:
            host: str
            port: int

        config = configmate.get_config(
            "config.yaml", 
            section='Database configuration', 
            validation=DatabaseConfig
        )
        print(config)

**Run Your Script with Different Configurations**

Execute your script, and override configurations using environment variables or command-line arguments:

.. code-block:: bash

    # Default configuration
    python example.py 
    >> DatabaseConfig(host='localhost', port=8000)

    # Override port using an environment variable
    DB_PORT=9000 python example.py
    >> DatabaseConfig(host='localhost', port=9000)

    # Override host using a command-line argument
    python example.py ++host foreignhost
    >> DatabaseConfig(host='foreignhost', port=8000)


Quick comparison
----------------

.. role:: centered
   :class: centered

.. role:: centered
   :class: centered

.. list-table::
   :widths: 25 10 10 10 10 10 10 10 10
   :header-rows: 1

   * - Feature / package
     - configmate
     - configparser
     - fileparsers (toml/yaml...)
     - argparse
     - pallets/click
     - google/fire
     - omegaconf
     - hydra
   * - No Boilerplate
     - :centered:`✅`
     - :centered:`❌`
     - :centered:`✅`
     - :centered:`❌`
     - :centered:`❌`
     - :centered:`✅`
     - :centered:`❌`
     - :centered:`✅`
   * - Support for Multiple File Formats
     - :centered:`✅`
     - :centered:`❌`
     - :centered:`✅`
     - :centered:`❌`
     - :centered:`❌`
     - :centered:`❌`
     - :centered:`❌`
     - :centered:`❌`
   * - Hierarchical Configuration
     - :centered:`✅`
     - :centered:`✅`
     - :centered:`✅`
     - :centered:`❌`
     - :centered:`❌`
     - :centered:`✅`
     - :centered:`✅`
     - :centered:`✅`
   * - Command-line Interface (CLI) Support
     - :centered:`✅`
     - :centered:`❌`
     - :centered:`❌`
     - :centered:`✅`
     - :centered:`✅`
     - :centered:`✅`
     - :centered:`❌`
     - :centered:`✅`
   * - Type Validation
     - :centered:`✅`
     - :centered:`❌`
     - :centered:`Partial`
     - :centered:`❌`
     - :centered:`✅`
     - :centered:`❌`
     - :centered:`Partial`
     - :centered:`Partial`
   * - Environment Variable Interpolation
     - :centered:`✅`
     - :centered:`✅`
     - :centered:`❌`
     - :centered:`❌`
     - :centered:`❌`
     - :centered:`❌`
     - :centered:`✅`
     - :centered:`✅`
   * - Dependency Count
     - :centered:`Low`
     - :centered:`Low`
     - :centered:`Low`
     - :centered:`Low`
     - :centered:`Low`
     - :centered:`Low`
     - :centered:`Low`
     - :centered:`Moderate`
 
