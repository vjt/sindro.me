---
title: "CouchDB 0.11 Invalid UTF-8 JSON: Solved"
date: 2010-04-03T19:00:00Z
tags: [couchdb, erlang, projects]
---

![CouchDB logo](/posts/2010-04-03-couchdb-invalid-utf8-json/couchdb.png)

If your CouchDB 0.11 gives you the "Invalid UTF-8 JSON" error on **every** POST
or PUT you issue to it, make sure that in your
`$prefix/usr/lib/couchdb/erlang/lib` there aren't leftovers from previous
installations.

On [our](http://exelab.eu/) dev server, I found there two directories
("couch-0.10" and "mochiweb-r97") from the old 0.10 setup that were causing
this issue.

This applies if you upgraded from source, as you've probably did, because there
aren't too many packages of CouchDB 0.11 as of April 2010 :-).

Huge thanks to [@couchdb](http://twitter.com/couchdb) for [hinting me in the
right direction](http://twitter.com/CouchDB/status/11495632471) after [reading
a report on the dev mailing
list](http://mail-archives.apache.org/mod_mbox/couchdb-dev/201002.mbox/%3c112036548.3241265012630999.JavaMail.jira@brutus.apache.org%3e)
but I didn't want to "remove and reinstall" because I like to understand what's
going on ;-).

<small>Footnote: could this be the end of Hiatus? I hope so ;-p</small>
