sortly
======

Uses Transmission .added files to correctly sort torrent downloads by tracker. Will hard link files so you dont double up on disk space, or tax the HDD by copying files. Will also only copy/hardlink if file does not already exist.

From what I can tell this requires Python 2.7 because it uses os.link. If you would like to use this with lower versions, comment out os.link in favor of shutil.copy.

Change the vars at the top to match your setup and needs. This script currently assumes that transmission will:

* Not delete the torrent files and will add a hash and append .added
* You have a temporary folder where current incomplete downloads are stored
* Downloads are moved to a final folder