from bs4 import BeautifulSoup
import requests
import json
import secrets
import sys
import sqlite3
import plotly.graph_objects as go 


BASEURL = "https://www.topmastersinhealthcare.com/best/masters-degrees-in-health-informatics/"

def get_uni_name(search):
    '''Creates a list of all the names of the universities and their rank
    
    Parameters
    ----------
    search - string
    Returns
    -------
    name_list:list
    '''
    university_name = search.find_all("h3")
    name_list =[]
    for name in university_name:
        name = name.text
        uni_text = name.replace("<h3>","")
        uni_text = name.replace("</h3>","")
        name_list.append(uni_text)
    return name_list
    # uni_text prints out all universities along with their rank
    
# create a function named def get_uni_loc()  
def get_uni_loc_degree(search):
    '''Creates a list of all the locations and names of degree of each university
    
    Parameters
    ----------
    search - string
    Returns
    -------
    loc_list:list
    '''
    university_location = search.find_all("h4")
    loc_list =[]
    for location in university_location:
        location = location.text
        uni_loc_degree = location.replace("<h4>","")
        uni_loc_degree = location.replace("</h4>","")
        loc_list.append(uni_loc_degree)
    return loc_list
    # uni_loc_degree prints out all university locations along with the name of the degre
    
# create a function named get_uni_link() 
   
def get_page_link(search):
    '''Creates a list of the website url of each university
    
    Parameters
    ----------
    search - string
    Returns
    -------
    sliced_list:list
    '''
    university_link = search.find_all( "a")
    link_list=[]
    for link in university_link:
        if link.has_attr('href'):
            main_link = link.attrs["href"]
            link_list.append(main_link)
            sliced_list =link_list[1:21]
    sliced_list.reverse()
    return sliced_list
    
        # prints out the main webpage link for details of the colleges
        
def load_cache(): 
    '''Read the cache file and check the contents 
    
    Parameters
    ----------
    None
        
    
    Returns
    -------
    cache
    '''
    try:
        cache_file = open("cache.json", 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache

def save_cache(cache): 
    
    '''Writes on the cache file too add new urls.
    
    Parameters
    ----------
    cache - dictionary
    
    Returns
    -------
    None
    '''
    cache_file = open('cache.json', 'w')
    contents_to_write = json.dumps(cache)
    cache_file.write(contents_to_write)
    cache_file.close()

def fetch_data(url, rank_input, cache={}):
    '''Requests url using the existing cache
    
    Parameters
    ----------
    url - string
    cache - dictionary
    
    Returns
    -------
    cache url 
    cache
    '''
    i = int(rank_input-1)
    if i in cache: 
        # If the data is in cache -> use that
        print("Using cache")     
        college_name, sliced_list_location, sliced_list_degree, page_link = cache[i]
    else:
        print("Fetching")
        #fetch data from url
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        search = soup.find(attrs= {"class":"modContents"})

        # Process on fetched data
        college_name = get_uni_name(search)
        college_name.reverse()
        college_location_degree = get_uni_loc_degree(search)
        college_location_degree.reverse()
        sliced_list_degree = college_location_degree[0:40:2] 
        sliced_list_location = college_location_degree[1:40:2]
        page_link = get_page_link(search)
        
        college_name = college_name[i]
        sliced_list_location = sliced_list_location[i]
        sliced_list_degree = sliced_list_degree[i]
        page_link = page_link[i]
        cache[i] = (college_name, sliced_list_location, sliced_list_degree, page_link)

    print("-------------------------\n UNIVERSITY NAME WITH RANK:\n--------------------------\n" + college_name)
    print("---------------------\n UNIVERSITY LOCATION:\n---------------------\n" + sliced_list_location)
    print("---------------------\n UNIVERSITY DEGREE:\n---------------------\n" + sliced_list_degree)
    print("-----------\n WEBPAGE:\n-----------\n" + page_link+ "\n-----------")
    return cache


conn = sqlite3.connect('mhi.sqlite')
cur = conn.cursor()

query = '''
SELECT Rank,University,Location,Degree_name
FROM whole_uni
 
'''
cur.execute(query)

for row in cur:
    print(f'{row[1]} is located in {row[2]}. It offers {row[3]}.')
    

conn.close()


print("--------------------------------------------")

xvals = [1, 2, 3, 4, 5]
yvals = ['Uwash','Umich','GeorgeMason','NovaSoutheastern','MarshalUni']

scatter_data = go.Scatter(x=xvals, y=yvals)
basic_layout = go.Layout(title="A  Plot displaying the College Rank matched to the University")
fig = go.Figure(data=scatter_data, layout=basic_layout)

fig.write_html("scatter.html", auto_open=True)



# make a __main__ and put user input promt here along with pretty printing the fetched data
if __name__ == "__main__":
    # load cache
    cache = load_cache()
    while True:
        print("--------------------------------------------")
        rank_input = input("Enter a rank number between 1 to 20 for a college proficient in the MHI program  or type 'exit':")
        if rank_input.isnumeric():
            rank_input = float(rank_input)
            if rank_input in list(range(1,21)):
                # Get data either from URL or from cache and display
                cache = fetch_data(BASEURL, rank_input, cache)
                # update the cache
                save_cache(cache)
            elif rank_input not in list(range(1,21)):
                print(f"[ERROR] Enter a rank between 1 and 20 [ERROR]")
            else:
                print(f"I'm not sure what you're searching.\nPlease enter a number between 1 and 20 to get corresponding college.")
        elif rank_input.isalpha():
            if rank_input in ['exit', 'Exit', 'EXIT']:
                sys.exit()
            elif rank_input not in ['exit', 'Exit', 'EXIT']:
                print("Do you wish to exit? If yes, then type exit.")
            else:
                print(f"I'm not sure what you're searching.\nPlease enter a number between 1 and 20 to get corresponding college.")
        else:
            print(f"I'm not sure what you're searching.\nPlease enter a number between 1 and 20 to get corresponding college.")
        