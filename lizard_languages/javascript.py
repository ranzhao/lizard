'''
Language parser for JavaScript
'''

from .code_reader import CodeReader
from .clike import CCppCommentsMixin
from .js_style_regex_expression import js_style_regex_expression
from .js_style_language_states import JavaScriptStyleLanguageStates


class JavaScriptReader(CodeReader, CCppCommentsMixin):
    # pylint: disable=R0903

    ext = ['js', 'we']
    language_names = ['javascript', 'js']

    @staticmethod
    @js_style_regex_expression
    def generate_tokens(source_code, extra=''):
        extra += r"|(?:\$\w+)"
        extra += r"|\<template\>.*<\/template\>"
        extra += r"|\<style\>.*<\/style\>"
        return CodeReader.generate_tokens(source_code, extra)

    def __init__(self, context):
        super(JavaScriptReader, self).__init__(context)
        self.parallel_states = [JavaScriptStyleLanguageStates(context)]
