from wxtalk import helper
files = helper.getListOfFiles(".")
count = 0
filecount = 0
for file in files:
    try:
        list = helper.loadJSONfromFile(file)
        count += len(list)
        filecount += 1
    except:
        iFile = open(file)
        oFile = open("possible errors/" + file,'w')
        print "Error found in " + file
        for line in iFile:
            oFile.write(line)
        oFile.close()
        iFile.close()
            
    print str(count) + " total tweets " + str(filecount) + " file count. File name = " + file


#before change 1.27 mill a day after api change 275k a day    4.6/1 ratio    
#collect ~165million tweets over 93 days
#cleaned up to 25,575,000 geo tagged tweets


#pg_dump weather > /home/steven/Desktop/T/weatherdb.bak
pg_dumpall | gzip -c > /home/steven/Desktop/T/all.dbs.out.gz
pg_dump weather | gzip -c > /home/steven/Desktop/T/weather.dump.out.gz
