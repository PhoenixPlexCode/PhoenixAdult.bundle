import re
import random
import urllib
import urllib2 as urllib
import urlparse
import json
from datetime import datetime
from PIL import Image
from cStringIO import StringIO
import pagenres

VERSION_NO = '2.2018.09.10.1'

def any(s):
    for v in s:
        if v:
            return True
    return False

def Start():
    HTTP.ClearCache()
    HTTP.CacheTime = CACHE_1MINUTE*20
    HTTP.Headers['User-agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
    HTTP.Headers['Accept-Encoding'] = 'gzip'

def capitalize(line):
    return ' '.join([s[0].upper() + s[1:] for s in line.split(' ')])

def tagAleadyExists(tag,metadata):
    for t in metadata.genres:
        if t.lower() == tag.lower():
            return True
    return False

def posterAlreadyExists(posterUrl,metadata):
    for p in metadata.posters.keys():
        Log(p.lower())
        if p.lower() == posterUrl.lower():
            Log("Found " + posterUrl + " in posters collection")
            return True

    for p in metadata.art.keys():
        if p.lower() == posterUrl.lower():
            return True
    return False



searchSites = [None] * 216
searchSites[1] = ["Blacked com","Blacked","https://www.blacked.com","https://www.blacked.com/search?q="]
searchSites[0] = ["Blackedraw com","BlackedRaw","https://www.blackedraw.com","https://www.blackedraw.com/search?q="]
searchSites[2] = ["Brazzers.com","Brazzers","http://www.brazzers.com","http://www.brazzers.com/search/all/?q="]
searchSites[4] = ["Blacked","Blacked","https://www.blacked.com","https://www.blacked.com/search?q="]
searchSites[3] = ["Blackedraw","BlackedRaw","https://www.blackedraw.com","https://www.blackedraw.com/search?q="]
searchSites[5] = ["My Friends Hot Mom","My Friends Hot Mom","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[6] = ["My First Sex Teacher","My First Sex Teacher","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[7] = ["Seduced By A Cougar","Seduced By A Cougar","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[8] = ["My Daughters Hot Friend","My Daughters Hot Friend","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[9] = ["My Wife is My Pornstar","My Wife is My Pornstar","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[10] = ["Tonights Girlfriend Class","Tonights Girlfriend Class","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[11] = ["Wives on Vacation","Wives on Vacation","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[12] = ["My Sisters Hot Friend","My Sisters Hot Friend","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[13] = ["Naughty Weddings","Naughty Weddings","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[14] = ["Dirty Wives Club","Dirty Wives Club","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[15] = ["My Dads Hot Girlfriend","My Dads Hot Girlfriend","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[16] = ["My Girl Loves Anal","My Girl Loves Anal","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[17] = ["Lesbian Girl on Girl","Lesbian Girl on Girl","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[18] = ["Naughty Office","Naughty Office","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[19] = ["I have a Wife","I have a Wife","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[20] = ["Naughty Bookworms","Naughty Bookworms","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[21] = ["Housewife 1 on 1","Housewife 1 on 1","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[22] = ["My Wifes Hot Friend","My Wifes Hot Friend","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[23] = ["Latin Adultery","Latin Adultery","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[24] = ["Ass Masterpiece","Ass Masterpiece","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[25] = ["2 Chicks Same Time","2 Chicks Same Time","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[26] = ["My Friends Hot Girl","My Friends Hot Girl","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[27] = ["Neighbor Affair","Neighbor Affair","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[28] = ["My Girlfriends Busty Friend","My Girlfriends Busty Friend","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[29] = ["Naughty Athletics","Naughty Athletics","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[30] = ["My Naughty Massage","My Naughty Massage","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[31] = ["Fast Times","Fast Times","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[32] = ["The Passenger","The Passenger","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[33] = ["Milf Sugar Babes Classic","Milf Sugar Babes Classic","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[34] = ["Perfect Fucking Strangers Classic","Perfect Fucking Strangers Classic","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[35] = ["Asian 1 on 1","Asian 1 on 1","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[36] = ["American Daydreams","American Daydreams","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[37] = ["SoCal Coeds","SoCal Coeds","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[38] = ["Naughty Country Girls","Naughty Country Girls","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[39] = ["Diary of a Milf","Diary of a Milf","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[40] = ["Naughty Rich Girls","Naughty Rich Girls","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[41] = ["My Naughty Latin Maid","My Naughty Latin Maid","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[42] = ["Naughty America","Naughty America","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[43] = ["Diary of a Nanny","Diary of a Nanny","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[44] = ["Naughty Flipside","Naughty Flipside","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[45] = ["Live Party Girl","Live Party Girl","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[46] = ["Live Naughty Student","Live Naughty Student","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[47] = ["Live Naughty Secretary","Live Naughty Secretary","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[48] = ["Live Gym Cam","Live Gym Cam","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[49] = ["Live Naughty Teacher","Live Naughty Teacher","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[50] = ["Live Naughty Milf","Live Naughty Milf","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[51] = ["Live Naughty Nurse","Live Naughty Nurse","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[52] = ["Vixen","Vixen","https://www.vixen.com","https://www.vixen.com/search?q="]
searchSites[53] = ["Girlsway","Girlsway","https://www.girlsway.com","https://www.girlsway.com/en/search/"]
searchSites[54] = ["Moms in Control","Moms in Control","http://www.brazzers.com","http://www.brazzers.com/search/all/?q="]
searchSites[55] = ["Pornstars Like It Big","Pornstars Like It Big","http://www.brazzers.com","http://www.brazzers.com/search/all/?q="]
searchSites[56] = ["Big Tits at Work","Big Tits at Work","http://www.brazzers.com","http://www.brazzers.com/search/all/?q="]
searchSites[57] = ["Big Tits at School","Big Tits at School","http://www.brazzers.com","http://www.brazzers.com/search/all/?q="]
searchSites[58] = ["Baby Got Boobs","Baby Got Boobs","http://www.brazzers.com","http://www.brazzers.com/search/all/?q="]
searchSites[59] = ["Real Wife Stories","Real Wife Stories","http://www.brazzers.com","http://www.brazzers.com/search/all/?q="]
searchSites[60] = ["Teens Like It Big","Teens Like It Big","http://www.brazzers.com","http://www.brazzers.com/search/all/?q="]
searchSites[61] = ["ZZ Series","ZZ Series","http://www.brazzers.com","http://www.brazzers.com/search/all/?q="]
searchSites[62] = ["Mommy Got Boobs","Mommy Got Boobs","http://www.brazzers.com","http://www.brazzers.com/search/all/?q="]
searchSites[63] = ["Milfs Like It Big","Milfs Like It Big","http://www.brazzers.com","http://www.brazzers.com/search/all/?q="]
searchSites[64] = ["Big Tits in Uniform","Big Tits in Uniform","http://www.brazzers.com","http://www.brazzers.com/search/all/?q="]
searchSites[65] = ["Doctor Adventures","Doctor Adventures","http://www.brazzers.com","http://www.brazzers.com/search/all/?q="]
searchSites[66] = ["BrazzersExxtra","Exxtra","http://www.brazzers.com","http://www.brazzers.com/search/all/?q="]
searchSites[67] = ["Big Tits in Sports","Big Tits in Sports","http://www.brazzers.com","http://www.brazzers.com/search/all/?q="]
searchSites[68] = ["Big Butts like it big","Big Butts like it big","http://www.brazzers.com","http://www.brazzers.com/search/all/?q="]
searchSites[69] = ["Big Wet Butts","Big Wet Butts","http://www.brazzers.com","http://www.brazzers.com/search/all/?q="]
searchSites[70] = ["Dirty Masseur","Dirty Masseur","http://www.brazzers.com","http://www.brazzers.com/search/all/?q="]
searchSites[71] = ["Hot and Mean","Hot and Mean","http://www.brazzers.com","http://www.brazzers.com/search/all/?q="]
searchSites[72] = ["Shes Gonna Squirt","Shes Gonna Squirt","http://www.brazzers.com","http://www.brazzers.com/search/all/?q="]
searchSites[73] = ["Asses In Public","Asses In Public","http://www.brazzers.com","http://www.brazzers.com/search/all/?q="]
searchSites[74] = ["Busty Z","Busty Z","http://www.brazzers.com","http://www.brazzers.com/search/all/?q="]
searchSites[75] = ["Busty and Real","Busty and Real","http://www.brazzers.com","http://www.brazzers.com/search/all/?q="]
searchSites[76] = ["Hot Chicks Big Asses","Hot Chicks Big Asses","http://www.brazzers.com","http://www.brazzers.com/search/all/?q="]
searchSites[77] = ["CFNM Clothed Female Male Nude","CFNM Clothed Female Male Nude","http://www.brazzers.com","http://www.brazzers.com/search/all/?q="]
searchSites[78] = ["Teens Like It Black","Teens Like It Black","http://www.brazzers.com","http://www.brazzers.com/search/all/?q="]
searchSites[79] = ["Racks and Blacks","Racks and Blacks","http://www.brazzers.com","http://www.brazzers.com/search/all/?q="]
searchSites[80] = ["Butts and Blacks","Butts and Blacks","http://www.brazzers.com","http://www.brazzers.com/search/all/?q="]
searchSites[81] = ["Brazzers","Brazzers","http://www.brazzers.com","http://www.brazzers.com/search/all/?q="]
searchSites[82] = ["X Art","X-Art","http://www.x-art.com","http://www.x-art.com/search/"]
searchSites[83] = ["Bang Bros","Bang Bros","https://bangbros.com","https://bangbros.com/search/"]
searchSites[84] = ["Ass Parade","Ass Parade","https://bangbros.com","https://bangbros.com/search/"]
searchSites[85] = ["AvaSpice","AvaSpice","https://bangbros.com","https://bangbros.com/search/"]
searchSites[86] = ["Back Room Facials","Back Room Facials","https://bangbros.com","https://bangbros.com/search/"]
searchSites[87] = ["Backroom MILF","Backroom MILF","https://bangbros.com","https://bangbros.com/search/"]
searchSites[88] = ["Ball Honeys","Ball Honeys","https://bangbros.com","https://bangbros.com/search/"]
searchSites[89] = ["Bang Bus","Bang Bus","https://bangbros.com","https://bangbros.com/search/"]
searchSites[90] = ["Bang Casting","Bang Casting","https://bangbros.com","https://bangbros.com/search/"]
searchSites[91] = ["Bang POV","Bang POV","https://bangbros.com","https://bangbros.com/search/"]
searchSites[92] = ["Bang Tryouts","Bang Tryouts","https://bangbros.com","https://bangbros.com/search/"]
searchSites[93] = ["BangBros 18","BangBros 18","https://bangbros.com","https://bangbros.com/search/"]
searchSites[94] = ["BangBros Angels","BangBros Angels","https://bangbros.com","https://bangbros.com/search/"]
searchSites[95] = ["Bangbros Clips","Bangbros Clips","https://bangbros.com","https://bangbros.com/search/"]
searchSites[96] = ["BangBros Remastered","BangBros Remastered","https://bangbros.com","https://bangbros.com/search/"]
searchSites[97] = ["Big Mouthfuls","Big Mouthfuls","https://bangbros.com","https://bangbros.com/search/"]
searchSites[98] = ["Big Tit Cream Pie","Big Tit Cream Pie","https://bangbros.com","https://bangbros.com/search/"]
searchSites[99] = ["Big Tits Round Asses","Big Tits Round Asses","https://bangbros.com","https://bangbros.com/search/"]
searchSites[100] = ["BlowJob Fridays","BlowJob Fridays","https://bangbros.com","https://bangbros.com/search/"]
searchSites[101] = ["Blowjob Ninjas","Blowjob Ninjas","https://bangbros.com","https://bangbros.com/search/"]
searchSites[102] = ["Boob Squad","Boob Squad","https://bangbros.com","https://bangbros.com/search/"]
searchSites[103] = ["Brown Bunnies","Brown Bunnies","https://bangbros.com","https://bangbros.com/search/"]
searchSites[104] = ["Can He Score","Can He Score","https://bangbros.com","https://bangbros.com/search/"]
searchSites[105] = ["Casting","Casting","https://bangbros.com","https://bangbros.com/search/"]
searchSites[106] = ["Chongas","Chongas","https://bangbros.com","https://bangbros.com/search/"]
searchSites[107] = ["Colombia Fuck Fest","Colombia Fuck Fest","https://bangbros.com","https://bangbros.com/search/"]
searchSites[108] = ["Dirty World Tour","Dirty World Tour","https://bangbros.com","https://bangbros.com/search/"]
searchSites[109] = ["Dorm Invasion","Dorm Invasion","https://bangbros.com","https://bangbros.com/search/"]
searchSites[110] = ["Facial Fest","Facial Fest","https://bangbros.com","https://bangbros.com/search/"]
searchSites[111] = ["Fuck Team Five","Fuck Team Five","https://bangbros.com","https://bangbros.com/search/"]
searchSites[112] = ["Glory Hole Loads","Glory Hole Loads","https://bangbros.com","https://bangbros.com/search/"]
searchSites[113] = ["Latina Rampage","Latina Rampage","https://bangbros.com","https://bangbros.com/search/"]
searchSites[114] = ["Living With Anna","Living With Anna","https://bangbros.com","https://bangbros.com/search/"]
searchSites[115] = ["Magical Feet","Magical Feet","https://bangbros.com","https://bangbros.com/search/"]
searchSites[116] = ["MILF Lessons","MILF Lessons","https://bangbros.com","https://bangbros.com/search/"]
searchSites[117] = ["Milf Soup","Milf Soup","https://bangbros.com","https://bangbros.com/search/"]
searchSites[118] = ["MomIsHorny","MomIsHorny","https://bangbros.com","https://bangbros.com/search/"]
searchSites[119] = ["Monsters of Cock","Monsters of Cock","https://bangbros.com","https://bangbros.com/search/"]
searchSites[120] = ["Mr CamelToe","Mr CamelToe","https://bangbros.com","https://bangbros.com/search/"]
searchSites[121] = ["Mr Anal","Mr Anal","https://bangbros.com","https://bangbros.com/search/"]
searchSites[122] = ["My Dirty Maid","My Dirty Maid","https://bangbros.com","https://bangbros.com/search/"]
searchSites[123] = ["My Life In Brazil","My Life In Brazil","https://bangbros.com","https://bangbros.com/search/"]
searchSites[124] = ["Newbie Black","Newbie Black","https://bangbros.com","https://bangbros.com/search/"]
searchSites[125] = ["Party of 3","Party of 3","https://bangbros.com","https://bangbros.com/search/"]
searchSites[126] = ["Pawg","Pawg","https://bangbros.com","https://bangbros.com/search/"]
searchSites[127] = ["Penny Show","Penny Show","https://bangbros.com","https://bangbros.com/search/"]
searchSites[128] = ["Porn Star Spa","Porn Star Spa","https://bangbros.com","https://bangbros.com/search/"]
searchSites[129] = ["Power Munch","Power Munch","https://bangbros.com","https://bangbros.com/search/"]
searchSites[130] = ["Public Bang","Public Bang","https://bangbros.com","https://bangbros.com/search/"]
searchSites[131] = ["Slutty White Girls","Slutty White Girls","https://bangbros.com","https://bangbros.com/search/"]
searchSites[132] = ["Stepmom Videos","Stepmom Videos","https://bangbros.com","https://bangbros.com/search/"]
searchSites[133] = ["Street Ranger","Street Ranger","https://bangbros.com","https://bangbros.com/search/"]
searchSites[134] = ["Tugjobs","Tugjobs","https://bangbros.com","https://bangbros.com/search/"]
searchSites[135] = ["Working Latinas","Working Latinas","https://bangbros.com","https://bangbros.com/search/"]
searchSites[136] = ["Tushy","Tushy","https://www.tushy.com","https://www.tushy.com/search?q="]
searchSites[137] = ["Reality Kings","Reality Kings", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[138] = ["40 Inch Plus", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[139] = ["8th Street Latinas","8th Street Latinas", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[140] = ["Bad Tow Truck","Bad Tow Truck", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[141] = ["Big Naturals","Big Naturals", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[142] = ["Big Tits Boss","Big Tits Boss", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[143] = ["Bikini Crashers","Bikini Crashers", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[144] = ["Captain Stabbin","Captain Stabbin", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[145] = ["CFNM Secret","CFNM Secret", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[146] = ["Cum Fiesta","Cum Fiesta", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[147] = ["Cum Girls","Cum Girls", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[148] = ["Dangerous Dongs","Dangerous Dongs", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[149] = ["Euro Sex Parties","Euro Sex Parties", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[150] = ["Extreme Asses","Extreme Asses", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[151] = ["Extreme Naturals","Extreme Naturals", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[152] = ["First Time Auditions","First Time Auditions", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[153] = ["Flower Tucci","Flower Tucci", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[154] = ["Girls of Naked","Girls of Naked", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[155] = ["Happy Tugs","Happy Tugs", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[156] = ["HD Love","HD Love", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[157] = ["Hot Bush","Hot Bush", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[158] = ["In the VIP","In the VIP", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[159] = ["Mike in Brazil","Mike in Brazil", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[160] = ["Mikes Apartment","Mike's Apartment", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[161] = ["Milf Hunter","Milf Hunter", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[162] = ["Milf Next Door","Milf Next Door", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[163] = ["Moms Bang Teens","Moms Bang Teens", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[164] = ["Moms Lick Teens","Moms Lick Teens", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[165] = ["Money Talks","Money Talks", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[166] = ["Monster Curves","Monster Curves", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[167] = ["No Faces","No Faces", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[168] = ["Pure 18","Pure 18", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[169] = ["Real Orgasms","Real Orgasms", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[170] = ["RK Prime","RK Prime", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[171] = ["Round and Brown","Round and Brown", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[172] = ["Saturday Night Latinas","Saturday Night Latinas", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[173] = ["See My Wife","See My Wife", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[174] = ["Sneaky Sex","Sneaky Sex", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[175] = ["Street BlowJobs","Street BlowJobs", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[176] = ["Team Squirt","Team Squirt", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[177] = ["Teens Love Huge Cocks","Teens Love Huge Cocks", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[178] = ["Top Shelf Pussy","Top Shelf Pussy", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[179] = ["Tranny Surprise","Tranny Surprise", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[180] = ["VIP Crew","VIP Crew", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[181] = ["We Live Together","We Live Together", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[182] = ["Wives in Pantyhose","Wives in Pantyhose", "https://www.realitykings.com/", "https://www.realitykings.com/tour/search/videos/"]
searchSites[183] = ["21Naturals","21Naturals","https://www.21naturals.com","https://www.21naturals.com/en/search/"]
searchSites[184] = ["PornFidelity","PornFidelity","https://www.pornfidelity.com","https://www.pornfidelity.com/?site=2&search="]
searchSites[185] = ["TeenFidelity","TeemFidelity","https://www.pornfidelity.com","https://www.pornfidelity.com/?site=3&search="]
searchSites[186] = ["Kelly Madison","Kelly Madison","https://www.pornfidelity.com","https://www.pornfidelity.com/?site=1&search="]
searchSites[187] = ["TeamSkeet", "TeamSkeet", "https://www.teamskeet.com","https://www.teamskeet.com/t1/search/results/?query="]
searchSites[188] = ["Exxxtra small","Exxxtra small", "https://www.teamskeet.com","https://www.teamskeet.com/t1/search/results/?query="]
searchSites[189] = ["Teen Pies","Teen Pies", "https://www.teamskeet.com","https://www.teamskeet.com/t1/search/results/?query="]
searchSites[190] = ["Innocent High","Innocent High", "https://www.teamskeet.com","https://www.teamskeet.com/t1/search/results/?query="]
searchSites[191] = ["Teen Curves","Teen Curves", "https://www.teamskeet.com","https://www.teamskeet.com/t1/search/results/?query="]
searchSites[192] = ["CFNM Teens","CFNM Teens", "https://www.teamskeet.com","https://www.teamskeet.com/t1/search/results/?query="]
searchSites[193] = ["Teens Love Anal","Teens Love Anal", "https://www.teamskeet.com","https://www.teamskeet.com/t1/search/results/?query="]
searchSites[194] = ["My Babysitters Club","My Babysitters Club", "https://www.teamskeet.com","https://www.teamskeet.com/t1/search/results/?query="]
searchSites[195] = ["She's New","She's New", "https://www.teamskeet.com","https://www.teamskeet.com/t1/search/results/?query="]
searchSites[196] = ["Teens Do Porn","Teens Do Porn", "https://www.teamskeet.com","https://www.teamskeet.com/t1/search/results/?query="]
searchSites[197] = ["POV Life","POV Life", "https://www.teamskeet.com","https://www.teamskeet.com/t1/search/results/?query="]
searchSites[198] = ["The Real Workout","The Real Workout", "https://www.teamskeet.com","https://www.teamskeet.com/t1/search/results/?query="]
searchSites[199] = ["This Girl Sucks","This Girl Sucks", "https://www.teamskeet.com","https://www.teamskeet.com/t1/search/results/?query="]
searchSites[200] = ["Teens Love Money","Teens Love Money", "https://www.teamskeet.com","https://www.teamskeet.com/t1/search/results/?query="]
searchSites[201] = ["Oye Loca","Oye Loca", "https://www.teamskeet.com","https://www.teamskeet.com/t1/search/results/?query="]
searchSites[202] = ["Titty Attack","Titty Attack", "https://www.teamskeet.com","https://www.teamskeet.com/t1/search/results/?query="]
searchSites[203] = ["Teeny Black","Teeny Black", "https://www.teamskeet.com","https://www.teamskeet.com/t1/search/results/?query="]
searchSites[204] = ["Lust HD","Lust HD", "https://www.teamskeet.com","https://www.teamskeet.com/t1/search/results/?query="]
searchSites[205] = ["Rub A Teen","Rub A Teen", "https://www.teamskeet.com","https://www.teamskeet.com/t1/search/results/?query="]
searchSites[206] = ["Her Freshman Year","Her Freshman Year", "https://www.teamskeet.com","https://www.teamskeet.com/t1/search/results/?query="]
searchSites[207] = ["Self Desire","Self Desire", "https://www.teamskeet.com","https://www.teamskeet.com/t1/search/results/?query="]
searchSites[208] = ["Solo Interviews","Solo Interviews", "https://www.teamskeet.com","https://www.teamskeet.com/t1/search/results/?query="]
searchSites[209] = ["Team Skeet Extras","Team Skeet Extras", "https://www.teamskeet.com","https://www.teamskeet.com/t1/search/results/?query="]
searchSites[210] = ["Dyked","Dyked", "https://www.teamskeet.com","https://www.teamskeet.com/t1/search/results/?query="]
searchSites[211] = ["Badmilfs","Badmilfs", "https://www.teamskeet.com","https://www.teamskeet.com/t1/search/results/?query="]
searchSites[212] = ["Gingerpatch","Gingerpatch", "https://www.teamskeet.com","https://www.teamskeet.com/t1/search/results/?query="]
searchSites[213] = ["BraceFaced","BraceFaced", "https://www.teamskeet.com","https://www.teamskeet.com/t1/search/results/?query="]
searchSites[214] = ["TeenJoi","TeenJoi", "https://www.teamskeet.com","https://www.teamskeet.com/t1/search/results/?query="]
searchSites[215] = ["StepSiblings","StepSiblings", "https://www.teamskeet.com","https://www.teamskeet.com/t1/search/results/?query="]

def getSearchBaseURL(siteID):
    return searchSites[siteID][2]
def getSearchSearchURL(siteID):
    return searchSites[siteID][3]
def getSearchFilter(siteID):
    return searchSites[siteID][0]
def getSearchSiteName(siteID):
    return searchSites[siteID][1]
def getSearchSiteIDByFilter(searchFilter):
    searchID = 0
    for sites in searchSites:
        if sites[0].lower() in searchFilter.lower().replace("."," "):
            return searchID
        searchID += 1
    return 9999
def getSearchSettings(mediaTitle):
    mediaTitle = mediaTitle.replace(".", " ")
    mediaTitle = mediaTitle.replace(" - ", " ")
    mediaTitle = mediaTitle.replace("-", " ")
    # Search Site ID or -1 is all
    searchSiteID = None
    # Date/Actor or Title
    searchType = None
    # What to search for
    searchTitle = None
    # Date search
    searchDate = None
    # Actors search
    searchActors = None

    # Remove Site from Title
    searchSiteID = getSearchSiteIDByFilter(mediaTitle)
    Log("^^^^^^^" + str(searchSiteID))
    if searchSiteID != 9999:
        Log("^^^^^^^ Shortening Title")
        if mediaTitle[:len(searchSites[searchSiteID][0])].lower() == searchSites[searchSiteID][0].lower():
            searchTitle = mediaTitle[len(searchSites[searchSiteID][0])+1:]
        else:
            searchTitle = mediaTitle
    else:
        searchTitle = mediaTitle

    #Search Type
    if unicode(searchTitle[:4], 'utf-8').isnumeric():
        if unicode(searchTitle[5:7], 'utf-8').isnumeric():
            if unicode(searchTitle[8:10], 'utf-8').isnumeric():
                searchType = 1
                searchDate = searchTitle[0:10].replace(" ","-")
                searchTitle = searchTitle[11:]
            else:
                searchType = 0
        else:
            searchType = 0
    else:
        searchType = 0

    return [searchSiteID,searchType,searchTitle,searchDate]

    

class EXCAgent(Agent.Movies):
    name = 'PhoenixAdult'
    languages = [Locale.Language.English]
    accepts_from = ['com.plexapp.agents.localmedia']
    primary_provider = True

    def search(self, results, media, lang):
        title = media.name
        if media.primary_metadata is not None:
            title = media.primary_metadata.title
        title = title.replace('"','').replace("'","").replace(":","").replace("!","").replace("(","").replace(")","").replace("&","")
        Log('*******MEDIA TITLE****** ' + str(title))

        # Search for year
        year = media.year
        if media.primary_metadata is not None:
            year = media.primary_metadata.year

        Log("Getting Search Settings for: " + title)
        searchSettings = getSearchSettings(title)
        if searchSettings[0] == 9999:
            searchAll = True
        else:
            searchAll = False
            searchSiteID = searchSettings[0]
            if searchSiteID == 3:
                searchSiteID = 0
            if searchSiteID == 4:
                searchSiteID = 1
        searchTitle = searchSettings[2]
        Log("Site ID: " + str(searchSettings[0]))
        Log("Search Title: " + searchSettings[2])
        if searchSettings[1]:
            searchByDateActor = True
            searchDate = searchSettings[3]
            Log("Search Date: " + searchSettings[3])
        else:
            searchByDateActor = False

        encodedTitle = urllib.quote(searchTitle)
        Log(encodedTitle)
        siteNum = 0
        for searchSite in searchSites:
            ###############
            ## Blacked and Blacked Raw Search
            ###############
            if siteNum == 0 or siteNum == 1:
                if searchAll or searchSiteID == 0 or searchSiteID == 1:
                    searchResults = HTML.ElementFromURL(getSearchSearchURL(siteNum) + encodedTitle)
                    for searchResult in searchResults.xpath('//article[@class="videolist-item"]'):
                        
                        
                        Log(searchResult.text_content())
                        titleNoFormatting = searchResult.xpath('.//h4[@class="videolist-caption-title"]')[0].text_content()
                        Log("Result Title: " + titleNoFormatting)
                        curID = searchResult.xpath('.//a[@class="videolist-link ajaxable"]')[0].get('href')
                        curID = curID.replace('/','_')
                        Log("ID: " + curID)
                        releasedDate = searchResult.xpath('.//div[@class="videolist-caption-date"]')[0].text_content()

                        Log(str(curID))
                        lowerResultTitle = str(titleNoFormatting).lower()
                        if searchByDateActor != True:
                            score = 102 - Util.LevenshteinDistance(searchTitle.lower(), titleNoFormatting.lower())
                        else:
                            searchDateCompare = datetime.strptime(searchDate, '%Y-%m-%d').strftime('%B %d, %y')
                            score = 102 - Util.LevenshteinDistance(searchDateCompare.lower(), releasedDate.lower())
                        titleNoFormatting = titleNoFormatting + " [" + searchSites[siteNum][1] + ", " + releasedDate + "]"
                        results.Append(MetadataSearchResult(id = curID + "|" + str(siteNum), name = titleNoFormatting, score = score, lang = lang))

            ###############
            ## Brazzers
            ###############
            if siteNum == 2:
                if searchAll or searchSiteID == 2 or (searchSiteID >= 54 and searchSiteID <= 81):
                    searchResults = HTML.ElementFromURL('http://www.brazzers.com/search/all/?q=' + encodedTitle)
                    for searchResult in searchResults.xpath('//h2[contains(@class,"scene-card-title")]//a'):
                        Log(str(searchResult.get('href')))
                        titleNoFormatting = searchResult.get('title')
                        curID = searchResult.get('href').replace('/','_')
                        lowerResultTitle = str(titleNoFormatting).lower()
                        score = 100 - Util.LevenshteinDistance(title.lower(), titleNoFormatting.lower())
                        
                        results.Append(MetadataSearchResult(id = curID + "|" + str(siteNum), name = titleNoFormatting + " [Brazzers]", score = score, lang = lang))
                            
            ###############
            ## Naughty America
            ###############
            if siteNum == 5:
                if searchAll or (searchSiteID >= 5 and searchSiteID <= 51): 
                    searchString = encodedTitle.replace(" ","+")
                    if not searchAll:
                        searchString = searchString + "+in+" + getSearchSiteName(searchSiteID).replace(" ","+")
                    searchResults = HTML.ElementFromURL(getSearchSearchURL(siteNum) + searchString)
                    for searchResult in searchResults.xpath('//div[@class="scene-item"]'):
                        titleNoFormatting = searchResult.xpath('.//a')[0].get("title")
                        Log("Result Title: " + titleNoFormatting)
                        curID = searchResult.xpath('.//a')[0].get('href')
                        curID = curID[31:-26]
                        curID = curID.replace('/','_')
                        Log("ID: " + curID)
                        releasedDate = searchResult.xpath('.//p[@class="entry-date"]')[0].text_content()

                        Log("CurID" + str(curID))
                        lowerResultTitle = str(titleNoFormatting).lower()
                        searchString = searchString.replace("+"," ")
                        if searchByDateActor != True:
                            score = 102 - Util.LevenshteinDistance(searchString.lower(), titleNoFormatting.lower())
                        else:
                            searchDateCompare = datetime.strptime(searchDate, '%Y-%m-%d').strftime('%b %d, %y')
                            score = 102 - Util.LevenshteinDistance(searchDateCompare.lower(), releasedDate.lower())
                        titleNoFormatting = titleNoFormatting + " [NA, " + releasedDate +"]"
                        results.Append(MetadataSearchResult(id = curID + "|" + str(siteNum), name = titleNoFormatting, score = score, lang = lang))

            ###############
            ## Vixen
            ###############
            if siteNum == 52:
                if searchAll or searchSiteID == 52:
                    searchResults = HTML.ElementFromURL(getSearchSearchURL(siteNum) + encodedTitle)
                    for searchResult in searchResults.xpath('//article[@class="videolist-item"]'):
                        
                        
                        Log(searchResult.text_content())
                        titleNoFormatting = searchResult.xpath('.//h4[@class="videolist-caption-title"]')[0].text_content()
                        Log("Result Title: " + titleNoFormatting)
                        curID = searchResult.xpath('.//a[@class="videolist-link ajaxable"]')[0].get('href')
                        curID = curID.replace('/','_')
                        Log("ID: " + curID)
                        releasedDate = searchResult.xpath('.//div[@class="videolist-caption-date"]')[0].text_content()

                        Log(str(curID))
                        lowerResultTitle = str(titleNoFormatting).lower()
                        if searchByDateActor != True:
                            score = 102 - Util.LevenshteinDistance(searchTitle.lower(), titleNoFormatting.lower())
                        else:
                            searchDateCompare = datetime.strptime(searchDate, '%Y-%m-%d').strftime('%B %d, %y')
                            score = 102 - Util.LevenshteinDistance(searchDateCompare.lower(), releasedDate.lower())
                        titleNoFormatting = titleNoFormatting + " [" + searchSites[siteNum][1] + ", " + releasedDate + "]"
                        results.Append(MetadataSearchResult(id = curID + "|" + str(siteNum), name = titleNoFormatting, score = score, lang = lang))
                
            ###############
            ## Girlsway
            ###############
            if siteNum == 53:
                if searchAll or searchSiteID == 53:
                    searchResults = HTML.ElementFromURL('https://www.girlsway.com/en/search/' + encodedTitle)

                    for searchResult in searchResults.xpath('//div[@class="tlcTitle"]'):

                        Log(searchResult.text_content())
                        titleNoFormatting = searchResult.xpath('.//a')[0].get("title")
                        curID = searchResult.xpath('.//a')[0].get("href")
                        curID = curID.replace('/','_')
                        Log(str(curID))
                        lowerResultTitle = str(titleNoFormatting).lower()
                        score = 100 - Util.LevenshteinDistance(title.lower(), titleNoFormatting.lower())
                        titleNoFormatting = titleNoFormatting + " [Girlsway]"
                        results.Append(MetadataSearchResult(id = curID + "|" + str(siteNum), name = titleNoFormatting, score = score, lang = lang))
                
            ###############
            ## X-Art
            ###############
            if siteNum == 82:
                if searchAll or searchSiteID == 82:
                    xartpost = {
                        "input_search_sm" : encodedTitle
                    }
                    searchResults = HTML.ElementFromURL('https://www.x-art.com/search/', values = xartpost)
                    
                    for searchResult in searchResults.xpath('//a[contains(@href,"videos")]'):
                        link = searchResult.xpath('.//img[contains(@src,"videos")]')
                        if len(link) > 0:
                            if link[0].get("alt") is not None:
                                
                                titleNoFormatting = link[0].get("alt")
                                curID = searchResult.get("href")[21:]
                                curID = curID.replace('/','+')
                                Log(str(curID))
                                lowerResultTitle = str(titleNoFormatting).lower()
                                score = 100 - Util.LevenshteinDistance(title.lower(), titleNoFormatting.lower())
                                titleNoFormatting = titleNoFormatting + " [X-Art]"
                                results.Append(MetadataSearchResult(id = curID + "|" + str(siteNum), name = titleNoFormatting, score = score, lang = lang))
            
            ###############
            ## Bang Bros
            ###############
            if siteNum == 83:
                if searchAll or (searchSiteID >= 83 and searchSiteID <= 135):
                    searchPageNum = 1
                    while searchPageNum <= 2:
                        searchResults = HTML.ElementFromURL(getSearchSearchURL(siteNum) + encodedTitle + "/" + str(searchPageNum))

                        for searchResult in searchResults.xpath('//div[@class="echThumb"]'):
                            if len(searchResult.xpath('.//a[contains(@href,"/video")]')) > 0:
                                titleNoFormatting = searchResult.xpath('.//a[contains(@href,"/video")]')[0].get("title")
                                curID = searchResult.xpath('.//a[contains(@href,"/video")]')[0].get("href")
                                curID = curID.replace('/','_')
                                Log(str(curID))


                                releasedDate = searchResult.xpath('.//span[@class="faTxt"]')[1].text_content()

                                Log(str(curID))
                                lowerResultTitle = str(titleNoFormatting).lower()
                                if searchByDateActor != True:
                                    score = 102 - Util.LevenshteinDistance(searchTitle.lower(), titleNoFormatting.lower())
                                else:
                                    searchDateCompare = datetime.strptime(searchDate, '%Y-%m-%d').strftime('%b %d, %y')
                                    score = 102 - Util.LevenshteinDistance(searchDateCompare.lower(), releasedDate.lower())
                                titleNoFormatting = titleNoFormatting + " [Bang Bros, " + releasedDate + "]"
                                results.Append(MetadataSearchResult(id = curID + "|" + str(siteNum), name = titleNoFormatting, score = score, lang = lang))
                        searchPageNum += 1

            ###############
            ## Tushy
            ###############
            if siteNum == 136:
                if searchAll or searchSiteID == 136:
                    
                    searchResults = HTML.ElementFromURL(getSearchSearchURL(siteNum) + encodedTitle)
                    for searchResult in searchResults.xpath('//article[@class="videolist-item"]'):
                        
                        
                        Log(searchResult.text_content())
                        titleNoFormatting = searchResult.xpath('.//h4[@class="videolist-caption-title"]')[0].text_content()
                        Log("Result Title: " + titleNoFormatting)
                        curID = searchResult.xpath('.//a[@class="videolist-link ajaxable"]')[0].get('href')
                        curID = curID.replace('/','_')
                        Log("ID: " + curID)
                        releasedDate = searchResult.xpath('.//div[@class="videolist-caption-date"]')[0].text_content()

                        Log(str(curID))
                        lowerResultTitle = str(titleNoFormatting).lower()
                        if searchByDateActor != True:
                            score = 102 - Util.LevenshteinDistance(searchTitle.lower(), titleNoFormatting.lower())
                        else:
                            searchDateCompare = datetime.strptime(searchDate, '%Y-%m-%d').strftime('%B %d, %y')
                            score = 102 - Util.LevenshteinDistance(searchDateCompare.lower(), releasedDate.lower())
                        titleNoFormatting = titleNoFormatting + " [" + searchSites[siteNum][1] + ", " + releasedDate + "]"
                        results.Append(MetadataSearchResult(id = curID + "|" + str(siteNum), name = titleNoFormatting, score = score, lang = lang))
                    if searchByDateActor == True:
                        searchResults = HTML.ElementFromURL(getSearchSearchURL(siteNum) + encodedTitle + "&page=2")
                        for searchResult in searchResults.xpath('//article[@class="videolist-item"]'):
                            
                            
                            Log(searchResult.text_content())
                            titleNoFormatting = searchResult.xpath('.//h4[@class="videolist-caption-title"]')[0].text_content()
                            Log("Result Title: " + titleNoFormatting)
                            curID = searchResult.xpath('.//a[@class="videolist-link ajaxable"]')[0].get('href')
                            curID = curID.replace('/','_')
                            Log("ID: " + curID)
                            releasedDate = searchResult.xpath('.//div[@class="videolist-caption-date"]')[0].text_content()

                            Log(str(curID))
                            lowerResultTitle = str(titleNoFormatting).lower()
                            if searchByDateActor != True:
                                score = 102 - Util.LevenshteinDistance(searchTitle.lower(), titleNoFormatting.lower())
                            else:
                                searchDateCompare = datetime.strptime(searchDate, '%Y-%m-%d').strftime('%B %d, %y')
                                score = 102 - Util.LevenshteinDistance(searchDateCompare.lower(), releasedDate.lower())
                            titleNoFormatting = titleNoFormatting + " [" + searchSites[siteNum][1] + ", " + releasedDate + "]"
                            results.Append(MetadataSearchResult(id = curID + "|" + str(siteNum), name = titleNoFormatting, score = score, lang = lang))

            ###############
            ## Reality Kings
            ###############
            if siteNum == 137:
                if searchAll or (searchSiteID >= 137 and searchSiteID <= 182):
                    searchResults = HTML.ElementFromURL(getSearchSearchURL(siteNum) + encodedTitle)
                    for searchResult in searchResults.xpath('//p[contains(@class,"card-info__title")]'):
                        titleNoFormatting = searchResult.xpath('.//a')[0].get('title')
                        curID = searchResult.xpath('.//a')[0].get('href').replace('/','_')
                        lowerResultTitle = str(titleNoFormatting).lower()
                        score = 100 - Util.LevenshteinDistance(title.lower(), titleNoFormatting.lower())
                        
                        results.Append(MetadataSearchResult(id = curID + "|" + str(siteNum), name = titleNoFormatting + " [Reality Kings]", score = score, lang = lang))
                            
            
            ###############
            ## 21Naturals
            ###############
            if siteNum == 183:
                if searchAll or searchSiteID == 183:
                    searchResults = HTML.ElementFromURL(getSearchSearchURL(siteNum) + encodedTitle)
                    for searchResult in searchResults.xpath('//div[contains(@class,"tlcItem")]'):
                        titleNoFormatting = searchResult.xpath('.//a')[0].get('title')
                        curID = searchResult.xpath('.//a')[0].get('href')
                        curID = curID.replace('/','_')
                        Log("ID: " + curID)
                        releasedDate = searchResult.xpath('.//span[@class="tlcSpecsDate"]//span[@class="tlcDetailsValue"]')[0].text_content()

                        Log(str(curID))
                        lowerResultTitle = str(titleNoFormatting).lower()
                        if searchByDateActor != True:
                            score = 102 - Util.LevenshteinDistance(searchTitle.lower(), titleNoFormatting.lower())
                        else:
                            searchDateCompare = datetime.strptime(searchDate, '%Y-%m-%d').strftime('%Y-%m-%d')
                            score = 102 - Util.LevenshteinDistance(searchDateCompare.lower(), releasedDate.lower())
                        titleNoFormatting = titleNoFormatting + " [" + searchSites[siteNum][1] + ", " + releasedDate + "]"
                        results.Append(MetadataSearchResult(id = curID + "|" + str(siteNum), name = titleNoFormatting, score = score, lang = lang))
                            

            ###############
            ## PornFidelity
            ###############
            if siteNum == 184:
                
                if searchAll or searchSiteID == 184:
                    searchPageContent = HTTP.Request("https://www.pornfidelity.com/episodes/search?site=2&search=" + encodedTitle)
                    searchPageContent = str(searchPageContent).split('":"')
                    searchPageResult = searchPageContent[len(searchPageContent)-1][:-2]
                    searchPageResult = searchPageResult.replace('\\n',"").replace('\\',"")
                    Log(searchPageResult)
                    searchResults = HTML.ElementFromString(searchPageResult)
                    for searchResult in searchResults.xpath('//div[contains(@class,"episode")]'):
                        titleNoFormatting = searchResult.xpath('.//div[@class="card-title"]')[0].text_content()
                        Log(titleNoFormatting)
                        curID = searchResult.xpath('.//a[contains(@class,"card-link")]')[0].get('href')
                        curID = curID.replace('/','_')
                        curID = curID[8:-19]
                        Log("ID: " + curID)
                        releasedDate = searchResult.xpath('.//div[contains(@class,"card-meta")]//div[contains(@class,"text-left")]')[0].text_content()[19:-4]
                        if ", 20" not in releasedDate:
                            releasedDate = releasedDate + ", " + str(datetime.now().year)
                        Log(str(curID))
                        lowerResultTitle = str(titleNoFormatting).lower()
                        if searchByDateActor != True:
                            score = 102 - Util.LevenshteinDistance(searchTitle.lower(), titleNoFormatting.lower())
                        else:
                            searchDateCompare = datetime.strptime(searchDate, '%Y-%m-%d').strftime('%b %m, $Y')
                            score = 102 - Util.LevenshteinDistance(searchDateCompare.lower(), releasedDate.lower())
                        titleNoFormatting = titleNoFormatting + " [" + searchSites[siteNum][1] + ", " + releasedDate + "]"
                        results.Append(MetadataSearchResult(id = curID + "|" + str(siteNum), name = titleNoFormatting, score = score, lang = lang))
            
            ###############
            ## TeenFidelity
            ###############
            if siteNum == 185:
                
                if searchAll or searchSiteID == 185:
                    searchPageContent = HTTP.Request("https://www.pornfidelity.com/episodes/search?site=3&search=" + encodedTitle)
                    searchPageContent = str(searchPageContent).split('":"')
                    searchPageResult = searchPageContent[len(searchPageContent)-1][:-2]
                    searchPageResult = searchPageResult.replace('\\n',"").replace('\\',"")
                    Log(searchPageResult)
                    searchResults = HTML.ElementFromString(searchPageResult)
                    for searchResult in searchResults.xpath('//div[contains(@class,"episode")]'):
                        titleNoFormatting = searchResult.xpath('.//div[@class="card-title"]')[0].text_content()
                        Log(titleNoFormatting)
                        curID = searchResult.xpath('.//a[contains(@class,"card-link")]')[0].get('href')
                        curID = curID.replace('/','_')
                        curID = curID[8:-19]
                        Log("ID: " + curID)
                        releasedDate = searchResult.xpath('.//div[contains(@class,"card-meta")]//div[contains(@class,"text-left")]')[0].text_content()[19:-4]
                        if ", 20" not in releasedDate:
                            releasedDate = releasedDate + ", " + str(datetime.now().year)
                        Log(str(curID))
                        lowerResultTitle = str(titleNoFormatting).lower()
                        if searchByDateActor != True:
                            score = 102 - Util.LevenshteinDistance(searchTitle.lower(), titleNoFormatting.lower())
                        else:
                            searchDateCompare = datetime.strptime(searchDate, '%Y-%m-%d').strftime('%b %m, $Y')
                            score = 102 - Util.LevenshteinDistance(searchDateCompare.lower(), releasedDate.lower())
                        titleNoFormatting = titleNoFormatting + " [" + searchSites[siteNum][1] + ", " + releasedDate + "]"
                        results.Append(MetadataSearchResult(id = curID + "|" + str(siteNum), name = titleNoFormatting, score = score, lang = lang))

            ###############
            ## Kelly Madison
            ###############
            if siteNum == 186:
                if searchAll or searchSiteID == 186:
                    searchPageContent = HTTP.Request("https://www.pornfidelity.com/episodes/search?site=1&search=" + encodedTitle)
                    searchPageContent = str(searchPageContent).split('":"')
                    searchPageResult = searchPageContent[len(searchPageContent)-1][:-2]
                    searchPageResult = searchPageResult.replace('\\n',"").replace('\\',"")
                    Log(searchPageResult)
                    searchResults = HTML.ElementFromString(searchPageResult)
                    for searchResult in searchResults.xpath('//div[contains(@class,"episode")]'):
                        titleNoFormatting = searchResult.xpath('.//div[@class="card-title"]')[0].text_content()
                        Log(titleNoFormatting)
                        curID = searchResult.xpath('.//a[contains(@class,"card-link")]')[0].get('href')
                        curID = curID.replace('/','_')
                        curID = curID[8:-19]
                        Log("ID: " + curID)
                        releasedDate = searchResult.xpath('.//div[contains(@class,"card-meta")]//div[contains(@class,"text-left")]')[0].text_content()[19:-4]
                        if ", 20" not in releasedDate:
                            releasedDate = releasedDate + ", " + str(datetime.now().year)
                        Log(str(curID))
                        lowerResultTitle = str(titleNoFormatting).lower()
                        if searchByDateActor != True:
                            score = 102 - Util.LevenshteinDistance(searchTitle.lower(), titleNoFormatting.lower())
                        else:
                            searchDateCompare = datetime.strptime(searchDate, '%Y-%m-%d').strftime('%b %m, $Y')
                            score = 102 - Util.LevenshteinDistance(searchDateCompare.lower(), releasedDate.lower())
                        titleNoFormatting = titleNoFormatting + " [" + searchSites[siteNum][1] + ", " + releasedDate + "]"
                        results.Append(MetadataSearchResult(id = curID + "|" + str(siteNum), name = titleNoFormatting, score = score, lang = lang))

        
            ###############
            ## Team Skeet
            ###############
            if siteNum == 187:
                if searchAll or (searchSiteID >= 187 and searchSiteID <= 215):
                    searchResults = HTML.ElementFromURL(getSearchSearchURL(siteNum) + encodedTitle)
                    for searchResult in searchResults.xpath('//div[@class="info"]'):
                        titleURL = searchResult.xpath('.//a')[0].get("href")
                        scenePage = HTML.ElementFromURL(titleURL)
                        
                        Log(searchResult.text_content())
                        titleNoFormatting = scenePage.xpath('//title')[0].text_content().split(" | ")[1]
                        Log("Result Title: " + titleNoFormatting)
                        curID = searchResult.xpath('.//a')[0].get("href").split("?")[0][8:]
                        curID = curID.replace('/','+')
                        Log("ID: " + curID)
                        releasedDate = scenePage.xpath('//div[@style="width:430px;text-align:left;margin:8px;border-right:3px dotted #bbbbbb;position:relative;"]//div[@class="gray"]')[0].text_content()[12:]
                        Log(releasedDate)
                        Log(str(curID))
                        lowerResultTitle = str(titleNoFormatting).lower()
                        if searchByDateActor != True:
                            score = 102 - Util.LevenshteinDistance(searchTitle.lower(), titleNoFormatting.lower())
                        else:
                            searchDateCompare = datetime.strptime(searchDate, '%Y-%m-%d').strftime('%B %d, %Y')
                            score = 102 - Util.LevenshteinDistance(searchDateCompare.lower(), releasedDate.lower())
                        titleNoFormatting = titleNoFormatting + " [" + searchSites[siteNum][1] + ", " + releasedDate + "]"
                        results.Append(MetadataSearchResult(id = curID + "|" + str(siteNum), name = titleNoFormatting, score = score, lang = lang))

            siteNum += 1 
        
        results.Sort('score', descending=True)

    def update(self, metadata, media, lang):
        movieGenres = PhoenixGenres()
        
        HTTP.ClearCache()

        Log('******UPDATE CALLED*******')
        
        siteID = int(str(metadata.id).split("|")[1])
        Log(str(siteID))
        ##############################################################
        ##                                                          ##
        ##   Blacked                                                ##
        ##                                                          ##
        ##############################################################
        if siteID == 1:
            temp = str(metadata.id).split("|")[0].replace('_','/')

            url = getSearchBaseURL(siteID) + temp
            detailsPageElements = HTML.ElementFromURL(url)

            # Summary
            metadata.studio = "Blacked"
            paragraph = detailsPageElements.xpath('//span[@class="moreless js-readmore"]')[0].text_content()
            paragraph = paragraph.replace('&13;', '').strip(' \t\n\r"').replace('\n','').replace('  ','') + "\n\n"
            metadata.summary = paragraph
            metadata.title = detailsPageElements.xpath('//h1[@id="castme-title"]')[0].text_content()
            date = detailsPageElements.xpath('//span[@class="player-description-detail"]//span')[0].text_content()
            date_object = datetime.strptime(date, '%B %d, %Y')
            metadata.originally_available_at = date_object
            metadata.year = metadata.originally_available_at.year    
                
            
            # Genres
            movieGenres.clearGenres()
            # No Source for Genres, add manual
            movieGenres.addGenre("Interracial")
            movieGenres.addGenre("Hardcore")
            movieGenres.addGenre("Heterosexual")


            # Actors
            metadata.roles.clear()
            actors = detailsPageElements.xpath('//p[@id="castme-subtitle"]//a')
            if len(actors) > 0:
                for actorLink in actors:
                    role = metadata.roles.new()
                    actorName = actorLink.text_content()
                    role.name = actorName
                    actorPageURL = actorLink.get("href")
                    actorPage = HTML.ElementFromURL("https://www.blacked.com"+actorPageURL)
                    actorPhotoURL = actorPage.xpath('//img[@class="thumb-img"]')[0].get("src")
                    role.photo = actorPhotoURL

            # Posters/Background
            valid_names = list()
            metadata.posters.validate_keys(valid_names)
            metadata.art.validate_keys(valid_names)
            posters = detailsPageElements.xpath('//div[@class="swiper-slide"]')
            background = detailsPageElements.xpath('//img[contains(@class,"player-img")]')[0].get("src")
            metadata.art[background] = Proxy.Preview(HTTP.Request(background, headers={'Referer': 'http://www.google.com'}).content, sort_order = 1)

            posterNum = 1
            for posterCur in posters:
                posterURL = posterCur.xpath('.//img[@class="swiper-content-img"]')[0].get("src")
                metadata.posters[posterURL] = Proxy.Preview(HTTP.Request(posterURL, headers={'Referer': 'http://www.google.com'}).content, sort_order = posterNum)
                posterNum = posterNum + 1

        ##############################################################
        ##                                                          ##
        ##   Blacked Raw                                            ##
        ##                                                          ##
        ##############################################################
        if siteID == 0:
            Log('******UPDATE CALLED*******')
            temp = str(metadata.id).split("|")[0].replace('_','/')

            url = getSearchBaseURL(siteID) + temp
            detailsPageElements = HTML.ElementFromURL(url)

            # Summary
            metadata.studio = "BlackedRaw"
            paragraph = detailsPageElements.xpath('//span[@class="moreless js-readmore"]')[0].text_content()
            paragraph = paragraph.replace('&13;', '').strip(' \t\n\r"').replace('\n','').replace('  ','') + "\n\n"
            metadata.summary = paragraph
            metadata.title = detailsPageElements.xpath('//div[@id="castme-title"]')[0].text_content()
            date = detailsPageElements.xpath('//span[@class="right"]//span')[0].text_content()
            date_object = datetime.strptime(date, '%B %d, %Y')
            metadata.originally_available_at = date_object
            metadata.year = metadata.originally_available_at.year    
                
            
            # Genres
            movieGenres.clearGenres()
            # No Source for Genres, add manual
            movieGenres.addGenre("Interracial")
            movieGenres.addGenre("Hardcore")
            movieGenres.addGenre("Heterosexual")


            # Actors
            metadata.roles.clear()
            actors = detailsPageElements.xpath('//span[@id="castme-subtitle"]//a')
            if len(actors) > 0:
                for actorLink in actors:
                    role = metadata.roles.new()
                    actorName = actorLink.text_content()
                    role.name = actorName
                    actorPageURL = actorLink.get("href")
                    actorPage = HTML.ElementFromURL(getSearchBaseURL(siteID)+actorPageURL)
                    actorPhotoURL = actorPage.xpath('//img[@class="thumb-img"]')[0].get("src")
                    role.photo = actorPhotoURL

            # Posters/Background
            valid_names = list()
            metadata.posters.validate_keys(valid_names)
            metadata.art.validate_keys(valid_names)
            posters = detailsPageElements.xpath('//div[@class="swiper-slide"]')
            background = detailsPageElements.xpath('//img[contains(@class,"player-img")]')[0].get("src")
            metadata.art[background] = Proxy.Preview(HTTP.Request(background, headers={'Referer': 'http://www.google.com'}).content, sort_order = 1)
            posterNum = 1
            for posterCur in posters:
                posterURL = posterCur.xpath('.//img[@class="swiper-content-img"]')[0].get("src")
                metadata.posters[posterURL] = Proxy.Preview(HTTP.Request(posterURL, headers={'Referer': 'http://www.google.com'}).content, sort_order = posterNum)
                posterNum = posterNum + 1   
        
        ##############################################################
        ##                                                          ##
        ##   Brazzers                                               ##
        ##                                                          ##
        ##############################################################
        if siteID == 2 or (siteID >= 54 and siteID <= 81):
            Log('******UPDATE CALLED*******')
            zzseries = False
            metadata.studio = 'Brazzers'
            temp = str(metadata.id).split("|")[0].replace('_','/')
            url = getSearchBaseURL(siteID) + temp
            detailsPageElements = HTML.ElementFromURL(url)

            # Summary
            paragraph = detailsPageElements.xpath('//p[@itemprop="description"]')[0].text_content()
            paragraph = paragraph.replace('&13;', '').strip(' \t\n\r"').replace('\n','').replace('  ','') + "\n\n"
            metadata.summary = paragraph[:-10]
            tagline = detailsPageElements.xpath('//span[@class="label-text"]')[0].text_content()
            metadata.collections.clear()
            metadata.tagline = tagline
            metadata.collections.add(tagline)
            metadata.title = detailsPageElements.xpath('//h1')[0].text_content()

            # Genres
            movieGenres.clearGenres()
            genres = detailsPageElements.xpath('//div[contains(@class,"tag-card-container")]//a')

            if len(genres) > 0:
                for genreLink in genres:
                    genreName = genreLink.text_content().strip('\n').lower()
                    movieGenres.addGenre(genreName)


            
            date = detailsPageElements.xpath('//aside[contains(@class,"scene-date")]')
            if len(date) > 0:
                date = date[0].text_content()
                date_object = datetime.strptime(date, '%B %d, %Y')
                metadata.originally_available_at = date_object
                metadata.year = metadata.originally_available_at.year
            

            # Starring/Collection 
            metadata.roles.clear()
            #starring = detailsPageElements.xpath('//p[contains(@class,"related-model")]//a')
            starring = detailsPageElements.xpath('//div[@class="model-card"]//a')
            memberSceneActorPhotos = detailsPageElements.xpath('//img[contains(@class,"lazy card-main-img")]')
            memberSceneActorPhotos_TotalNum = len(memberSceneActorPhotos)
            memberTotalNum = len(starring)/2
            Log('----- Number of Actors: ' +str(memberTotalNum) + ' ------')
            Log('----- Number of Photos: ' +str(memberSceneActorPhotos_TotalNum) + ' ------')
            
            memberNum = 0
            for memberCard in starring:
                # Check if member exists in the maleActors list as either a string or substring
                #if any(member.text_content().strip() in m for m in maleActors) == False:
                    role = metadata.roles.new()
                    # Add to actor and collection
                    #role.name = "Test"
                    memberName = memberCard.xpath('//h2[contains(@class,"model-card-title")]//a')[memberNum]
                    memberPhoto = memberCard.xpath('//img[@class="lazy card-main-img" and @alt="'+memberName.text_content().strip()+'"]')[0].get('data-src')
                    role.name = memberName.text_content().strip()
                    memberNum = memberNum + 1
                    memberNum = memberNum % memberTotalNum
                    Log('--------- Photo   ---------- : ' + memberPhoto)
                    role.photo = "http:" + memberPhoto.replace("model-medium.jpg","model-small.jpg")

            detailsPageElements.xpath('//h1')[0].text_content()

            #Posters
            i = 1
            background = "http:" + detailsPageElements.xpath('//*[@id="trailer-player"]/img')[0].get('src')
            Log("BG DL: " + background)
            metadata.art[background] = Proxy.Preview(HTTP.Request(background, headers={'Referer': 'http://www.google.com'}).content, sort_order = 1)
            for poster in detailsPageElements.xpath('//a[@rel="preview"]'):
                posterUrl = "http:" + poster.get('href').strip()
                thumbUrl = "http:" + detailsPageElements.xpath('//img[contains(@data-src,"thm")]')[i-1].get('data-src')
                if not posterAlreadyExists(posterUrl,metadata):            
                    #Download image file for analysis
                    try:
                        img_file = urllib.urlopen(posterUrl)
                        im = StringIO(img_file.read())
                        resized_image = Image.open(im)
                        width, height = resized_image.size
                        #posterUrl = posterUrl[:-6] + "01.jpg"
                        #Add the image proxy items to the collection
                        if(width > 1):
                            # Item is a poster
                            
                            metadata.posters[posterUrl] = Proxy.Preview(HTTP.Request(posterUrl, headers={'Referer': 'http://www.google.com'}).content, sort_order = i)
                        if(width > 100):
                            # Item is an art item
                            metadata.art[posterUrl] = Proxy.Preview(HTTP.Request(posterUrl, headers={'Referer': 'http://www.google.com'}).content, sort_order = i+1)
                        i = i + 1
                    except:
                        pass
                
        ##############################################################
        ##                                                          ##
        ##   Naughty America                                        ##
        ##                                                          ##
        ##############################################################        
        if siteID >= 5 and siteID <= 51:
            temp = str(metadata.id).split("|")[0].replace('_','/')

            url = getSearchBaseURL(siteID) + temp
            detailsPageElements = HTML.ElementFromURL(url)

            # Summary
            metadata.studio = "Naughty America"
            #paragraph = detailsPageElements.xpath('//span[@class="moreless js-readmore"]')[0].text_content()
            #paragraph = paragraph.replace('&13;', '').strip(' \t\n\r"').replace('\n','').replace('  ','') + "\n\n"
            metadata.summary = detailsPageElements.xpath('//p[@class="synopsis_txt"]')[0].text_content()
            site = detailsPageElements.xpath('//a[@class="site-title grey-text"]')[0].text_content()
            metadata.title = " in " + site
            date = detailsPageElements.xpath('//p[@class="scenedate"]//span')[0].text_content()
            date_object = datetime.strptime(date, '%b %d, %Y')
            metadata.originally_available_at = date_object
            metadata.year = metadata.originally_available_at.year    
                
            # Actors
            metadata.roles.clear()
            titleActors = ""
            actors = detailsPageElements.xpath('//a[@class="scene-title grey-text"]')
            if len(actors) > 0:
                for actorLink in actors:
                    role = metadata.roles.new()
                    actorName = actorLink.text_content()
                    role.name = actorName
                    titleActors = titleActors + actorName + " & "
                    actorPageURL = actorLink.get("href")
                    actorPage = HTML.ElementFromURL(actorPageURL)
                    actorPhotoURL = "http:" + actorPage.xpath('//img[@class="performer-pic"]')[0].get("src")
                    role.photo = actorPhotoURL
                titleActors = titleActors[:-3]
                metadata.title = titleActors + metadata.title

            # Genres
            movieGenres.clearGenres()
            genres = detailsPageElements.xpath('//a[@class="cat-tag"]')
            if len(genres) > 0:
                for genre in genres:
                    movieGenres.addGenre(genre.text_content())


            # Posters/Background
            valid_names = list()
            metadata.posters.validate_keys(valid_names)
            metadata.art.validate_keys(valid_names)
            posters = detailsPageElements.xpath('//a[contains(@class,"scene-image")]')
            background = "http:" + detailsPageElements.xpath('//video')[0].get("poster")
            metadata.art[background] = Proxy.Preview(HTTP.Request(background, headers={'Referer': 'http://www.google.com'}).content, sort_order = 1)

            posterNum = 1
            for posterCur in posters:
                posterURL = "http:" + posterCur.get("href")
                metadata.posters[posterURL] = Proxy.Preview(HTTP.Request(posterURL, headers={'Referer': 'http://www.google.com'}).content, sort_order = posterNum)
                posterNum = posterNum + 1


        ##############################################################
        ##                                                          ##
        ##   Vixen                                                  ##
        ##                                                          ##
        ##############################################################
        if siteID == 52:
            temp = str(metadata.id).split("|")[0].replace('_','/')

            url = getSearchBaseURL(siteID) + temp
            detailsPageElements = HTML.ElementFromURL(url)

            # Summary
            metadata.studio = "Vixen"
            paragraph = detailsPageElements.xpath('//span[@class="moreless js-readmore"]')[0].text_content()
            paragraph = paragraph.replace('&13;', '').strip(' \t\n\r"').replace('\n','').replace('  ','') + "\n\n"
            metadata.summary = paragraph
            metadata.title = detailsPageElements.xpath('//h1[@id="castme-title"]')[0].text_content()
            date = detailsPageElements.xpath('//span[@class="player-description-detail"]//span')[0].text_content()
            date_object = datetime.strptime(date, '%B %d, %Y')
            metadata.originally_available_at = date_object
            metadata.year = metadata.originally_available_at.year    
                
            
            # Genres
            movieGenres.clearGenres()
            # No Source for Genres, add manual

            movieGenres.addGenre("Hardcore")
            movieGenres.addGenre("Heterosexual")
            movieGenres.addGenre("Boy Girl")
            movieGenres.addGenre("Caucasian Men")
            movieGenres.addGenre("Glamcore")

            # Actors
            metadata.roles.clear()
            actors = detailsPageElements.xpath('//p[@id="castme-subtitle"]//a')
            if len(actors) > 0:
                for actorLink in actors:
                    role = metadata.roles.new()
                    actorName = actorLink.text_content()
                    role.name = actorName
                    actorPageURL = actorLink.get("href")
                    actorPage = HTML.ElementFromURL("https://www.vixen.com"+actorPageURL)
                    actorPhotoURL = actorPage.xpath('//img[@class="thumb-img"]')[0].get("src")
                    role.photo = actorPhotoURL

            # Posters/Background
            posters = detailsPageElements.xpath('//div[@class="swiper-slide"]')
            background = detailsPageElements.xpath('//img[contains(@class,"player-img")]')[0].get("src")
            metadata.art[background] = Proxy.Preview(HTTP.Request(background, headers={'Referer': 'http://www.google.com'}).content, sort_order = 1)
            posterNum = 1
            for posterCur in posters:
                posterURL = posterCur.xpath('.//img[@class="swiper-content-img"]')[0].get("src")
                metadata.posters[posterURL] = Proxy.Preview(HTTP.Request(posterURL, headers={'Referer': 'http://www.google.com'}).content, sort_order = posterNum)
                posterNum = posterNum + 1

        ##############################################################
        ##                                                          ##
        ##   Girlsway                                               ##
        ##                                                          ##
        ##############################################################
        if siteID == 53:

            temp = str(metadata.id).split("|")[0].replace('_','/')

            url = getSearchBaseURL(siteID) + temp
            detailsPageElements = HTML.ElementFromURL(url)

            # Summary
            metadata.summary = detailsPageElements.xpath('//div[contains(@class,"sceneDesc")]')[0].text_content()[60:]
            metadata.title = detailsPageElements.xpath('//h1[@class="title"]')[0].text_content()
            metadata.studio = "Girlsway"
            date = detailsPageElements.xpath('//div[@class="updatedDate"]')[0].text_content()[14:24]
            Log(date)
            date_object = datetime.strptime(date, '%Y-%m-%d')
            metadata.originally_available_at = date_object
            metadata.year = metadata.originally_available_at.year    
            
            # Genres
            movieGenres.clearGenres()
            genres = detailsPageElements.xpath('//div[contains(@class,"sceneColCategories")]//a')
            if len(genres) > 0:
                for genreLink in genres:
                    genreName = genreLink.text_content().lower()
                    movieGenres.addGenre(capitalize(genreName))

            # Actors
            metadata.roles.clear()
            actors = detailsPageElements.xpath('//div[contains(@class,"sceneColActors")]//a')
            if len(actors) > 0:
                for actorLink in actors:
                    role = metadata.roles.new()
                    actorName = actorLink.text_content()
                    role.name = actorName
                    actorPageURL = "https://www.girlsway.com" + actorLink.get("href")
                    actorPage = HTML.ElementFromURL(actorPageURL)
                    actorPhotoURL = actorPage.xpath('//img[@class="actorPicture"]')[0].get("src")
                    role.photo = actorPhotoURL
            
            # Posters/Background
            posterURL = detailsPageElements.xpath('//meta[@name="twitter:image"]')[0].get("content")
            Log("PosterURL: " + posterURL)
            metadata.art[posterURL] = Proxy.Preview(HTTP.Request(posterURL, headers={'Referer': 'http://www.google.com'}).content, sort_order = 1)
            metadata.posters[posterURL] = Proxy.Preview(HTTP.Request(posterURL, headers={'Referer': 'http://www.google.com'}).content, sort_order = 1)


        ##############################################################
        ##                                                          ##
        ##   X-Art                                                  ##
        ##                                                          ##
        ##############################################################
        if siteID == 82:
            Log('******UPDATE CALLED*******')
            temp = str(metadata.id).split("|")[0].replace('+','/')

            url = getSearchBaseURL(siteID) + temp
            detailsPageElements = HTML.ElementFromURL(url)

            # Summary
            metadata.studio = "X-Art"
            paragraphs = detailsPageElements.xpath('//p')
            pNum = 0
            summary = ""
            for paragraph in paragraphs:
                if pNum > 0 and pNum <= (len(paragraphs)-7):
                    summary = summary + paragraph.text_content()
                pNum += 1
            metadata.summary = summary
            metadata.title = detailsPageElements.xpath('//title')[0].text_content()[8:]
            date = detailsPageElements.xpath('//h2')[2].text_content()[:-1]
            date_object = datetime.strptime(date, '%b %d, %Y')
            metadata.originally_available_at = date_object
            metadata.year = metadata.originally_available_at.year    
                
            
            # Genres
            movieGenres.clearGenres()
            # No Source for Genres, add manual
            movieGenres.addGenre("Artistic")


            # Actors
            metadata.roles.clear()
            actors = detailsPageElements.xpath('//h2//a')
            if len(actors) > 0:
                for actorLink in actors:
                    role = metadata.roles.new()
                    actorName = actorLink.text_content()
                    role.name = actorName
                    actorPageURL = actorLink.get("href")
                    actorPage = HTML.ElementFromURL(actorPageURL)
                    actorPhotoURL = actorPage.xpath('//img[@class="info-img"]')[0].get("src")
                    role.photo = actorPhotoURL

            # Posters/Background
            valid_names = list()
            metadata.posters.validate_keys(valid_names)
            metadata.art.validate_keys(valid_names)
            posters = detailsPageElements.xpath('//div[@class="gallery-item"]')[0]
            poster = posters.xpath('.//img')[0].get('src')
            background = detailsPageElements.xpath('//img[contains(@alt,"'+metadata.title+'")]')[0].get("src")
            metadata.art[background] = Proxy.Preview(HTTP.Request(background).content, sort_order = 1)
            posterURL = poster[:-21] + "2.jpg"
            metadata.posters[posterURL] = Proxy.Preview(HTTP.Request(posterURL).content, sort_order = 1)

        ##############################################################
        ##                                                          ##
        ##   Bang Bros                                              ##
        ##                                                          ##
        ##############################################################
        if siteID >= 83 and siteID <= 135:
            Log('******UPDATE CALLED*******')
            temp = str(metadata.id).split("|")[0].replace('_','/')

            url = getSearchBaseURL(siteID) + temp
            detailsPageElements = HTML.ElementFromURL(url)

            # Summary
            metadata.studio = "Bang Bros"
            metadata.summary = detailsPageElements.xpath('//div[@class="vdoDesc"]')[0].text_content()
            metadata.title = detailsPageElements.xpath('//h1')[0].text_content()
            releaseID = detailsPageElements.xpath('//div[@class="vdoCast"]')[1].text_content()[9:]
            searchResults = HTML.ElementFromURL(getSearchSearchURL(siteID) + releaseID)
            searchResult = searchResults.xpath('//div[@class="echThumb"]')[0]
            releasedDate = searchResult.xpath('.//span[@class="faTxt"]')[1].text_content()
            date_object = datetime.strptime(releasedDate, '%b %d, %Y')
            metadata.originally_available_at = date_object
            metadata.year = metadata.originally_available_at.year 
            metadata.tagline = detailsPageElements.xpath('//a[contains(@href,"/websites")]')[1].text_content()
            metadata.collections.clear()
            metadata.collections.add(metadata.tagline)

            # Genres
            movieGenres.clearGenres()
            movieGenres.clearGenres()
            genres = detailsPageElements.xpath('//div[contains(@class,"vdoTags")]//a')

            if len(genres) > 0:
                for genreLink in genres:
                    genreName = genreLink.text_content().strip('\n').lower()
                    movieGenres.addGenre(genreName)

            # Actors
            metadata.roles.clear()
            actors = detailsPageElements.xpath('//div[@class="vdoCast"]//a[contains(@href,"/model")]')
            if len(actors) > 0:
                for actorLink in actors:
                    role = metadata.roles.new()
                    actorName = actorLink.text_content()
                    role.name = actorName
                    actorPageURL = actorLink.get("href")
                    actorPage = HTML.ElementFromURL(getSearchBaseURL(siteID) + actorPageURL)
                    actorPhotoURL = "http:" + actorPage.xpath('//div[@class="profilePic_in"]//img')[0].get("src")
                    role.photo = actorPhotoURL

            # Posters/Background
            valid_names = list()
            metadata.posters.validate_keys(valid_names)
            metadata.art.validate_keys(valid_names)

            background = "http:" + detailsPageElements.xpath('//img[contains(@id,"player-overlay-image")]')[0].get("src")
            try:
                metadata.art[background] = Proxy.Preview(HTTP.Request(background).content, sort_order = 1)
            except:
                pass
            
            posters = detailsPageElements.xpath('//div[@class="WdgtPic modal-overlay"]')
            posterNum = 1
            for poster in posters:
                posterURL = "http:" + poster.xpath('.//img')[0].get("src")
                posterURL = posterURL[:-5] + "big" + posterURL[-5:]
                metadata.posters[posterURL] = Proxy.Preview(HTTP.Request(posterURL).content, sort_order = posterNum)
                posterNum += 1

        ##############################################################
        ##                                                          ##
        ##   Tushy                                                  ##
        ##                                                          ##
        ##############################################################
        if siteID == 136:
            Log('******UPDATE CALLED*******')
            temp = str(metadata.id).split("|")[0].replace('_','/')

            url = getSearchBaseURL(siteID) + temp
            detailsPageElements = HTML.ElementFromURL(url)
           
            # Summary
            metadata.studio = "Tushy"
            paragraph = detailsPageElements.xpath('//span[@class="moreless js-readmore"]')[0].text_content()
            paragraph = paragraph.replace('&13;', '').strip(' \t\n\r"').replace('\n','').replace('  ','') + "\n\n"
            metadata.summary = paragraph
            metadata.title = detailsPageElements.xpath('//h1[@id="castme-title"]')[0].text_content()
            date = detailsPageElements.xpath('//span[@class="player-description-detail"]//span')[0].text_content()
            date_object = datetime.strptime(date, '%B %d, %Y')
            metadata.originally_available_at = date_object
            metadata.year = metadata.originally_available_at.year    
                
            
            # Genres
            movieGenres.clearGenres()
            # No Source for Genres, add manual
            movieGenres.addGenre("Anal")
            movieGenres.addGenre("Hardcore")
            movieGenres.addGenre("Heterosexual")


            # Actors
            metadata.roles.clear()
            actors = detailsPageElements.xpath('//p[@id="castme-subtitle"]//a')
            if len(actors) > 0:
                for actorLink in actors:
                    role = metadata.roles.new()
                    actorName = actorLink.text_content()
                    role.name = actorName
                    actorPageURL = actorLink.get("href")
                    actorPage = HTML.ElementFromURL(getSearchBaseURL(siteID)+actorPageURL)
                    actorPhotoURL = actorPage.xpath('//img[@class="thumb-img"]')[0].get("src")
                    role.photo = actorPhotoURL

            # Posters/Background
            valid_names = list()
            metadata.posters.validate_keys(valid_names)
            metadata.art.validate_keys(valid_names)
            posters = detailsPageElements.xpath('//div[@class="swiper-slide"]')
            background = detailsPageElements.xpath('//img[contains(@class,"player-img")]')[0].get("src")
            metadata.art[background] = Proxy.Preview(HTTP.Request(background, headers={'Referer': 'http://www.google.com'}).content, sort_order = 1)
            posterNum = 1
            for posterCur in posters:
                posterURL = posterCur.xpath('.//img[@class="swiper-content-img"]')[0].get("src")
                metadata.posters[posterURL] = Proxy.Preview(HTTP.Request(posterURL, headers={'Referer': 'http://www.google.com'}).content, sort_order = posterNum)
                posterNum = posterNum + 1


        ##############################################################
        ##                                                          ##
        ##   Reality Kings                                          ##
        ##                                                          ##
        ##############################################################
        if siteID >= 137 and siteID <= 182:
            Log('******UPDATE CALLED*******')
            temp = str(metadata.id).split("|")[0].replace('_','/')

            url = getSearchBaseURL(siteID) + temp
            detailsPageElements = HTML.ElementFromURL(url)

            # Summary
            metadata.studio = "Reality Kings"
            paragraph = detailsPageElements.xpath('//div[@id="trailer-desc-txt"]//p')[0].text_content()
            paragraph = paragraph.replace('&13;', '').strip(' \t\n\r"').replace('\n','').replace('  ','') + "\n\n"
            metadata.summary = paragraph
            metadata.title = detailsPageElements.xpath('//h1[@class="section_title"]')[0].text_content()
            metadata.tagline = detailsPageElements.xpath('//div[@id="trailer-desc-txt"]//h3//a')[0].text_content()
            metadata.collections.clear()
            metadata.collections.add(metadata.tagline)
            dateElements = HTML.ElementFromURL(getSearchSearchURL(siteID) + urllib.quote(metadata.title))
            date = dateElements.xpath('//span[@class="card-info__meta-date"]')[0].text_content()
            Log("Date:" + date)
            date_object = datetime.strptime(date, '%B %d, %Y')
            metadata.originally_available_at = date_object
            metadata.year = metadata.originally_available_at.year    
                
            
            # Genres
            movieGenres.clearGenres()
            # No Source for Genres, add manual
            t = metadata.tagline
            if t == "40 Inch Plus" or t == "Extreme Asses" or t == "Round and Brown":
                movieGenres.addGenre("Big Butt")
            if t == "First Time Auditions":
                movieGenres.addGenre("Audition")
            if t == "Dangerous Dongs" or t == "Teens Love Huge Cocks":
                movieGenres.addGenre("Big Dick")
            if t == "Big Naturals" or t == "Big Tits Boss":
                movieGenres.addGenre("Big Tits")
            if t == "Bikini Crashers":
                movieGenres.addGenre("Bikini")
            if t == "Street Blowjobs":
                movieGenres.addGenre("Blowjob")
            if t == "Captain Stabbin":
                movieGenres.addGenre("Boat")
            if t == "In The VIP":
                movieGenres.addGenre("Club")
            if t == "Round and Brown":
                movieGenres.addGenre("Ebony")
            if t == "Euro Sex Parties" or t == "Mikes Apartment":
                movieGenres.addGenre("Euro")
            if t == "Euro Sex Parties":
                movieGenres.addGenre("Group")
            if t == "Hot Bush":
                movieGenres.addGenre("Hairy Pussy")
            if t == "We Live Together" or t == "Moms Lick Teens":
                movieGenres.addGenre("Lesbian")
            if t == "8th Street Latinas" or t == "Saturday Night Latinas":
                movieGenres.addGenre("Latina")
            if t == "Happy Tugs":
                movieGenres.addGenre("Massage")
                movieGenres.addGenre("Handjob")
            if t == "Milf Hunter" or t == "Milf Next Door" or t == "Moms Lick Teens" or t == "Moms Bang Teens":
                movieGenres.addGenre("MILF")
            if t == "Real Orgasms":
                movieGenres.addGenre("Masturbation")
                movieGenres.addGenre("Solo")
            if t == "Wives in Pantyhouse":
                movieGenres.addGenre("Pantyhouse")
            if t == "Team Squirt":
                movieGenres.addGenre("Squirt")
            if t == "Pure 18" or t == "Teens Love Huge Cocks" or t == "Moms Bang Teens":
                movieGenres.addGenre("Teen")
            if t == "Tranny Surprise":
                movieGenres.addGenre("Tranny")
                movieGenres.addGenre("Shemale")
            movieGenres.addGenre("Hardcore")
            movieGenres.addGenre("Heterosexual")


            # Actors
            metadata.roles.clear()
            actors = detailsPageElements.xpath('//div[@id="trailer-desc-txt"]//h2')
            if len(actors) > 0:
                for actorLink in actors:
                    role = metadata.roles.new()
                    actorName = actorLink.xpath('.//a')[0].text_content()
                    role.name = actorName
                    actorPageURL = actorLink.xpath('.//a')[0].get("href")

                    actorPage = HTML.ElementFromURL(getSearchBaseURL(siteID)+actorPageURL)
                    
                    actorPhotoURL = actorPage.xpath('//div[contains(@class,"model-picture__thumb js-model-picture__thumb")]')[0]
                    actorPhotoURL = actorPhotoURL.xpath('.//img')[0].get("data-bind").split("'")[1]
                    Log("pic: " + actorPhotoURL)
                    role.photo = actorPhotoURL

            # Posters/Background
            valid_names = list()
            metadata.posters.validate_keys(valid_names)
            metadata.art.validate_keys(valid_names)
            posters = detailsPageElements.xpath('//a[@class="card-thumb__img"]')
            background = detailsPageElements.xpath('//video')[0].get("poster")
            metadata.art[background] = Proxy.Preview(HTTP.Request(background, headers={'Referer': 'http://www.google.com'}).content, sort_order = 1)
            posterNum = 1
            for posterCur in posters:
                posterURL = posterCur.get("href")
                metadata.posters[posterURL] = Proxy.Preview(HTTP.Request(posterURL, headers={'Referer': 'http://www.google.com'}).content, sort_order = posterNum)
                posterNum = posterNum + 1


        ##############################################################
        ##                                                          ##
        ##   21Naturals                                             ##
        ##                                                          ##
        ##############################################################
        if siteID == 183:
            Log('******UPDATE CALLED*******')
            temp = str(metadata.id).split("|")[0].replace('_','/')

            url = getSearchBaseURL(siteID) + temp
            detailsPageElements = HTML.ElementFromURL(url)

            # Summary
            metadata.studio = "21Naturals"
            metadata.summary = detailsPageElements.xpath('//div[contains(@class,"sceneDesc")]')[0].text_content()[70:]
            metadata.title = detailsPageElements.xpath('//h1')[0].text_content()
            releasedDate = detailsPageElements.xpath('//div[@class="updatedDate"]')[0].text_content()[14:24]
            date_object = datetime.strptime(releasedDate, '%Y-%m-%d')
            metadata.originally_available_at = date_object
            metadata.year = metadata.originally_available_at.year 
           

            # Genres
            movieGenres.clearGenres()
            genres = detailsPageElements.xpath('//div[contains(@class,"sceneColCategories")]//a')

            if len(genres) > 0:
                for genreLink in genres:
                    genreName = genreLink.text_content().strip('\n').lower()
                    movieGenres.addGenre(genreName)

            # Actors
            metadata.roles.clear()
            actors = detailsPageElements.xpath('//div[contains(@class,"sceneColActors")]//a')
            if len(actors) > 0:
                for actorLink in actors:
                    role = metadata.roles.new()
                    actorName = actorLink.text_content()
                    role.name = actorName
                    actorPageURL = actorLink.get("href")
                    actorPage = HTML.ElementFromURL(getSearchBaseURL(siteID) + actorPageURL)
                    actorPhotoURL = actorPage.xpath('//img[@class="actorPicture"]')[0].get("src")
                    role.photo = actorPhotoURL

            # Posters/Background
            valid_names = list()
            metadata.posters.validate_keys(valid_names)
            metadata.art.validate_keys(valid_names)

            background = detailsPageElements.xpath('//meta[contains(@name,"twitter:image")]')[0].get("content")
            metadata.art[background] = Proxy.Preview(HTTP.Request(background).content, sort_order = 1)
            metadata.posters[background] = Proxy.Preview(HTTP.Request(background).content, sort_order = 1)

        ##############################################################
        ##                                                          ##
        ##   PornFidelity                                           ##
        ##                                                          ##
        ##############################################################
        if siteID == 184:
            Log('******UPDATE CALLED*******')
            temp = str(metadata.id).split("|")[0].replace('_','/')

            url = "https://" + temp
            detailsPageElements = HTML.ElementFromURL(url)

            # Summary
            metadata.studio = "PornFidelity"
            metadata.summary = detailsPageElements.xpath('//p[contains(@class,"card-text")]')[0].text_content()
            metadata.title = detailsPageElements.xpath('//h4')[0].text_content()[36:]
            Log(metadata.title)
            metadataParts = detailsPageElements.xpath('//div[contains(@class,"episode-summary")]//h4')
            for metadataPart in metadataParts:
                if "Published" in metadataPart.text_content():
                    releasedDate = metadataPart.text_content()[39:49]
                    Log(releasedDate)
                    date_object = datetime.strptime(releasedDate, '%Y-%m-%d')
                    metadata.originally_available_at = date_object
                    metadata.year = metadata.originally_available_at.year 
            
           

            # Genres
            movieGenres.clearGenres()
            movieGenres.addGenre("Hardcore")
            movieGenres.addGenre("Heterosexual")

            # Actors
            metadata.roles.clear()
            actors = detailsPageElements.xpath('//div[contains(@class,"episode-summary")]//a[contains(@href,"/models/")]')
            if len(actors) > 0:
                for actorLink in actors:
                    role = metadata.roles.new()
                    actorName = actorLink.text_content()
                    role.name = actorName
                    actorPageURL = actorLink.get("href")
                    actorPage = HTML.ElementFromURL(actorPageURL)
                    actorPhotoURL = actorPage.xpath('//img[@class="img-fluid"]')[0].get("src")
                    role.photo = actorPhotoURL

            # Posters/Background
            valid_names = list()
            pageSource = str(HTTP.Request(url))
            posterStartPos = pageSource.index('poster: "')
            posterEndPos = pageSource.index('"',posterStartPos+10)
            background = pageSource[posterStartPos+9:posterEndPos]
            metadata.posters.validate_keys(valid_names)
            metadata.art.validate_keys(valid_names)
            try:
                metadata.art[background] = Proxy.Preview(HTTP.Request(background).content, sort_order = 1)
            except:
                pass
            try:
                metadata.posters[background] = Proxy.Preview(HTTP.Request(background).content, sort_order = 1)
            except:
                pass

        ##############################################################
        ##                                                          ##
        ##   TeenFidelity                                           ##
        ##                                                          ##
        ##############################################################
        if siteID == 185:
            Log('******UPDATE CALLED*******')
            temp = str(metadata.id).split("|")[0].replace('_','/')

            url = "https://" + temp
            detailsPageElements = HTML.ElementFromURL(url)

            # Summary
            metadata.studio = "TeenFidelity"
            metadata.summary = detailsPageElements.xpath('//p[contains(@class,"card-text")]')[0].text_content()
            metadata.title = detailsPageElements.xpath('//h4')[0].text_content()[36:]
            Log(metadata.title)
            metadataParts = detailsPageElements.xpath('//div[contains(@class,"episode-summary")]//h4')
            for metadataPart in metadataParts:
                if "Published" in metadataPart.text_content():
                    releasedDate = metadataPart.text_content()[39:49]
                    Log(releasedDate)
                    date_object = datetime.strptime(releasedDate, '%Y-%m-%d')
                    metadata.originally_available_at = date_object
                    metadata.year = metadata.originally_available_at.year 
            
           

            # Genres
            movieGenres.clearGenres()
            movieGenres.addGenre("Hardcore")
            movieGenres.addGenre("Heterosexual")

            # Actors
            metadata.roles.clear()
            actors = detailsPageElements.xpath('//div[contains(@class,"episode-summary")]//a[contains(@href,"/models/")]')
            if len(actors) > 0:
                for actorLink in actors:
                    role = metadata.roles.new()
                    actorName = actorLink.text_content()
                    role.name = actorName
                    actorPageURL = actorLink.get("href")
                    actorPage = HTML.ElementFromURL(actorPageURL)
                    actorPhotoURL = actorPage.xpath('//img[@class="img-fluid"]')[0].get("src")
                    role.photo = actorPhotoURL

            # Posters/Background
            valid_names = list()
            pageSource = str(HTTP.Request(url))
            posterStartPos = pageSource.index('poster: "')
            posterEndPos = pageSource.index('"',posterStartPos+10)
            background = pageSource[posterStartPos+9:posterEndPos]
            metadata.posters.validate_keys(valid_names)
            metadata.art.validate_keys(valid_names)
            try:
                metadata.art[background] = Proxy.Preview(HTTP.Request(background).content, sort_order = 1)
            except:
                pass
            try:
                metadata.posters[background] = Proxy.Preview(HTTP.Request(background).content, sort_order = 1)
            except:
                pass

        ##############################################################
        ##                                                          ##
        ##   Kelly Madison                                          ##
        ##                                                          ##
        ##############################################################
        if siteID == 186:
            Log('******UPDATE CALLED*******')
            temp = str(metadata.id).split("|")[0].replace('_','/')

            url = "https://" + temp
            detailsPageElements = HTML.ElementFromURL(url)

            # Summary
            metadata.studio = "Kelly Madison"
            metadata.summary = detailsPageElements.xpath('//p[contains(@class,"card-text")]')[0].text_content()
            metadata.title = detailsPageElements.xpath('//h4')[0].text_content()[36:]
            Log(metadata.title)
            metadataParts = detailsPageElements.xpath('//div[contains(@class,"episode-summary")]//h4')
            for metadataPart in metadataParts:
                if "Published" in metadataPart.text_content():
                    releasedDate = metadataPart.text_content()[39:49]
                    Log(releasedDate)
                    date_object = datetime.strptime(releasedDate, '%Y-%m-%d')
                    metadata.originally_available_at = date_object
                    metadata.year = metadata.originally_available_at.year 
            
           

            # Genres
            movieGenres.clearGenres()
            movieGenres.addGenre("Hardcore")
            movieGenres.addGenre("Heterosexual")

            # Actors
            metadata.roles.clear()
            actors = detailsPageElements.xpath('//div[contains(@class,"episode-summary")]//a[contains(@href,"/models/")]')
            if len(actors) > 0:
                for actorLink in actors:
                    role = metadata.roles.new()
                    actorName = actorLink.text_content()
                    role.name = actorName
                    actorPageURL = actorLink.get("href")
                    actorPage = HTML.ElementFromURL(actorPageURL)
                    actorPhotoURL = actorPage.xpath('//img[@class="img-fluid"]')[0].get("src")
                    role.photo = actorPhotoURL

            # Posters/Background
            valid_names = list()
            pageSource = str(HTTP.Request(url))
            posterStartPos = pageSource.index('poster: "')
            posterEndPos = pageSource.index('"',posterStartPos+10)
            background = pageSource[posterStartPos+9:posterEndPos]
            metadata.posters.validate_keys(valid_names)
            metadata.art.validate_keys(valid_names)
            try:
                metadata.art[background] = Proxy.Preview(HTTP.Request(background).content, sort_order = 1)
            except:
                pass
            try:
                metadata.posters[background] = Proxy.Preview(HTTP.Request(background).content, sort_order = 1)
            except:
                pass

        ##############################################################
        ##                                                          ##
        ##   TeamSkeet                                              ##
        ##                                                          ##
        ##############################################################
        if siteID >= 187 and siteID <= 215:
            Log('******UPDATE CALLED*******')
            temp = str(metadata.id).split("|")[0].replace('+','/')

            url = "https://" + temp
            detailsPageElements = HTML.ElementFromURL(url)

            # Summary
            metadata.studio = "TeamSkeet"
            metadata.summary = detailsPageElements.xpath('//div[@class="gray"]')[1].text_content()
            metadata.title = detailsPageElements.xpath('//title')[0].text_content().split(" | ")[1]
            releasedDate = detailsPageElements.xpath('//div[@style="width:430px;text-align:left;margin:8px;border-right:3px dotted #bbbbbb;position:relative;"]//div[@class="gray"]')[0].text_content()[12:].replace("th","").replace("st","").replace("nd","").replace("rd","")
            date_object = datetime.strptime(releasedDate, '%B %d, %Y')
            metadata.originally_available_at = date_object
            metadata.year = metadata.originally_available_at.year 
            metadata.tagline = detailsPageElements.xpath('//div[@style="white-space:nowrap;"]//a')[0].text_content()[0:-4]
            Log(metadata.tagline)
            metadata.collections.clear()
            metadata.collections.add(metadata.tagline)

            # Genres
            movieGenres.clearGenres()
            genres = detailsPageElements.xpath('//a[contains(@href,"?tags=")]')

            if len(genres) > 0:
                for genreLink in genres:
                    genreName = genreLink.text_content().strip('\n').lower()
                    movieGenres.addGenre(genreName)

            # Actors
            metadata.roles.clear()
            actors = detailsPageElements.xpath('//a[contains(@href,"/profile/")]')
            if len(actors) > 0:
                for actorLink in actors:
                    role = metadata.roles.new()
                    actorName = actorLink.text_content()
                    role.name = actorName
                    actorPageURL = actorLink.get("href")
                    actorPage = HTML.ElementFromURL(actorPageURL)
                    actorPhotoURL = actorPage.xpath('//img[@id="profile_image"]')[0].get("src")
                    role.photo = actorPhotoURL

            # Posters/Background
            valid_names = list()
            metadata.posters.validate_keys(valid_names)
            metadata.art.validate_keys(valid_names)

            background = detailsPageElements.xpath('//video')[0].get("poster")
            try:
                metadata.art[background] = Proxy.Preview(HTTP.Request(background).content, sort_order = 1)
            except:
                pass
            
            posters = detailsPageElements.xpath('//a[contains(@href,"/trailers/")]')
            posterNum = 1
            for poster in posters:
                posterURL = poster.get("href")
                metadata.posters[posterURL] = Proxy.Preview(HTTP.Request(posterURL).content, sort_order = posterNum)
                posterNum += 1























        ##############################################################
        ## Cleanup Genres and Add
        metadata.genres.clear()
        Log("Genres")
        movieGenres.processGenres(metadata)