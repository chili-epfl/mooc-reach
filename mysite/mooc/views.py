from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from mooc.forms import SearchForm
from django.core.urlresolvers import reverse
from .models import Search

#IMPORTS TWITTER
import twitter
import json
from collections import Counter
import string
from geopy import geocoders
from geopy.geocoders import Nominatim

import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
from scipy.misc import imread
#IMPORTS GITHUB
import requests
from getpass import getpass
import json
from github import Github
from math import ceil
from calendar import timegm
import rfc822
import time
import datetime
from email.Utils import formatdate
#IMPORTS STACK OVERFLOW
import string
import stackexchange
from math import ceil

BASE_DIRECTORY = ¨PATH¨

def index(request):
    if request.method== 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            keyword = form.cleaned_data['keyword']
            derivative = form.cleaned_data['derivative']
            return redirect('mooc.views.results', keyword, derivative)
    else:
        form = SearchForm()
    return render(request, 'mooc/index.html', locals())

def date_creation(self):
    return timegm(rfc822.parsedate(self))


def from_json_to_rfc_datetime(date):
    date_new_format= datetime.datetime.strptime(str(date), '%Y-%m-%dT%H:%M:%SZ')
    rfc_date= formatdate(time.mktime(date_new_format.timetuple()))
    return rfc_date

def from_date_to_seconds(self):
    rfc_date= formatdate(time.mktime(self.timetuple()))
    return timegm(rfc822.parsedate(rfc_date))

def binary_search(A, x, l, r): #We assume A is sorted
    mid= l+int(ceil((r-l)/2))
    if (l<=r):
        if x<A[mid]:
            return binary_search(A,x, l, mid-1)
        elif x>A[mid]:
            return binary_search(A,x,mid+1, r)
        elif x== A[mid]:
            return mid
    else: #if we don't find, we take the value right before in the array
        temp= r
        r=l
        l=temp
        return r


def results(request, keyword, derivative):

#TWITTER

    #Authentication
    CONSUMER_KEY = ' '
    CONSUMER_SECRET = ' '
    ACCESS_TOKEN_KEY = ' '
    ACCESS_TOKEN_SECRET = ' '
    api = twitter.Api(consumer_key = CONSUMER_KEY,
                  consumer_secret = CONSUMER_SECRET,
                  access_token_key = ACCESS_TOKEN_KEY,
                  access_token_secret = ACCESS_TOKEN_SECRET)
                  
    COUNT = 1000

    statuses = api.GetSearch(keyword, count= COUNT) #Can't get more than 100 actually
    if derivative is True:
        if keyword[len(keyword)-1] != 's':
            statuses += api.GetSearch(keyword+'s', count= COUNT)
        else:
            statuses+= api.GetSearch(keyword[:-1], count= COUNT)

    positive_statuses = api.GetSearch(keyword+ " :)", count = COUNT)
    negative_statuses = api.GetSearch(keyword+ " :(", count = COUNT)
 
                                      
    #Getting the TZ
    time_zones = [s.user.time_zone for s in statuses]
    tweets_per_tz=[] # tableau bi-dimensionnel: Country <-> nbr of tweets
    countries=[]
    number_tweets=[]
    for item in [time_zones]:
        c= Counter(item)
        tweets_per_tz.append(c.most_common()[:len(statuses)])
                                      

    for country in tweets_per_tz:
        for i in range(0, len(tweets_per_tz[0])):
            countries.append(country[i][0])
            number_tweets.append(country[i][1])
                                    
									  
                                      
    donnees= [['Time zone', 'Number of tweets']]
    for i in range(0, len(countries)):
        donnees.append([str(countries[i]), number_tweets[i]])
                                      
                                      
    ######
    # Ratio positive/negative tweets
    nb_pos_tw= len(positive_statuses)
    nb_neg_tw= len(negative_statuses)
    total_nb_tw= nb_pos_tw+nb_neg_tw
                                      
    positive_tw_percentage= nb_pos_tw*100/total_nb_tw
    negative_tw_percentage= nb_neg_tw*100/total_nb_tw

    ratio_tweets= [['Attitude', 'Number of tweets'],[':)',nb_pos_tw], [':(', nb_neg_tw]]
    
    ###### MAP
    #Map
    
    GEO_APP_KEY= ' '
    g= geocoders.Bing(GEO_APP_KEY)

    geolocator = Nominatim()
    locations=[]
    coordinates= []

    for country in countries:
        if country is not None and country.find("(") != -1:
            i = country.find("(")+1
            j = country.find(")")
            country = str(country[i:j])
        location = geolocator.geocode(country,timeout=10)
        locations.append(location)


    locations_count=[]
    locations_without_rep=[]
    for location in [locations]:
        c= Counter(item)
        locations_count.append(c.most_common()[:len(locations)])

    for i in range(0,len(locations_count[0])):
        locations_without_rep.append(locations_count[0][i][0])


    tweets_count=[0]*len(locations_without_rep)
    for i in range(0,len(countries)):
        for j in range(0,len(locations_without_rep)):
            if countries[i]==locations_without_rep[j]:
                tweets_count[i]= tweets_count[i]+number_tweets[i]

    if locations_without_rep[0] is None:
        del locations_without_rep[0]
        del tweets_count[0]

    for i in range(0, len(locations_without_rep)):
        location = geolocator.geocode(locations_without_rep[i], timeout=10)
        if location is None:
            coordinates.append([0,0])
        else:
            coordinates.append([location.latitude, location.longitude])



    ######
    #WordCloud
    
    en_statuses = api.GetSearch(keyword, count= COUNT, lang= 'en') #Can't get more than 100 actually
    if derivative:
        if keyword[len(keyword)-1] != 's':
            statuses += api.GetSearch(keyword+'s', count= COUNT, lang= 'en')
        else:
            statuses+= api.GetSearch(keyword[:-1], count= COUNT, lang= 'en')

    words = ' '.join(s.text for s in en_statuses)


    # remove URLs, RTs, and twitter handles
    no_urls_no_tags = " ".join([word for word in words.split()
                            if 'http' not in word
                            and not word.startswith('@')
                            and word != 'RT'
                            ])
    

    twitter_mask = imread(BASE_DIRECTORY+'twitter_mask.png', flatten=True)

    wordcloud = WordCloud(
                      font_path='/Users/Library/Fonts/Arial.ttf',
                      stopwords=STOPWORDS,
                      background_color='white',
                      width=1800,
                      height=1400,
                      mask=twitter_mask
                      ).generate(no_urls_no_tags)

    plt.ioff()
    plt.imshow(wordcloud)
    plt.axis("off")
    figure= plt.savefig("YOUR PATH TO DIRECTORY"+'/mooc-reach/mysite/mooc/static/mooc/my_twitter_wordcloud_2.png', dpi=300)
    plt.cla()
    plt.clf()

    #plt.show()
    
    #####

#GITHUB
    #Authentication

    username = ' ' # GitHub username
    password = ' ' # GitHub password

    # Credentials will be transmitted over a secure SSL connection
    url = 'https://api.github.com/authorizations'
    note = 'Data Mining Github'
    post_data = {'scopes':['repo'],'note': note }

    response = requests.post(
                             url,
                             auth = (username, password),
                             data = json.dumps(post_data),
                             )
    #Collecting Data
    ACCESS_TOKEN = ' '

    PER_PAGE=100;
    LIMIT_REP= 1000;
    getrepos =requests.request('GET', "https://api.github.com/search/repositories?q="+keyword+"&per_page="+str(PER_PAGE))

    nb_repos= getrepos.json()['total_count']
    nb_pages= int(ceil(nb_repos/float(PER_PAGE)));

    created_at=[]
    languages= []
    created_in_seconds = []

    for page in range(1,(LIMIT_REP/PER_PAGE)-1):
        URL= "https://api.github.com/search/repositories?q="+keyword+"&page="+str(page)+"&per_page=100"
        getrepos= requests.request('GET', URL)
        for i in range(0,PER_PAGE):
            created_at.append(getrepos.json()['items'][i]['created_at'])
            languages.append(getrepos.json()['items'][i]['language'])

    for i in range(0, len(created_at)):
        rfc_date= from_json_to_rfc_datetime(created_at[i])
        created_in_seconds.append(date_creation(rfc_date))

    created_in_seconds.sort()
    created_at.sort()

    

    ######
    #Histogram
    plt.ioff()
    plt.ylabel('Number of repositories')
    plt.xlabel('Time')
    x= []
    labels= []
    for i in range(1,len(created_at), 100):
        x.append(created_in_seconds[i])
        labels.append(from_json_to_rfc_datetime(created_at[i])[8:16])
    plt.xticks(x, labels, rotation= 20)
    plt.title('Number of repositories containing the keyword '+ keyword + ' created in function of time')
    plt.hist(created_in_seconds, 150)
    plt.axis([created_in_seconds[0], created_in_seconds[len(created_in_seconds)-1], 0, 30])
    plt.grid(True)
    figure= plt.savefig("YOUR PATH TO DIRECTORY"+'/mooc-reach/mysite/mooc/static/mooc/hist.png', dpi=400)
    plt.cla()
    plt.clf()


#Main prog.languages


    languages_count= []
    for item in [languages]:
        c= Counter(item)
        languages_count.append(c.most_common()[:len(languages)])

    #Creating an list that has the adequate form for Google data visualization on results.html
    languages_list=[['Languages', 'Number of repositories']]
    for i in range(0, len(languages_count[0])):
        languages_list.append([str(languages_count[0][i][0]), languages_count[0][i][1]])

######
#STACK OVERFLOW
#Authentication

    API_KEY = ' '
    API_CLIENT_ID = ' '
    API_CLIENT_SECRET = ' '
    PAGESIZE = 100
    PAGE=1

    api = stackexchange.Site(stackexchange.StackOverflow, API_KEY)
    search= api.search(intitle=keyword, pagesize=PAGESIZE, page=PAGE)
    questions= search
    while search.has_more:
        PAGE+=1
        search= api.search(intitle=keyword, pagesize=PAGESIZE, page=PAGE)
        questions+=search

    users=[]
    creation_dates=[]
    creation_dates_in_seconds=[]
    for i in range(0, len(questions)):
        try:
            owner= questions[i].owner
        except(UnicodeEncodeError,AttributeError):
            owner= None
        users.append(owner)
        tmp_date= questions[i].creation_date
        creation_dates.append(tmp_date)
        creation_dates_in_seconds.append(from_date_to_seconds(tmp_date))

    creation_dates.sort()
    creation_dates_in_seconds.sort()

    initial_date= datetime.date(2015,9,1) #Histogram with questions from september
    initial_date_seconds= from_date_to_seconds(initial_date)

    initial_date_index= binary_search(creation_dates_in_seconds, initial_date_seconds,
                                      0,len(creation_dates_in_seconds)-1)

    dates= creation_dates_in_seconds[initial_date_index:len(creation_dates_in_seconds)]
    if len(dates)>0:
        plt.ioff()
        plt.ylabel('Number of Questions')
        plt.xlabel('Time')
        x= []
        labels= []
        for i in range(1,len(dates), 110):
            x.append(dates[i])
            labels.append(str(creation_dates[i+initial_date_index])[0:10])

        plt.ioff()
        plt.xticks(x, labels, rotation= 20)
        plt.title('Number of questions containing the keyword  \''+ keyword + ' \' created in function of time')
        plt.hist(dates, 50)
        plt.grid(True)
        figure= plt.savefig("YOUR PATH TO DIRECTORY"+'/mooc-reach/Django/mysite/mooc/static/mooc/hist_so.png', dpi=400)
        plt.cla()
        plt.clf()

######



    positive_statuses=positive_statuses[0:10]
    if len(negative_statuses)<10:
        negative_statuses=negative_statuses[0:len(negative_statuses)]
    else:
        negative_statuses= negative_statuses[0:10]

    return render(request, 'mooc/results.html', {'keyword': keyword, 'derivative':derivative, 'positive_statuses':positive_statuses,'negative_statuses':negative_statuses, 'tweets_per_tz': tweets_per_tz, 'countries':countries, 'number_tweets':number_tweets, 'donnees': donnees, 'ratio_tweets':ratio_tweets, 'locations': locations, 'coordinates': coordinates,'languages_list': languages_list,'tweets_count':tweets_count,})





