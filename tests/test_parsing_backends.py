import configparser as builtin_configparser

from configmate import interface, parsing_backends


def test_json_parser():
    data = interface.ConfigLike(
        """
    {
        "section1": {
            "option1": "value1",
            "option2": "value2"
        },
        "section2": {
            "option3": "value3",
            "option4": "value4"
        }
    }
    """
    )
    expected = {
        "section1": {"option1": "value1", "option2": "value2"},
        "section2": {"option3": "value3", "option4": "value4"},
    }
    parser = parsing_backends.JsonParser()
    result = parser.parse(data)
    assert result == expected


def test_ini_parser():
    data = interface.ConfigLike(
        """
    [Section1]
    option1 = value1
    option2 = value2

    [Section2]
    option3 = value3
    option4 = value4
    """
    )
    expected = {
        "Section1": {"option1": "value1", "option2": "value2"},
        "Section2": {"option3": "value3", "option4": "value4"},
    }
    configparser = builtin_configparser.ConfigParser()
    parser = parsing_backends.IniParser(configparser)
    result = parser.parse(data)
    assert result == expected


def test_xml_parser():
    data = interface.ConfigLike(
        """
    <root>
        <section1>
            <option1>value1</option1>
            <option2>value2</option2>
            <section1.1>
                <option1.1.1>value1.1.1</option1.1.1>
                <option1.1.2>value1.1.2</option1.1.2>
            </section1.1>
        </section1>
        <section2>
            <option3>value3</option3>
            <option4>value4</option4>
        </section2>
    </root>
    """
    )
    expected = {
        "section1": {
            "option1": "value1",
            "option2": "value2",
            "section1.1": {
                "option1.1.1": "value1.1.1",
                "option1.1.2": "value1.1.2",
            },
        },
        "section2": {"option3": "value3", "option4": "value4"},
    }
    parser = parsing_backends.XmlParser()
    result = parser.parse(data)
    print(result)
    assert result == expected


### Optional parsers from extensions
def test_toml_parser():
    data = interface.ConfigLike(
        """
    [section1]
    option1 = "value1"
    option2 = "value2"

    [section2]
    option3 = "value3"
    option4 = "value4"
    """
    )
    expected = {
        "section1": {"option1": "value1", "option2": "value2"},
        "section2": {"option3": "value3", "option4": "value4"},
    }
    parser = parsing_backends.TomlParser()
    result = parser.parse(data)
    assert result == expected


def test_yaml_safe_load_parser():
    data = interface.ConfigLike(
        """
    section1:
        option1: value1
        option2: value2

    section2:
        option3: value3
        option4: value4
    """
    )
    expected = {
        "section1": {"option1": "value1", "option2": "value2"},
        "section2": {"option3": "value3", "option4": "value4"},
    }
    parser = parsing_backends.YamlSafeLoadParser()
    result = parser.parse(data)
    assert result == expected


def test_yaml_unsafe_load_parser():
    data = interface.ConfigLike(
        """
    section1:
        option1: value1
        option2: value2

    section2:
        option3: value3
        option4: value4
    """
    )
    expected = {
        "section1": {"option1": "value1", "option2": "value2"},
        "section2": {"option3": "value3", "option4": "value4"},
    }
    parser = parsing_backends.YamlUnsafeLoadParser()
    result = parser.parse(data)
    assert result == expected
