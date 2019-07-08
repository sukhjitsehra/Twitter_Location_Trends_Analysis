CREATE DATABASE IF NOT EXISTS LocationTrends;

CREATE TABLE IF NOT EXISTS Locations(
    woeid INT NOT NULL,
    name VARCHAR(255),
    
    PRIMARY KEY(woeid)
);

CREATE TABLE IF NOT EXISTS TwitterDigest(
    id INT AUTO_INCREMENT,
    created_at DATETIME,
    as_of DATETIME,
    woeid INT,
    
    PRIMARY KEY (id),
    FOREIGN KEY (woeid) REFERENCES Locations(woeid)
);

CREATE TABLE IF NOT EXISTS DigestJson(
    id INT AUTO_INCREMENT,
    date_time DATETIME,
    digest JSON,
    
    PRIMARY KEY(id)
);

CREATE TABLE IF NOT EXISTS Trends(
    id INT AUTO_INCREMENT,
    name VARCHAR(255),
    tweet_volume INT,
    promoted_content VARCHAR(255),
    url VARCHAR(255),
    
    PRIMARY KEY(id)
);

CREATE TABLE IF NOT EXISTS TimeTrendMapping(
    id INT AUTO_INCREMENT,
    digest_id INT NOT NULL,
    trend_id INT NOT NULL,
    
    PRIMARY KEY (id),
    FOREIGN KEY (digest_id) REFERENCES TwitterDigest(id),
    FOREIGN KEY (trend_id) REFERENCES Trends(id)
);

ALTER TABLE TwitterDigest AUTO_INCREMENT=1;
ALTER TABLE Trends AUTO_INCREMENT=1;
ALTER TABLE TimeTrendMapping AUTO_INCREMENT=1;
ALTER TABLE DigestJson AUTO_INCREMENT=1;