'''
Language parser for JavaScript
'''
from lizard_languages import JavaScriptReader
from .code_reader import CodeReader
from .js_style_regex_expression import js_style_regex_expression
from .js_style_language_states import JavaScriptStyleLanguageStates


class VueReader(JavaScriptReader):
    # pylint: disable=R0903

    ext = ['vue', 'we']
    language_names = ['vue', 'weex']

    @staticmethod
    # @js_style_regex_expression
    def generate_tokens(source_code, extra=''):
        extra += r"|\<template\>.*<\/template\>"
        extra += r"|\<style\>.*<\/style\>"
        return JavaScriptReader.generate_tokens(source_code, extra)

    def __init__(self, context):
        super(VueReader, self).__init__(context)
        # self.parallel_states = [JavaScriptStyleLanguageStates(context)]
