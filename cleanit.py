import os


def pyc_clean(dir):
    findcmd = 'find %s -name "*.bak" -print' % dir
    count = 0
    for f in os.popen(findcmd).readlines():
        count += 1
        print(str(f[:-1]))
        os.remove(str(f[:-1]))
    print("Removed %d .bak files" % count)

if __name__ == "__main__":    
    pyc_clean(".")

