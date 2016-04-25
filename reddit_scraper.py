# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 12:24:41 2013

@author:    RahulGarg
@email:     vihu89@gmail.com
"""

import praw
from time import gmtime
import re
from bs4 import BeautifulSoup
import requests


def get_author_info(a):
    processed_users = {}

    if a:
        if a.id in processed_users:
            return processed_users[a.id]
        else:
            d = {}
            d['author_name'] = a.name
            d['author_over_18'] = a.over_18
            d['author_is_mod'] = a.is_mod
            d['author_is_gold'] = a.is_gold
            t = gmtime(a.created_utc)
            d['author_created_year_utc'] = t.tm_year
            d['author_created_mon_utc'] = t.tm_mon
            d['author_created_day_of_year_utc'] = t.tm_yday
            d['author_created_day_of_month_utc'] = t.tm_mday
            d['author_created_day_of_week_utc'] = t.tm_wday
            d['author_created_hour_utc'] = t.tm_hour
            d['author_created_min_utc'] = t.tm_min
            d['author_created_sec_utc'] = t.tm_sec
            processed_users[a.id] = d
            return d
    else:
        return {'author_name': '',
                'author_over_18': None,
                'author_is_mod': None,
                'author_is_gold': None,
                'author_created_year_utc': None,
                'author_created_mon_utc': None,
                'author_created_day_of_year_utc': None,
                'author_created_day_of_month_utc': None,
                'author_created_day_of_week_utc': None,
                'author_created_hour_utc': None,
                'author_created_min_utc': None,
                'author_created_sec_utc': None}


def process_post(post):
    d = {}
    postdict = vars(post)
    POST_KEYS = ['title', 'created_utc', 'score', 'subreddit', 'domain', 'is_self', 'over_18', 'selftext']

    for key in POST_KEYS:
        val = postdict[key]
        try:
            val = val.lower()
        except:
            pass
        d[key] = val

    d['has_thumbnail'] = (post.thumbnail != u'default') and (post.thumbnail != u'self')

    post.replace_more_comments(limit=None, threshold=0)
    comments = post.comments
    flat_comments = praw.helpers.flatten_tree(comments)
    d['n_comments'] = len(list(flat_comments))

    return d


def get_video_url(url):

    if 'stream' in url:
        resp = requests.get(url)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            video_link = 'https:' + str(soup.findAll('source', type='video/mp4')[0].get('src'))
    else:
        video_link = url

    return video_link


def generate_list_of_dicts(SUBREDDITS):
    r = praw.Reddit('Reddit Dataset builder')
    ids = []
    posts = []

    if len(SUBREDDITS) > 0:
        for subreddit in SUBREDDITS:
            print 'scraping subreddit:', subreddit
            sub = r.get_subreddit(subreddit)

            print 'scraping new posts...'
        #    posts =  [process_post(p) for p in sub.get_new(limit=10)]
        #    ids = [p['id'] for p in posts]
            for post in sub.get_new(limit=10):
                if post.id not in ids:
                    print post.title
                    posts.append(process_post(post))

    else:
        raise Exception('Enter a subreddit')

    print 'scraped ', len(posts), ' posts'

    for post in posts:
        link = str(post['selftext'])
        url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', link)[0]
        page_url = url.rstrip(')')
        video = get_video_url(page_url)
        post['video'] = video
        post['name'] = post['title']
        post['genre'] = 'Sports'

    return posts
