Class2Go 
========

Class2Go is Stanford's internal open-source platform for on-line
education. A team of eight built the first version over the summer
2012, and it is still under active development.  Class2Go launched
this Fall for six on-campus classes and two "massive open online 
courses" (MOOC's): [Computer Networking][net] and 
[Solar Cells, Fuel Cells, and Batteries][sol].
  [net]: http://networking.class.stanford.edu/
  [sol]: http://solar.class.stanford.edu/

Class2Go was built to be an open platform for learning and research.
Professors have access to the classes' data to learn how their
students learn. We will facilitate experiments.  For example, we
intend this to be the best plaform for running A/B/N tests to measure
the impact of different teaching methods on student outcomes, or
to build interesting features to try out new ways of presenting
material or grading exercises.  We believe an open source platform
is the best way to do this.

For community support of c2g users, we have a Google group at
https://groups.google.com/forum/#!forum/class2go-users.

If you are interested in reaching the team email us at 
<c2g-contact@class.stanford.edu>.


Philosophy 
----------

There are some principles that have guided our project:

* **Open**. The platform is open source to make it easier for users
    (faculty members) to give us feedback on what we are doing.
    We would love to have others use the platform.  We are working
    with others who are interested in using Class2Go for on-line
    education: universities, private schools, even NGO's.

* **Portable**. Valuable course content shouldn't be tied to any
    one platform. Documents are already portable; the videos are
    outside our system (on YouTube) and the assets themselves can
    be repurposed as faculty see fit.  

* **Interoperable**. We don't want to build or maintain more than we
    have to. See the section below for a list of all the shoulders
    we are standing on.


Key Features
------------

To bring this to life we've built a system. Here are some of its
important and distinguishing features.

* **Video and Problem Set Management**. Professors (and TA's) can
    upload assets to S3; videos are then uploaded to YouTube.

* **Exercises**. We support two kinds of exercises: formative, for
    learning and encouraging engagement; and summative, for assessment,
    like quizzes and tests.  Students can attempt each formative
    problems many times as they want without penalty, but may be
    penalized for multiple submissions in summative sets. In both
    types of problem sets, feedback is available immediately so
    students can learn along the way.

* **Content Management**. We have built a simple content management
    system where course information (videos, static pages, problem
    sets) can be created, reviewed, and then published. One important
    ability is an automatic live date, so a professor (or, most
    likely, their TA) doesn't have to click a button at midnight to
    publish a problem set.

* **Frame Extraction**. We have a simple tool for extracting frames
    from a video (using ```ffmpeg```) and differencing them to find 
    key frames.  The thumbnails of these frames are used as an index
    to the video for navigation. It's called the Kelvinator after
    its first author, Kelvin Do.

* **Reporting**. We have a set of ad-hoc and scheduled reports so
    teachers can get feedback and adjust.


Leveraging Others
-----------------

Thanks to all the projects we are relying on to make this work. Some
commercial, some open source. But a ton of good stuff.

* [YouTube] [yt] and [Popcorn.js] [pop] for video
* [Piazza] [pz] for forums
* [MySQL] [mys] is our database
* The massive [Python] [p] [Django] [dj] ecosystem: eg. South, Registration
* [Amazon AWS] [a] suite for hosting (EC2, S3, RDS, Route53, IAM)
* Chef from [Opscode] [oc] for configuration management
* [Github] [gh] for source code management and issues

  [yt]:   http://www.youtube.com/
  [pop]:  http://www.popcornjs.org/
  [pz]:   http://www.piazza.com/
  [mys]:  http://www.mysql.org/
  [p]:    http://www.python.org/
  [dj]:   http://www.djangoproject.com/
  [a]:    http://aws.amazon.com/
  [oc]:   http://www.opscode.org/
  [gh]:   http://www.github.com/


Contributing
------------

We welcome others contributing to Class2Go.  Begin by checking out
our source from here and using README_SETUP.md to get a development
environment set up.  There are also some docs available on the
Project Wiki here on GitHub.

Before sending unsolicited pull requests it is often best to discuss your
intentions with the core dev team. Send us mail: <c2g-contact@class.stanford.edu>.

If you want to get an idea of the kinds of things to do on the project,
check out our
<a href="https://github.com/Stanford-Online/class2go/issues?state=open">issue list right here on GitHub</a>.  
We keep it here for all to see.  Feel free to comment on bugs and make 
suggestions.  If you want to fix a bug, go ahead fork, fix, test, and send 
a pull request.


Using Class2Go Yourself
-----------------------

We intend for other colleges, universities, and even private
organizations to be able to stand up their own instance of Class2Go
to host their own courses.  Unfortunately, the tooling and instructions
for this aren't turnkey just yet.  We also need to do some development
to make it less Stanford-specific.  Maybe you can help with that?

If you're interested, your the first step, just like contributing,
is to stand up a development environment on your own laptop and try
it out.  We have people who got this demo-sized Class2Go up and running
pretty quickly on their local machine.

Send us mail at <c2g-contact@class.stanford.edu> and we can give
you an idea what would be involved.



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

