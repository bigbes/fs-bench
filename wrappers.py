import subprocess
from subprocess import PIPE

class DD:
    """Basic wrapper for dd"""
    #TODO: move this code to other file
    #TODO: more arguments, but this is ok too
    def __init__(self, __if, __of, __bs="", __count="1",  __dd="/bin/dd"):
        #-------------------
        self._dd = __dd

        #-------------------
        if type(__if) == type(""):
            self._if = "if="+__if
        else:
            self._if = "if="+Device.table[__if]

        #-------------------
        if type(__of) == type(""):
            self._of = "of="+__of
        else:
            self._of = "of="+Device.table[__of]

        #-------------------
        if __bs == "":
            self._bs = ""
        else:
            self._bs = "bs="+str(__bs)

        #-------------------
        if __count == "":
            self._count = ""
        else:
            self._count = "count="+str(__count)

        self.run()

    def run(self):
        try:
            print "####### {0} {1} {2} {3}".format(self._dd, self._if, self._of, self. _bs, self._count)
            proc1 = subprocess.Popen([self._dd, self._if, self._of, self._bs, self._count])
            return proc1.wait()
        except OSError:
            print "nonexecutable file - strange."
        except ValueError:
            print "wrong argumentsssss"

class Device:
    """Basic enum for devices"""
    #TODO: complete it
    #TODO: move this code to other file
    rand  = 1
    urand = 2
    zero  = 3
    null  = 4
    table = {1:"/dev/random", 2:"/dev/urandom", \
            3:"/dev/zero", 4:"dev/null"}

class Sudo:
    _pass = "121211\n"

    def __init__(self, command,  password = ""):
        if password == "":
            password = Sudo._pass
        command = command.split()
        proc = subprocess.Popen(["/usr/bin/sudo","-S", "-p",""]+command,  stdin = PIPE, stdout = PIPE)
        proc.communicate(password)
        proc.wait()

if __name__ == "__main__":
    print  "This is library, stupid!"
