'''
This is an extension to lizard. It count the reccurance of every identifier
in the source code (ignoring the comments and strings), and then generate
a tag cloud based on the popularity of the identifiers.
The tag cloud is generated on an HTML5 canvas. So it will eventually save
the result to an HTML file and open the browser to show it.
'''
import re

from lizard_ext.keywords import IGNORED_WORDS
from lizard_ext.ignore_dependency import IGNORED_DEPENDENCIES

class LizardExtension(object):
    ignoreList = IGNORED_WORDS
    match_pattern = re.compile(r"[<\"](\w+(/\w+){0,}\.h)[>\"]", re.M | re.S)

    def __init__(self, option=None):
        self.result = {}
        self.rut_tokens = []
        self.br_count = 0

    def __call__(self, tokens, reader):
        '''
        The function will be used in multiple threading tasks.
        So don't store any data with an extension object.
        '''

        dependency_keywords = {
            'java': 'import',
            'm': '#import',
            'js': 'require'
        }

        dependency_matches = {
            'java': self._state_match_until_semicolon,
            'm': self._state_match_next_token,
            'js': self.in_assertion
        }

        reader_type = reader.ext[0]
        self.context = reader.context
        self.dependency_keyword = dependency_keywords[reader_type]
        self.dependency_match_state = dependency_matches[reader_type]
        self._state = self._state_global

        for token in tokens:
            self._state(token)
            yield token

    def print_result(self):
        pass

    def _state_global(self, token):
        if token == self.dependency_keyword:
            self._state = self.dependency_match_state

    # @staticmethod
    def read_until_then(tokens):
        def decorator(func):
            def read_until_then_token(self, token):
                if token in tokens:
                    func(self, token, self.rut_tokens)
                    self.rut_tokens = []
                else:
                    self.rut_tokens.append(token)

            return read_until_then_token

        return decorator

    @read_until_then(';')
    def _state_match_until_semicolon(self, token, saved):
        if token == ';':
            dependency = ''.join(filter(lambda x: x not in ['static'], saved))
            if not filter(lambda x: dependency.startswith(x), IGNORED_DEPENDENCIES): self.context.add_dependency(
                dependency)
            self._state = self._state_global

    # @staticmethod
    def read_inside_brackets_then(brs):
        def decorator(func):
            def read_until_matching_brackets(self, token):
                self.br_count += {brs[0]: 1, brs[1]: -1}.get(token, 0)
                if self.br_count == 1 and token is not brs[0]:
                    self.rut_tokens.append(token)
                if self.br_count == 0:
                    func(self, self.rut_tokens)
                    self.rut_tokens = []
            return read_until_matching_brackets
        return decorator

    @read_inside_brackets_then("()")
    def in_assertion(self, saved):
        dependency = ''.join(filter(lambda x: x not in ['static'], saved))
        if not filter(lambda x: dependency.startswith(x), IGNORED_DEPENDENCIES): self.context.add_dependency(
            dependency)
        self._state = self._state_global

    def _state_match_next_token(self, token):
        match = self.match_pattern.match(token)
        if match:
            self.context.add_dependency(match.group(1))
        self._state = self._state_global
