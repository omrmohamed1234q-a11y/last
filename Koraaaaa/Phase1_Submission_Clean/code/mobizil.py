import csv
import time
import requests
from bs4 import BeautifulSoup
from serpapi import GoogleSearch

def get_models(file_name):
    with open(f"{file_name}.csv", "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        models = []
        for row in reader:
            spec = row["specifications"]

            for line in spec.split("\n"):
                if "Model Name" in line:
                    model_name = line.split(":")[1].strip()
                    if model_name not in models:
                        models.append(model_name)
    return models
def get_link(phone):
    params = {
        "engine": "google",
        "q": f"{phone} + Mobizil",
        "api_key": ""
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    organic =results.get('organic_results', [])
    if organic:
        for x in results['organic_results']:
            link = x['link']
            if 'mobizil.com' in link:
                print(link)
                return link


    return None

def get_review(link):
    if link:
        response = requests.get(link)
        print(response)
        organised = BeautifulSoup(response.content, 'html5lib')
        try:
            pros_container = organised.find('ul', class_="bs-shortcode-list list-style-check")
            pros = pros_container.find_all('li')
            pros = [x.text for x in pros]
            pros = '\n'.join(pros)
        except:
            pros = "Not found"

        try:
            cons_container = organised.find('ul', class_="bs-shortcode-list list-style-asterisk")
            cons = cons_container.find_all('li')
            cons = [x.text for x in cons]
            cons = '\n'.join(cons)
        except:
            cons = "Not found"
        review = [pros, cons]
        return review
    else:
        return ['unable to get the link','unable to get the link']


def write_review(read_file):
    with open(f"{read_file}_reviews.csv", "w", newline="", encoding="utf-8") as file:
        fieldnames = ["model_name", "pros" , "cons" , "review_link"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for x in get_models(read_file):
            link=get_link(x)
            time.sleep(2)
            review=get_review(link)
            rev_dict={"model_name":x,"pros":review[0],"cons":review[1],"review_link":link}
            writer.writerow(rev_dict)

#write_review("first_category")
#write_review("second_category")
write_review("third_category")
