# -*- coding: utf-8 -*-

import sys, os, argparse, logging
from FATtools import vhdutils, vdiutils, vmdkutils
from FATtools import Volume

DEBUG = 0
from FATtools.debug import log

logging.basicConfig(level=logging.DEBUG, filename='cp.log', filemode='w')



def is_vdisk(s):
    "Returns the base virtual disk image path if it contains a known extension or an empty string"
    image_path=''
    for ext in ('vhd', 'vdi', 'vmdk', 'img', 'dsk', 'raw', 'bin'):
        if '.'+ext in s.lower():
            i = s.lower().find(ext)
            image_path = s[:i+len(ext)]
            break
    return image_path

def cp(srcs_list, dest):
    "Copies items from srcs_list to a target directory (real or inside an image)"
    if is_vdisk(dest):
        dst_image = is_vdisk(dest)
        sub_path = dest[len(dst_image):]
        if DEBUG: log("cp: target is virtual disk '%s', path '%s'", dst_image, sub_path)
        dest = Volume.vopen(dst_image, 'r+b')
        if sub_path:
            dest = dest.mkdir(sub_path[1:])
        Volume.copy_in(srcs_list, dest, printn, 2)
    else:
        if DEBUG: log("cp: target is real filesystem")
        if not os.path.isdir(dest):
            if DEBUG: log("cp: target does not exist!")
            raise FileNotFoundError('cp: fatal, target directory "%s" does not exist!'%dest)
        for it in srcs_list:
            src_image = is_vdisk(it)
            sub_path = it[len(src_image)+1:]
            if DEBUG: log("cp: source is virtual disk '%s', path '%s'", src_image, sub_path)
            src = Volume.vopen(src_image, 'rb')
            Volume.copy_out(src, [sub_path], dest, printn, 2)

def printn(s): print(s)



if __name__ == '__main__':
    help_s = """
    cp.py <file1 or dir1> [file2 or dir2...] <destination>
    """
    par = argparse.ArgumentParser(usage=help_s,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description="Copies items between real and virtual volumes. Wildcards accepted.\nCopy between virtual disk images is not supported yet.",
    epilog="Examples:\ncp.py File1.txt File2.txt Dir1 image.vhd\ncp.py File*.txt Dir? image.vhd/Subdir\ncp.py image.vhd\\*.py image.vhd/Subdir1 C:\\MyDir")
    par.add_argument('items', nargs='*')
    args = par.parse_args()

    if len(args.items) < 2:
        print("copy error: you must specify at least one source and the destination!")
        par.print_help()
        sys.exit(1)

    dest = args.items.pop()
    cp(args.items, dest)