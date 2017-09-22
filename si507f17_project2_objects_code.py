# coding=utf-8
# SI 507 F17 Project 2 - Objects
import requests
import json
import unittest
import csv

print("\n*** *** PROJECT 2 *** ***\n")


#####

def params_unique_combination(baseurl, params_d, private_keys=["api_key"]):
    alphabetized_keys = sorted(params_d.keys())
    res = []
    for k in alphabetized_keys:
        if k not in private_keys:
            res.append("{}-{}".format(k, params_d[k]))
    return baseurl + "_".join(res)


def sample_get_cache_itunes_data(search_term, media_term="all"):
    CACHE_FNAME = 'cache_file_name.json'
    try:
        cache_file = open(CACHE_FNAME, 'r')
        cache_contents = cache_file.read()
        CACHE_DICTION = json.loads(cache_contents)
        cache_file.close()
    except:
        CACHE_DICTION = {}
    baseurl = "https://itunes.apple.com/search"
    params = {}
    params["media"] = media_term
    params["term"] = search_term
    unique_ident = params_unique_combination(baseurl, params)
    if unique_ident in CACHE_DICTION:
        return CACHE_DICTION[unique_ident]
    else:
        CACHE_DICTION[unique_ident] = json.loads(requests.get(baseurl, params=params).text)
    full_text = json.dumps(CACHE_DICTION)
    cache_file_ref = open(CACHE_FNAME, "w")
    cache_file_ref.write(full_text)
    cache_file_ref.close()
    return CACHE_DICTION[unique_ident]


# [PROBLEM 1] [250 POINTS]
print("\n***** PROBLEM 1 *****\n")


class Media(object):

    def __init__(self, media_dict):
        # ensure that user enters in a dictionary
        if not isinstance(media_dict, dict):
            return ValueError("input should be a dictionary representing \
                               a piece of media from itunes")

        self.itunes_id = media_dict["trackId"]
        self.author = media_dict["artistName"]

        # some media dicts do not have trackViewUrl
        try:
            self.itunes_URL = media_dict["trackViewUrl"]
        except:
            self.itunes_URL = media_dict["collectionViewUrl"]

        try:
            # if getting song or something in a trilogy
            self.title = media_dict["trackName"]
        except:
            # if getting book or movie
            self.title = media_dict["collectionName"]

    def __str__(self):
        # - a special string method, that returns a string of the form
        # 'TITLE by AUTHOR'
        return "%s by %s" % (self.title, self.author)

    def __repr__(self):
        # - a special representation method, which returns
        # "ITUNES MEDIA: <itunes id>" with the iTunes id number
        # for the piece of media (e.g. the track) only in place of <itunes id>
        return "ITUNES MEDIA: %s" % self.itunes_id

    def __len__(self):
        # - a special len method, which, for the Media class,
        # returns 0 no matter what.
        return 0

    def __contains__(self, title_input):
        return title_input in self.title

# [PROBLEM 2] [400 POINTS]
print("\n***** PROBLEM 2 *****\n")


class Song(Media):
    # Subclass of Media that assumes you get a dictionary for a song

    def __init__(self, song_dict):
        # use __init__ method from parent
        super(Song, self).__init__(song_dict)

        # get additional instance variables
        self.album = song_dict['collectionName']
        self.track_number = song_dict["trackNumber"]
        self.genre = song_dict["primaryGenreName"]

        # song length in milliseconds
        self.song_length_milli = song_dict["trackTimeMillis"]

    def __len__(self):
        # song length in seconds
        return int(self.song_length_milli / 1000)


class Movie(Media):
    # subclass of Media class. Assumes you get a dictionary for a movie

    def __init__(self, movie_dict):
        super(Movie, self).__init__(movie_dict)

        self.rating = movie_dict["contentAdvisoryRating"]
        self.genre = movie_dict["primaryGenreName"]
        try:
            self.description = movie_dict["longDescription"].encode('utf-8')
        except:
            self.description = None

        try:
            self.movie_length_milli = movie_dict["trackTimeMillis"]
        except:
            self.movie_length_milli = 0

    def __len__(self):
        # length in minutes
        return int(self.movie_length_milli * 1.66667e-5)

    def title_words_num(self):
        if self.description is None:
            return 0
        else:
            return len(self.description.split())

# [PROBLEM 3] [150 POINTS]
print("\n***** PROBLEM 3 *****\n")


media_samples = sample_get_cache_itunes_data("love")["results"]

song_samples = sample_get_cache_itunes_data("love", "music")["results"]

movie_samples = sample_get_cache_itunes_data("love", "movie")["results"]


media_list = [Media(sample) for sample in media_samples]
song_list = [Song(sample) for sample in song_samples]
movie_list = [Movie(sample) for sample in movie_samples]


# [PROBLEM 4] [200 POINTS]
print("\n***** PROBLEM 4 *****\n")

# Finally, write 3 CSV files:
# - movies.csv
# - songs.csv
# - media.csv

# Each of those CSV files should have 5 columns each:
# - title
# - artist
# - id
# - url (for the itunes url of that thing)
# - length


def write_to_csv(media_list, file_name):
    if '.csv' not in file_name.lower():
        file_name = file_name + '.csv'

    # output the header row
    header = ['title', 'artist', 'id', 'url', 'length']

    # output each of the rows:
    with open(file_name, 'w') as outfile:
        outwriter = csv.writer(outfile, delimiter=',')
        outwriter.writerow(header)

        for media in media_list:
            row = [media.title, media.author, str(media.itunes_id),
                   media.itunes_URL, str(len(media))]
            outwriter.writerow(row)

write_to_csv(movie_list, 'movies.csv')
write_to_csv(media_list, 'media.csv')
write_to_csv(song_list, 'songs.csv')
