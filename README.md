# MeatsByDre

Use 

`python3 test_new.py n` to run, where `n` is 0, 1, or 2 to select different tutorial texts.

Use left and right to turn, forward and backwards to walk. Press escape to quit.

# Requires

**pip3:**

`pip3 install numpy`

`pip3 install pygame`

`pip3 install gTTS`

**apt:**

`sudo apt install mpg123`

`sudo apt install libopenal-dev`

**other**

[PyAL](https://github.com/NicklasTegner/PyAL)

`git clone https://github.com/NicklasMCHD/PyAL.git`

`cd PyAl`

`python setup.py install`

`cp -R openal/loaders /usr/local/lib/python3.7/dist-packages/openal/loaders`

if those give you a permission denied error, run

`chown -R $USERNAME /usr/local/lib/python3.7/dist-packages`

and try again, rather than running them with `sudo`. If you aren't using python 3.7, change the number to your version of python.
