-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.
--
-- 07/31/15     File Created
--
-- Database for the Swiss-system tournament
--

--  Holds player information
CREATE TABLE player (
    id      serial PRIMARY KEY,
    name    VARCHAR(40)
);


-- Tournament Info.  Tournament name should be unique
CREATE TABLE tournament (
    id              serial PRIMARY KEY,
    name            VARCHAR(40),
    num_players     INTEGER,
    num_rounds      INTEGER,
    UNIQUE (name)
);


--  Details of each tournament round.  When a round is complete
--  the status changes from READY to COMPLETE
--  Note:  One Round has many Matches (tournament_match)
CREATE TABLE tournament_round (
    id              INTEGER,
    tournament_id   INTEGER REFERENCES tournament(id),
    status          VARCHAR(10),
    PRIMARY KEY(id, tournament_id)   
);

--  Conatains the players that are registered for the tournament and
--  their stats
CREATE TABLE player_tournament_register (
    player_id       INTEGER REFERENCES player(id),
    tournament_id   INTEGER REFERENCES tournament(id),
    player_matches  INTEGER DEFAULT 0,
    player_wins     INTEGER DEFAULT 0,
    player_losses   INTEGER DEFAULT 0,
    PRIMARY KEY(player_id, tournament_id)   
);


--  Stores the details for each match in the tournament
--  Note that each match should result in two records.  One where the first
--  player is stored in the player_id field and the other where the second
--  player is stored in the player_id field.  Makes it easier to locate
--  all matches for a particular player
CREATE TABLE tournament_match (
    player_id       INTEGER REFERENCES player(id),
    tournament_id   INTEGER,
    round_id        INTEGER,
    player_score    INTEGER DEFAULT 0,
    opponent_id     INTEGER REFERENCES player(id),
    opponent_score  INTEGER DEFAULT 0,
    PRIMARY KEY(player_id, tournament_id, round_id),
    FOREIGN KEY (tournament_id, round_id) REFERENCES tournament_round(tournament_id, id)
);


--  View to calculate the total wins of all the players that a
--  single player played against.  Used as a secondary ranking factor 
--  when two players have the same number of tournament points 
CREATE VIEW opponent_match_wins AS
    SELECT player_tournament_register.player_id, 
       player_tournament_register.tournament_id, 
           opponent_wins.sum AS sum 
     FROM  player_tournament_register, 
           (SELECT tournament_match.player_id,
	  	           tournament_match.tournament_id,
                   SUM(player_tournament_register.player_wins) AS sum
              FROM tournament_match, player_tournament_register
             WHERE tournament_match.opponent_id = player_tournament_register.player_id
               AND tournament_match.tournament_id = player_tournament_register.tournament_id
          GROUP BY tournament_match.player_id, tournament_match.tournament_id)
                AS opponent_wins    
     WHERE opponent_wins.tournament_id = player_tournament_register.tournament_id
       AND opponent_wins.player_id = player_tournament_register.player_id
       ORDER BY player_tournament_register.player_id, 
                opponent_wins.sum DESC;  



