'''
This is an extension to lizard. It count the reccurance of every identifier
in the source code (ignoring the comments and strings), and then generate
a tag cloud based on the popularity of the identifiers.
The tag cloud is generated on an HTML5 canvas. So it will eventually save
the result to an HTML file and open the browser to show it.
'''
import json
import re
from fnmatch import fnmatch

from lizard_ext.command_executor import execute
from lizard_ext.extension_base import ExtensionBase


def cpd(path, languages, min_tokens, exclude_patterns):
    if not path.endswith('/'):
        path += '/'

    command = '~/Projects/pmd-bin-5.5.1/bin/run.sh cpd --files %s --language %s --minimum-tokens %d' % (path, languages, min_tokens)
    text = execute(command)
    cpd_infos = []
    lines, tokens, files = 0, 0, []
    for line in text:
        duplication_match = re.match(r'^Found a (\d+) line \((\d+) tokens\) duplication in the following files:', line)
        if duplication_match is not None:
            if lines > 0:
                assert len(files) > 0
                files = filter(lambda f: all(not fnmatch(f['file'], p) for p in exclude_patterns), files)
                if len(files) > 1:
                    cpd_infos.append({'lines': lines, 'tokens': tokens, 'files': files})
                files = []
            lines = int(duplication_match.group(1))
            tokens = int(duplication_match.group(2))

        duplication_file_match = re.match(r'^Starting at line (\d+) of (.+)', line)
        if duplication_file_match is not None:
            files.append({'start_line': duplication_file_match.group(1), 'file': duplication_file_match.group(2)})

    if lines > 0:
        assert len(files) > 0
        files = filter(lambda f: all(not fnmatch(f['file'], p) for p in exclude_patterns), files)
        if len(files) > 1:
            cpd_infos.append({'lines': lines, 'tokens': tokens, 'files': files})

    return cpd_infos


class LizardExtension(ExtensionBase):
    def __init__(self, option, context=None):
        self.option = option
        pass

    def _state(self, token):
        pass

    @staticmethod
    def set_args(parser):
        parser.add_argument("-cpd", "--cpd_file",
                            help='''update parse result to json ''',
                            type=str,
                            dest="cpd_file")
        parser.add_argument("-tokens", "--minimum_tokens",
                            help='''the minimum token length which should be reported as a duplicate.''',
                            type=int,
                            dest="cpd_tokens",
                            default=100)

    def print_result(self):
        self.option.cpd_infos = []
        for path in self.option.paths:
            self.option.cpd_infos += (cpd(path, self.option.languages[0], self.option.cpd_tokens, self.option.exclude))

        if hasattr(self.option, 'paths') and len(self.option.cpd_infos) > 0:
            with open(self.option.cpd_file, 'w') as f:
                f.write(json.dumps(self.option.cpd_infos, sort_keys=True, indent=4))
