Class2Go 
========

Class2Go is Stanford's internal open-source platform for on-line courses. We
began building Class2Go in June 2012. A team of eight has worked on
it through the summer, and it is launching Fall 2012 for a handful
of internal classes and two public classes (MOOC's): [Computer
Networking] [net] and [Solar Cells, Fuel Cells, and Batteries] [sol]
  [net]: http://networking.class.stanford.edu/
  [sol]: http://solar.class.stanford.edu/

Class2Go is intended to be an open platform for learning and research.
Professors will have direct access to the data for their classes
to learn how their students learn. We will facilitate experiments.
This could be A/B/N testing of how different things affect student
learning, or even bespoke code to try out interesting new features.

If you are interested in discussing with us, the team can be reached 
at <class2go-contact@cs.stanford.edu>


Philosophy 
----------

There are som principles that have guided our project:

* *Open*. The platform is open source to make it easier for users
    (faculty members) to give us feedback on what we are doing.
    We would love to have others use the platform, or
    to collaborate with similar efforts in other places.

* *Portable*. We believe strongly that valuable course content
    shouldn't be tied to any one platform. Documents are already
    portable; the videos are outside our system (on YouTube) and
    the assets themselves can be repurposed as faculty see fit.
    And our exercises and problem sets, instead of being trapped
    in a proprietary database, are in the Khan Academy format, so
    they can be used elsewhere.

* *Interoperable*. We don't want to build or maintain more than we
    have to. See the section below for a list of all the shoulders
    we are standing on.


Key Features
------------

To bring this to life we've built a system. Here are some of its
important and distinguishing features.

* *Video and Problem Set Management*. Professors (and TA's) can
    upload assets to S3; videos are then uploaded to YouTube.

* *Exercises*. We support two kinds of exercises: formative (for
    learning) and summative (for assessment, like quizzes and tests).
    Students can attempt each problem as many times as they want
    without penalty in formative problem sets, but may be penalized
    for multiple submissions in summative sets. In both types of
    problem sets, feedback is available immediately so students can
    learn along the way.

* *Content Management*. We have built a simple content management
    system where course information (videos, static pages, problem
    sets) can be created, reviewed, and then published. One important
    ability is an automatic live date, so a professor (or, most
    likely, a TA) doesn't have to click a button at midnight to
    publish a problem set.

* *Frame Extraction*. We have a tool for extracting frames from
    a video (using ```ffmpeg```) differencing them to find key
    frames, and then using thumbnails of these frames as an index
    to the video. It's called the Kelvinator after its author,
    Kelvin Do.


Leveraging Others
-----------------

Thanks to all the projects we are relying on to make this work. Some
commercial, some open source. But a ton of good stuff.

* [YouTube] [yt] for video
* [Khan Academy] [ka] for their HTML-based exercise framework
* [Piazza] [pz] for forums
* [MySQL] [mys] is our database
* The massive [Python] [p] [Django] [dj] ecosystem: eg. South, Registration
* [Amazon AWS] [a] suite for hosting (EC2, S3, RDS, Route53, IAM)
* Chef from [Opscode] [oc] for configuration management
* [Github] [gh] for source code management and issues

  [yt]:   http://www.youtube.com/
  [ka]:   http://www.khanacademy.org/
  [pz]:   http://www.piazza.com/
  [mys]:  http://www.mysql.org/
  [p]:    http://www.python.org/
  [dj]:   http://www.djangoproject.com/
  [a]:    http://aws.amazon.com/
  [oc]:   http://www.opscode.org/
  [gh]:   http://www.github.com/


License
-------

Copyright 2012 Stanford University

Licensed under the Apache License, Version 2.0 (the "License"); 
you may not use this file except in compliance with the License. 
You may obtain a copy of the License at 

<http://www.apache.org/licenses/LICENSE-2.0>

Unless required by applicable law or agreed to in writing, software 
distributed under the License is distributed on an "AS IS" BASIS, 
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
See the License for the specific language governing permissions and 
limitations under the License.

