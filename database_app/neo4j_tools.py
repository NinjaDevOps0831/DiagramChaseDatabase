

def escape_regex_str(string):
    string = string.replace('\\', r'\\')  # BUGFIX: double escape is usually needed in Neo4j regex
    #string = string.replace("'", r"\'")
    string = string.replace('{', r'\{')
    string = string.replace('}', r'\}')
    string = string.replace('(', r'\(')
    string = string.replace(')', r'\)')
    return string


def neo4j_escape_regex_str(string):
    string = string.replace('\\', r'\\\\')  # BUGFIX: double escape is usually needed in Neo4j regex
    string = string.replace("'", r"\'")
    string = string.replace('{', r'\{')
    string = string.replace('}', r'\}')
    string = string.replace('(', r'\(')
    string = string.replace(')', r'\)')
    return string