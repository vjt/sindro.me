---
date: "2009-02-10T18:08:34Z"
title: "How to mirror a static copy of the opensource.org website"
tags: [bash, mirror, opensource]
---

I currently maintain the [italian mirror](http://opensource.antifork.org/) of
the [Open Source Initiative](http://opensource.org/) web site, and today I
realized that the script I wrote some months ago wasn't doing its job well..
because the CSS files weren't downloaded at all, causing a rather unpleasant
rendering of the site.

To mirror opensource org I'm currently using the plain'ol [GNU
Wget](http://www.gnu.org/software/wget/) -r --mirror and so on. While the
good'ol **wget** downloads each page prerequisite defined in the HTML source,
it doesn't support @import CSS rules, and doesn't download images referenced in
CSS with url() rules.

BTW, nothing that can't be resolved with some regex-fu: that's why I'm [sharing
the script](http://gist.github.com/61474) I'm currently using to mirror the
opensource.org web site, hoping it will generate either a new mirror or some
insights on how to do this job better :).

The script: [`update_opensource_mirror.sh`](http://gist.github.com/61474)

Enjoy! :)
