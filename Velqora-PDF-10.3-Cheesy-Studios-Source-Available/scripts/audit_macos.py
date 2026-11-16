"""Static audit of final .app, usable on macOS or Linux. Does not prove Big Sur execution."""
import argparse,json,plistlib,sys
from pathlib import Path
from macho import read_macho,MAGICS

def audit(app, architecture='x86_64'):
    app=Path(app).resolve();errors=[];binaries=[]
    info_path=app/'Contents/Info.plist'
    if not info_path.exists():raise ValueError('Missing Info.plist')
    info=plistlib.loads(info_path.read_bytes())
    if info.get('LSMinimumSystemVersion')!='11.0':errors.append('Info.plist minimum must be 11.0')
    executable=app/'Contents/MacOS'/info.get('CFBundleExecutable','')
    if not executable.is_file():errors.append('Missing application executable')
    if not (app/'Contents/Resources'/info.get('CFBundleIconFile','icon.icns')).is_file():errors.append('Missing application icon')
    records={}
    for path in app.rglob('*'):
        if path.is_symlink():
            if not path.exists():errors.append(f'Broken symlink: {path.relative_to(app)}')
            elif not path.resolve().is_relative_to(app):errors.append(f'External symlink: {path.relative_to(app)}')
            continue
        if not path.is_file():continue
        with path.open('rb') as f:
            if f.read(4) not in MAGICS:continue
        slices=read_macho(path.read_bytes());native=next((s for s in slices if s['arch']==architecture),None)
        if not native:errors.append(f'No {architecture} slice: {path.relative_to(app)}');continue
        if native['minimum'] is None:errors.append(f'Missing deployment target: {path.relative_to(app)}')
        elif native['minimum']>[11,0,0] or native['platform']!=1:errors.append(f'Incompatible target {native["minimum"]}: {path.relative_to(app)}')
        records[path.resolve()]=native
    main=records.get(executable.resolve(),{})
    def expand(value,loader):
        return Path(value.replace('@loader_path',str(loader.parent)).replace('@executable_path',str(executable.parent)))
    for path,native in records.items():
        dependencies=[]
        for dep in native['dependencies']:
            name=dep['name'];target=None
            if name.startswith(('/System/Library/','/usr/lib/')):
                dependencies.append(dict(dep,resolution='macOS system library'));continue
            if name.startswith('@rpath/'):
                for rp in native['rpaths']:
                    candidate=expand(rp,path)/name[len('@rpath/'):]
                    if candidate.exists():target=candidate.resolve();break
                if target is None:
                    for rp in main.get('rpaths',[]):
                        candidate=expand(rp,executable)/name[len('@rpath/'):]
                        if candidate.exists():target=candidate.resolve();break
            elif name.startswith(('@loader_path/','@executable_path/')):target=expand(name,path).resolve()
            elif name.startswith('/'):target=Path(name).resolve()
            if target is None or not target.exists() or not target.is_relative_to(app):
                errors.append(f'Unresolved/external dependency {name}: {path.relative_to(app)}')
                resolution='UNRESOLVED'
            else:resolution=str(target.relative_to(app))
            dependencies.append(dict(dep,resolution=resolution))
        binaries.append({'path':str(path.relative_to(app)),'minimum':native['minimum'],'rpaths':native['rpaths'],'dependencies':dependencies})
    if not main:errors.append(f'Main executable has no valid {architecture} Mach-O slice')
    if not binaries:errors.append('No Mach-O binaries found')
    return {'scope':'Static bundle audit only; Big Sur runtime test still required','architecture':architecture,'minimum_system_version':info.get('LSMinimumSystemVersion'),'binaries':binaries,'errors':errors}

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('app')
    parser.add_argument('--architecture', choices=['x86_64','arm64'], default='x86_64')
    args=parser.parse_args()
    try:report=audit(args.app,args.architecture)
    except Exception as ex:report={'errors':[str(ex)]}
    print(json.dumps(report,indent=2));sys.exit(bool(report['errors']))
