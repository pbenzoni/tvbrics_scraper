import requests
from bs4 import BeautifulSoup
import csv
import time

def fetch_page_content(page_number,lang, ibl):
    """
    Fetch the HTML content for a given page number.
    Returns the raw HTML text.
    """
    url = "https://tvbrics.com/"+ lang+ "/ajax/more_items.php"
    params = {
        "PAGEN_1": page_number,
        "p": 100,
        "prefix": "news",
        "wrap": "js-center_news",
        "f": '{"!PROPERTY_ELEMENTS_LINK":"q303ZwA9"}',
        "ibl": str(ibl),
        "type": "-",
        "d": "/"+lang+"/news/#ELEMENT_CODE#/",
        "sort": "ACTIVE_FROM",
        "sort_order": "DESC"
    }

    headers = {
        "authority": "tvbrics.com",
        "method": "GET",
        "path": "/" + lang+ "/ajax/more_items.php?PAGEN_1="+str(page_number)+"&p=100&prefix=news&wrap=js-center_news"
                "&f=%7B%22!PROPERTY_ELEMENTS_LINK%22%3A%22q303ZwA9%22%7D&ibl="+str(ibl)+"&type=-"
                "&d=%2F"+lang+"%2Fnews%2F%23ELEMENT_CODE%23%2F&sort=ACTIVE_FROM&sort_order=DESC",
        "scheme": "https",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "priority": "u=1, i",
        "referer": "https://tvbrics.com/"+lang+"/news/",
        "sec-ch-ua": "\"Not A(Brand)\";v=\"8\", \"Chromium\";v=\"132\", \"Google Chrome\";v=\"132\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "x-requested-with": "XMLHttpRequest"
    }

    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    return response.text

def parse_titles_and_links(html):
    """
    Parse the HTML content to extract news item titles and their links.
    Returns a list of tuples (title, link).
    """
    soup = BeautifulSoup(html, "html.parser")
    results = []

    # Each item is contained in a div with class="news__center-column-content-item"
    items = soup.find_all("div", class_="news__center-column-content-item")

    for item in items:
        # The title is in a div with class="news-item__name"
        name_div = item.find("div", class_="news-item__name")
        if name_div:
            # Extract the text for the title
            title = name_div.get_text(strip=True)
            # The link is within an <a> inside the same name_div
            link_tag = name_div.find("a", href=True)
            link = link_tag["href"] if link_tag else ""
            # Clean up any trailing text if needed
            # Append title, link to results
            results.append((title, link))

    return results

def save_to_csv(data, filename="tvbrics_news.csv", lang="en"):
    """
    Save a list of tuples to a CSV file with UTF-8 encoding to support multiple languages.
    """
    with open(filename, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "Link"])
        writer.writerows(data)
    #save to json
    import json
    with open('tvbrics_news_'+lang+'.json', 'w', encoding='utf-8-sig') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)



def main():
    # Paginate through, for example, ten pages
    for lang in [ "en", "", "pt", "cn", "es",  "ar"]: #"" is for russian, removed en bc it ran already
        time.sleep(.5)
        for page in range(1, 100):
            ibl = 44 if lang == "en" else 60 if lang == "" else 63 if lang == "cn" else 73 if lang == "pt" else 129 if lang == "es" else 148 if lang == "ar" else 0
            html_content = fetch_page_content(page, lang, ibl)
            parsed_data = parse_titles_and_links(html_content)
            if not parsed_data:
                # If we hit an empty response, break out of the loop
                break
            if parsed_data[0] in all_articles:
                # If the first item is already in the list, we have reached the end
                break
            all_articles.extend(parsed_data)

        # Save all collected data to a CSV file
        save_to_csv(all_articles, "tvbrics_news_"+ lang +".csv", lang)
        print("Data saved to tvbrics_news.csv")

if __name__ == "__main__":
    main()