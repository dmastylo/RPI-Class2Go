gdata Patch: ytservice_file_len.patch
=====================================

We need to apply this patch to the youtube/service.py file in order
for video uploads to youtube to work. The patch modifies one line in
the function InsertVideoEntry which accesses the content length of
the uploaded file using the wrong attribute len, to use the correct
attribute size.	  

The updated gdata package with the patched file gdata-2.0.17-c2g.tar.gz
is what the recipe uses.

To apply the patch manually...
-------------------
Go to your python packages to your gdata/youtube directory. This is
where the service.py we are patching is located. The path will look
like /path/to/site-packages/gdata/youtube/

Once you are in this directory, run the following command, supplying
your patch's location:  
sudo patch < /path/to/ytservice_file_len.patch

You can reverse the patch by running the same command with the -R
option:  
sudo patch -R < /path/to/ytservice_file_len.patch

Your patch should now be applied to allow YouTube uploads to work.
