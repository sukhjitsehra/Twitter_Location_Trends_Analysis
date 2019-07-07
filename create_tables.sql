CREATE TABLE IF NOT EXISTS Locations(
    woeid INT NOT NULL,
    name VARCHAR(255),
    
    PRIMARY KEY(woeid)
);

CREATE TABLE IF NOT EXISTS DailyDigest(
    id INT AUTO_INCREMENT,
    created_at VARCHAR(255),
    as_of VARCHAR(255),
    woeid INT,
    
    PRIMARY KEY (id),
    FOREIGN KEY (woeid) REFERENCES Locations(woeid)
);

CREATE TABLE IF NOT EXISTS Trends(
    id INT AUTO_INCREMENT,
    name VARCHAR(255),
    tweet_volume VARCHAR(255),
    promoted_content VARCHAR(255),
    url VARCHAR(255),
    
    PRIMARY KEY(id)
);

CREATE TABLE IF NOT EXISTS DailyTrends(
    id INT AUTO_INCREMENT,
    daily_digest_id INT NOT NULL,
    trend_id INT NOT NULL,
    
    PRIMARY KEY (id),
    FOREIGN KEY (daily_digest_id) REFERENCES DailyDigest(id),
    FOREIGN KEY (trend_id) REFERENCES Trends(id)
);

ALTER TABLE DailyDigest AUTO_INCREMENT=1;
ALTER TABLE Trends AUTO_INCREMENT=1;
ALTER TABLE DailyTrends AUTO_INCREMENT=1;