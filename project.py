#! /usr/bin/env python

import os,time,sys
import sqlite3
import datetime
from distutils.util import get_platform


# GLOBAL VARS

platform = get_platform()
db = sqlite3.connect('log.db')
cursor = db.cursor()


def logToDB(event,location):  # http://docs.python.org/library/sqlite3.html
   cursor.execute("INSERT INTO logs VALUES(?,?,?)",(event,location,datetime.datetime.today()))
   db.commit()



def watchOther(path):  # http://docs.python.org/library/os.html
   try:
      before = []
      for root,subFolders,files in os.walk(path):
         before.append(root)
         for f in files:
            before.append(os.path.join(root,f))
      flag = True
      while flag:
         after = []
         for root,subFolders,files in os.walk(path):
            after.append(root)
            for f in files:
               after.append(os.path.join(root,f))
        
         added = [f for f in after if not f in before]
         removed = [f for f in before if not f in after]
      
         if added:
            print 'ADDED: ' + str(added)
            logToDB('ADDED',str(added))
            # flag = False
         if removed:
            print 'REMOVED: ' + str(removed)
            logToDB('REMOVED',str(removed))
            # flag = False
         before = after
   except KeyboardInterrupt:
      db.close()
      sys.exit()
   
def watchLinux(path):            # http://trac.dbzteam.org/pyinotify/wiki/Tutorial
   try:
      import pyinotify
      wm = pyinotify.WatchManager()
      mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE # Events to watch for
      class HandleEvents(pyinotify.ProcessEvent):
         def process_IN_CREATE(self, event):
            print 'ADDED: ', event.pathname
            logToDB('ADDED',event.pathname)
         def process_IN_DELETE(self, event):
            print 'REMOVED: ', event.pathname
            logToDB('REMOVED',event.pathname)
      notifier = pyinotify.Notifier(wm,HandleEvents())
      wdd = wm.add_watch(path,mask,rec=True,auto_add=True)
      notifier.loop()
   except KeyboardInterrupt:
      wm.rm_watch(wdd.values())
      notifier.stop()
      db.close()
      sys.exit()

def main(path):
   if(platform.startswith('win')):
      print "OS IDENTIFIED : WINDOWS"
      watchOther(path)
   elif(platform.startswith('linux')):
      print "OS IDENTIFIED : LINUX"
      watchLinux(path)      
   elif(platform.startswith('mac')):
      print "OS IDENTIFIED : MAC"
      watchOther(path)
   else:
      print "OS : " + platform
      watchOther(path)

if __name__ == '__main__':
   try:
      path = sys.argv[1]
      print "Monitoring Directory " + sys.argv[1]
      print "Ctrl-C to Stop"
      main(path)
   except IndexError:
      print "ERROR!"
      print "Usage : project.py <directory_to_monitor>"
      
           
