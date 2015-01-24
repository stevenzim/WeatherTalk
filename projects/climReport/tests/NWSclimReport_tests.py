from nose.tools import *
from climReport import NWSclimReport
import os



def loadTestReport(fileName):
	testFilePath = "testData/"
	report = open(testFilePath + fileName, 'r')
	reportLines = []
	for line in report:
		reportLines.append(line.rstrip())	
	return reportLines


	
def test_no_report():
	assert_equal(NWSclimReport.getReport("see","SEA") , {"SEA" : "see is wrong WFO office code"})
	assert_equal(NWSclimReport.getReport("sew","SEE") , {"SEE" : "SEE is wrong WFO climate station code"})

def test_sky():
	assert_equal(NWSclimReport.getSkyCover(loadTestReport("testReport1.txt")) , {'AVERAGE SKY COVER' : 0.7})
	assert_equal(NWSclimReport.getSkyCover(loadTestReport("testReport2.txt")) , {'AVERAGE SKY COVER' : 'MISSING'})	
	
	


	
#	iFile = open(testFilePath + "test1-wrong-office.report" , 'r')
	

# def test_room():
    # gold = Room("GoldRoom",
                # """This room has gold in it you can grab. There's a
                # door to the north.""")
    # assert_equal(gold.name, "GoldRoom")
    # assert_equal(gold.paths, {})

# def test_room_paths():
    # center = Room("Center", "Test room in the center.")
    # north = Room("North", "Test room in the north.")
    # south = Room("South", "Test room in the south.")

    # center.add_paths({'north': north, 'south': south})
    # assert_equal(center.go('north'), north)
    # assert_equal(center.go('south'), south)

# def test_map():
    # start = Room("Start", "You can go west and down a hole.")
    # west = Room("Trees", "There are trees here, you can go east.")
    # down = Room("Dungeon", "It's dark down here, you can go up.")

    # start.add_paths({'west': west, 'down': down})
    # west.add_paths({'east': start})
    # down.add_paths({'up': start})

    # assert_equal(start.go('west'), west)
    # assert_equal(start.go('west').go('east'), start)
    # assert_equal(start.go('down').go('up'), start)