'''output in html format'''
import json


def json_output(result, options, _):
    result = filter(lambda f: f.function_list != [], result)
    saved_fileinfos = []
    for fileinfo in result:
        method = [{'name':function.name, 'ccn':function.cyclomatic_complexity, 'start_line':function.start_line} for function in fileinfo.function_list]
        saved_fileinfos.append({'name':fileinfo.filename, 'nloc':fileinfo.nloc, 'children':method, 'fanout':len(fileinfo.dependency_list)})

    print(json.dumps(saved_fileinfos, sort_keys=True, indent=4))
    return 0
