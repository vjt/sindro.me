---
date: 2009-04-26T23:00:00Z
title: "Facebook Developer Garage 2009, Milan (Italy)"
tags: [event, facebook, networking, social, web2.0]
categories: [development, all]
---

<div style="float:left; margin:8px 10px 4px 0;"><img src="/posts/2009-04-26-facebook-developers-garage-2009-milan-italy/logofb.jpg"/></div>

<p>This is my recap of the first <a
href="http://fb.mikamai.com/programma/">italian facebook developer garage</a>,
held in milan on <a
href="http://www.facebook.com/event.php?eid=70473476888">April 23, 2009</a>,
and hosted by <a href="http://mikamai.com/">mikamai</a>. the morning has been
dedicated to developer sessions, the afternoon to marketing &#38; communication
ones. some videos of the event are available <a
href="http://qik.com/istintoweb">here</a>.</p>


<h1>Morning: developer session</h1>


<p>The first talk was held by <a
href="http://www.facebook.com/people/James-Leszczenski/4800348">James
Leszczenski</a>, facebook engineer, who presented the <a
href="http://developers.facebook.com/connect.php">connect platform</a> vision,
mission, and values. interesting, besides the talk, for user participation: the
audience was deeply interested about <a
href="http://wiki.developers.facebook.com/index.php/Authenticating_Users_with_Facebook_Connect">which
information they get</a> from facebook, <a
href="http://wiki.developers.facebook.com/index.php/Facebook_Connect_Policies">how
should they handle it</a>, and which means connect does provide to <a
href="http://wiki.developers.facebook.com/index.php/Linking_Accounts_and_Finding_Friends">match
identities and find friends</a> on an enabled web site.</p>


<p><a name="continue"></a> Later I had the occasion to ask <a
href="http://www.facebook.com/people/James-Leszczenski/4800348">James</a> about
whether FB was inclined or not to adopt <a href="http://openid.net/">OpenID</a>
as an authentication method: he said that connect and OpenID both allow users
to have unique login credentials to access multiple sites, but connect also
allows to exploit the power of facebook social graph to allow users to
communicate and share information. so, the short answer is &#8220;no&#8221;.
Then I proposed him to implement OpenID on FB itself, so that connect could
become really a superset of openID, but he said that &#8220;as a company, these
are tough decisions I could not give an answer right now&#8221;. Fair enough
:).</p>


<blockquote> <strong><span class="caps">UPDATE</span></strong>: on April 27th
2009, techcrunch reports <em>they heard</em> that Facebook will <a
href="http://www.techcrunch.com/2009/04/27/facebook-first-big-site-to-really-embrace-openid/">embrace
OpenID</a> as a mean to authenticate users. Great news, looking forward for an
official statement from Facebook! :) </blockquote>

<p>The second talk was held by <a href="http://acinapura.com/">Vincenzo
Acinapura</a>, who described the basic means to create an application on the
facebook platform. He explored the technologies behind it (<a
href="http://wiki.developers.facebook.com/index.php/XFBML"><span
class="caps">XFBML</span></a>, <a
href="http://wiki.developers.facebook.com/index.php/FQL"><span
class="caps">FQL</span></a>, <a
href="http://wiki.developers.facebook.com/index.php/FBJS"><span
class="caps">FBJS</span></a>), the main <a
href="http://wiki.developers.facebook.com/index.php/Anatomy_of_a_Facebook_App">integration
points</a> whitin the platform (notifications, publisher, ...), and he showed
sample code to implement some of the most used <span class="caps">FBML</span>
tags (<code>fb:comments</code>, <code>fb:share</code>, <code>fb:feed</code>, <a
href="http://wiki.developers.facebook.com/wiki/FBML">and so on</a>). He
eventually remembered the importance of automating the deploy of applications,
and suggested to use <a href="http://www.capify.org/">capistrano</a> to achieve
it.</p>


<p>Then, the <a href="http://fb.mikamai.com/programma/">Facebook Sumo
Contest</a> was started: three developers had <del>one</del> two hours to cook
up a functional facebook application that would then be judged by
Facebook&#8217;s James and by the claps of the audience :). In the end only two
of them made it, the first one being an italian guy who wrote an app to give
gifts to friends; the second one a french (I think) guy who built an app to
organize parties with friends, invite people, and enjoy. The former won, but in
my opinion at least the latter did show a bit more creativity. Of course both
of them were victims of the <a
href="http://en.wikipedia.org/wiki/Murphy's_Law">murphy&#8217;s law</a>,
because the apps didn&#8217;t work on the first shot :).</p>


<p style="text-align:center;"><img src="/posts/2009-04-26-facebook-developers-garage-2009-milan-italy/pilu_and_reggie.jpg"/></p>


<p><a href="http://qik.com/video/1529172">Third talk</a> by <a
href="http://www.linkedin.com/pub/2/129/894">andrea reginato</a> and <a
href="http://gravityblast.com/">andrea franz</a>, who started up defining what
does <strong>viral</strong> mean, and how the social graph can allow anyone to
distribute content to a very large number of users. in a nutshell, as long as
your content is <a
href="http://modernl.com/article/how-to-write-great-headlines">well worded</a>
and interesting, word-of-mouth distribution via social networks on which
content publishing is &#8220;easy as pie&#8221; is a powerful way to make your
content spread across millions of potential interested people.</p>


<p>How to achieve it? They explored how FB connect can augment our sites and
give users ability to comment and interact with them using their facebook
credentials, and then spread the interactions via facebook in order to reach a
broader audience. it isn&#8217;t rocket science, but from my experience, it can
work, as long as the content is itself <strong>useful</strong> and
<strong>valuable</strong>, and most importantly it does not appear
<strong>fake</strong> and as <strong>advertisement</strong> to the majority of
the users.  I think that facebook and <a href="http://twitter.com/">twitter</a>
are also powerful tools to <a href="http://monitter.com/">analyze</a> and <a
href="http://hashtags.org/">identify</a> which kind of content is
<strong>interesting</strong> right now for people, and model the viral
distribution upon these insights.</p>


<p>There has been much interaction between the audience, interested mainly on
how to integrate it within their web site while maintaining their own
signup/login system, privacy concerns, policing and caching of information
(which one to cache, how, and for how long), and legal issues. When there is
complaint on data shown on my web but posted and hosted on facebook servers,
who is the legal representative to question about? A spokesman from <a
href="http://civile.it/">civile.it</a> stated that the responsible is to be
tracked by the owner of the servers on which data is hosted: it&#8217;s
facebook itself.</p>


<p>The two Andreas eventually showcased a demo game for the fb platform built
with <a href="http://sinatrarb.com/">sinatra</a>, <a
href="http://prototypejs.org/">prototype</a> and <a
href="http://wiki.developers.facebook.com/wiki/FBJS"><span
class="caps">FBJS</span></a>. The app asks you to identify one of your friends
by looking at a subset of profile pictures: every one you guess (in 10 seconds
at most), another picture appears, and difficulty increases. The number of
friends you identified determines the &#8220;level&#8221;, that you can post on
your profile once you&#8217;re done :).</p>


<p>After their talk, we did a lunch break and finally I joined with a friend of
mine, who arrived late as usual ;).</p>


<p style="text-align:center;"><img src="/posts/2009-04-26-facebook-developers-garage-2009-milan-italy/relax_at_facebook_developer_garage_2009_in_milan.jpg"/></p>

<h1>Afternoon: marketing and communication</h1>

<p>The afternoon was dedicated to marketing and communication, and to all the
ways you can exploit the facebook platform to bring traffic to your site, or to
generate viral information via the social connections between people, and
featured some case histories by the authors of <a
href="http://www.facebook.com/apps/application.php?id=8827826004">who has the
biggest brain</a> application, &#8220;Ninja Marketing:http://ninjamarketing.it
and the makers of <a href="http://www.cayenne.it/">skoda in love</a>
application (cayenne marketing).</p>


<p>First of all, Lorenzo Viscanti (mikamai co-founder) described how facebook
pages can help marketers to advertise content and analyze user traffic in order
to improve conversions: because facebook permits users to insert much
information about themselves, this data can be aggregated and effectively shown
in the statistics part of a facebook page. For a more detailed explanation,
check out the <a
href="http://www.facebook.com/advertising/FacebookPagesProductGuide.pdf">Facebook
pages product guide</a> published back in march 2009.</p>


<p>Then, fun time, because of the projection of a video by the ironic
neomelodic singer Manuele D&#8217;Amore, with his song <a
href="http://www.catepol.net/2009/03/28/facebook-neomelodico-lasciarsi-su-facebook/">lasciarsi
su facebook</a> (breaking up on facebook). Who doesn&#8217;t know neomelodic
neapolitan songs, they are a product of the popular naples culture of which <a
href="http://en.wikipedia.org/wiki/Gigi_D'Alessio">Gigi D&#8217;Alessio</a> is
one of the most known performers.</p>

**EDIT 2023-08: sorry, this video is gone**

<p>Then, politics time. <a
href="http://www.facebook.com/pages/Ivan-Scalfarotto/21997441531">Ivan
Scalfarotto</a> (running for 2009 european elections) and <a
href="http://www.civati.it/cv.htm">Giuseppe Civati</a> were on stage, and
talked about politics and social networking, a much buzzed topic these days,
mainly because of <a
href="http://en.wikipedia.org/wiki/Barack_Obama#2008_presidential_campaign">obama&#8217;s
successfull usage  of it</a> that resulted him taking office at the white house
on january 20, 2009. I think that the core of it was his message, not being
&#8220;vote for myself&#8221;, rather being &#8220;go vote, you dumbxxx!&#8221;
:), a perfect example of giving voice to a psico-social tension via the
internet. People spread out via facebook, twitter, and other social networks
their action of being gone to vote, and as <a
href="http://en.wikipedia.org/wiki/Robert_Cialdini">psychologists</a> have
explained many times, &#8220;People will do things that they see other people
are doing&#8221;.</p>


<p>The downside of this talk was that was too much politics oriented, and
wheter we should talk about politics and the internet, some <a
href="http://twitter.com/fedepo/statuses/1594019457">felt that the guy was
pushing it too hard</a>. Hey, that&#8217;s what good about social media: give
voice to everyone, and when someone is abusing the stage, shout it loud!
:).</p>


<p>After politics, deep marketing time: the most interesting (in my opinion)
talk of the whole day was the one held by the folks at <a
href="http://ninjamarketing.it/">ninja marketing</a>, who identified the
&#8220;chemistry of viral marketing&#8221; being the &#8220;viral <span
class="caps">DNA</span>&#8221; and appropriate &#8220;seeding&#8221; thru
social media. The <span class="caps">DNA</span> is about emotions: joy, anger,
sadness, fear, and (of course) surprise, but the most important of them all is
<a href="http://en.wikipedia.org/wiki/Catharsis">catharsis</a>. Citing
Wikipedia:</p>


<blockquote> [..] the term &#8220;catharsis&#8221; refers [..] to the
sensation, or literary effect, that would ideally overcome an audience upon
finishing watching a tragedy (a release of pent-up emotion or energy).
</blockquote>

<p>These emotions suddenly identify a psycho-social tension, over which you
should be smart enough to build means to give it voice through social media,
like the <a href="http://www.whoppersacrifice.com/">whopper sacrifice</a>
marketers did. The tension here was the shared willingness to remove
&#8220;friends&#8221; from our social graph, but the inability to do it in
order to avoid possible remarks from them. But when you had a reason to do it
to gain a free whopper, here&#8217;s that people started to drop others from
their friend lists, even if they were not interested in the whopper at all. The
Obama experiment also (IMHO) is a vivid example of a psycho-social tension (as
I stated before), that was successfully exploited and gave its results.</p>


<p style="text-align:center;"><a href="http://www.ninjamarketing.it/"><img
src="http://www.ninjamarketing.it/wp-content/themes/ninja_4/images/ninja-logo.gif"
alt="" /></a></p>


<p>The penultimate talk, held by Daniela Cangiano, described a case history by
the marketers that realized the <a
href="http://www.skoda-auto.it/skoda_in_love_octavia.asp">skoda in love</a> for
skoda cars (now unavailable on facebook). In a nutshell, the app asked the user
five questions and found out of them the best match for a date by choosing from
your friends. The app, by design, chose the results <strong>randomly</strong>
and <strong>always</strong> gave a percent match greater than 80%. When
displaying the match, the advertisement was also shown, inviting the user to
buy a skoda car and go out with the matching friend for a date.</p>


<p>The key points of the app were the seasonality (launched some days before
valentine day), the wording, very simplicistic and ironic, communication,
interactivity, yada, yada yada. The host then pointed out that facebook is an
&#8220;amplifier of social interactions&#8221; (because of the missing physical
contact and the written communication, I&#8217;d add) and that is a powerful
vehicle to convey information to customers. Daniela then stated that businesses
should neither underestimate facebook value, being it the &#8220;resonance of
the pulsating heart of the &#8216;net&#8221;, nor considering it simply a dumb
vehicle, because it is &#8220;by people, for people&#8221;. I think that her
claims were valid at a first glance, but quite exaggerated because the key here
is &#8220;the internet&#8221;, not &#8220;facebook&#8221;. The internet opened
up our minds by giving us endless points of view shared by millions of people
that daily blog, tweet, and also update their status on facebook. But
it&#8217;s the <strong>internet</strong>, dude.</p>


<p>Also, Daniela&#8217;s claims weren&#8217;t reflected in the application they
built, as an audience member noted: &#8220;if you say that facebook is by
people and for people, why did you made an app that gave them a false result?
Which kind of enjoyment did it make to them, apart from finding a false
match?&#8221;. She answered that the app wasn&#8217;t meant to actually find
matches, but just to &#8220;give some minutes of &#8220;fun&#8221; to the user,
and then convey the advertising message&#8221;. To me, it looks awful
marketing, abusing an already abused seasonality (valentine day), and
it&#8217;s just an example on how things should <span class="caps">NOT</span>
be done.</p>


<p>But, did it work? The audience asked &#8220;how many conversions (in terms
of cars sold) did you have from the app?&#8221; She replied: &#8220;well, this
is only a part of a broader marketing campaign, and I cannot give out results
here. if you&#8217;re interested, mail me at daniela <span
class="caps">DOT</span> cangiano AT cayenne <span class="caps">DOT</span>
it&#8221;. If you mail her, let everyone know by posting a comment, thanks
:).</p>


<p>The last talk was held by the lead developer of <a
href="http://hellotxt.com/">helloTxt</a>, an app that allows you to update your
status on multiple networks by using a single form. He described how, once the
core frameworks and interfaces of your web site are up and running, it&#8217;s
just a matter of weeks to code up a facebook app and start spreading it: they
took only 1 developer, 1 designer, 1 copywriter and 1 marketer to have it
running.</p>


<h1>Conclusions</h1>


<p>To me, the event was really interesting and I thank both the <a
href="http://mikamai.com/">hosts</a> and everyone who held talks on stage, my
brain was really satiated at the end :). As you&#8217;ve read from this post
(hey, thanks for making it to the end! :) the topics were spanned on really
many fields (technology, sociology, politics, marketing), and it&#8217;s
amazing that the internet (and social media) can blur all of them into a single
platform, and give humans new ways of study and implement them.</p>


<p>I hope only that james AT facebook <span class="caps">DOT</span> com will
take the advice I gave him before leaving: &#8220;<strong><span class="caps">BE
OPEN</span></strong>!&#8221; because we need open technologies, open standards,
and open knowledge, so that no private company can control them, for
humanity&#8217;s sake.</p>


<p>I&#8217;d love to hear your opinion, thoughts, and critics. Share them in
the comments!</p>


<p>~ <a href="mailto:vjt@openssl.it">vjt@openssl.it</a></p>
