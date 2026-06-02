BEGIN TRANSACTION;
SAVEPOINT create_sports;

CREATE TABLE sports(
    sport_id INT PRIMARY KEY,-- MLB = 1
    sport_name VARCHAR(255) UNIQUE NOT NULL,-- e.g. Major League Baseball
    sport_code VARCHAR(4) UNIQUE NOT NULL,
    sort_order INT CHECK ( sort_order > 0 ),
    sport_link varchar(255) NOT NULL CHECK (sport_link ~ '^/api/v\d(?:\.\d+)?(?:/[a-zA-Z0-9]+)+$')
);

 COMMIT;