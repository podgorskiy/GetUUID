import os
import argparse
import binascii

from macholib.util import is_platform_file
from macholib.MachO import MachO
from macholib.mach_o import *
    
class UUIdGetter:           
    def GetMachObject(self, path):
        if not os.path.exists(path):
            raise Exception('No such file or directory: ' + path)
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for fn in files:
                    path = os.path.join(root, fn)
                    if is_platform_file(path):
                        return path
        else:
            if is_platform_file(path):
                return path
        raise Exception('No mach object found')
    
    def OpenBundle(self, pathToBundle):
        pathToMachObject = self.GetMachObject(pathToBundle)
        self.m_machObject = MachO(pathToMachObject)
    
    def GetPlatform(self, header):
        if header.MH_MAGIC == MH_MAGIC_64:
            sz = '64-bit'
        else:
            sz = '32-bit'
        arch = CPU_TYPE_NAMES.get(header.header.cputype,  header.header.cputype)
        cpuType = get_cpu_subtype(header.header.cputype,  header.header.cpusubtype)
        return (arch, cpuType, sz)
        
    def GetUUID(self, header): 
        for cmd in header.commands:
            (cmd_load, cmd_cmd, cmd_data) = cmd
            if cmd_load.cmd == LC_UUID:
                return cmd_cmd.uuid
        raise Exception("No UUID found")
        
    def GetListOfUUIDs(self):
        uuids = []
        for header in self.m_machObject.headers:
            uuids.append((self.GetPlatform(header), self.GetUUID(header)))    
        return uuids
    
    def PrintBundleInformation(self):
        uuids = self.GetListOfUUIDs()
        for platform, uuid in uuids:
            (arch, cpuType, sz) = platform            
            print '%s %s %s' % (arch, cpuType, sz)   
            print 'UUID: ' + binascii.hexlify(bytearray(uuid))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Tool for getting UUID.')
    parser.add_argument('bundle', metavar='bundle', type=str, help='path to bundle or dSYM')
    args = parser.parse_args()
    uuidGetter = UUIdGetter()  
    uuidGetter.OpenBundle(args.bundle)
    uuidGetter.PrintBundleInformation()
