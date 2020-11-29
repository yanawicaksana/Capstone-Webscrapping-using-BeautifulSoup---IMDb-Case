from flask import Flask, render_template
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests
import seaborn as sns

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #don't change this code

#This is fuction for scrapping
url_get = requests.get('https://www.imdb.com/search/title/?release_date=2019-01-01,2019-12-31')
soup = BeautifulSoup(url_get.content,"html.parser")
    
#Find the key to get the information
table = soup.find(class_="lister-list",attrs={'class'})
pages = np.arange(1,101,50)

temp = [] #initiating a tuple
headers = {"Accept-Language": "en-US,en;q=0.5"}

for page in pages:
   page = requests.get('https://www.imdb.com/search/title/?release_date=2019-01-01,2019-12-31&start='+str(page)+'&ref_=adv_nxt',headers=headers)
    
   soup = BeautifulSoup(page.text,'html.parser')
   movie_div = soup.find_all('div', class_='lister-item mode-advanced')
        
   for row in movie_div:
        #title movie 
        title = row.find(class_="lister-item-header").find('a', href=True).text
        
        #year
        year = row.find(class_="lister-item-year text-muted unbold").text
        
        #imdb rating
        if row.find(class_="inline-block ratings-imdb-rating") is None:
           imdb = row.find(class_="inline-block ratings-imdb-rating").find('strong')
        else:
           imdb = row.find(class_="inline-block ratings-imdb-rating").find('strong').text
        #metascore, use if else due to we have null value for several movie
        if row.find(class_="metascore mixed") is None:
           meta = row.find(class_="metascore mixed") 
        else:
           meta = row.find(class_="metascore mixed").text  
    
        #votes
        votes = row.find(class_="sort-num_votes-visible").text.split()[1]
        
        #duration, because some movie also don't have duration
        if row.find('p', class_="text-muted").find(class_="runtime") is None:
           duration = row.find('p', class_="text-muted").find(class_="runtime")
        else:
           duration = row.find('p', class_="text-muted").find(class_="runtime").text
        
        #genre
        genre = row.find(class_="genre").text.strip()
        
        #temp variable used for collect all variables result of scrapping
        temp.append((title,year,imdb,meta,votes,duration, genre))    
    
data = pd.DataFrame(temp, columns=('title','year','imdb','meta','votes','duration','genre'))
#creating the dataframe
#data wranggling -  try to change the data type to right data type
    
data['duration']= data['duration'].str.replace(" min","")
data['rank_popularity']=range(1,len(data)+1)
data['imdb']=data['imdb'].astype('float64')
data['votes']=data['votes'].str.replace(",","").astype('int64')
data['duration'] = data['duration'].fillna(0).astype('int64')
data['meta'] = data['meta'].fillna(0).astype('int64')
top7 = data.head(7)
#end of data wranggling

@app.route("/")
def index(): 
	card_data = data["imdb"].mean()
   # generate plot
	sns.lineplot(data=top7, x='title', y='imdb', color = "red", linewidth=4,
              solid_joinstyle='bevel', solid_capstyle='round', sort=False)
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]


	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)
