                         ___ __  __ __ __
                        /_  /_) /_  / (
                       /   / \ /_  / __)
                      _        __    __  __
                     (_)/\/   /_  / /_) /_
                             /   / / \ /_

             >>------------------------------------>>
              |   http://www.unrealvoodoo.org      |
             >>------------------------------------>>
              |                                    |
              | 1. Introduction                    |
              |                                    |
              | 2. Requirements                    |
              |                                    |
              | 3. Playing the game                |
              |                                    |
              | 4. Editing and Importing songs     |
              |                                    |
              | 5. Importing Guitar Hero(tm) songs |
              |                                    |
              | 6. Troubleshooting                 |
              |                                    |
             >>------------------------------------>>

 >>-------------------------------------------------------------------->>
  |  1. Introduction                                                   |
 >>-------------------------------------------------------------------->>

  Frets on Fire is a game of musical skill and fast fingers. The
  aim of the game is to play guitar with the keyboard as accurately
  as possible.

 >>-------------------------------------------------------------------->>
  |  2. Requirements                                                   |
 >>-------------------------------------------------------------------->>

  Windows:

    >> 128 MB of RAM
    >> a fairly fast OpenGL graphics card (shader support not necessary,
       antialiasing support recommended)
    >> Direct X compatible sound card

  Linux:

    >> 128 MB of RAM
    >> a fairly fast OpenGL graphics card (shader support not necessary,
       antialiasing support recommended)
    >> SDL compatible sound card

 Mac OS X:

    >> Mac OS X 10.5 or later
    >> OpenGL accelerated video card

 >>-------------------------------------------------------------------->>
  |  3. Playing the game                                               |
 >>-------------------------------------------------------------------->>

  First of all, these are the keys you'll need to navigate the menus:
  
   Arrow keys     -   Change menu selection
   Enter          -   Accept
   Escape         -   Cancel
     
  These keys are used in the game itself:
  
    F1-F5         -   Frets one through five
    Enter         -   Pick
    
  Note that these keys are default keys and they can be changed
  from the game settings menu.
  
  The easiest way to learn to play the game is to watch the tutorial.
  The basic idea is to press and hold the approriate frets when notes
  appear and tap the pick button when the notes hit the row of keys at
  the bottom of the screen. With longer notes, you need to hold the frets
  down for the whole duration.
  
  You get points for hitting notes. For each ten correctly played
  notes, your score multiplier increases up to four times. If you make
  a mistake, the score multiplier is reset back to one. For long notes,
  the longer you hold down the frets the more points you get. Chords award
  you twice the points of normal notes.

 >>-------------------------------------------------------------------->>
  |  4. Editing and Importing Songs                                    |
 >>-------------------------------------------------------------------->>
 
  With the included song editor you can import your own songs into the
  game. Ideally you should have two versions of your song: the guitar
  track and the background track. This is because the game needs to
  be able to mute the guitar when play it incorrectly. Both must be in
  the Ogg Vorbis format. A song can also be composed of just the main track,
  but in that case the whole music is muted when mistakes are made.
  
  These keys are used in the editor:
  
    Arrow keys    -   Move cursor.
    Escape        -   Bring up the editor menu.
    Enter         -   Add a note at the current cursor position.
                      Hold down Enter and press the right arrow key
                      to add longer notes.
    Space         -   Play and pause the song. Note that only the guitar
                      track is played in the editor.
    Delete        -   Remove notes at the current cursor position.
    PgUp/PgDown   -   Change difficulty level
    
  Follow these guidelines when composing different difficulty levels:
  
       Easy Difficulty: Frets 1-4 used, no chords.
      
     Medium Difficulty: Frets 1-4 and chords used.
  
    Amazing Difficulty: Anything goes.
    
  Remember that you shouldn't place notes on top of each other.

 >>-------------------------------------------------------------------->>
  |  5. Importing Guitar Hero(tm) songs                                |
 >>-------------------------------------------------------------------->>

  The game has a built-in importer for the songs in Guitar Hero(tm) by
  RedOctane. To use it, you'll need to have the game DVD, at least 500
  megabytes of free disk space and a lot of patience.

  You'll also need to have the OGG Vorbis command line compressor
  installed. In Linux, you can usually get it in a package called
  vorbis-tools. In Windows, copy the encoder (oggenc.exe) into the
  game directory.

  The importer can be started by choosing Song Editor in the main menu,
  followed by "Import Guitar Hero(tm) Songs". The importer will ask you
  the path to where the game files can be found. Usually this is just the
  driver letter of your DVD drive, e.g. 'D:'.
 
  After you have entered the correct path, the importer will start ripping
  the songs. Note that this will take a very long time. For example, on a
  1.8 GHz Pentium M laptop with 2 gigabytes of RAM the process took about
  4 hours. It is recommended that you run the game in windowed mode so that
  you can leave the importer running in the background and do other things
  while it's doing its magic.

  Once the importer is finished, you'll find the songs in the regular
  song selector. Note that if you abort the importer midway, it will
  mostly pick up where it left off when you run it again.

 >>-------------------------------------------------------------------->>
  |  6. Troubleshooting                                                |
 >>-------------------------------------------------------------------->>

  Q: Some chords don't work.
  A: Some keyboard manufactures reduce costs by making some key combinations
     impossible to press. This is especially true with laptop keyboards and
     some cheaper PC keyboards. The solution is to change the keys to different
     ones. For example, swapping the Enter key with Shift should help a lot,
     or changing the frets to i.e. numbers 1-5. Use the key tester in the
     settings menu to check your chosen key set.

  Q: The sound crackles.
  A: Increase your audio buffer size or change to 22050 Hz sampling frequency.
     You can do this from the Audio Settings.
     
  Q: The colors look ugly on my ATI video card.
  A: Don't use tweaked drivers (e.g. Omega Drivers) that reduce the color
     depth to 16 bits.
       
  Q: I can't hit those notes!
  A: You either need to practice more or adjust the A/V delay option in the
     audio settings. Try increasing or decreasing the delay by 50 and seeing
     if it helps.

  Q: I can't see my scores on the world charts.
  A: You need to enable score uploading in the settings menu first.

  Q: I get a strange OpenGL error on startup.
  A: If your desktop color quality is set to 16 bits, increase it to 32 bits.

  Q: No matter what I do, I get lousy scores.
  A: Sell your gear.

 >>-------------------------------------------------------------------->>
