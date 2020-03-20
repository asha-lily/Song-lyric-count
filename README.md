# Song-lyric-word-count

This program takes the user's input of artist name and returns the average number of words across all of their songs. There is the option to view extra statistics such as the longest and shortest words, a histogram showing the distribution of song lengths, and a bar plot of the average word count per album by year of release.

This program uses the MusicBrainz API to retrieve the artist's list of songs, an the Apiary API to retrieve lyrics for a specified artist and song.

## Getting Started

### Pre-requisites

This program requires Python 3.

### Installations
Install the relevant libraries as shown below

```
pip install musicbrainzngs requests numpy statistics matplotlib datetime
```

### Usage

Run:

```
python Song-lyric-word-count.py
```

Upon running the program the user is first asked to input the name of an artist of their choice. One of the following messages is returned, depending on the input received:

- "Artist name empty - please try again": no words were found in the input

- "No artists by that name were found \nPlease try again" 

- "Did you mean: {} " : if an exact match is not found but the user input returns results very similar to itself, the first result in the list is displayed. The user is asked to input [Y/N] depending on whether they’d like to select this artist or not.

- "Artist found" : this is displayed if an artist exactly matching the user input is found, or the user selects the artist shown in the previous case.

“Collecting lyrics...” is displayed whilst all of the artist’s recordings are browsed through and each song title added to a list. This can take a while for artists with many songs.

Next, the average number of songs by the artist is displayed, followed by the option to show statistics. A user input is required to select whether or not statistics are shown.

```
Average number of words in songs by ... is ...
Show statistics? [Y/N]
```
An example of these statistics is shown below. Note that statistics cannot be calculated if all of an artist's songs consist of 0 lyrics.

```
--------------------------------------------------------------------------------
Beyoncé: Song Metrics

Average word count: 516.6
Standard deviation: 207.0

Song with fewest words is Step on Over, with 44 words
Song with the most words is Get Me Bodied (instrumental), with 1240 words
--------------------------------------------------------------------------------
Plotting histogram...
(Close figure to continue)
```
This is followed by a histogram of average song lengths which is displayed in a new window. 
Upon closing this, album data is collected and a bar chart plotted; this shows the average number of words per album against the year of release.

```
Collecting album data...
```
The user then has the option to enter another artist, or to quit the program.

### Note

The Apiary API seems to often return different lyrics for the exact same request (i.e same artist and song name). This results in some inconsistency in the average number of words produced for a given artist, as well as the songs that are displayed as having the most/fewest words.



