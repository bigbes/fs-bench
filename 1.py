#!/usr/bin/env python
import os
import subprocess
import shutil
from wrappers import DD,  Device,  Sudo

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

    def set_name(self, Name):
        self.name = Name
        self.dir = "dir_"+self.name

    def set_ftype(self, Ftype):
        self.ftype = Ftype

    def set_size(self, Size):
        self.size = Size


    def __init__(self):
        self.set_num()

        self.set_name(FileDevice._name + str(self.num))
        self.set_size(self._size)
        self.set_ftype(FileDevice._ftype)
        self.__mount = 0
        self.__qty = 0

    def set_num(self):
        try:
            self.num
        except AttributeError:
            self.num = self._num
            FileDevice._num += 1

    def make(self):
        if self.ftype == FileSystems.ramfs:
            return self
        DD(Device.zero, self.name, "1M", self.size)
        if subprocess.call(["/sbin/mkfs.{0}".format(
            FileSystems.table[self.ftype]),self.name, "-F", "-q"],):
            print "Error, when mkfs"
            exit(1)
        return self

    def erase(self, rand_flag = 0):
        if self.ftype == FileSystems.ramfs:
            return
        if rand_flag:
            DD(Device.urand, self.name, "1M", self.size())
        else:
            DD(Device.zero, self.name, "1M", self.size())
        return self

    def mount(self):
        if self.__mount:
            print "Already mounted"
            return

        print "Mounted! {0}".format(self.num)
        self.__mount = 1
        #if not there
        #make dir
        try:
            os.mkdir("dir_{0}".format(self.name))
        except OSError:
            pass

        if self.ftype == FileSystems.ramfs:
            Sudo("mount -t {2} {2} {0} -o size={1}M".format(self.name,self.size, FileSystems.table[self.ftype]))
        else:
            Sudo("mount {0} dir_{0} -t {1} -o loop".format(self.name,FileSystems.table[self.ftype]))

        return self

    def remount_RO(self):
        if not self.__mount:
            print "Not mounted"
            return

        Sudo("mount -o remount,ro /dir_{0}".format(self.name))
        return self

    def make_files(self, Qty = _size - 1, Size = 1, Suff = "M"):
        if not self.__mount:
            print "Not mounted"
            return
        for i in xrange(Qty):
            if DD(Device.urand, "dir_{0}/tmp{1}".format(self.name, i),str(Size)+Suff, 1) == 1:
                os.remove("dir_{0}/tmp{1}".format(self.name, i - 1))
                self.__qty = i - 2
                return self

    def delete_last(self):
        if not self.__qty:
            return

        os.removde("dir_{0}/tmp{1}".format(self.name, self.__qty))
        self.__qty = self.__qty - 1
        return self

    def copy_exec(self, exe = "a.out"):
        self.__exe = __exe
        shutil.copy2(self.__exe, "dir_{0}".format(self.name))
        return self

    def run(self):
        proc = subprocess.Popen(["dir_{0}/{1}".format(self.name, self.__exe)])
        #TODO: we may calculate this in parallel. move from _wait to _result.
        return proc.wait()

    #def copy_and_run(self):
    #    shutil.copy2("a.out", "dir_{0}".format(self.name))
    #    proc = subprocess.Popen(["dir_{0}/a.out".format(self.name)])
    #    return proc.wait()

    def umount(self):
        if not self.__mount:
            print "Not Mounted!"
            return
        print "Umounted! {0}".format(self.num)
        Sudo("umount dir_{0}".format(self.name))

    def __del__(self):
        pass

if __name__ == "__main__":
    fd = FileDevice().make().mount().umount()
    pass

