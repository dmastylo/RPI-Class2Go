Requirements
------------
PDFKit has a number of system-level dependencies to work correctly:
 - wkhtmltopdf
 - libicu
 - an xserver

On a Debian-family Linux such as Ubuntu, the easiest way to get these is to run 
  sudo apt-get install wkhtmltopdf xvfb libicu-dev libicu48

Running
-------
To run successfully, wkhtmltopdf needs a running X server. If you're already
running Linux on your desktop, congratulations. If not, you'll need to start
one. In a headless environment like AWS, the easiest way to get an X server
is with xvfb.

The following is not guaranteed to work, but has been tested to run ok on
Ubuntu 12.04 AWS images as of March 2013:

    Xvfb :0 -fp /usr/share/X11/fonts/misc -screen 0 1280x1024x24 
    export DISPLAY=:0.0
    ./manage.py issue_certificate_multi <course_handle> <no_certs_file> <certification_conditions_file>

The important idea is that the DISPLAY variable should point to the display
handle of a running X instance before you invoke manage.py.
