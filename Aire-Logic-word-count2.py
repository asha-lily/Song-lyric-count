import musicbrainzngs
from multiprocessing import Pool
from math import floor
import requests
import json
import numpy as np
import re
from statistics import stdev, StatisticsError
from matplotlib import pyplot as plt
import datetime

#Install libraries
#pip install musicbrainzngs requests numpy statistics matplotlib datetime

musicbrainzngs.set_useragent('Retrieve_Songs', '1.0')


def match_artist(user_input):
    '''Searches for artists by the name of user_input via MusicBrainz API

Once a matching artist name has been found, the artist name and id are returned
Returns False if no artist found '''

    artist_search = musicbrainzngs.search_artists(artist=user_input)

    if artist_search['artist-count'] >= 1:
        for artist in artist_search['artist-list']:
            if artist['name'] == user_input:
                return artist['name'], artist['id'], artist_search
        #else:
        print("Did you mean: {} ".format(
            artist_search['artist-list'][0]['name']))
        user_input3 = input('[Y/N] \n')

        if user_input3 == 'Y':
            artist_name = artist_search['artist-list'][0]['name']
            artist_id = artist_search['artist-list'][0]['id']
            return artist_name, artist_id, artist_search
        else:
            print('Please try again')
            return False


def find_artist():
    """ Asks user to input name of artist until matching artist is found via MusicBrainz API

    If user input contains no words, user is asked to try again
    Otherwise, repeats 'match_artist' function until a matching artist is found

    """

    artist_invalid = True
    #artist_name_found = False
    is_word_pattern = re.compile('\w+')

    while artist_invalid:

        user_input = input('Enter artist name \n')

        if not is_word_pattern.match(user_input):
            print("Artist name empty - please try again")
            artist_invalid = True

        else:
            artist = match_artist(user_input)
            if not artist:
                print("No artists by that name were found \nPlease try again")
                continue
            else:
                artist_name, artist_id, artist_search = artist
                print("Artist found")
                artist_invalid = False

    return artist_name, artist_id


def get_lyrics(artist_id):
    """ Browses all pages of artist's recordings by increasing the offset by the limit

    For each recording the song name is added to a list ('recordings')

 """

    print("Collecting lyrics ...")

    offset = 0
    limit = 100

    recordings_browse = musicbrainzngs.browse_recordings(
        artist=artist_id, limit=limit, offset=offset
    )  # Gets all recordings linked to artist - returns dict with keys ['recording-list', 'recording-count']
    num_recordings = recordings_browse['recording-count']  # 1746 for Beyonce
    recordings = [None] * num_recordings

    for page_num in range(num_recordings // 100):

        recordings_browse = musicbrainzngs.browse_recordings(
            artist=artist_id, limit=limit, offset=offset
        )  # Gets all recordings linked to artist - returns dict with keys ['recording-list', 'recording-count']

        for position in range(limit):
            song_name = recordings_browse['recording-list'][position]['title']
            index = (page_num * 100) + position
            recordings[index] = song_name
        offset += limit

    recordings_browse = musicbrainzngs.browse_recordings(
        artist=artist_id, limit=limit, offset=offset
    )  # Gets all recordings linked to artist - returns dict with keys ['recording-list', 'recording-count']

    max_index = num_recordings - ((num_recordings // 100) * 100)
    for position in range(max_index):
        song_name = recordings_browse['recording-list'][position]['title']
        index = ((num_recordings // 100) * 100) + position
        recordings[index] = song_name

    recordings = list(
        dict.fromkeys(recordings)
    )  # removes duplicates by converting 'recordings' list to a dictionary then back to a list
    return recordings


def word_count(args):
    """ Given an artist and song, this function retrieves the song's lyrics from the Apiary API

All instances of \n in the lyrics are replaced by a space, before splitting the lyrics each time a space occurs
After splitting the number of words in the lyrics are counted """

    song, artist_name = args
    header = {'Accept': 'application/json'}

    try:
        response = requests.get(
            'https://api.lyrics.ovh/v1/{}/{}'.format(artist_name, song),
            headers=header
        )  # make a get request to the artist/song entity of the Apiary API

    except requests.exceptions.RequestException as e:
        response = None

    if response == None:
        return (song, 0)

    elif response.status_code == 200:

        response = response.json(
        )  # converts text of json file to a dictionary
        lyrics = response[
            'lyrics']  # accesses the 'lyrics' key of the dictionary (the only key it contains)
        lyrics = lyrics.replace(
            '\n', ' ')  # replace all instances of '\n' with a space
        lyrics_split = lyrics.split(
            ' '
        )  # splits the lyrics string into a list of strings, splitting wherever a space occurs - the number of words can be found from the length of the resulting list

        if (
                len(lyrics_split) > 1
        ) and lyrics_split is not None:  # some 'songs' are empty and produce a count of 1 - this ensures that such songs are eliminated
            return (song, len(lyrics_split))

        else:
            return (song, 0)  # song empty

    else:
        return (song, 0)  # song not found


def get_albums(artist_id):
    """ Browses all releases of a given artist id, where release type is 'album'

    For each release, if not alreay in the dictionary then the title and date are added to one dictionary, whilst title and release id are added to another.
    For each release (album), its recordings (songs) are compared to those in words_dict2 (found previously by browsing the artist's recordings) -
    where songs match their word counnt is found from words_dict2 and thus the average number of words in each album is calculated.
    A bar chart of each album's year of release and the average number of words is plotted.

    """
    limit = 100
    offset = 0

    releases_browse = musicbrainzngs.browse_releases(
        release_type=['album'], artist=artist_id, limit=limit, offset=offset
    )  # Gets all recordings linked to artist - returns dict with keys ['recording-list', 'recording-count']

    num_releases = releases_browse['release-count']
    albums = [None] * num_releases

    for page_num in range(num_releases // 100):

        releases_browse = musicbrainzngs.browse_releases(
            release_type=['album'],
            artist=artist_id,
            limit=limit,
            offset=offset
        )  # Gets all recordings linked to artist - returns dict with keys ['recording-list', 'recording-count']

        for position in range(limit):  # 0 to 99
            album_info = releases_browse['release-list'][position]
            index = (page_num * 100) + position
            albums[index] = album_info
        offset += limit

    releases_browse = musicbrainzngs.browse_releases(
        release_type=['album'], artist=artist_id, limit=limit, offset=offset
    )  # Gets all recordings linked to artist - returns dict with keys ['recording-list', 'recording-count']

    max_index = num_releases - ((num_releases // 100) * 100)
    for position in range(max_index):  # 0 to 99
        album_info = releases_browse['release-list'][position]
        index = ((num_releases // 100) * 100) + position
        albums[index] = album_info

    #albums = list(dict.fromkeys(albums))

    album_id = {}
    album_dates = {}

    for album in albums:
        if album['title'] not in album_id.keys(
        ) and album['title'] not in album_dates.keys():
            try:
                album_date = datetime.datetime.strptime(
                    str(album['date'])[:4], '%Y').date()
                album_dates.update({album['title']: album_date.year})
                album_id.update({album['title']: album['id']})
            except KeyError:
                pass

    album_songs = {}

    for album_name, release_id in album_id.items():
        album_words = 0
        album_num_songs = 0
        recordings = musicbrainzngs.browse_recordings(
            release=release_id, limit=100, offset=0
        )  # Gets all recordings linked to artist - returns dict with keys ['recording-list', 'recording-count']
        for recording in recordings['recording-list']:
            title = recording['title']
            for key, value in words_dict2.items():
                if key == title:
                    album_num_songs += 1
                    album_words += value
        if album_num_songs != 0:
            album_av = album_words / album_num_songs
        else:
            album_av = 0
        album_songs.update({album_name: album_av})

    album_name, av_words = zip(
        *album_songs.items())  # unpack a list of pairs into two tuples
    album_name, album_date = zip(
        *album_dates.items())  # unpack a list of pairs into two tuples

    plt.bar([str(date) for date in album_date], height=av_words)
    plt.axhline(average,
                linewidth=1,
                color='m',
                linestyle='--',
                label="Average over all songs")
    plt.xlabel("Year", fontsize=12)
    plt.ylabel("Average number of words", fontsize=12)
    plt.title(
        "Graph of average number of words in album \n alongside year of release \n for {}"
        .format(artist_name))
    plt.xticks(rotation=90)
    plt.legend()
    plt.show()


def plot_histogram(words_dict2, std_dev):
    """ Plots histogram of frequency of occurrence of different song lengths (word count)

    Takes values (song word counts) from words_dict2
    The number of bins is calculated by a separate function on the number of songs"""

    plt.hist(words_dict2.values(),
             bins=number_of_bins(num_songs),
             color='skyblue',
             edgecolor='white')
    plt.xlabel("Number of words in song", fontsize=12)
    plt.ylabel("Frequency", fontsize=12)
    plt.axvline(average + std_dev,
                linewidth=1,
                color='m',
                linestyle='--',
                label="Mean + $\sigma$")
    plt.axvline(average - std_dev,
                linewidth=1,
                color='y',
                linestyle='--',
                label="Mean - $\sigma$")
    plt.axvline(average, linewidth=1, color='g', linestyle='--', label="Mean")
    plt.title(
        "Histogram showing frequency of occurrence \n of different song lengths (word count) \n in songs by {}"
        .format(artist_name))
    plt.xticks(rotation=90)
    plt.legend()
    plt.show()


def display_statistics(words_dict2, num_songs):
    """ Displays Artist Metrics and calls 'plot_histogram' function

    Statistics error raised if, for example, all songs have word count 0 """
    try:
        std_dev = stdev(words_dict2.values())
        print(
            "--------------------------------------------------------------------------------"
        )
        print("{}: Song Metrics \n".format(artist_name))
        print("Average word count: {}".format(round(average, 1)))
        print("Standard deviation: {} \n".format(round(std_dev, 1)))

        min_song = min(words_dict2.items(), key=lambda x: x[1])
        print("Song with fewest words is {}, with {} words".format(
            min_song[0], min_song[1]))
        max_song = max(words_dict2.items(), key=lambda x: x[1])
        print("Song with the most words is {}, with {} words".format(
            max_song[0], max_song[1]))
        print(
            "--------------------------------------------------------------------------------"
        )

        print("Plotting histogram...")
        print("(Close figure to continue)")

        plot_histogram(words_dict2, std_dev)

    except StatisticsError:
        print("Could not calculate statistics")


def number_of_bins(n):
    """ Calculates number of bins to plot in histogram as a function of the number of songs (n) """

    if n < 25 * 10:
        return 10
    else:
        return n // 25


if __name__ == '__main__':
    """ Gets list of artist's songs and applies word_count function to each using multiprocessing
    Stores results i.e song title:song word count in a dictionary from which the average over all songs is calculated
    User has the option of viewing statistics and choosing another artist, or exiting """

    looping = True
    while looping:

        artist_name, artist_id = find_artist()
        songs = get_lyrics(artist_id)
        args = [(song, artist_name) for song in songs]

        with Pool(25) as pool:
            words = pool.map(word_count, args)

        words_dict = {title: length for title, length in words}
        words_dict2 = {}

        for song, length in words_dict.items():
            if length != 0:
                words_dict2.update({song: length})

        num_songs = len(words_dict2)
        total = sum(words_dict2.values())
        if num_songs != 0:
            average = total / num_songs
            print("Average number of words in songs by {} is: {} ".format(
                artist_name, round(average, 1)))
        else:
            print("Average number of words in songs by {} is: {} ".format(
                artist_name, 0))

        user_input4 = input("Show statistics? [Y/N]\n").lower()
        if user_input4 == 'y':
            display_statistics(words_dict2, num_songs)
            if num_songs != 0:
                print("Collecting album data...")
                get_albums(artist_id)

        user_input5 = input("Try another artist? [Y/N]\n").lower()
        if user_input5 != 'y':
            looping = False
