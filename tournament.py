""" Methods to Implement a Swiss System Tournament """
# !/usr/bin/env python
#
#  07/31/15     Program created
#
#  Description: Methods to implement Swiss-system tournament.
#               In a Swiss system tournament, players are never eliminated.
#               Instead, players are paired in every single round (the number
#               of rounds being predetermined) and the winner is the player
#               who earns the most points at the end of the tournament.


import psycopg2
import math
import random
import sys
import time
from random import randint


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection.
       or exit the program if a connection cannot be established."""

    conn = None

    try:
        conn = psycopg2.connect("dbname=tournament")
    except psycopg2.DatabaseError, e:

        print ("System Error: " + str(e))
        print ("Terminating Program")

        sys.exit(1)

    return conn


def deletePlayers():
    """Remove all the player records from the database."""

    conn = connect()

    c = conn.cursor()

    c.execute("""DELETE FROM player;""")

    conn.commit()

    conn.close()


def countPlayers():
    """Count and return the number of players currently registered.

    Returns:
      totalPlayers: number of players registered in the system.
    """

    conn = connect()

    c = conn.cursor()

    c.execute("""SELECT count(*) FROM player;""")

    totalPlayers = c.fetchone()[0]

    conn.close()

    return totalPlayers


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """

    conn = connect()

    c = conn.cursor()

    c.execute("""INSERT INTO player (name) VALUES ( %s );""", (name,))

    conn.commit()

    conn.close()


def createTournament(name, num_players):
    """Create a tournament in the tournament database.

    This includes a record of the tournament and a record for each round
    of the tournament.

    The database assigns a unique serial id number for the tournament.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Restriction: Odd number of players is not allowed

    Args:
      name: name of the tournament(should be unique).
      num_players:  number of players in the tournament.

    Returns:
      tournament_id: ID of the newly created tournament
    """

    if num_players % 2 != 0:
        print ("System Error: Odd number of players not allowed")
        print ("Terminating Program")

        sys.exit(1)

    #  calculate the number of tournament rounds based on number of players
    rounds = int(math.ceil(math.log(num_players, 2)))

    conn = None

    #  If a tournament with the same name exists then do not create the
    #  tournament and about the program
    try:

        conn = connect()

        c = conn.cursor()

        c.execute("""INSERT INTO tournament (name, num_players, num_rounds)
                     VALUES ( %s , %s, %s ) RETURNING id;""",
                  (name, num_players, rounds,))

        tournament_id = c.fetchone()[0]

        for x in range(1, rounds + 1):
            c.execute("""INSERT INTO tournament_round
                      (id, tournament_id, status) VALUES ( %s, %s, %s );""",
                      (x, tournament_id, "READY",))

        conn.commit()

    except psycopg2.IntegrityError, e:
        if conn:
            conn.rollback()

        print ("System Error: Tournament with name - " +
               name + " - already exists")
        print ("Terminating Program")

        sys.exit(1)
    finally:
        if conn:
            conn.close()

    return tournament_id


def setupTournament(tournament_id):
    """  Assign players to a tournament based on the getPlayersForTournament
         function.

    Args:
      tournament_id: ID of the tournament
      num_players: number of players expected for this tournament
    """

    num_players = getNumberOfPlayers(tournament_id)

    playerList = getPlayersForTournament(num_players)

    conn = connect()

    c = conn.cursor()

    for player in playerList:
        c.execute("""INSERT INTO player_tournament_register
                     VALUES ( %s, %s );""",
                  (player[0], tournament_id,))

    conn.commit()

    conn.close()


def getNumberOfPlayers(tournament_id):
    """ Return the number of players for the tournament

        Args:
          tournament_id: ID of the tournament

        Returns:
          num_players: Number of players expected to register for the
                       tournment
    """

    conn = connect()

    c = conn.cursor()

    c.execute("""SELECT num_players FROM tournament
                 WHERE id = ( %s )""", (tournament_id,))

    num_players = c.fetchone()[0]

    conn.commit()

    conn.close()

    return num_players


def deleteTournaments():
    """Remove all the tournament records (and tournament related records)
       from the database."""

    conn = connect()

    c = conn.cursor()

    #  Delete ant tournament matches that have been played
    c.execute("""DELETE FROM tournament_match;""")

    #  Delete all the tournament round records created
    c.execute("""DELETE FROM tournament_round;""")

    #  Any players registered?  They are gone now
    c.execute("""DELETE FROM player_tournament_register;""")

    #  Finally delete the tournament
    c.execute("""DELETE FROM tournament;""")

    conn.commit()

    conn.close()


def deleteMatches(tournament_id):
    """ Delete all the matches played in a tournament to date.  Used
        if we wish to rerun the tournament.

    Args:
      tournament_id: ID of the tournment for whioch the matches sould be
                     deleted
    """

    conn = connect()

    c = conn.cursor()

    #  Delete matches
    c.execute("""DELETE FROM tournament_match WHERE tournament_id = ( %s );""",
              (tournament_id,))

    #  Reset the player scores in the register
    c.execute("""UPDATE player_tournament_register
                    SET player_matches = 0, player_wins = 0,
                        player_losses = 0
                  WHERE player_tournament_register.tournament_id = ( %s );""",
              (tournament_id,))

    #  Reset round status so we are ready to begin again
    c.execute("""UPDATE tournament_round
                    SET status = %s
                  WHERE tournament_round.tournament_id = ( %s );""",
              ("READY", tournament_id,))

    conn.commit()

    conn.close()


def getPlayersForTournament(num_players):
    """  Return a list of players for a tournament.  Currently returns the
         first player records in 'id' order.  Change this function if you
         would like to return players in another fashion (ie. randomly).

    Args:
      num_players: expected number of player IDs to return

    Returns:
      playerList: List of player IDs
    """
    conn = connect()

    c = conn.cursor()

    c.execute("""SELECT id FROM player LIMIT ( %s ) ;""", (num_players,))

    playerList = c.fetchall()

    conn.commit()

    conn.close()

    return playerList


def runTournament(tournament_id):
    """  Run the tournament.  For each round we will pair up players and
         run the matches.  Once complete the round will be completed.

    Args:
      tournament_id: ID of the tournament to run
    """

    num_rounds = getNumberOfRounds(tournament_id)

    #  Each round, pair up players and execute matches
    for currentRound in range(1, num_rounds + 1):

        pairings = swissPairings(tournament_id)

        for (id1, name1, id2, name2) in pairings:
            runMatch(tournament_id, id1, id2)

        completeRound(tournament_id)


def playerStandings(tournament_id):
    """Returns a list of the players and their win records, sorted by wins.

    In case of a tie, the player with the most opponent wins is returned
    first.

    The first entry in the list should be the player in first place, or a
    player tied for first place if there is currently a tie.

    Args:
      tournament_id: ID of the tournament to report

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """

    conn = connect()

    c = conn.cursor()

    # Order standings by wins and opponent match wins.  Uses the VIEW
    # opponent_match_wins to retrive the wins of each opponent
    c.execute("""SELECT player.id, player.name,
                        player_tournament_register.player_wins,
                        player_tournament_register.player_matches
                   FROM player, player_tournament_register
                        LEFT JOIN opponent_match_wins ON
                            player_tournament_register.tournament_id =
                                             opponent_match_wins.tournament_id
                         AND player_tournament_register.player_id =
                                             opponent_match_wins.player_id
                  WHERE player.id = player_tournament_register.player_id
                    AND player_tournament_register.tournament_id = ( %s )
               ORDER BY player_tournament_register.player_wins desc,
                        opponent_match_wins.sum desc;""",
              (tournament_id,))

    standings = c.fetchall()

    conn.commit()

    conn.close()

    return standings


def reportPlayerStandings(standings):
    """  Prints the player standings in a nice format to the screen

         Args:
           standings:  The player standings in format (ID, Name, Wins, Matches)
    """

    print "ID       Name    Matches   Wins"
    print "--  ---------    -------   ----"

    for player in standings:
        print ("{0:>0}  {1:>8}  {2:>6}   {3:>5}"
               .format(player[0], player[1], player[3], player[2],))


def runMatch(tournament_id, player1, player2):
    """ Run one match in the tournament.

    To simulate a match a random number between 1 and 10 is generated for
    each player.  The player with the highest score is declared the winner.

    No ties are allowed so if one occurs we will regenerate the the second
    player's score until it is different than the first player

    Args:
      tournament_id: ID of the tournment for which the match is run
      player1: ID of the first player
      player2: ID of the second player
    """

    round_id = getCurrentRound(tournament_id)

    player1_score = randint(1, 10)
    player2_score = randint(1, 10)

    #  No ties allowed.  Generate score for player 2 until it is
    #  different from player 1
    while player1_score == player2_score:
        player2_score = randint(1, 10)

    #  Report the match based on the winner.
    if player1_score > player2_score:
        reportMatch(tournament_id, round_id, player1, player1_score,
                    player2, player2_score)
    else:
        reportMatch(tournament_id, round_id, player2, player2_score,
                    player1, player1_score)


def reportMatch(tournament_id, round_id, winner, winner_score,
                loser, loser_score):
    """Records the outcome of a single match between two players.

    Args:
      tournament_id: ID of tournament that this match belongs to
      round_id: Round ID of the tournament
      winner:  The ID number of the player who won
      winner_score: Score of the winner
      loser:  the id number of the player who lost
      loser_score: Score of the loser
    """

    conn = connect()

    c = conn.cursor()

    #  Record match for the winner
    c.execute("""INSERT INTO tournament_match
                 VALUES ( %s, %s, %s, %s, %s, %s );""",
              (winner, tournament_id, round_id,
               winner_score, loser, loser_score,))

    #  Record the match for the loser
    c.execute("""INSERT INTO tournament_match
                 VALUES ( %s, %s, %s, %s, %s, %s );""",
              (loser, tournament_id, round_id,
               loser_score, winner, winner_score,))

    #  Update the win column for the winner
    c.execute("""UPDATE player_tournament_register
                    SET player_matches = player_matches + 1,
                        player_wins = player_wins + 1
                  WHERE player_id = ( %s )
                    AND tournament_id = ( %s );""",
              (winner, tournament_id,))

    #  Update the loss column for the loser
    c.execute("""UPDATE player_tournament_register
                    SET player_matches = player_matches + 1,
                        player_losses = player_losses + 1
                  WHERE player_id = ( %s )
                    AND tournament_id = ( %s );""",
              (loser, tournament_id,))

    conn.commit()

    conn.close()


def getCurrentRound(tournament_id):
    """  Return the current tournament round.

    Tells us the current tournament round that is being played.  Current
    round is identified by finding the first round in status READY.

    Args:
      tournament_id: ID of the tournament to inquire

    Return:
      round_id:  Current round ID
    """

    conn = connect()

    c = conn.cursor()

    c.execute("""SELECT tournament_round.id FROM tournament_round
                  WHERE status = ( %s )
                    AND tournament_round.tournament_id = ( %s )
               ORDER BY status, id
               LIMIT 1;""",
              ("READY", tournament_id,))

    round_id = c.fetchone()[0]

    conn.commit()

    conn.close()

    return round_id


def getNumberOfRounds(tournament_id):
    """  Return the number of rounds in the tournament.

    Args:
      tournament_id: ID of the tournament

    Returns:
      num_rounds: Number of total rounds expected for the tournament
    """

    conn = connect()

    c = conn.cursor()

    c.execute("""SELECT num_rounds FROM tournament
                  WHERE id = ( %s );""",
              (tournament_id,))

    num_rounds = c.fetchone()[0]

    conn.commit()

    conn.close()

    return num_rounds


def completeRound(tournament_id):
    """  Complete one round of the tournament.

    Once a round is complete the status is changed from READY to COMPLETE.

    Args:
      tournament_id:  ID of the tournament
    """

    round_id = getCurrentRound(tournament_id)

    conn = connect()

    c = conn.cursor()

    c.execute("""UPDATE tournament_round
                    SET status = %s
                  WHERE tournament_id = ( %s ) AND id = ( %s );""",
              ("COMPLETE", tournament_id, round_id,))

    conn.commit()

    conn.close()


def swissPairings(tournament_id):
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Args:
      tournament_id: ID of the tournament for which players we are pairing

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    round_id = getCurrentRound(tournament_id)

    conn = connect()

    c = conn.cursor()

    #  Round 1 pairing is random.  Subsequent rounds are paired based on
    #  win record.  Players with the same score are randomized before
    #  pairing.
    if round_id == 1:
        c.execute("""SELECT player.id, player.name
                       FROM player, player_tournament_register
                      WHERE player.id = player_tournament_register.player_id
                        AND player_tournament_register.tournament_id = ( %s )
                   ORDER BY random();""",
                  (tournament_id,))
    else:
        c.execute("""SELECT player.id, player.name
                       FROM player, player_tournament_register
                      WHERE player.id = player_tournament_register.player_id
                        AND player_tournament_register.tournament_id = ( %s )
                    ORDER BY player_tournament_register.player_wins desc,
                             random();""",
                  (tournament_id,))

    standings = c.fetchall()

    conn.commit()

    conn.close()

    pairings = []

    #  Report pairings back based in player ID order
    for i, k in zip(standings[0::2], standings[1::2]):
        if i[0] < k[0]:
            pairings.append(i + k)
        else:
            pairings.append(k + i)

    return pairings

"""  Sample tournament utilizing main tournament functions.  Just uncomment
     the code below and run.  """

"""
# Set these parameters to create the tournament
tournament_name = "Sample Tournament"
num_players = 16


deleteTournaments()
deletePlayers()

registerPlayer("Player1")
registerPlayer("Player2")
registerPlayer("Player3")
registerPlayer("Player4")
registerPlayer("Player5")
registerPlayer("Player6")
registerPlayer("Player7")
registerPlayer("Player8")
registerPlayer("Player9")
registerPlayer("Player10")
registerPlayer("Player11")
registerPlayer("Player12")
registerPlayer("Player13")
registerPlayer("Player14")
registerPlayer("Player15")
registerPlayer("Player16")

tournament_id = createTournament(tournament_name, num_players)

setupTournament(tournament_id)

standings = playerStandings(tournament_id)

print ("INITIAL PLAYER STANDINGS")
print ("")
reportPlayerStandings (standings)

print("")
print ("EXPECTED NUMBER OF ROUNDS: {0}"
       .format(getNumberOfRounds(tournament_id,)))
print "RUNNING TOURNAMENT: {0} .....".format(tournament_name,)
print("")
runTournament(tournament_id)

standings = playerStandings(tournament_id)

print ("FINAL PLAYER STANDINGS")
reportPlayerStandings (standings)
"""
