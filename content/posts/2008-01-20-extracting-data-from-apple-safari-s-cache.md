---
title: Extracting data from Apple Safari's cache
date: 2008-01-20
tags: [apple, cache, extract, recover, safari, sqlite]
categories: [development]
---

Five minutes ago, I overwritten the super-shining-new CSS stylesheet that
implements the current color scheme, because i wanted to restore the original
one and put it in a new theme for this site, so that people who enjoyed the old
theme could continue to use it. But, as the most kiddiest system administrator,
i uncompressed the original files from the backup archive OVER the current
ones..

Safari to the rescue! Every cached item by safari is stored into a SQlite3
database located in `~/Library/Caches/com.apple.Safari`, let’s inspect how it
is structured:


```
 13:54:42 vjt@voyager:~/Library/Caches/com.apple.Safari$ sqlite3 Cache.db 
SQLite version 3.5.1
Enter ".help" for instructions

sqlite> .tables
cfurl_cache_blob_data       cfurl_cache_schema_version
cfurl_cache_response      

sqlite> .schema cfurl_cache_response 
CREATE TABLE cfurl_cache_response(
  entry_ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
  version INTEGER,
  hash_value INTEGER,
  storage_policy INTEGER,
  request_key TEXT UNIQUE,
  time_stamp NOT NULL DEFAULT CURRENT_TIMESTAMP);

sqlite> .schema cfurl_cache_blob_data
CREATE TABLE cfurl_cache_blob_data(
  entry_ID INTEGER PRIMARY KEY,
  response_object BLOB,
  request_object BLOB,
  receiver_data BLOB,
  proto_props BLOB,
  user_info BLOB);

sqlite> select * from cfurl_cache_response limit 3;
1|0|1897220634|0|http://..../|2008-01-19 11:10:33
2|0|-662909776|0|http://..../|2008-01-19 11:10:33
```

Wow. Impressive. That’s why i love Apple products, because they are so well
structured that you can freely inspect them and use them and their resources
for every unplanned task you could have to complete.. even to fix your own
mistakes ;). And it’s also intriguing, because you have to scratch your own
itch and find the solution while exploring a beautifully constructed software
product.

To make a long story short, every cached URL is stored into the `request_key`
field of the `cfurl_cache_response` table, while in the `receiver_data` field
of the `cfurl_cache_blob_data` there is the actual cached data. Now we can look
for the overwritten bbs theme CSS stylesheet:

```
sqlite> select entry_ID, request_key from cfurl_cache_response
   ...> where request_key like '%bbs/style.css';
??1950??|http://sindro.me/sites/all/themes/bbs/style.css
```

Now, let’s search in the `blob_data` table the entry with ID 1950:

```
sqlite> select receiver_data from cfurl_cache_blob_data
   ...> where entry_ID = 1950;
/**
 * Themetastic, for Drupal 5.0
 * Stefan Nagtegaal, iStyledThis [dot] nl
 * Steven Wittens, acko [dot] net`
 *
 * If you use a customized color scheme, you must regenerate it after
 * modifying this file.
[......rest of the stylesheet removed.....]
```

YAY! Found it! A quick cut&paste.. and the lost theme is back! :D
