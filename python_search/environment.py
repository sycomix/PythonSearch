import os


def is_mac():
    import platform

    return platform.system() == "Darwin"


def is_archlinux():
    return os.system("uname -r | grep -i ARCH") == 0


def is_linux():
    return os.system("/etc/*release | grep -i  linux") == 0
