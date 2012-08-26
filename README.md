Class2Go 
-------------

Class2Go is the project codename for Stanford's internal platform
for on-line courses.  We began building Class2Go in June 2012.  A
team of eight has worked on it through the summer.  It will launch
in Fall 2012 to host a handful of internal and open Stanford classes.

(TODO: list of classes, links here)

Class2Go is intended to be an open platform for research.  Professors
will have direct access to the data for their classes to learn how
their students learn.  We will facilitate experiments.  This could
be A/B/N testing of how different things effect student learning, or 
even bespoke code to try out interesting new features.

If you are interested in discussing with us, the team can be reached 
at [class2go@cs.stanford.edu] [mail].

  [mail]: mailto:class2go@cs.stanford.edu

Philosophy and Key Features
-------------------------

Here is what is important to us.

* *Open*. The platform is open source to make it easier for users
    (faulty members) to give us feedback on what we are doing.
    Eventually we would love to have others use the platform, or
    to collaborate with similar efforts in other places.

* *Portable*. We believe strongly that valuable course content
    shouldn't be tied to any one platform. Documents are already
    portable; the videos are outside our system (on YouTube) and
    the assets themselves can be repurposed as faculty see fit.  And
    our exercises and problem sets, instead of being trapped in a
    proprietary database, are in the Khan Academy format, so they
    can be used elsewhere.

* *Interoperable*. We don't want to build or maintain more than we
    have to.  See the section below for a list of all the shoulders
    we are standing on.

To bring this to life then we've built a few key features:

* *Content Management*. We have built a simple content management
    system where course information (videos, static pages, problem
    sets) can be created, reviewed, and then published.  One important
    ability is an automatic live date, so a professor (or, most
    likely, a TA) doesn't have to click a button at midnight to
    publish a problem set.

* *Video and Problem Set Management*. Professors (and TA's) can
    upload assets to S3; videos are then uploaded to YouTube.

* *Frame Extraction*.  We have a tool for extracting frames from
    a video (using ```ffmpeg```) differencing them to find key
    frames, and then using thumbnails of these frames as an index to 
    the video.  We call it the Kelvinator because it was written by Kelvin.

* *Exercises*.  We support two kinds of exercises: formative (for
    learning) and summative (for assessment, like quizzes and tests).  Students
    can attempt each problem as many times as they want without penalty in
    formative problem sets, but may be penalized for multiple submissions
    in summative sets.  In both types of problem sets, feedback is
    immediately so students can learn along the way.


Leveraging Others
-------------------------

Thanks to all the projects we are relying on to make this work.  Some
commercial, some open source.  But a ton of good stuff.

* [YouTube] [yt] for videos
* [Khan Academy] [ka] for their HTML-based exercise framework
* [Piazza] [pz] for forums
* [MySQL] [mys] is our database
* The massive [Python] [p] [Django] [dj] ecosystem: eg. South, Registration
* [Amazon] [a] AWS suite for hosting (EC2, S3, Route53, IAM)
* Chef from [Opscode] [oc] for configuration management
* [Github] [gh] for source code management and issues

  [yt]:    http://www.youtube.com/
  [ka]:    http://www.khanacademy.org/
  [pz]:    http://www.piazza.com/
  [mys]:   http://www.mysql.org/
  [p]:     http://www.python.org/
  [dj]:    http://www.djangoproject.com/
  [a]:     http://aws.amazon.com/
  [oc]:    http://www.opscode.org/
  [gh]:    http://www.github.com/


License
-------------------------

TODO: license terms

