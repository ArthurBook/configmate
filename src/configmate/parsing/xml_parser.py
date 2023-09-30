from typing import Any, Dict, Optional, Union
from xml.etree import ElementTree as etree

from configmate.parsing import base_parser


class XmlParser(base_parser.BaseConfigParser):
    def _parse(self, data: str) -> Any:
        root = etree.fromstring(data)
        return convert_to_dict(root)


Tree = Dict[str, Optional[Union[str, "Tree"]]]


def convert_to_dict(element: etree.Element) -> Optional[Union[str, Tree]]:
    children = list(element)
    if not children:
        return element.text

    return {
        child.tag: child.text if not list(child) else convert_to_dict(child)
        for child in children
    }
