import requests
from bs4 import BeautifulSoup

url = "https://python.langchain.com/v0.1/docs/modules/model_io/"
r = requests.get(url)
soup = BeautifulSoup(r.text, "lxml")
url_list_1=[]
counter_1 = 0  # Initialize counter

while counter_1 < 8:  # Continue loop until counter reaches 7
    np = soup.find("a", class_="pagination-nav__link pagination-nav__link--next").get("href")
    cnp = "https://python.langchain.com/" + np
    print(cnp)
    url_list_1.append(cnp)
    url = cnp
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    
    counter_1 += 1
    
url = "https://python.langchain.com/v0.1/docs/modules/model_io/prompts/few_shot_examples/"
r = requests.get(url)
soup = BeautifulSoup(r.text, "lxml")

counter_2 = 0  # Initialize counter

while counter_2 < 7:  # Continue loop until counter reaches 7
    np = soup.find("a", class_="pagination-nav__link pagination-nav__link--next").get("href")
    cnp = "https://python.langchain.com/" + np
    print(cnp)
    url_list_1.append(cnp)
    url = cnp
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    
    counter_2 += 1 
    
url = "https://python.langchain.com/v0.1/docs/modules/model_io/chat/structured_output/"
r = requests.get(url)
soup = BeautifulSoup(r.text, "lxml")

counter_3 = 0  # Initialize counter

while counter_3 < 7:  # Continue loop until counter reaches 7
    np = soup.find("a", class_="pagination-nav__link pagination-nav__link--next").get("href")
    cnp = "https://python.langchain.com/" + np
    print(cnp)
    url_list_1.append(cnp)
    url = cnp
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    
    counter_3 += 1 
    
url = "https://python.langchain.com/v0.1/docs/modules/model_io/llms/custom_llm/"
r = requests.get(url)
soup = BeautifulSoup(r.text, "lxml")

counter_4 = 0  # Initialize counter

while counter_4 < 5:  # Continue loop until counter reaches 7
    np = soup.find("a", class_="pagination-nav__link pagination-nav__link--next").get("href")
    cnp = "https://python.langchain.com/" + np
    print(cnp)
    url_list_1.append(cnp)
    url = cnp
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    
    counter_4 += 1 


url = "https://python.langchain.com/v0.1/docs/modules/model_io/output_parsers/custom/"
r = requests.get(url)
soup = BeautifulSoup(r.text, "lxml")

counter_5 = 0  # Initialize counter

while counter_5 < 15:  # Continue loop until counter reaches 7
    np = soup.find("a", class_="pagination-nav__link pagination-nav__link--next").get("href")
    cnp = "https://python.langchain.com/" + np
    print(cnp)
    url_list_1.append(cnp)
    url = cnp
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    
    counter_5 += 1 
    
url = "https://python.langchain.com/v0.1/docs/modules/data_connection/document_loaders/custom/"
r = requests.get(url)
soup = BeautifulSoup(r.text, "lxml")

counter_6 = 0  # Initialize counter

while counter_6 < 8:  # Continue loop until counter reaches 7
    np = soup.find("a", class_="pagination-nav__link pagination-nav__link--next").get("href")
    cnp = "https://python.langchain.com/" + np
    print(cnp)
    url_list_1.append(cnp)
    url = cnp
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    
    counter_6 += 1 

url = "https://python.langchain.com/v0.1/docs/modules/data_connection/document_transformers/HTML_header_metadata/"
r = requests.get(url)
soup = BeautifulSoup(r.text, "lxml")

counter_7 = 0  # Initialize counter

while counter_7 < 9:  # Continue loop until counter reaches 7
    np = soup.find("a", class_="pagination-nav__link pagination-nav__link--next").get("href")
    cnp = "https://python.langchain.com/" + np
    print(cnp)
    url_list_1.append(cnp)
    url = cnp
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    
    counter_7 += 1 

url = "https://python.langchain.com/v0.1/docs/modules/data_connection/text_embedding/caching_embeddings/"
r = requests.get(url)
soup = BeautifulSoup(r.text, "lxml")

counter_8 = 0  # Initialize counter

while counter_8 < 3:  # Continue loop until counter reaches 7
    np = soup.find("a", class_="pagination-nav__link pagination-nav__link--next").get("href")
    cnp = "https://python.langchain.com/" + np
    print(cnp)
    url_list_1.append(cnp)
    url = cnp
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    
    counter_8 += 1 

url = "https://python.langchain.com/v0.1/docs/modules/data_connection/retrievers/MultiQueryRetriever/"
r = requests.get(url)
soup = BeautifulSoup(r.text, "lxml")

counter_9 = 0  # Initialize counter

while counter_9 < 12:  # Continue loop until counter reaches 7
    np = soup.find("a", class_="pagination-nav__link pagination-nav__link--next").get("href")
    cnp = "https://python.langchain.com/" + np
    print(cnp)
    url_list_1.append(cnp)
    url = cnp
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    
    counter_9 += 1 
    
url = "https://python.langchain.com/v0.1/docs/modules/agents/how_to/custom_agent/"
r = requests.get(url)
soup = BeautifulSoup(r.text, "lxml")

counter_10 = 0  # Initialize counter

while counter_10 < 14:  # Continue loop until counter reaches 7
    np = soup.find("a", class_="pagination-nav__link pagination-nav__link--next").get("href")
    cnp = "https://python.langchain.com/" + np
    print(cnp)
    url_list_1.append(cnp)
    url = cnp
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    
    counter_10 += 1 
    
url = "https://python.langchain.com/v0.1/docs/modules/agents/how_to/custom_agent/"
r = requests.get(url)
soup = BeautifulSoup(r.text, "lxml")

counter_11 = 0  # Initialize counter

while counter_11 < 27:  # Continue loop until counter reaches 7
    np = soup.find("a", class_="pagination-nav__link pagination-nav__link--next").get("href")
    cnp = "https://python.langchain.com/" + np
    print(cnp)
    url_list_1.append(cnp)
    url = cnp
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    
    counter_11 += 1 
    
url = "https://python.langchain.com/v0.1/docs/modules/callbacks/async_callbacks/"
r = requests.get(url)
soup = BeautifulSoup(r.text, "lxml")

counter_12 = 0  # Initialize counter

while counter_12 < 5:  # Continue loop until counter reaches 7
    np = soup.find("a", class_="pagination-nav__link pagination-nav__link--next").get("href")
    cnp = "https://python.langchain.com/" + np
    print(cnp)
    url_list_1.append(cnp)
    url = cnp
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    
    counter_12 += 1 
    

def fetch_and_save_to_file(url_list, path):
    for i, url in enumerate(url_list, 1):
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')
        text = soup.get_text()
        filename = f"{i}.txt"  # File name in ascending order
        with open(f"{path}/{filename}", "w", encoding="utf-8") as f:
            f.write(text)



fetch_and_save_to_file(url_list_1, "data")