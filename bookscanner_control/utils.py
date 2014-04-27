###############################################################################
# -*- coding: utf-8 -*-
###############################################################################

import os
import time
import itertools
import subprocess
import multiprocessing
import settings

###############################################################################

DEVICES = [x for x in subprocess.check_output(
        ["gphoto2", "--auto-detect"]).split() if "usb" in x]

for device in DEVICES:
    subprocess.call(["gphoto2", "--port", device, "--set-config",
                     "capturetarget=card"])
    
###############################################################################

def get_files(d, num=0):
    '''
    Returns list of files arranged into pairs (as book pages)
    '''
    files = sorted(os.listdir(d))
    ret = { 'dirname': d, 'files': []}
    if files:
        if num*2 > len(files) or num is 0:
            # take all files
            num = len(files)/2
        ret['files'] = [ (files[i*2], files[i*2+1]) for i in range(num)]
    return ret

###############################################################################

def inc(fname):
    '''
    Returns filename increased by 1
    >>> inc('001.jpg')
    '002.jpg'
    '''
    name, ext = os.path.splitext(fname)
    return '{0:03d}{1}'.format(int(name) + 2, ext)

###############################################################################

def capture_job(left, right, device, n):
    '''
    Job single camera does to capture page image
    '''
    curdir = os.getcwd()
    filename = left
    rotate = '-90'
    if n == 1:
        time.sleep(0.3)
        filename = right
        rotate = '90'
    try:
        os.mkdir(device)
    except:
        pass
    # position into camera dir and take photo
    os.chdir(device)
    #subprocess.call(['gphoto2', '--port', device, '--capture-tethered'])
    subprocess.call(['gphoto2', '--port', device,
                     '--capture-image-and-download'])
    os.chdir(curdir)
    # rotate and rename image
    subprocess.call(['mogrify', '-rotate', rotate,
                     '{}/capt0000.jpg'.format(device)])
    os.rename('{}/capt0000.jpg'.format(device), '{}'.format(filename))

###############################################################################

def capture(left, right):
    '''
    Init photo capturing
    '''
    jobs = []
    for n, device in enumerate(DEVICES):
        capt_job = multiprocessing.Process(target=capture_job,
                                           args=(left, right, device, n))
        jobs.append(capt_job)
        capt_job.start()
    [j.join() for j in jobs]
    return True

###############################################################################

def insert(d, left, right):
    '''
    Inserts pair of images in the directory 'd' after images 'left' and 'right'
    '''
    data = get_files(d)
    dn = data['dirname']
    if data['files']:
        files = []
        # make list of files after insert point
        # (because maybe we will have to rename these files...)
        for i in itertools.dropwhile(
            lambda x: dn + x[0] <> left and dn + x[1] <> right, data['files']):
            files.append(i[0])
            files.append(i[1])
        # generate new names
        nl, nr = dn + inc(files[0]), dn + inc(files[1])
        # skip current pair
        files = files[2:]
        # if there are files to be renamed, first make sure that there is not
        # empty pair (that can happen after Delete action)
        if len(files) >= 2:
            if nl <> dn+files[0] and nr <> dn+files[1]:
                files = [] # pages are in order, nothing to rename
        # rename files (if any)
        [os.rename(dn+i, dn + inc(i)) for i in sorted(files, reverse=True)]
    else:
        # no files - make initial names
        nl, nr = d + '001.jpg', d + '002.jpg'
    # init photo capturing
    return capture(nl, nr)

###############################################################################

def switch_pages():
    '''
    Reverse left and right camera
    '''
    DEVICES.reverse()

###############################################################################

def delete_all_files(d):
    '''
    Empty directory 'd'
    '''
    [os.remove(os.path.join(d, f)) for f in os.listdir(d)]

###############################################################################

def set_bookname(name):
    '''
    Set current book name
    '''
    settings.BOOK_NAME = name
    return settings.BOOK_NAME

###############################################################################

def upload(remote):
    '''
    Upload scanned images to remote server
    '''
    return(remote)
