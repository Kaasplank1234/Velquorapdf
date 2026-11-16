"""Synthetic Mach-O fixtures test audit decisions without pretending to run macOS."""
import json,plistlib,struct,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from macho import read_macho
from audit_macos import audit

def binary(minimum=0x000b0000,dependency=None):
    commands=[struct.pack('<IIIIII',0x32,24,1,minimum,0x000f0000,0)]
    if dependency:
        name=dependency.encode()+b'\0';size=(24+len(name)+7)&~7
        commands.append(struct.pack('<IIIIII',0xc,size,24,0,0,0)+name+b'\0'*(size-24-len(name)))
    return struct.pack('<IIIIIIII',0xfeedfacf,0x01000007,3,2,len(commands),sum(map(len,commands)),0,0)+b''.join(commands)

class Audit(unittest.TestCase):
    def test_thin_and_fat_headers(self):
        raw=binary(); self.assertEqual(read_macho(raw)[0]['minimum'],[11,0,0])
        fat=struct.pack('>II',0xcafebabe,1)+struct.pack('>IIIII',0x01000007,3,4096,len(raw),12)
        self.assertEqual(read_macho(fat+b'\0'*(4096-len(fat))+raw)[0]['arch'],'x86_64')
    def test_audit_target_and_dependency(self):
        with tempfile.TemporaryDirectory() as temp:
            app=Path(temp)/'Test.app';contents=app/'Contents';(contents/'MacOS').mkdir(parents=True);(contents/'Resources').mkdir()
            (contents/'Info.plist').write_bytes(plistlib.dumps({'CFBundleExecutable':'test','CFBundleIconFile':'icon.icns','LSMinimumSystemVersion':'11.0'}))
            (contents/'Resources/icon.icns').write_bytes(b'fixture')
            exe=contents/'MacOS/test';exe.write_bytes(binary())
            self.assertEqual(audit(app)['errors'],[])
            exe.write_bytes(binary(minimum=0x000c0000));self.assertTrue(any('Incompatible target' in x for x in audit(app)['errors']))
            exe.write_bytes(binary(dependency='/opt/homebrew/lib/libmissing.dylib'));self.assertTrue(any('Unresolved/external' in x for x in audit(app)['errors']))
            exe.write_bytes(binary(dependency='@loader_path/../Frameworks/libincluded.dylib'))
            frameworks=contents/'Frameworks';frameworks.mkdir();(frameworks/'libincluded.dylib').write_bytes(binary())
            self.assertEqual(audit(app)['errors'],[])
    def test_truncated_fat_refused(self):
        with self.assertRaises(ValueError):
            read_macho(struct.pack('>II',0xcafebabe,1)+struct.pack('>IIIII',0x01000007,3,4096,100,12))
if __name__=='__main__':unittest.main(verbosity=2)
