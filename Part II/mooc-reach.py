import csv
import requests
from collections import defaultdict
from collections import Counter
from github import Github
import statistics

username = ' ' # Your GitHub username
password = ' ' # Your GitHub password
ACCESS_TOKEN = ' '
g = Github(username, password)

kw='scala'
users= []
emails= []
full_names=[]
PER_PAGE=100;
LIMIT_REP= 1000;

for page in range(1,(LIMIT_REP/PER_PAGE)-1):
    URL= "https://api.github.com/search/repositories?q="+kw+"&page="+str(page)+"&per_page=100"
    getmoocs= requests.request('GET', URL)
    for i in range(0,100):
        users.append(getmoocs.json()['items'][i]['owner']['login'])
        full_names.append(getmoocs.json()['items'][i]['full_name'])


for i in range(0, len(users)):
    emails.append(g.get_user(users[i]).email)


columns = defaultdict(list)
with open('emails_grades.csv') as f:
    reader = csv.reader(f)
    reader.next()
    for row in reader:
        for (i,v) in enumerate(row):
            columns[i].append(v)
scala_list= columns[0]
scala_session= columns[1]
grades= columns[2]


#DATABASE

dict_users_emails= dict(zip(users, emails))
dict_emails_users=dict(zip(emails,users))



#Emails without duplicates
emails_count= []
for item in [emails]:
    c= Counter(item)
    emails_count.append(c.most_common()[:len(emails)])

matching_emails=[]
matching_sessions=[]
for i in range (0, len(scala_list)):
    for j in range(0, len(emails_count[0])):
        if scala_list[i]==emails_count[0][j][0]:
            matching_emails.append(scala_list[i])
            matching_sessions.append(scala_session[i])

scala_users=[]
matching_grades=[]
for j in range(0, len(scala_list)):
    for i in range(0, len(matching_emails)):
        if matching_emails[i]== scala_list[j]:
            scala_users.append(dict_emails_users[matching_emails[i]])
            matching_grades.append(grades[j])
            break


matching_users=[]
matching_full_names=[]
for i in range(0, len(full_names)):
    for j in range(0, len(scala_users)):
        if scala_users[j] == users[i]:
            full_name=full_names[i]
            split_full_name=full_name.split('/')
            matching_users.append(split_full_name[0])
            matching_full_names.append(full_name)



repos=[]
for i in range(0,len(matching_full_names)):
    repos.append(g.get_repo(matching_full_names[i]))

stargazers_count=[]
for i in range(0, len(repos)):
    stargazers_count.append(repos[i].stargazers_count)

dict_full_names_stars=dict(zip(matching_full_names, stargazers_count))


dict_users_grades={}
for i in range(0, len(scala_users)):
    if not dict_users_grades.has_key(scala_users[i]):
        dict_users_grades[scala_users[i]] = [matching_grades[i]]
    else:
        dict_users_grades[scala_users[i]].append(matching_grades[i])


dict_users_session={}
for i in range(0, len(scala_users)):
    if not dict_users_session.has_key(scala_users[i]):
        dict_users_session[scala_users[i]] = [matching_sessions[i]]
    else:
        dict_users_session[scala_users[i]].append(matching_sessions[i])

users_from_full_names= []
matches=[]

for i in range(0, len(dict_full_names_stars)):
    full_name=dict_full_names_stars.keys()[i]
    split_full_name=full_name.split('/')
    users_from_full_names.append(split_full_name[0])

for i in range(0, len(users_from_full_names)):
    for j in range(0, len(dict_users_grades.keys())):
        if users_from_full_names[i]==dict_users_grades.keys()[j]:
            matches.append(dict_users_grades.values()[j])


users_from_full_names_grades=[]
for i in range(0, len(users_from_full_names)):
    for j in range(0, len(dict_users_grades)):
        if dict_users_grades.keys()[j]==users_from_full_names[i]:
            users_from_full_names_grades.append(dict_users_grades.values()[j])


emails_corresponding_to_full_names=[]
for i in range(0, len(users_from_full_names_grades)):
    for j in range(0, len(dict_users_emails)):
        if dict_users_emails.keys()[j]== users_from_full_names[i]:
            emails_corresponding_to_full_names.append(dict_users_emails.values()[j])

sessions_corresponding_to_full_names=[]
for i in range(0, len(users_from_full_names)):
    for j in range(0, len(dict_users_session)):
        if dict_users_session.keys()[j]== users_from_full_names[i]:
            sessions_corresponding_to_full_names.append(dict_users_session.values()[j])


# Changing sessions to years
for i in range(0, len(dict_users_session)):
    session = dict_users_session.values()[i]
    for j in range(0, len(session)):
        if session[j] =='progfun-2012-001':
            dict_users_session.values()[i][j]='2012'
        else:
            dict_users_session.values()[i][j]='201'+ str(int(session[j][-1:])+1)


dict_users_from_full_names_grades=dict(zip(dict_full_names_stars.keys(),users_from_full_names_grades))


max_grades=[]
for i in range(0, len(users_from_full_names_grades)):
    for j in range(0, len(users_from_full_names_grades[i])):
        if users_from_full_names_grades[i][j]=='NULL':
            users_from_full_names_grades[i][j]='0'
        else:
            users_from_full_names_grades[i][j]=users_from_full_names_grades[i][j]

for i in range(0, len(users_from_full_names_grades)):
    max_grades.append(float(max(users_from_full_names_grades[i])))


dict_max_grades_stars= dict(zip(max_grades, dict_full_names_stars.values()))

sorted_dict= sorted(dict_max_grades_stars.iteritems())
sorted_grades= []
sorted_stars=[]
for i in range(0, len(sorted_dict)):
    sorted_grades.append(sorted_dict[i][0])
    sorted_stars.append(sorted_dict[i][1])

import matplotlib.pyplot as plt
plt.ylabel('Stars')
plt.xlabel('Grades')
plt.plot(sorted_grades, sorted_stars )
plt.grid(True)
#figure= plt.savefig('/Users/inesbahej/Desktop/grades.png', dpi=400)
plt.show()


##### Statistics
count1=0.0
count2=0.0

for i in range(0, len(dict_users_from_full_names_grades)):
    grade= dict_users_from_full_names_grades.values()[i]
    stars= dict_full_names_stars.values()[i]
    for g in grade:
        if g=='NULL':
            g=0
        if stars>100:
            tab1.append(float(g))
        else:
            tab2.append(float(g))

print "Average grade of users whose repositories have more than 100 stars",sum(tab1)/len(tab1)
print "Standard deviation",statistics.stdev(tab1)

print "Average grade of users whose repositories have less than 100 stars"sum(tab2)/len(tab2)
print "Standard deviation",statistics.stdev(tab2)





