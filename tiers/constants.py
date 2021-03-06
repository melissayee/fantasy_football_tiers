tier_url = 'https://s3-us-west-1.amazonaws.com/fftiers/out/text_{p}{s}.txt'

season = 2020

lineup_dict = {0: 'QB',
               1: 'TQB',
               2: 'RB',
               3: 'RB/WR',
               4: 'WR',
               5: 'WR/TE',
               6: 'TE',
               7: 'OP',  # Punter
               9: 'DE',
               16: 'D/ST',
               17: 'K',
               20: 'Bench',
               21: 'IR',
               23: 'FLEX',
               }

lineup_order = {'QB': 0,
                'TQB': 1,
                'RB': 2,
                'RB/WR': 3,
                'WR': 4,
                'WR/TE': 5,
                'TE': 6,
                'FLEX': 7,
                'D/ST': 8,
                'K': 9,
                'Bench': 20,
                'IR': 21,
                }

position_dict = {1: 'QB',
                 2: 'RB',
                 3: 'WR',
                 4: 'TE',
                 5: 'K',
                 16: 'D/ST',
                 }

team_ids = {1: 'Atlanta Falcons',
            2: 'Buffalo Bills',
            3: 'Chicago Bears',
            4: 'Cincinnati Bengals',
            5: 'Cleveland Browns',
            6: 'Dallas Cowboys',
            7: 'Denver Broncos',
            8: 'Detroit Lions',
            9: 'Green Bay Packers',
            10: 'Tennessee Titans',
            11: 'Indianapolis Colts',
            12: 'Kansas City Chiefs',
            13: 'Oakland Raiders',
            14: 'Los Angeles Rams',
            15: 'Miami Dolphins',
            16: 'Minnesota Vikings',
            17: 'New England Patriots',
            18: 'New Orleans Saints',
            19: 'New York Giants',
            20: 'New York Jets',
            21: 'Philadelphia Eagles',
            22: 'Arizona Cardinals',
            23: 'Pittsburgh Steelers',
            24: 'Los Angeles Chargers',
            25: 'San Francisco 49ers',
            26: 'Seattle Seahawks',
            27: 'Tampa Bay Buccaneers',
            28: 'Washington Football Team',
            29: 'Carolina Panthers',
            30: 'Jacksonville Jaguars',
            33: 'Baltimore Ravens',
            34: 'Houston Texans'
            }
