select t.id, t.tweet_volume, td.id from trends as t, twitterdigest as td, timetrendmapping as ttm where t.id=ttm.trend_id  and td.id=ttm.id;

select id from trends;

select t.name, t.tweet_volume,  td.as_of from trends as t, timetrendmapping as ttm,  twitterdigest as td where t.id=ttm.trend_id and ttm.digest_id=td.id order by td.as_of  ;

#for volume date wise added 

select t.name, t.tweet_volume, td.as_of from trends as t, timetrendmapping as ttm,  twitterdigest as td where t.id=ttm.trend_id and ttm.digest_id=td.id;

#Date wise total volume
select  sum(t.tweet_volume),  td.as_of from trends as t, timetrendmapping as ttm,  twitterdigest as td where t.id=ttm.trend_id and ttm.digest_id=td.id group by td.as_of order by td.as_of  ;

# get the name and tweet volume for a given date 

select  t.tweet_volume,  t.name  from trends as t, timetrendmapping as ttm,  twitterdigest as td where t.id=ttm.trend_id and ttm.digest_id=td.id and td.as_of= '2019-07-07 18:30:57' ;


select distinct(t.name), t.tweet_volume, td.as_of from trends as t, timetrendmapping as ttm,  twitterdigest as td where t.id=ttm.trend_id and ttm.digest_id=td.id;

select sum(t.name), t.tweet_volume, td.as_of from trends as t, timetrendmapping as ttm,  twitterdigest as td where t.id=ttm.trend_id and ttm.digest_id=td.id group by t.name;

# Total average of trends tag wise.

select t.name, sum(t.tweet_volume) as vol from trends as t, timetrendmapping as ttm,  twitterdigest as td where t.id=ttm.trend_id and ttm.digest_id=td.id group by t.name order by vol;

#Total trends datewise
select count(t.name),td.as_of, sum(t.tweet_volume) as vol from trends as t, timetrendmapping as ttm,  twitterdigest as td where t.id=ttm.trend_id and ttm.digest_id=td.id group by td.as_of order by vol;







