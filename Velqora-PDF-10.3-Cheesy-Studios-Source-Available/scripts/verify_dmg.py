"""Mount read-only; verify app, Applications link and bundled startup; always detach."""
import argparse,hashlib,json,os,platform,plistlib,subprocess,sys,tempfile,time
from pathlib import Path
from audit_macos import audit

def main():
    parser=argparse.ArgumentParser();parser.add_argument('dmg');parser.add_argument('--reports',default='dist/reports');args=parser.parse_args()
    dmg=Path(args.dmg).resolve();reports=Path(args.reports).resolve();reports.mkdir(parents=True,exist_ok=True)
    result={'status':'failed','dmg':dmg.name,'sha256':hashlib.sha256(dmg.read_bytes()).hexdigest(),'big_sur_runtime_verified':False}
    mounted=False
    with tempfile.TemporaryDirectory(prefix='librepdf-dmg-') as temp:
        mount=Path(temp)/'volume';mount.mkdir()
        try:
            subprocess.run(['hdiutil','verify',str(dmg)],check=True)
            attach=subprocess.run(['hdiutil','attach','-readonly','-nobrowse','-plist','-mountpoint',str(mount),str(dmg)],check=True,capture_output=True)
            mounted=True
            info=plistlib.loads(attach.stdout)
            result['volume_attached']=any(x.get('mount-point') and Path(x['mount-point']).resolve()==mount.resolve() for x in info.get('system-entities',[]))
            if not result['volume_attached']:raise RuntimeError('Unexpected mount point')
            app=mount/'Velqora PDF.app';shortcut=mount/'Applications'
            if not app.is_dir() or not shortcut.is_symlink() or os.readlink(shortcut)!='/Applications':raise RuntimeError('Missing .app or incorrect Applications shortcut')
            contents=sorted(p.name for p in mount.iterdir());result['root_contents']=contents
            bundle=audit(app,platform.machine());(reports/'dmg-bundle-audit.json').write_text(json.dumps(bundle,indent=2))
            if bundle['errors']:raise RuntimeError('Mounted bundle failed dependency/architecture audit')
            subprocess.run(['codesign','--verify','--deep','--strict',str(app)],check=True)
            subprocess.run([sys.executable,str(Path(__file__).with_name('run_app_test.py')),str(app),str(reports/'dmg-app-selftest.json'),'--platform','cocoa'],check=True)
            result['status']='passed'
        except Exception as ex:
            result['error']=str(ex);raise
        finally:
            if mounted:
                for attempt in range(5):
                    detached = subprocess.run(['hdiutil', 'detach', str(mount)], capture_output=True)
                    if detached.returncode == 0:
                        break
                    time.sleep(1)
                else:
                    subprocess.run(['hdiutil', 'detach', '-force', str(mount)], check=True)
            (reports/'dmg-verification.json').write_text(json.dumps(result,indent=2))
if __name__=='__main__':main()
