'''
This is an extension to lizard. It count the reccurance of every identifier
in the source code (ignoring the comments and strings), and then generate
a tag cloud based on the popularity of the identifiers.
The tag cloud is generated on an HTML5 canvas. So it will eventually save
the result to an HTML file and open the browser to show it.
'''
import csv
import re
from fnmatch import fnmatch

from lizard_ext.command_executor import execute
from lizard_ext.extension_base import ExtensionBase

LANGUAGE_EXTENSION = {'java': ['java', 'xml', 'gradle']
                , 'objectivec': ['m', 'mm', 'h', 'c', 'cpp', 'plist', 'xib']
                , 'javascript': ['js', 'css', 'html']}

class Activity(dict):
    def __missing__(self, key):
        return 0


def _put(files, filename):
    files[filename] += 1


def _is_supported(filename, extension, exclude):
    return filename[filename.rfind('.') + 1:] in extension and all(not fnmatch(filename, p) for p in exclude)


def _git_activity(path, languages, exclude):
    if not path.endswith('/'):
        path += '/'

    extensions = []
    for language in languages:
        extensions += LANGUAGE_EXTENSION[language];

    command = 'cd %s;' % path + ' git log --numstat --author-date-order  --pretty=format:"%h %ad %aE" --date=short --since=1.month.ago HEAD'
    lines = execute(command)
    activity = Activity()
    for line in lines:
        match_object = re.match(r'^(\d+)\s+(\d+)\s+(.*)', line)
        if match_object is not None and _is_supported(match_object.group(3), extensions, exclude):
            _put(activity, path + match_object.group(3))

    return activity


class LizardExtension(ExtensionBase):
    def __init__(self, option, context=None):
        self.option = option
        self.active_files_info = []
        if hasattr(option, 'paths'):
            self.active_files = _git_activity(option.paths[0], option.languages, option.exclude)
        pass

    def _state(self, token):
        pass

    @staticmethod
    def set_args(parser):
        parser.add_argument("-activity", "--activity_file",
                            help='''update parse result to csv ''',
                            type=str,
                            dest="activity_file")

    def reduce(self, fileinfo):
        '''
        Combine the statistics from each file.
        Because the statistics came from multiple thread tasks. This function
        needs to be called to collect the combined result.
        '''
        def max_ccn(f):
            cyclomatic_complexities = list(func.cyclomatic_complexity for func in f.function_list)
            return 0 if (cyclomatic_complexities == []) else max(cyclomatic_complexities)

        if self.active_files.has_key(fileinfo.filename):
            self.active_files_info.append({'file': fileinfo.filename
                                              , 'activity': self.active_files[fileinfo.filename]
                                              , 'nloc': fileinfo.nloc
                                              , 'fanout': len(fileinfo.dependency_list)
                                              , 'ccn': max_ccn(fileinfo)})

    def print_result(self):
        rows = sorted(self.active_files_info, key=lambda r: r['activity'], reverse=True)
        header = ['file', 'activity', 'nloc', 'fanout', 'ccn']
        with open(self.option.activity_file, 'w') as f:
            f_csv = csv.DictWriter(f, header)
            f_csv.writeheader()
            f_csv.writerows(rows)
