#!/usr/bin/env python
import os
import subprocess
import shutil
import time

from subprocess import PIPE
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
            return# self
        DD(Device.zero, self.name, "1M", self.size)
        if subprocess.call(["/sbin/mkfs.{0}".format(
            FileSystems.table[self.ftype]),self.name, "-F", "-q", "-N", str(90000)],):
            print "Error, when mkfs"
            exit(1)
        #return self

    def erase(self, rand_flag = 0):
        if self.ftype == FileSystems.ramfs:
            return
        if rand_flag:
            DD(Device.urand, self.name, "1M", self.size())
        else:
            DD(Device.zero, self.name, "1M", self.size())
        #return self

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

        #return self

    def remount_RO(self):
        if not self.__mount:
            print "Not mounted"
            return

        Sudo("mount -o remount,ro /dir_{0}".format(self.name))
        #return self

    def make_files(self, Qty = -1, Size = 1, Suff = "M"):
        if Qty == -1:
            Qty = self.size * 1024 * 1024
            Qty = Qty / Size
            if Suff == "K":
                Qty = Qty / 1024
            if Suff == "M":
                Qty = Qty / (1024*1024)

        if not self.__mount:
            print "Not mounted"
            return

        for i in xrange(Qty):
            if not DD(Device.urand, "dir_{0}/tmp{1}".format(self.name, i),str(Size)+Suff, 1):
                self.__qty = i - 2
                print self.__qty
                time.sleep(2)
                return

    def delete_last(self):
        print self.__qty
        if not self.__qty:
            return

        print "dir_{0}/tmp{1}".format(self.name, self.__qty)
        os.remove("dir_{0}/tmp{1}".format(self.name, self.__qty))
        self.__qty = self.__qty - 1
        #return self

    def copy_exec(self, exe = "a.out"):
        self.__exe = exe
        shutil.copy2(self.__exe, "dir_{0}".format(self.name))
        #return self

    def run(self):
        os.chdir("dir_{0}".format(self.name))
        proc = subprocess.Popen(["./{0}".format(self.__exe)], stdout=PIPE, stderr=PIPE)
        os.chdir("..")
        #TODO: we may calculate this in parallel. move from _wait to _result.:w
        return proc.communicate()[0]

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

    def clean(self):
        os.rmdir("dir_{0}".format(self.name))
        os.remove("{0}".format(self.name))

    def __del__(self):
        pass


def check_write(fs_type = FileSystems.ext2, fd_size = 16, cf_size = 1, cf_postfix="M"):
    fd = FileDevice()
    fd.set_ftype(fs_type)
    fd.set_size(fd_size)

    fd.make()
    fd.mount()

    fd.copy_exec("write")
    fd.make_files(Size = cf_size, Suff = cf_postfix)
    time.sleep(3)
    #ret = map(lambda x: int(x), fd.run().split())

    #print "Testing write(2) if ENOSPC for {0} and cf_size {2}{3}".format(
    #        FileSystems.table[fs_type], fd.num, cf_size, cf_postfix)
    #print "First launch "+str(ret)

    #ret = map(lambda x: int(x), fd.run().split())

    #_iters = 0
    #while ret[3] == 0:
    #    print ret
    #    fd.delete_last()
    #    ret = map(lambda x: int(x), fd.run().split())
    #    _iters += 1
    #print "Next launch "+str(_iters)+" "+str(ret)

    fd.umount()
    fd.clean()

def check_ro(fd_size = 16):
    pass

def check_erase(fd_size = 16):
    pass

if __name__ == "__main__":
    #table = ((1, "c"), (128, "c"), (4, "K"), (1, "M"), (16, "M"), (32, "M"))
    table = ((4, "K"), (1, "M"), (16, "M"), (32, "M"))
    for elem in table:
        check_write(cf_size = elem[0], cf_postfix = elem[1], fd_size = 72)
    pass
