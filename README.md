# Twitter Location based Trends Analysis
## Problem Statement
Understand daily trending topics for Canada from twitter data 

## Tasks
- Ingest data from twitter’s public API: https://developer.twitter.com/en/docs/trends/locations-with-trending-topics/api-reference/get-trends-available
- Store raw data for historical purpose into MySQL
- Process data so we get a snapshot of list of trending topics on a given date for Canada.
- Pull data daily while retaining raw data file using Cron Jobs.
- Insert new data to the processed table.
- Store data in MySQL.
- Connect to the data via Power BI.

## Technologies and Packages
- Python 3 and Packages
    - pymysql
    - requests
    - base64
    - json
    - pytz
- MySQL Server
- MySQL OBDC connector
- Power BI for visualizations

## Introduction

The scripts for scrapping the twitter trends based on location are written in python, these use the twitter authentication key and tokens to register the application. This enables the user to fetch the information from the twitter using API calls to (https://developer.twitter.com/en/docs/trends/locations-with-trending-topics/api-reference/get-trends-available). The data is downloaded into the MySQL database and using the cron jobs used to update the exising trends for Canada. Power BI connects to MySQL for creating the required visulaizations. 

### Prerequisites

- Install Anaconda/ Python 3
- Install the mentioned packages
- Install MySQL from https://dev.mysql.com/downloads/installer/
- Install Power BI from https://powerbi.microsoft.com/en-us/desktop/

# Attributes of Twitter Trends API data
It returns the top 50 trending topics for a specific WOEID, if trending information is available for it.

- name - it is name of the trend
- URL - specified URL for trend
- promoted content
- query
- tweet_volume value returns the volume for each trend. This is the volume of tweets per trend for the last 24 hours.

# DB Design 

![DB Design](./snapshot/DbDesign.png)

# Store and search the trending data

## Enter correct configurations in the settings.json file.

### To extract data from twitter and store in db run:
 - python main.py store

### To search data from db run:
- python main.py search hourly 30 (This will give hourly trends for last 30 hours)

or

- python main.py search daily 7 (This will give daily trends for last 7 days)

or

- python main.py search date 2019-07-07 (This will give hourly trends for a given day in YYYY-MM-DD format)

# Setting up the cron jobs

## For Windows

We can use Task Scheduler to run the 'main.py store' on hourly basis. 

## For Unix/Mac

We can use crontab for scheduling the job to download the twitter trends hourly basis. Following steps must be taken for the same. 

- In your terminal enter 'crontab -e'
- it will open edit windows 
- type 'i' to go into insert mode 
- type ' 0 0 * * * cd /directory/location/folder /location/of/python /location/of/file.py' to run every hour to run at the beginning of the hour.
- press escape button and enter :wq to save and exit
- use crontab -l to see the running jobs
- use crontab -r to kill the jobs 

# For visualization 
- Install Power Bi Desktop
- Install Mysql ODBC connector
- Enter the credentails to connect to data through get command in Power BI. 
- Create the desired visualization.
- Snapshot of dashboard is saved in 'snapshot' directory.


