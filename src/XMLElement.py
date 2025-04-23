import re

class XMLElement:
    """
    Represents an XML element with a tag name, attributes, text content, and child elements.
    """
    def __init__(self, tag, properties, content="", children=None):
        """
        Initialize an XMLElement.

        Parameters:
        tag (str): The name of the XML tag.
        properties (dict): Attributes of the element as key-value pairs.
        content (str): Text content inside the element (excluding child elements).
        children (list of XMLElement): Nested child elements.
        """
        self.tag = tag
        self.properties = properties
        self.content = content  # Only text content, not including child elements
        self.children = children if children is not None else []


class XMLCollection:
    """
    Parses XML content into a tree of XMLElement objects and provides both tree and flat views.
    """
    def __init__(self, file_content):
        """
        Initialize the XMLCollection by parsing raw XML content.

        Parameters:
        file_content (list of str): Lines or segments of an XML document.
        """
        self.root_elements = self.parse_xml(file_content)
        # For backward compatibility, also maintain a flat list of all elements
        self.elements = self.flatten_elements(self.root_elements)

    def parse_xml(self, content):
        """
        Parse raw XML content into top-level XMLElement objects.

        Parameters:
        content (list of str): Lines or segments of the XML document.

        Returns:
        list of XMLElement: Top-level elements parsed from the content.
        """
        full_content = ''.join(content)
        return self.parse_elements(full_content)

    def parse_elements(self, content):
        """
        Recursively parse XML content and build an element tree.

        Parameters:
        content (str): A string of XML markup to parse.

        Returns:
        list of XMLElement: Parsed elements found at the current level.
        """
        elements = []
        pos = 0
        content_length = len(content)

        while pos < content_length:
            tag_start = content.find('<', pos)
            if tag_start == -1:
                break

            # Skip declarations and comments
            if content[tag_start:].startswith('<?') or content[tag_start:].startswith('<!'):
                tag_end = content.find('>', tag_start)
                if tag_end == -1:
                    break
                pos = tag_end + 1
                continue

            # Handle self-closing tags
            self_closing_match = re.match(r'<(\w+)([^>]*)/>', content[tag_start:])
            if self_closing_match:
                tag = self_closing_match.group(1)
                raw_properties = self_closing_match.group(2).strip()
                properties = {}
                if raw_properties:
                    prop_pattern = r'(\w+)=["\'](.*?)["\']'
                    properties = {m.group(1): m.group(2) for m in re.finditer(prop_pattern, raw_properties)}
                element = XMLElement(tag, properties, "", [])
                elements.append(element)
                pos = tag_start + len(self_closing_match.group(0))
                continue

            # Handle opening tags
            tag_match = re.match(r'<(\w+)([^>]*)>', content[tag_start:])
            if not tag_match:
                pos = tag_start + 1
                continue

            tag = tag_match.group(1)
            raw_properties = tag_match.group(2).strip()
            inner_start = tag_start + len(tag_match.group(0))

            open_tag = f'<{tag}'
            close_tag = f'</{tag}>'
            nesting_level = 1
            close_pos = inner_start

            # Find matching closing tag, accounting for nesting
            while nesting_level > 0 and close_pos < content_length:
                next_open = content.find(open_tag, close_pos)
                next_close = content.find(close_tag, close_pos)
                if next_close == -1:
                    break
                if next_open != -1 and next_open < next_close:
                    close_pos = next_open + len(open_tag)
                    if content[close_pos:close_pos+1] in [' ', '>', '/']:
                        nesting_level += 1
                else:
                    close_pos = next_close + len(close_tag)
                    nesting_level -= 1

            if nesting_level > 0:
                pos = tag_start + 1
                continue

            inner_content = content[inner_start:next_close]
            properties = {}
            if raw_properties:
                prop_pattern = r'(\w+)=["\'](.*?)["\']'
                properties = {m.group(1): m.group(2) for m in re.finditer(prop_pattern, raw_properties)}

            children = self.parse_elements(inner_content)
            pure_content = self.extract_pure_content(inner_content, children)
            element = XMLElement(tag, properties, pure_content, children)
            elements.append(element)
            pos = close_pos

        return elements

    def extract_pure_content(self, full_content, children):
        """
        Extract text content that is not part of any child elements.

        Parameters:
        full_content (str): The inner XML markup of a parent element.
        children (list of XMLElement): Child elements parsed from the content.

        Returns:
        str: The concatenated text outside of child tags.
        """
        if not children:
            return re.sub(r'<[^>]*>', '', full_content).strip()

        temp_content = full_content
        for child in children:
            child_tag = child.tag
            open_tag = f'<{child_tag}'
            close_tag = f'</{child_tag}>'
            start_pos = 0
            while True:
                tag_start = temp_content.find(open_tag, start_pos)
                if tag_start == -1:
                    break
                tag_end = temp_content.find('>', tag_start)
                if tag_end == -1:
                    start_pos = tag_start + 1
                    continue
                inner_start = tag_end + 1
                nesting_level = 1
                close_pos = inner_start
                while nesting_level > 0 and close_pos < len(temp_content):
                    next_open = temp_content.find(open_tag, close_pos)
                    next_close = temp_content.find(close_tag, close_pos)
                    if next_close == -1:
                        break
                    if next_open != -1 and next_open < next_close:
                        close_pos = next_open + len(open_tag)
                        if close_pos < len(temp_content) and temp_content[close_pos:close_pos+1] in [' ', '>', '/']:
                            nesting_level += 1
                    else:
                        close_pos = next_close + len(close_tag)
                        nesting_level -= 1
                if nesting_level > 0:
                    start_pos = tag_start + 1
                    continue
                full_match = temp_content[tag_start:close_pos]
                temp_content = temp_content.replace(full_match, '', 1)
                start_pos = tag_start
        temp_content = re.sub(r'<\w+[^>]*/>', '', temp_content)
        temp_content = re.sub(r'<[^>]*>', '', temp_content)
        return temp_content.strip()

    def flatten_elements(self, elements, flattened=None):
        """
        Convert a tree of XMLElement objects into a flat list.

        Parameters:
        elements (list of XMLElement): The nested elements to flatten.
        flattened (list of XMLElement): Accumulator for recursion (do not set externally).

        Returns:
        list of XMLElement: All elements in a single list.
        """
        if flattened is None:
            flattened = []
        for element in elements:
            flattened.append(element)
            self.flatten_elements(element.children, flattened)
        return flattened

