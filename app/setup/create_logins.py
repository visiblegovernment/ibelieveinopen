# encoding: utf-8

import sys
import os
import time
import random

path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['DJANGO_SETTINGS_MODULE'] = 'app.settings'
sys.path.append(path)

from app.mainapp.models import Politician, Signup, Pledge, PoliticianPledge
from django.contrib.auth.models import User, Group
from app.utils import  UnicodeWriter
from django.conf import settings


def add_user_to_grp(usr, grpname):
 #   """docstring for add_user_to_grp"""
    if Group.objects.filter(name=grpname).count() == 0:
        grp = Group(name=grpname)
        grp.save()
    grp = Group.objects.get(name__exact=grpname)
    usr = User.objects.get(username__exact=usr)
    if grp and usr:
        usr.groups.add(grp)
        usr.save()

def add_new_user(cid,firstname,lastname,passcode):
    user = User.objects.create_user(cid, '', passcode)
    user.first_name = firstname
    user.last_name = lastname
    user.is_active = True
    user.save()
    add_user_to_grp(cid, 'Candidates')

def main():

    pols = Politician.objects.all()
    is_new_file = not os.path.isfile(settings.PASSCODE_FILE)
    writer = UnicodeWriter(open(settings.PASSCODE_FILE, "ab"))
    if is_new_file:
        writer.writerow(('ID','Lastname','Firstname','Riding', 'EDID', 'Province','url','passcode'))

    cnt = 0
    for pol in pols:
        id = int(pol.id) + 2000
        cid = 'c%s' % (id, )

        if User.objects.filter(username=cid).count() == 0:
            print "adding " + cid
            url = 'http://%s/ipledge/c%s/' % (settings.SITE_ROOT, id )
            passcode = random.randrange(1001, 9999)
            writer.writerow((str(pol.id), pol.lname, pol.fname, pol.riding_id.name,str(pol.riding_id.edid),pol.province,url,str(passcode)))
            add_new_user(cid,pol.fname, pol.lname,passcode)
            cnt += 1

    print '%s candidate users added.' % (cnt, )


if __name__ == '__main__':
    main()

