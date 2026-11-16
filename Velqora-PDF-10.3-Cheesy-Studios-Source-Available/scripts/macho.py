"""Read Mach-O metadata without executing it; usable on Linux for preflight.
Only binary headers/load commands are inspected, never patched.
"""
import struct

X86_64=0x01000007
ARM64=0x0100000C
MAGICS=(b'\xce\xfa\xed\xfe',b'\xcf\xfa\xed\xfe',b'\xfe\xed\xfa\xce',b'\xfe\xed\xfa\xcf',b'\xca\xfe\xba\xbe',b'\xbe\xba\xfe\xca',b'\xca\xfe\xba\xbf',b'\xbf\xba\xfe\xca')

def version(n):return [n>>16,(n>>8)&255,n&255]

def read_macho(data):
    """Return one dict per slice, or [] for a non-Mach-O file."""
    magic=data[:4]
    if magic not in MAGICS:return []
    if magic in MAGICS[4:]:
        endian='>' if magic in (MAGICS[4],MAGICS[6]) else '<'
        is64=magic in MAGICS[6:]
        count=struct.unpack_from(endian+'I',data,4)[0]
        if count>128:raise ValueError('Invalid fat architecture count')
        slices=[]
        for n in range(count):
            at=8+n*(32 if is64 else 20)
            fields=struct.unpack_from(endian+('IIQQII' if is64 else 'IIIII'),data,at)
            offset,size=fields[2:4]
            if offset+size>len(data):raise ValueError('Truncated fat binary')
            slices.extend(read_macho(data[offset:offset+size]))
        return slices
    endian='<' if magic in MAGICS[:2] else '>'
    is64=magic in (MAGICS[1],MAGICS[3])
    cpu,subcpu,kind,ncmds,sizeofcmds=struct.unpack_from(endian+'IIIII',data,4)
    at=32 if is64 else 28
    if at+sizeofcmds>len(data):raise ValueError('Truncated Mach-O load commands')
    result={'cpu':cpu,'arch':{X86_64:'x86_64',ARM64:'arm64'}.get(cpu,hex(cpu)), 'filetype':kind,'minimum':None,'platform':None,'dependencies':[],'rpaths':[]}
    for _ in range(ncmds):
        cmd,size=struct.unpack_from(endian+'II',data,at)
        if size<8 or at+size>len(data):raise ValueError('Invalid Mach-O command size')
        if cmd==0x32:
            platform,minos=struct.unpack_from(endian+'II',data,at+8)
            result.update(minimum=version(minos),platform=platform)
        elif cmd==0x24:
            result.update(minimum=version(struct.unpack_from(endian+'I',data,at+8)[0]),platform=1)
        elif cmd in (0xc,0x80000018,0x8000001f,0x80000023,0x20):
            offset=struct.unpack_from(endian+'I',data,at+8)[0]
            name=data[at+offset:at+size].split(b'\0',1)[0].decode('utf-8')
            result['dependencies'].append({'name':name,'weak':cmd==0x80000018})
        elif cmd==0x8000001c:
            offset=struct.unpack_from(endian+'I',data,at+8)[0]
            result['rpaths'].append(data[at+offset:at+size].split(b'\0',1)[0].decode('utf-8'))
        at+=size
    return [result]
