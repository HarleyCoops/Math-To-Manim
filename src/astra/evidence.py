"""Build structured text evidence without duplicating a rendered scene's source."""
import json
from pathlib import Path


def text_evidence(folder, paths):
    result={}
    for path in paths:
        path=Path(path)
        if path.suffix not in {'.json','.py'}:continue
        text=path.read_text(encoding='utf-8')
        result[path.relative_to(folder).as_posix()]=json.loads(text) if path.suffix=='.json' else text
    sources={name:value for name,value in result.items() if name.endswith('.py')}
    for name,value in list(result.items()):
        if isinstance(value,dict) and isinstance(value.get('content'),str):
            match=next((source for source,text in sources.items() if text==value['content']),None)
            if match:
                result[name]=dict(value,content={'exact_source_supplied_under':match})
    return result


def design_summary(report):
    return {'policy':report['policy'],'advisory_only':True,'priority':report['priority'],
            'findings':[{k:f[k] for k in ['id','score','confidence','status','action','repair']}
                        for f in report['findings']]}
