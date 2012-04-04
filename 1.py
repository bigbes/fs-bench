#!/usr/bin/env python
import os
import subprocess
import shutil
from lib import DD,  Device,  Sudo

class FileSystems:
    """Enum for basic FS types"""
    ext2  = 1
    ext3  = 2
    ext4  = 3
    btrfs = 4
    xfs   = 5
    jfs   = 6
    ramfs = 7
    table = {1:"ext2", 2:"ext3", 3:"ext4",
            4:"btrfs", 5:"xfs", 6:"jfs", 7:"tmpfs"}

class FileDevice:
    _name = "td"
    _num = 0
    #in MB
    _size = 16
    _ftype = FileSystems.ext2

    def __init__(self):
        self.num = FileDevice._num
        FileDevice._num += 1

        setName(FileDevice._name + str(self.num))
        setSize(_size)
        setFType(FileDevice._ftype)

    def __init__(self, Size = _size, Ftype = _ftype):
        self.num = FileDevice._num
        FileDevice._num += 1

        self.setName(FileDevice._name+"_"+str(self.num))
        self.setSize(Size)
        self.setFType(Ftype)


    def setNum(self):
        try:
            self.num
        except NameError:
            self.num = _num
            _num += 1

    def setName(self, Name):
        self.name = Name
        self.dir = "dir_"+self.name

    def setFType(self, Ftype):
        self.ftype = Ftype

    def setSize(self, Size):
        self.size = Size

    def make(self):
        if self.ftype == FileSystems.ramfs:
            return self
        DD(Device.zero, self.name, "1M", self.size).run()
        subprocess.call(["/sbin/mkfs.{0}".format(
                FileSystems.table[self.ftype]),self.name, "-F"])
        return self

    def mount(self):
        if self.ftype == FileSystems.ramfs:
            os.mkdir(self.name)
            Sudo("mount -t {2} {2} {0} -o size={1}M".format(self.name,
                self.size, FileSystems.table[self.ftype]))
            return self
        os.mkdir("dir_{0}".format(self.name))
        Sudo("mount {0} dir_{0} -t {1} -o loop".format(self.name,
            FileSystems.table[self.ftype]))
        return self

    def makefiles(self, Qty = _size - 1, Size = 1, Suff = "M"):
        for i in xrange(Qty):
            if DD(Device.urand, "dir_{0}/tmp{1}".format(self.name, i),
                    str(Size)+Suff, 1).run() == 1:
                self.qty = i - 2
                os.remove("dir_{0}/tmp{1}".format(self.name, i-1))
                return self

    def copyAndRun(self):
        shutil.copy2("a.out", "dir_{0}".format(self.name))
        proc = subprocess.Popen(["dir_{0}/a.out".format(self.name)])
        return proc.wait()

    def umount(self):
        Sudo("umount dir_{0}".format(self.name))

    def __del__(self):
        pass

if __name__ == "__main__":
    fd = FileDevice()
    fd.setFType(FileSystems.ext3)
    print fd.make().mount()
#    for i in xrange(1,7):
#        fd = FileDevice()
#        fd.setFType(i)
#        fd.make()
