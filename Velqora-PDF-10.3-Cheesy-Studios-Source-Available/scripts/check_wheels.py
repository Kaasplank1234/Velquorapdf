"""Static preflight of macOS wheels; does NOT prove Big Sur execution."""
import json,sys,zipfile,hashlib
from pathlib import Path
from macho import read_macho,MAGICS

def inspect(directory):
    reports=[];errors=[]
    for wheel in sorted(Path(directory).glob('*.whl')):
        binaries=[]
        with zipfile.ZipFile(wheel) as z:
            for info in z.infolist():
                if info.is_dir() or info.file_size<4:continue
                with z.open(info) as f:
                    if f.read(4) not in MAGICS:continue
                slices=read_macho(z.read(info))
                intel=next((s for s in slices if s['arch']=='x86_64'),None)
                if not intel:errors.append(f'{wheel.name}:{info.filename}: no Intel slice')
                else:
                    binaries.append({'path':info.filename,'minimum':intel['minimum'],'platform':intel['platform']})
                    if intel['minimum'] is None or intel['minimum']>[11,0,0] or intel['platform']!=1:
                        errors.append(f'{wheel.name}:{info.filename}: incompatible target {intel["minimum"]}')
        reports.append({'wheel':wheel.name,'sha256':hashlib.sha256(wheel.read_bytes()).hexdigest(),'intel_binaries':binaries})
    if not reports:errors.append('No wheels found')
    return {'scope':'Static headers only; not a runtime test, not a final app audit','wheels':reports,'errors':errors}

if __name__=='__main__':
    report=inspect(sys.argv[1]);print(json.dumps(report,indent=2));sys.exit(bool(report['errors']))
