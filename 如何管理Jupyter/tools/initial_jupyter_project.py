"""
Initialize a Data-Science-friendly project.

Dependency:
    python: only test 3.6.*

author: Huang Baochen (Cube)
create at: 2018-11-04
update at: 2018-11-04
"""
import pathlib, sys
import getopt
import json
from datetime import datetime


if __name__ == '__main__':
    if len(sys.argv) == 1:
        target_dir = pathlib.Path('.') 
    else:
        target_dir = pathlib.Path(sys.argv[1])
    
    dir_name = input('Project directory name: ')
    project_name = input('Project name: ')
    author = input('Anthor: ')
    tags = input('Tags(using \', \' as sep): ').split(', ')
    info_json = dict(
        dir_name = dir_name,
        author = author,
        create_at = datetime.now().strftime('%y-%m-%d'),
        description = "",
        tags = tags
    )

    p = target_dir / dir_name

    path_new = [ 
        p / 'SQL',
        p / 'notebook',
        p / 'src',
        p / 'data', 
        p / 'data' / 'pickle',
        p / 'data' / 'excel',
        p / 'data' / 'csv',
        p / 'temp_module',
        p / 'output',
        p / 'temp'
    ]
    list(map(lambda x: x.mkdir(parents=True, exist_ok=True), path_new))

    file_new = [
        p / 'README.md',
        p / 'SQL' / 'contents.md',
        p / 'data' / 'contents.md',
        p / 'info.json',
        p / 'temp_module' / '__init__.py',
    ]

    list(map(lambda x: x.touch(), file_new))

    open(p / 'info.json', 'w').write(json.dumps(info_json))

    

