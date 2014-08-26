#!/usr/bin/env python
#
# This library is free software, distributed under the terms of
# the GNU Lesser General Public License Version 3, or any later version.
# See the COPYING file included in this archive
#
# The docstrings in this module contain epytext markup; API documentation
# may be created by processing this file with epydoc: http://epydoc.sf.net
import tarfile
import time
import os

class BackupTool:
    """
    Simple backup utility.

    @author Angel Leon <gubatron@gmail.com>
    Created August 23, 2014.
    """
    @staticmethod
    def backup(openbazaarInstallationPath, backupFolderPath, onSucessCallback=None, onErrorCallback=None):
        """
        Creates an 'openbazaar-YYYY-MM-DD-hh-mm-ss.tar.gz' file
        inside the html/backups/ folder.
        folder.

        openbazaarInstallationPath : String -> The path to OpenBazaar's installation, where the db/ and msig/ folders live.
        backupFolderPath : String -> The folder where the backup file will exist.

        Optional callback functions can be passed.
            onSucessCallback(backupFilePath : String)
            onErrorCallback(errorMessage : String)
        """
        dateTime = time.strftime('%Y-%h-%d-%H-%M-%S')
        outputFilepath = backupFolderPath + os.sep + "openbazaar-%s.tar.gz" % dateTime

        try:
            os.makedirs(backupFolderPath)
        except:
            #folder might already exist, no biggie
            pass

        try:
            tar = tarfile.open(outputFilepath, "w:gz")
            db_folder = openbazaarInstallationPath + os.sep + "db"
            msig_folder = openbazaarInstallationPath + os.sep + "msig"
            tar.add(db_folder, os.path.basename(db_folder))
            tar.add(msig_folder, os.path.basename(msig_folder))
            tar.close()
        except Exception, e:
            if onErrorCallback is not None:
                onErrorCallback(e)
                return

        if onSucessCallback is not None:
            onSucessCallback(outputFilepath)
            return

    @staticmethod
    def restore(backupTarFilepath):
        pass


class Backup:
    """
    A (meant to be immutable) POPO to represent a backup. So that we can tell
    our Web client about the available backups made.
    """
    def __init__(self, file_name=None, 
                 full_file_path=None, 
                 created_timestamp_millis=None,
                 size_in_bytes=None):
        self.file_name = file_name
        self.full_file_path = full_file_path
        self.created_timestamp_millis = created_timestamp_millis
        self.size_in_bytes = size_in_bytes

    def __str__(self):
        return "{ file_name: '%s', full_file_path: '%s', created_timestamp_millis: %d, size_in_bytes: %d}" % \
            (self.file_name,
             self.full_file_path,
             long(self.created_timestamp_millis),
             long(self.size_in_bytes))

    @staticmethod
    def get_backups(backups_folder_path):
        '''
        Returns a list of Backup objects found in the backup folder path given.
        '''
        result = []
        if backups_folder_path is not None and os.path.isdir(backups_folder_path):
            if backups_folder_path.endswith(os.sep):
                backups_folder_path = backups_folder_path[:-1] #trim trailing '/'
            result = [Backup.get_backup(backups_folder_path+os.sep+x) for x in os.listdir(backups_folder_path)]
        return result

    @staticmethod
    def get_backup(backup_file_path):
        result = None

        try:
            file_stat = os.stat(backup_file_path)
            file_name = os.path.basename(backup_file_path)
            created_timestamp = file_stat.st_ctime
            size_in_bytes = file_stat.st_size

            result = Backup(file_name,
                            backup_file_path,
                            created_timestamp,
                            size_in_bytes)
        except:
            pass
        return result


if __name__ == '__main__':
    # tests here.
    def onBackUpDone(backupFilePath):
        print "Backup succeeded!\nOutput file at", backupFilePath

    def onError(errorMessage):
        print "Backup failed!", errorMessage

    BackupTool.backup("/Users/gubatron/workspace.frostwire/OpenBazaar", 
                      "/Users/gubatron/workspace.frostwire/OpenBazaar/html/backups",
                      onBackUpDone, 
                      onError)
    for x in Backup.get_backups("/Users/gubatron/workspace.frostwire/OpenBazaar/html/"):
        print x

