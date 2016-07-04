'''
Language parser for Java
'''

from .clike import CLikeReader, CLikeStates, CLikeNestingStackStates
from .code_reader import CodeStateMachine
from .ignore_dependency import IGNORED_DEPENDENCIES


class JavaReader(CLikeReader):
    # pylint: disable=R0903

    ext = ['java']
    language_names = ['java']

    def __init__(self, context):
        super(JavaReader, self).__init__(context)
        self.parallel_states = [
                JavaStates(context),
                CLikeNestingStackStates(context)]


class JavaStates(CLikeStates):  # pylint: disable=R0903
    def _state_old_c_params(self, token):
        if token == '{':
            self._state_dec_to_imp(token)

    def _state_global(self, token):
        if token == '@':
            self._state = self._state_decorator
            return
        # if token == 'import':
        #     self._state = self._imports
        #     return
        super(JavaStates, self)._state_global(token)

    def _state_decorator(self, _):
        self._state = self._state_post_decorator

    def _state_post_decorator(self, token):
        if token == '.':
            self._state = self._state_decorator
        else:
            self._state = self._state_global
            self._state(token)
    #
    # @CodeStateMachine.read_until_then(';')
    # def _imports(self, token, saved):
    #     if token == ';':
    #         dependency = ''.join(filter(lambda x: x not in ['static'], saved))
    #         if not filter(lambda x: dependency.startswith(x), IGNORED_DEPENDENCIES): self.context.add_dependency(dependency)
    #         self._state = self._state_global
