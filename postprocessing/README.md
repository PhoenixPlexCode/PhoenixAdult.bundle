# Post Processing Script for SabNZBD
This script will automatically rename and move files after they are downloaded.

## Features
- Supports Windows and Linux systems
- Renames file according to scene title
- Adds Scene ID to filename if necessary
- Designed to make plex matching with this metadata agent work smoothly/automatically
- Deletes leftover files and empty folders
- Bulk rename old collections
- Dry-Run option to test rename fucntionality


- Customisation:
  - Specify how to handle duplicates
  - Specify where to move renamed files
  - Include Media Info in the file or folder name. e.g Resolution/Framerate
  
## Dependancies
- lxml
  - `pip install lxml`
- If using Media Info Options:
  - `pip install pymediainfo`
  - https://mediaarea.net/en/MediaInfo for the MediaInfo.DLL file

## Instructions
1. Place the files in you sabnzbd script folder
2. Point SabNZBD to pa_renamer_post.py
3. Customise your settings in siteConfig.py
   - Don't forget the log directory
   - If on Linux you may need to edit lines 1 and 2 of pa_renamer_post.py.
4. Set sabnzbd to run this post processing script after appropriate downloads complete

### To Run Manually:
`python pa_renamer_post.py [options] (Directory containing one video file)`

**Options**

- "-d" "--dryrun", help="Don't do it for real, just show what will happen"
- "-b", "--batch", help="Changes how logging works when bulk matching to avoid an error with permissions"

- "-c", "--cleanup", help="Delete leftover files and cleanup folders after rename"
- "-m", "--mediainfo", help="Add media info to the folder. Resolution and framerate"
- "-m2", "--mediainfo2", help="Add media info to the filename. Resolution and framerate"
- "-n", "--filerename", help="Use the filename instead of the folder name. Not recommended"

**Note:** If options are enabled in siteConfig.py they will be enabled when run manually also.

### Processing old collections

For old collections where the media is structured with multiple video files in one folder you will need to enable the use_filename parameter in siteConfig.py (or use the -n option above). This will make the code use the name of each individual file instead of the folder name. The file need to be named in a compatible format. If you have files not in the correct format we can attempt to code a regex match for it if you provide an example in an issue.

**Warning!!**

When procesing multiple files in this way I have had one instance of files being named incorrectly when moving them into the same directory. I attempted to code around this and I have not had it happen again but I cannot guarentee I have resolved it.

## Supported Sites

- FakeHub Network
- Family Strokes
- Little Caprice Dreams
- Nubiles Network
- Mofos Network (at this stage sharemyBF only)
- Porn Pros Network (cum4k, lubed, nannyspy, passionhd, spyfam, tiny4k)
- Reality Kings
- SexyHub Network
- Sis Loves Me
- Vixen
- X-Art

Not every site is necessarily supported within the network site. I have supported sites I wanted to use. If you want something specific feel free to request things or submit working code yoursef.
