import os
import subprocess
import shlex

from subprocess import PIPE

nil = open(os.devnull, 'w')

DEBUG = False

class WrapperError(Exception):
    def __init__(self, value, wrapper):
        self.value = value
        self.wrapper = wrapper

    def __str__(self):
        return self.wrapper + ": " + self.value


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

    def run(self):
        try:
            exec_prog = self._dd +" "+ self._if +" "+ self._of
            exec_prog = exec_prog +" "+self._bs +" "+self._count

            #proc = subprocess.Popen(shlex.split(exec_prog))
            if not DEBUG:
                return subprocess.Popen(shlex.split(exec_prog),stdout=nil.fileno(), stderr=nil.fileno()).wait()
            else:
                return subprocess.Popen(shlex.split(exec_prog)).wait()

        except OSError:
            print "dd is Non-Executable File"
        except ValueError:
            print "Wrong Arguments"

class Device:
    """Basic enum for devices"""
    #TODO: complete it
    #TODO: move this code to other file
    rand  = 1
    urand = 2
    zero  = 3
    null  = 4
    table = {1:"/dev/random", 2:"/dev/urandom",
            3:"/dev/zero", 4:"/dev/null"}

class Sudo:
    _pass = "121211\n"

    def __init__(self, command,  password = ""):
        if password == "":
            password = Sudo._pass

        exec_prog = "/usr/bin/sudo -S"

        if type(command) is type(""):
            exec_prog = exec_prog +" "+ command
            exec_prog = shlex.split(exec_prog)
        elif type(command) is type(list()):
            exec_prog = shlex.split(exec_prog) + command
        else:
            raise WrapperError("""Wrong 'Command' Argument""","Sudo")
        print exec_prog
        #proc = subprocess.Popen(["/usr/bin/sudo","-S", "-p",""]+ command, stdin=PIPE, stdout=PIPE)

        proc = subprocess.Popen(exec_prog,
            stdin=PIPE, stdout=nil.fileno(), stderr=nil.fileno())
        proc.communicate(password)
        proc.wait()

if __name__ == "__main__":
    print  "This is library, stupid!"
