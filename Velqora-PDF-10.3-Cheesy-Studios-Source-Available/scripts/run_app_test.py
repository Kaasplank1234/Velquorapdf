"""Launch only the bundled executable, without Python/Qt/DYLD environment hints."""
import argparse,json,os,platform,subprocess,sys
from pathlib import Path

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('app');parser.add_argument('report');parser.add_argument('--platform',choices=['offscreen','cocoa'],default='cocoa');args=parser.parse_args()
    app=Path(args.app).resolve();report=Path(args.report).resolve();report.parent.mkdir(parents=True,exist_ok=True)
    env={k:v for k,v in os.environ.items() if not k.startswith(('PYTHON','QT_','QML','DYLD_','VIRTUAL_ENV','CONDA_'))}
    env['PATH']='/usr/bin:/bin:/usr/sbin:/sbin'
    env['QT_QPA_PLATFORM']=args.platform
    executable=app/'Contents/MacOS/Velqora PDF'
    try:
        process=subprocess.run([str(executable),'--self-test','--report',str(report)],env=env,cwd='/tmp',text=True,capture_output=True,timeout=120)
        report.with_suffix('.stdout.log').write_text(process.stdout or '')
        report.with_suffix('.stderr.log').write_text(process.stderr or '')
        if process.returncode:raise RuntimeError(f'Bundled app exited {process.returncode}: {process.stderr[-3000:]}')
        result=json.loads(report.read_text())
        if result.get('status')!='passed' or result.get('frozen') is not True or result.get('machine')!=platform.machine():
            raise RuntimeError(f'Invalid self-test result: {result}')
        print(json.dumps(result,indent=2))
    except Exception as ex:
        print(str(ex),file=sys.stderr);sys.exit(1)
