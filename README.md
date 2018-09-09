# PhoenixAdult metadata agent

This metadata agent will receive data from multiple sites for scene video releases.

##Features
============
The agent searches in two ways, Scene title or scene date with atleast one star name

Currently the features of this metadata agent are:
- Grabs Metadata
- Title
- Studio
- Release Data
- Genres
- Porn Stars stored in Actors with photo
- Movie Poster
- Video banner as video background

##Supported Networks/Site
============
- **Blacked** *Title Search *Date/Actor Search
- **BlackedRaw** *Title Search *Date/Actor Search
- **Brazzers Network** *Title Search
-	Moms in Control
-	Pornstars Like It Big
-	Big Tits at Work
-	Big Tits at School
-	Baby Got Boobs
-	Real Wife Stories
-	Teens Like It Big
-	ZZ Series
-	Mommy Got Boobs
-	Milfs Like It Big
-	Big Tits in Uniform
-	Doctor Adventures
-	Exxtra
-	Big Tits in Sports
-	Big Butts like it big
-	Big Wet Butts
-	Dirty Masseur
-	Hot and Mean
-	Shes Gonna Squirt
-	Asses In Public
-	Busty Z
-	Busty and Real
-	Hot Chicks Big Asses
-	CFNM Clothed Female Male Nude
-	Teens Like It Black
-	Racks and Blacks
-	Butts and Blacks
- **Girlsway** *Title Search
- **Naughty America Network** *Date/Actor Search
-	My Friends Hot Mom
-	My First Sex Teacher
-	Seduced By A Cougar
-	My Daughters Hot Friend
-	My Wife is My Pornstar
-	Tonights Girlfriend Class
-	Wives on Vacation
-	My Sisters Hot Friend
-	Naughty Weddings
-	Dirty Wives Club
-	My Dads Hot Girlfriend
-	My Girl Loves Anal
-	Lesbian Girl on Girl
-	Naughty Office
-	I have a Wife
-	Naughty Bookworms
-	Housewife 1 on 1
-	My Wifes Hot Friend
-	Latin Adultery
-	Ass Masterpiece
-	2 Chicks Same Time
-	My Friends Hot Girl
-	Neighbor Affair
-	My Girlfriends Busty Friend
-	Naughty Athletics
-	My Naughty Massage
-	Fast Times
-	The Passenger
-	Milf Sugar Babes Classic
-	Perfect Fucking Strangers Classic
-	Asian 1 on 1
-	American Daydreams
-	SoCal Coeds
-	Naughty Country Girls
-	Diary of a Milf
-	Naughty Rich Girls
-	My Naughty Latin Maid
-	Naughty America
-	Diary of a Nanny
-	Naughty Flipside
-	Live Party Girl
-	Live Naughty Student
-	Live Naughty Secretary
-	Live Gym Cam
-	Live Naughty Teacher
-	Live Naughty Milf
-	Live Naughty Nurse
- **Vixen** *Title Search *Date/Actor Search



##File Naming
============
**Plex Video Files Scanner needs to be set as the library scanner for best results.

For best results, file names should follow the layout below

Title Search
============
- Site - Scene Title.[ext]

Examples:
- Blacked - Hot Vacation Adventures.mp4
- Blackedraw - Pass Me Around.mp4

Date/Actor Search
============
- Site - YYYY-MM-DD - Porn Star Names.[ext]
- Site - YYYY-MM-DD - Porn Star Name Porn Star Name.[ext]

Examples:
- Blacked.com - 2018-09-07 - Alecia Fox.mp4
- Blacked.com - 2018-09-07 - Alecia Fox Joss Lescaf.mp4
- Blacked.com - 2018-09-04 - Haley Reed.mp4
- Blacked.com - 2018-09-04 - Haley Reed Jason Luv.mp4

The site can be missing from the filename, but all sites will then be searched possibly causing a mismatch.

##Installation
============
Here is how to find the plug-in folder location:
https://support.plex.tv/hc/en-us/articles/201106098-How-do-I-find-the-Plug-Ins-folder-

Plex main folder location:

    * '%LOCALAPPDATA%\Plex Media Server\'                                        # Windows Vista/7/8
    * '%USERPROFILE%\Local Settings\Application Data\Plex Media Server\'         # Windows XP, 2003, Home Server
    * '$HOME/Library/Application Support/Plex Media Server/'                     # Mac OS
    * '$PLEX_HOME/Library/Application Support/Plex Media Server/',               # Linux
    * '/var/lib/plexmediaserver/Library/Application Support/Plex Media Server/', # Debian,Fedora,CentOS,Ubuntu
    * '/usr/local/plexdata/Plex Media Server/',                                  # FreeBSD
    * '/usr/pbi/plexmediaserver-amd64/plexdata/Plex Media Server/',              # FreeNAS
    * '${JAIL_ROOT}/var/db/plexdata/Plex Media Server/',                         # FreeNAS
    * '/c/.plex/Library/Application Support/Plex Media Server/',                 # ReadyNAS
    * '/share/MD0_DATA/.qpkg/PlexMediaServer/Library/Plex Media Server/',        # QNAP
    * '/volume1/Plex/Library/Application Support/Plex Media Server/',            # Synology, Asustor
    * '/raid0/data/module/Plex/sys/Plex Media Server/',                          # Thecus
    * '/raid0/data/PLEX_CONFIG/Plex Media Server/'                               # Thecus Plex community    

Get the latest source zip in github release at https://github.com/PhoenixPlexCode/PhoenixAdult.bundle > "Clone or download > Download Zip
- Open PhoenixAdult.bundle-master.zip and copy the folder inside (PhoenixAdult.bundle-master) to the plug-ins folders
- Rename folder to "PhoenixAdult.bundle" (remove -master)

##Notice
============
No real error checking is implemented. It was quickly tested on 10+ titles per site before the initial posting.

** Plex Video Files Scanner needs to be set as the library scanner for best results. **

##Change Log/Updates
============

**2018-09-09 6:00PM CST** - Initial Upload