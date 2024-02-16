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

***

<p><strong>ConfigMate</strong> streamlines heavyweight config parsing into a sleek,
zero-boilerplate experience that lets you configure with confidence.</p>

<h2>Key Features</h2>

<ul>
  <li><strong>Extensible file format support</strong>: Automatic detection &amp; 
  parsing of all standard config file formats.</li>

  <li><strong>Environment variable interpolation</strong>: Parse environment 
  variables while keeping defaults in your configuration file.</li>

  <li><strong>Override files</strong>: Segregate base configuration management 
  such as DEV/STAG/PROD overrides in separate files.</li>

  <li><strong>CLI support</strong>: Override configuration values with files 
  or values directly from an automatically generated command line interface.</li>

  <li><strong>Type validation</strong>: Custom validation support, and seamless 
  extension for Pydantic's fantastic validation capabilities.</li>
</ul>

## Get started with ConfigMate

ConfigMate simplifies your configuration management. Get started with these easy steps:

### Installation

Install ConfigMate with all standard features:

```bash
pip install "configmate[standard]"
```

Alternatively, install with specific features (e.g., Pydantic):

```bash
pip install "configmate[pydantic]"
```

#### Set Up Configuration

1. Create a Configuration File:
   In this example we will do YAML, but ConfigMate supports all standard config file formats(json, toml, ini - you name it):

```yaml
# config.yaml
Database configuration:
    host: localhost
    port: ${DB_PORT:8000}
```

2. Load your config in python:
   Use ConfigMate to load and validate configuration in your script:

```python
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
```

3. Run Your Script with Different Configurations
   Execute your script, and override configurations using environment variables or command-line arguments:

```bash
# Default configuration
python example.py 
>> DatabaseConfig(host='localhost', port=8000)

# Override port using an environment variable
DB_PORT=9000 python example.py
>> DatabaseConfig(host='localhost', port=9000)

# Override host using a command-line argument
python example.py ++host foreignhost
>> DatabaseConfig(host='foreignhost', port=8000)
```

## Quick comparison with other config parsers

| Feature / Package                     | ConfigMate | ConfigParser | File Parsers (TOML/YAML/...) | ArgParse | Pallets/Click | Google/Fire | OmegaConf | Hydra |
|---------------------------------------|:----------:|:------------:|:---------------------------:|:--------:|:-------------:|:-----------:|:---------:|:-----:|\
| No Boilerplate                        |     ✅     |      ❌      |              ✅             |    ❌    |      ❌       |     ✅      |    ❌     |  ✅   |
| Support for Multiple File Formats     |     ✅     |      ❌      |              ✅             |    ❌    |      ❌       |     ❌      |    ❌     |  ❌   |
| Hierarchical Configuration            |     ✅     |      ✅      |              ✅             |    ❌    |      ❌       |     ✅      |    ✅     |  ✅   |
| Command-line Interface (CLI) Support  |     ✅     |      ❌      |              ❌             |    ✅    |      ✅       |     ✅      |    ❌     |  ✅   |
| Type Validation                       |     ✅     |      ❌      |          Partial            |    ❌    |      ✅       |     ❌      |  Partial  | Partial|
| Environment Variable Interpolation    |     ✅     |      ✅      |              ❌             |    ❌    |      ❌       |     ❌      |    ✅     |  ✅   |
| Dependency Count                      |     Low    |      Low     |            Low              |    Low   |      Low      |     Low     |    Low    | Moderate |
