#!/usr/bin/env python
#
# Test cases for tournament.py
#
# 07/31/15  Program Created by Udacity
# 08/05/15  Updated to handle changes for multiple tournaments
#           Changes Include:
#               - Rename deleteMatches to deleteTournaments as deleteMatches
#                   will now delete all matches for 1 tournament only
#               - Extra calls added to createTournament and setupTournament
#                   for tests 5 - 8
#               - Additional tournament_id parameter added to playerStandings
#                   and swissPairings to point to expected tournament
#               - Additional paramaters added to reportMatch to apply results
#                   to correct tournament and record the actual score of each
#                   player as well as the winner and loser 
#

from tournament import *

def testDeleteTournaments():
    deleteTournaments()
    deletePlayers()
    print "1. Old matches can be deleted."


def testDelete():
    deleteTournaments()
    deletePlayers()
    print "2. Player records can be deleted."


def testCount():
    deleteTournaments()
    deletePlayers()
    c = countPlayers()
    if c == '0':
        raise TypeError(
            "countPlayers() should return numeric zero, not string '0'.")
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "3. After deleting, countPlayers() returns zero."


def testRegister():
    deleteTournaments()
    deletePlayers()
    registerPlayer("Chandra Nalaar")
    c = countPlayers()
    if c != 1:
        raise ValueError(
            "After one player registers, countPlayers() should be 1.")
    print "4. After registering a player, countPlayers() returns 1."


def testRegisterCountDelete():
    deleteTournaments()
    deletePlayers()
    registerPlayer("Markov Chaney")
    registerPlayer("Joe Malik")
    registerPlayer("Mao Tsu-hsi")
    registerPlayer("Atlanta Hope")
    c = countPlayers()
    if c != 4:
        raise ValueError(
            "After registering four players, countPlayers should be 4.")
    deletePlayers()
    c = countPlayers()
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "5. Players can be registered and deleted."


def testStandingsBeforeMatches():
    deleteTournaments()
    deletePlayers()
    registerPlayer("Melpomene Murray")
    registerPlayer("Randy Schwartz")
    tournament_id = createTournament("Test Tourney", 2)
    setupTournament(tournament_id)
    standings = playerStandings(tournament_id)
    if len(standings) < 2:
        raise ValueError("Players should appear in playerStandings even before "
                         "they have played any matches.")
    elif len(standings) > 2:
        raise ValueError("Only registered players should appear in standings.")
    if len(standings[0]) != 4:
        raise ValueError("Each playerStandings row should have four columns.")
    [(id1, name1, wins1, matches1), (id2, name2, wins2, matches2)] = standings
    if matches1 != 0 or matches2 != 0 or wins1 != 0 or wins2 != 0:
        raise ValueError(
            "Newly registered players should have no matches or wins.")
    if set([name1, name2]) != set(["Melpomene Murray", "Randy Schwartz"]):
        raise ValueError("Registered players' names should appear in standings, "
                         "even if they have no matches played.")
    print "6. Newly registered players appear in the standings with no matches."


def testReportMatches():
    deleteTournaments()
    deletePlayers()
    registerPlayer("Bruno Walton")
    registerPlayer("Boots O'Neal")
    registerPlayer("Cathy Burton")
    registerPlayer("Diane Grant")
    tournament_id = createTournament("Test Tourney2", 4)
    setupTournament(tournament_id)
    standings = playerStandings(tournament_id)
    
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(tournament_id, 1, id1, 10, id2, 9)
    reportMatch(tournament_id, 1, id3, 8, id4, 7)
    completeRound(tournament_id)
    standings = playerStandings(tournament_id)
    for (i, n, w, m) in standings:
        if m != 1:
            raise ValueError("Each player should have one match recorded.")
        if i in (id1, id3) and w != 1:
            raise ValueError("Each match winner should have one win recorded.")
        elif i in (id2, id4) and w != 0:
            raise ValueError("Each match loser should have zero wins recorded.")
    print "7. After a match, players have updated standings."


def testPairings():
    deleteTournaments()
    deletePlayers()
    registerPlayer("Twilight Sparkle")
    registerPlayer("Fluttershy")
    registerPlayer("Applejack")
    registerPlayer("Pinkie Pie")
    tournament_id = createTournament("Test Tourney3", 4)
    setupTournament(tournament_id)
    standings = playerStandings(tournament_id)
    
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(tournament_id, 1, id1, 10, id2, 9)
    reportMatch(tournament_id, 1, id3, 8, id4, 7)
    completeRound(tournament_id)

    pairings = swissPairings(tournament_id)
    if len(pairings) != 2:
        raise ValueError(
            "For four players, swissPairings should return two pairs.")
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4)] = pairings
    correct_pairs = set([frozenset([id1, id3]), frozenset([id2, id4])])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "After one match, players with one win should be paired.")
    print "8. After one match, players with one win are paired."


if __name__ == '__main__':
    testDeleteTournaments()
    testDelete()
    testCount()
    testRegister()
    testRegisterCountDelete()
    testStandingsBeforeMatches()
    testReportMatches()
    testPairings()
    print "Success!  All tests pass!"


