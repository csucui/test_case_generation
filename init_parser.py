from tree_sitter import Language, Parser,Node

PYTHON_LANGUAGE = Language('build/my-languages.so', 'python')
CPP_LANGUAGE = Language('build/my-languages.so', 'cpp')
JAVA_LANGUAGE = Language('build/my-languages.so', 'java')

def init_python_parser():
    python_parser = Parser()
    python_parser.set_language(PYTHON_LANGUAGE)
    return python_parser

def init_app_parser():
    cpp_parser = Parser()
    cpp_parser.set_language(CPP_LANGUAGE)
    return cpp_parser

def init_python_parser():
    java_parser = Parser()
    java_parser.set_language(JAVA_LANGUAGE)
    return java_parser
