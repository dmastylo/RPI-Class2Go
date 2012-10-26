We distribute ffmpeg ourselves since we need a version linked with the libx264 codec.
Compiled on a linux 12.4 LTE machine, rough instructions like this:


git clone git://git.videolan.org/x264.git
cd x264
./configure --enable-static --prefix=/usr/local
make && make install


git clone git://git.videolan.org/ffmpeg.git 
cd ffmpeg
./configure --enable-libx264 --enable-gpl --prefix=/usr/local
make 


