import os
import argparse
import binascii

from macholib.util import is_platform_file
from macholib.MachO import MachO
from macholib.mach_o import *
    
class UUIdGetter:           
    m_pathToMachObject = ''

    def GetMachObject(self, path):
        if not os.path.exists(path):
            print '%s: No such file or directory' % path
            exit()
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for fn in files:
                    path = os.path.join(root, fn)
                    if is_platform_file(path):
                        self.m_pathToMachObject = path
                        return True
        else:
            if is_platform_file(path):
                self.m_pathToMachObject = path
                return True
        return False

    def PrintUUIdForPlatform(self, header):
        if header.MH_MAGIC == MH_MAGIC_64:
            sz = '64-bit'
        else:
            sz = '32-bit'

        arch = CPU_TYPE_NAMES.get(header.header.cputype,  header.header.cputype)
        cpuType = get_cpu_subtype(header.header.cputype,  header.header.cpusubtype)

        print '%s %s %s' % (arch, cpuType, sz)                    

        UUID = 0
        for cmd in header.commands:
            (cmd_load, cmd_cmd, cmd_data) = cmd
            if cmd_load.cmd == LC_UUID:
                UUID = cmd_cmd.uuid
        UUID_str = binascii.hexlify(bytearray(UUID))
        print 'UUID: ' + UUID_str

    def PrintUUID(self, bundle):          
        if not self.GetMachObject(bundle):
            print 'No mach object found'
            return            
        print 'Mach object found: ' + self.m_pathToMachObject
 
        machObject = MachO(self.m_pathToMachObject)
        
        for header in machObject.headers:
            self.PrintUUIdForPlatform(header)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Tool for getting UUID.')
    parser.add_argument('bundle', metavar='bundle', type=str, help='path to bundle or dSYM')
    args = parser.parse_args()
    uuidGetter = UUIdGetter()  
    uuidGetter.PrintUUID(args.bundle)
