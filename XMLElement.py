import re


class XMLElement():

    def __init__(self, tag, properties, content="", children=None):
        self.tag = tag
        self.properties = properties
        self.content = content  # Only text content, not including child elements
        self.children = children if children is not None else []

class XMLCollection():

    def __init__(self, file_content):
        self.root_elements = self.parse_xml(file_content)
        # For backward compatibility
        self.elements = self.flatten_elements(self.root_elements)

    def parse_xml(self, content):
        """Parse XML content into a tree structure of XMLElement objects"""
        # Join all lines into a single string
        full_content = ''.join(content)

        # Find all top-level tags
        return self.parse_elements(full_content)

    def parse_elements(self, content):
        """Recursively parse XML content and build element tree"""
        elements = []

        # Keep track of the position we're processing
        pos = 0
        content_length = len(content)

        while pos < content_length:
            # Look for the next tag
            tag_start = content.find('<', pos)

            if tag_start == -1:
                # No more tags
                break

            # Check if it's a self-closing tag
            if content[tag_start:].startswith('<?') or content[tag_start:].startswith('<!'):
                # Skip XML declarations and comments
                tag_end = content.find('>', tag_start)
                if tag_end == -1:
                    break
                pos = tag_end + 1
                continue

            # Check if it's a self-closing tag
            self_closing_match = re.match(r'<(\w+)([^>]*)/>', content[tag_start:])
            if self_closing_match:
                tag = self_closing_match.group(1)
                raw_properties = self_closing_match.group(2).strip()

                # Extract properties
                properties = {}
                if raw_properties:
                    prop_pattern = r'(\w+)=["\'](.*?)["\']'
                    properties = {m.group(1): m.group(2) for m in re.finditer(prop_pattern, raw_properties)}

                # Create element with no content or children
                element = XMLElement(tag, properties, "", [])
                elements.append(element)

                # Move past this tag
                pos = tag_start + len(self_closing_match.group(0))
                continue

            # It's a regular opening tag
            tag_match = re.match(r'<(\w+)([^>]*)>', content[tag_start:])
            if not tag_match:
                # Invalid tag, move on
                pos = tag_start + 1
                continue

            tag = tag_match.group(1)
            raw_properties = tag_match.group(2).strip()

            # Find the matching closing tag
            # We need to handle nested tags of the same type
            open_tag = f'<{tag}'
            close_tag = f'</{tag}>'

            # Skip past the opening tag
            inner_start = tag_start + len(tag_match.group(0))

            # Find the matching closing tag (accounting for nesting)
            nesting_level = 1
            close_pos = inner_start

            while nesting_level > 0 and close_pos < content_length:
                next_open = content.find(open_tag, close_pos)
                next_close = content.find(close_tag, close_pos)

                if next_close == -1:
                    # No matching closing tag found
                    break

                if next_open != -1 and next_open < next_close:
                    # Found another opening tag before the closing tag
                    close_pos = next_open + len(open_tag)
                    # Only count it if it's a complete tag and not part of another word
                    if content[close_pos:close_pos+1] in [' ', '>', '/']:
                        nesting_level += 1
                else:
                    # Found a closing tag
                    close_pos = next_close + len(close_tag)
                    nesting_level -= 1

            if nesting_level > 0:
                # No proper closing tag found
                pos = tag_start + 1
                continue

            # Extract the inner content
            inner_content = content[inner_start:next_close]

            # Extract properties
            properties = {}
            if raw_properties:
                prop_pattern = r'(\w+)=["\'](.*?)["\']'
                properties = {m.group(1): m.group(2) for m in re.finditer(prop_pattern, raw_properties)}

            # Recursively parse children
            children = self.parse_elements(inner_content)

            # Extract pure text content
            pure_content = self.extract_pure_content(inner_content, children)

            # Create element
            element = XMLElement(tag, properties, pure_content, children)
            elements.append(element)

            # Move past this entire element
            pos = close_pos

        return elements

    def extract_pure_content(self, full_content, children):
        """Extract text content that doesn't belong to child elements"""
        # If there are no children, all content is pure text
        if not children:
            return re.sub(r'<[^>]*>', '', full_content).strip()

        # Create a working copy of the content
        temp_content = full_content

        # For each child, remove its entire content (including tags and text)
        for child in children:
            # Find the exact match for this child in the content
            child_tag = child.tag

            # Look for the complete tag with its content, handling nested tags properly
            open_tag = f'<{child_tag}'
            close_tag = f'</{child_tag}>'

            # Find all potential matches
            start_pos = 0
            while True:
                # Find the next opening tag
                tag_start = temp_content.find(open_tag, start_pos)
                if tag_start == -1:
                    break

                # Make sure it's a complete tag
                tag_end = temp_content.find('>', tag_start)
                if tag_end == -1:
                    start_pos = tag_start + 1
                    continue

                # Find the matching closing tag (accounting for nesting)
                inner_start = tag_end + 1
                nesting_level = 1
                close_pos = inner_start

                while nesting_level > 0 and close_pos < len(temp_content):
                    next_open = temp_content.find(open_tag, close_pos)
                    next_close = temp_content.find(close_tag, close_pos)

                    if next_close == -1:
                        # No matching closing tag found
                        break

                    if next_open != -1 and next_open < next_close:
                        # Found another opening tag before the closing tag
                        close_pos = next_open + len(open_tag)
                        # Only count it if it's a complete tag and not part of another word
                        if close_pos < len(temp_content) and temp_content[close_pos:close_pos+1] in [' ', '>', '/']:
                            nesting_level += 1
                    else:
                        # Found a closing tag
                        close_pos = next_close + len(close_tag)
                        nesting_level -= 1

                if nesting_level > 0:
                    # No proper closing tag found
                    start_pos = tag_start + 1
                    continue

                # Remove the entire element (including tags and content)
                full_match = temp_content[tag_start:close_pos]
                temp_content = temp_content.replace(full_match, '', 1)

                # Continue searching from the current position
                start_pos = tag_start

        # Also remove self-closing tags (like <code some properties />)
        temp_content = re.sub(r'<\w+[^>]*/>', '', temp_content)

        # Remove any remaining XML tags
        temp_content = re.sub(r'<[^>]*>', '', temp_content)

        return temp_content.strip()

    def flatten_elements(self, elements, flattened=None):
        """Convert tree structure to flat list for backward compatibility"""
        if flattened is None:
            flattened = []

        for element in elements:
            flattened.append(element)
            self.flatten_elements(element.children, flattened)

        return flattened



