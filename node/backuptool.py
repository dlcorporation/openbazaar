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
            # folder might already exist, no biggie
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

if __name__ == '__main__':
    def onBackUpDone(backupFilePath):
        print "Backup succeeded!\nOutput file at", backupFilePath

    def onError(errorMessage):
        print "Backup failed!", errorMessage

    BackupTool.backup("/Users/gubatron/workspace.frostwire/OpenBazaar",
                      "/Users/gubatron/workspace.frostwire/OpenBazaar/html/backups",
                       onBackUpDone,
                       onError)
