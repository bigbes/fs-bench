#!/usr/bin/env python
import os
import subprocess
import shutil
import time
import shlex

from subprocess import PIPE
from wrappers import DD,  Device,  Sudo

DEBUG = False

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

fs_table = FileSystems.table

class FileDevice:
    _name = "td"
    _num = 0
    #in mb
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
            return
        if self.ftype >= FileSystems.ext2 and self.ftype <= FileSystems.ext4:
            exec_prog = " -F -q -N 90000 "
        elif self.ftype == FileSystems.xfs:
            exec_prog = " -q -f "
        elif self.ftype == FileSystems.jfs:
            exec_prog = " -q "
        else:
            exec_prog = " "
            self.size = 256

        exec_prog = shlex.split("/sbin/mkfs."+fs_table[self.ftype]+exec_prog+self.name)
        if DEBUG:
            print exec_prog

        DD(Device.zero, self.name, "1M", self.size).run()

        if subprocess.call(exec_prog):
            print "Error, when mkfs"
            exit(1)

    def erase(self, rand_flag = 0):
        if self.ftype == FileSystems.ramfs:
            return
        if rand_flag:
            DD(Device.urand, self.name, "1M", self.size).run()
        else:
            DD(Device.zero, self.name, "1M", self.size).run()

    def mount(self):
        if self.__mount:
            print "Already mounted"
            return

        print "Mounted! Number " + str(self.num)
        self.__mount = 1
        try:
            os.mkdir("dir_{0}".format(self.name))
        except OSError:
            pass

        if self.ftype == FileSystems.ramfs:
            exec_prog = "mount -t"+2*(" "+fs_table[self.ftype])+" -o size="+str(self.size)+"M"
            Sudo(exec_prog)
        else:
            exec_prog = "mount "+self.name+" dir_"+self.name+" -t "+fs_table[self.ftype]+" -o loop"
            Sudo(exec_prog)

        exec_prog = "chmod a+rwx -R dir_"+self.name
        Sudo(exec_prog)

        #return self

    def remount_RO(self):
        if not self.__mount:
            print "Not mounted"
            return -1
        Sudo("mount -o remount,ro dir_{0}".format(self.name))
        return 0

    def make_files(self, Size = 1, Suff = "M"):
        if not self.__mount:
            print "Not mounted"
            return -1
        i = 0
        place = "dir_"+self.name+"/tmp"
        while not DD(Device.urand, place+str(i), str(Size)+Suff, 1).run():
            i += 1

        try:
            os.remove(place+str(i))
        except OSError:
            pass

        self.__qty = i - 1
        if DEBUG:
            print "Quantity of Garbage Files: "+str(self.__qty)
        return 0

    def delete_last(self, ret = ""):
        if self.__qty < 0:
            print "No more files"
            return -1
        place = "dir_"+self.name+"/tmp"

        if DEBUG:
            print "Delete file "+place+str(self.__qty)+str(ret)

        try:
            os.remove(place+str(self.__qty))
        except OSError:
            pass
        self.__qty -= 1 #!!
        return 0

    def copy_exec(self, exe = "a.out"):
        self.__exe = exe
        shutil.copy2(self.__exe, "dir_{0}".format(self.name))
        #return self


    def run(self):
        os.chdir("dir_{0}".format(self.name))
        proc = subprocess.Popen(["./"+self.__exe], stdout=PIPE, stderr=PIPE)
        os.chdir("..")
        return proc.communicate()[0]

    def run_inb(self):
        os.chdir("dir_{0}".format(self.name))
        proc = subprocess.Popen(["./{0}".format(self.__exe)], stdout=PIPE, stderr=PIPE)
        os.chdir("..")
        return proc

    #def copy_and_run(self):
    #    shutil.copy2("a.out", "dir_{0}".format(self.name))
    #    proc = subprocess.Popen(["dir_{0}/a.out".format(self.name)])
    #    return proc.wait()

    def umount(self):
        if not self.__mount:
            print "Not Mounted!"
            return -1

        place = "dir_"+self.name
        if DEBUG:
            print "Umounted! "+place
        Sudo("umount "+place)
        self.__mount = 0

    def clean(self):
        try:
            os.rmdir("dir_"+self.name)
            os.remove(self.name)
        except OSError:
            pass

    def __del__(self):
        #self.umount()
        #self.clean()
        pass

def cool(x):
    if x == "-":
        return x
    return int(x)


def check_write(fs_type = FileSystems.ext2, fd_size = 16, cf_size = 1, cf_postfix="M"):
    print "\n##########WRITE#####"
    print "Checking on FS - {3}. Size {0}, F Size {1}{2}".format(fd_size, cf_size, cf_postfix, fs_table[fs_type])

    fd = FileDevice()
    fd.set_ftype(fs_type)
    fd.set_size(fd_size)

    fd.make()
    fd.mount()

    fd.copy_exec("write")
    fd.make_files(Size = cf_size, Suff = cf_postfix)
    #subprocess.call("df -i".split())
    #subprocess.call("df -h".split())
    #time.sleep(10)

    #ret = map(lambda x: int(x), fd.run().split())
    ret = map(cool, fd.run().split())

    #print "Testing write(2) if ENOSPC for {0} and cf_size {2}{3}".format(
    #        fs_table[fs_type], fd.num, cf_size, cf_postfix)
    print "First launch " + str(ret)

    #ret = map(lambda x: int(x), fd.run().split())
    ret = map(cool, fd.run().split())

    _iters = 0
    while ret[2] == 0:
        #print ret
        if fd.delete_last(ret):
            break

        #ret = map(lambda x: if x!="-": int(x), fd.run().split())
        ret = map(cool, fd.run().split())
        _iters += 1
    print "Next launch "+str(_iters)+" "+str(ret)

    fd.umount()
    fd.clean()



def check_ro_before(fs_type = FileSystems.ext2, fd_size = 32):
    print "\n##########RO#BEFORE##"
    print "Checking on FS {1} Size {0}".format(fd_size, fs_table[fs_type])

    fd = FileDevice()
    fd.set_ftype(fs_type)
    fd.set_size(fd_size)

    fd.make()
    fd.mount()
    fd.copy_exec("ro_before")
    fd.remount_RO()
    ret = fd.run()
    print ret

    fd.umount()
    fd.clean()


def check_ro_after(fs_type = FileSystems.ext2, fd_size = 32):
    print "\n##########RO#AFTER###"
    print "Checking on FS {1} Size {0}".format(fd_size, fs_table[fs_type])

    fd = FileDevice()
    fd.set_ftype(fs_type)
    fd.set_size(fd_size)

    fd.make()
    fd.mount()
    fd.copy_exec("ro_after")
    ret = fd.run_inb()
    fd.remount_RO()
    print ret.communicate()[0]

    fd.umount()
    fd.clean()

def check_erase(fs_type = FileSystems.ext2, fd_size = 16):
    print "\n####ERASE#SUPERBLOCK##"
    print "Checking on FS {1} Size {0}".format(fd_size, fs_table[fs_type])

    fd = FileDevice()
    fd.set_ftype(fs_type)
    fd.set_size(fd_size)

    fd.make()
    fd.mount()
    fd.copy_exec("erase")
    ret = fd.run_inb()
    fd.erase()
    print ret.communicate()[0]

    fd.umount()
    fd.clean()

if __name__ == "__main__":
    #table = ((128, "c"), (4, "K"), (1, "M"), (16, "M"), (32, "M"))
    table = ((1, "M"), (16, "M"), (32, "M"))
    #for elem in table:
    #    check_write(cf_size = elem[0], cf_postfix = elem[1], fd_size = 72)
    #check_
    for f in xrange(4, 7):
    #for f in xrange(1, 4):
        for t in table:
            check_write(f, 72, t[0], t[1])
    pass
