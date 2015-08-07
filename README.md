Swiss System Tournament Planner
===============================

Description
-----------
 	
	This project consists of a module containing functions to create and
    run a Swiss-System Tournament as well as a schema for a PostgreSQL database
    to store all player and tournament information.  Some tests are included to
    confirm everything is functioning well.
    
    The module contains functions to add or delete players, create or delete 
    tournaments, simulate the running of the tournament, track scores and
    display standings.  Please see file tournament.py for detailed descriptions
    of all functions.    
    
Requirements
------------	
	### Files
		-  tournament.py - Tournament Functions
		-  tournament_test.py - Tests of Tournament Functions
		-  tournament.sql - PostgreSQL Database Schema
	
	### Python version 2.7.6 installed
    ### PostgreSQL version 9.3.9 installed
	
Setup Instructions
------------------
	1. Execute psql, the PostgreSQL command line interface
    2. At the psql prompt execute the following commands to create the database and 
       load the schema:
               CREATE DATABASE tournament;
               \c tournament
               \i tournament.sql
    3. Back at main command prompt run tournament_test.py to confirm everything is 
       setup correctly:
               python tournament_test.py
    
    If all 8 tests pass then the module is ready for use.
        
Database Schema
---------------
    The database consists of 5 tables and 1 view.
    
    Tables
        player - Player Information
        tournament - Basic Tournament Information
        tournament_round - Contains entry for each tournament round
        player_tournament_register - Tracks the players that are in the tournament along
                                     with their tournament scores
        tournament_match - records the results of each match in the tournament 
               
	View
        opponent_match_wins - returns the number of wins for each opponent that each player
                              has faced.  In cases where players have the same number of wins
                              in the tournament, order will be decided by the total number of
                              wins of players that they have played against.                              
	