import pandas as pd
import numpy as np

# helpful modules
import fuzzywuzzy
from fuzzywuzzy import process
import chardet

import os
import datetime
from datetime import datetime
import pickle
import matplotlib.pyplot as plt 

os.chdir('Documents/IBA/IDM/project')
dfOr = pd.read_csv("PakistanSuicideAttacks Ver 11 (30-November-2017).csv",encoding='Windows-1252')

cities = len(df['City'].unique())


#Problem with cities - trailing spaces and casing

#lower case
df['City'] = df['City'].str.lower()

#remove white spaces
df['City']=df['City'].str.strip()


#PROVINCE
df['Province'] = df['Province'].str.lower()

#remove white spaces
df['Province']=df['Province'].str.strip()


#Holiday Type issue - Eid ul Azha recorded as different attributes

c=df['Holiday Type'].unique()

#dfBackup = df.copy

#i=0

for i in range(len(df)):
    if 'zha' in str(df['Holiday Type'][i]):
        df['Holiday Type'][i]='Eid-ul-Azha'
        
        

#Using fuzzy matching to match words
        
matches = fuzzywuzzy.process.extract("D.I. Khan", dfOr['City'].unique(), limit=10, scorer=fuzzywuzzy.fuzz.token_sort_ratio)



def replaceMatches(df, column, string_to_match, min_ratio = 90):
    strings = df[column].unique()
    
    matches = fuzzywuzzy.process.extract(string_to_match, strings, 
                                         limit=10, scorer=fuzzywuzzy.fuzz.token_sort_ratio)

    close_matches = [matches[0] for matches in matches if matches[1] >= min_ratio]

    rows_with_matches = df[column].isin(close_matches)

    df.loc[rows_with_matches, column] = string_to_match
    
    print("All done!")
    
    
replaceMatches(df=df, column='Location Sensitivity', string_to_match="Low")


replaceMatches(df=df, column='Province', string_to_match="baluchistan")





#Separating Day and Date
date = df['Date']
date=list(date)
day=[]
dates=[]
for i in range(len(date)):
    sp1= date[i].replace(' ','-')
    sp=sp1.split('-')
    day.append(sp[0])
    dates.append(sp[1:len(sp)])


df['Day']=day

fDates=[]
for i in dates:
    date_str=i[0]+' '+i[1]+' '+i[2]
    try:
        fDates.append(datetime.strptime(date_str, '%B %d %Y'))
    except:
        fDates.append(datetime.strptime(date_str, '%b %d %Y'))


df['Date-old']=date
df['Date']=fDates

df.to_pickle('processedDF2.pkl')




#CHECKING NULL VALUES

#NULL VALUES IN EACH COLUMN
x=df.isnull().sum()


#NULL VALUES IN EACH ROW
for i in range(len(df.index)) :
    print("Nan in row ", i , " : " ,  df.iloc[i].isnull().sum())
    
    
#CONVERTING DATES TO ISLAMIC DATES
from ummalqura.hijri_date import HijriDate
from datetime import date

islamicDates=[]
for i in range(len(df)):
    
    curDate=df['Date'][i]
    um = HijriDate(curDate.year, curDate.month, curDate.day, gr=True)
    islamicDates.append(um)

df['Islamic Date Old']=df['Islamic Date']
df['Islamic Date']=islamicDates

f = open('mapData.txt','w+')

mapString=""


color=''
for i in range(447):
    if i not in [449,450,492]:
        if (df['Province'][i]=='sindh'):
            color='blue'
        elif (df['Province'][i]=='baluchistan'):
            color='red'
        elif (df['Province'][i]=='capital'):
            color='green'
        elif (df['Province'][i]=='punjab'):
            color='orange'
        elif (df['Province'][i]=='fata'):
            color='white'
        elif (df['Province'][i]=='kpk'):
            color='black'
        else:
            color='yellow'
            
        
        mapString = mapString + '\n' + str(lats[i])+'\t'+str(longF[i])+'\tcircle1\t'+color+'\t '+str(i)+'\t'+df['City'][i]

f.write(mapString)

f.close()


lats = list(df['Latitude'])
longs = list(df['Longitude'])


#REMOVE LINE THINGY
df = df.replace('\n',' ', regex=True)

df['coordinates']=coords

coords=[]
for i in range(len(df)):
    coords.append('('+str(df['Latitude'][i])+','+str(df['Longitude'][i])+')')
    
df.to_csv('df2.csv')

#VISUALIZATIONS
cities = df['City'].unique()
cities.sort()
citiesNum=[]
citiesKilledMin=[]
citiesKilledMax=[]

for i in cities:
    citiesNum.append(len(df[df.City==i]))
    citiesKilledMin.append(df[df.City==i]['Killed Min'].sum())
    citiesKilledMin.append(df[df.City==i]['Killed Max'].sum())
    
pr = df['Province'].unique()
pr.sort()
prNum=[]
prKilledMin=[]
prKilledMax=[]

for i in pr:
    prNum.append(len(df[df.Province==i]))
    prKilledMin.append(df[df.Province==i]['Killed Min'].sum())
    prKilledMax.append(df[df.Province==i]['Killed Max'].sum())
    

plt.pie(prNum, labels=pr, startangle=90, autopct='%.1f%%')
plt.pie(prKilledMax, labels=pr, startangle=90, autopct='%.1f%%')
plt.pie(citiesNum2, labels=cities2, startangle=90, autopct='%.1f%%')


cities2=[]
citiesNum2=[]
for i in range(len(citiesNum)):
    if citiesNum[i]>15:
        cities2.append(cities[i])
        citiesNum2.append(citiesNum[i])


df.to_pickle('df3.pkl')
import pickle
df = pd.read_pickle('df3.pkl')

x=list(df['Islamic Month'])

import collections
x.sort()
c = collections.Counter(x)
c = sorted(c.items())
months_num = [i[0] for i in c]
month_names = [months[i[0]-1] for i in c]
freq = [i[1] for i in c]


f, ax = plt.subplots()


plt.bar(months_num, freq)
plt.title("Attacks per Islamic Month")
plt.xlabel("Months")
plt.ylabel("Frequency")
ax.set_xticks(range(1, 13))
ax.set_xticklabels(range(1,13))

plt.show()


x='Muharram,Safar,Rabi-ul-Awwal,Rabi-al-Thani,Jumadalula,Jummda-al-akhira,Rajab,Shaban,Ramadan,Shawal,Dhu al Qadah,Dhu al Hijjah'
monthLabels=x.split(',')


holidays = df['Holiday Type'].unique()
hNums=[]
for i in holidays:
    hNums.append(len(df[df['Holiday Type']==i]))

plt.pie(hNums, labels=holidays, startangle=90, autopct='%.1f%%')





df['Year']=''

for i in range(len(df)):
    df['Year'][i]=df['Date'][i].year
    
x=list(df['Year'])

import collections
x.sort()
c = collections.Counter(x)
c = sorted(c.items())
freq = [i[1] for i in c]


f, ax = plt.subplots()


plt.bar(months_num, freq)
plt.title("Attacks per Year")
plt.xlabel("Months")
plt.ylabel("Frequency")
#ax.set_xticks(range(1, 13))
#ax.set_xticklabels(range(1,13))

plt.show()

