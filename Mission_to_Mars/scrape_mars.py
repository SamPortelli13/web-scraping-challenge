import pandas as pd
import time
from splinter import Browser
from bs4 import BeautifulSoup as bs
from webdriver_manager.chrome import ChromeDriverManager

#def init_browser():
#    # @NOTE: Replace the path with your actual path to the chromedriver
#    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
#    return Browser("chrome", **executable_path, headless=False)

# set up a function to reinitialise the browser with a new URL
def init_browser():
    executable_path = {"executable_path": ChromeDriverManager().install()}
    #executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)

# helper function to build mars report
def build_report(mars_report):
    final_report = ""
    for p in mars_report:
        final_report += " " + p.get_text()
        print(final_report)
    return final_report

def scrape():
    mars_data = {}

    # URL of first page to be scraped   ---------------------------------------------

    browser = init_browser()
    mars_url = "https://redplanetscience.com"
  
    browser.visit("https://redplanetscience.com")
    time.sleep(10)
    #browser.is_element_present_by_text("more info", wait_time=5)
    # Retrieve page 
    html=browser.html
    # Create BeautifulSoup object; parse with 'html.parser'
    news_soup = bs(html, "html.parser")
    #print(news_soup.prettify())
    # Find the latest news title and text and print them
    news_title = news_soup.find("div", class_ = "content_title")
    news_title = news_title.text.strip()
    news_text = news_soup.find("div", class_ = "article_teaser_body")
    news_text = news_text.text.strip()

    # URL of page to be scraped - JPL Mars Space Images  ---------------------------------------------
    #browser = init_browser()
    mars_images_url = "http://spaceimages-mars.com/"
    browser.visit("http://spaceimages-mars.com/")
    time.sleep(2)
    # Retrieve page 
    html=browser.html
    # Create BeautifulSoup object; parse with 'html.parser'
    images_soup = bs(html, "html.parser")
    # Locate and print the Featured Image URL
    featured_image = images_soup.find("img", class_ = "headerimage fade-in")
    featured_image_url = mars_images_url+featured_image['src']

    # URL of page to be scraped - Mars Facts    ---------------------------------------------
    mars_facts_url = "https://galaxyfacts-mars.com/"
    tables = pd.read_html(mars_facts_url)
    time.sleep(2)
    df=tables[0]
    # Make the first row the column headings & drop the first row
    df.columns = df.iloc[0]
    df = df.drop(0)
    # Convert the table to a HTML string
    mars_facts_data_html= df.to_html(columns=["Mars - Earth Comparison","Mars","Earth"],index=False)
    # create soup object from html
    html = mars_facts_data_html
    mars_facts_report = bs(html, "html.parser")
    mars_report = mars_facts_report.find_all("tr")

    # URL of page to be scraped - Mars Hemisphere Images   --------------------------------------------- 
    #browser = init_browser()
    hemisphere_images_url = "http://marshemispheres.com/"
    browser.visit(hemisphere_images_url)
    time.sleep(2)
    html=browser.html
    hemisphere_images_soup = bs(html, "html.parser")
    hemisphere_urls = hemisphere_images_soup.find_all("div", class_ = "description")
    hemisphere_urls_list = []
    for hem_urls in hemisphere_urls:
            hemisphere_url = hem_urls.find("a")["href"]
            hemisphere_urls_list.append(hemisphere_images_url+hemisphere_url)

    # for each hemisphere retrieve the image details:   ---------------------------------------------
    # store them in a dictionary
    #browser.quit()
    all_hemisphere_dicts = []

    try:
        for hem_url in hemisphere_urls_list:
            browser.visit(hem_url)
            time.sleep(2)
            html=browser.html
            hemisphere_images_soup = bs(html, "html.parser")
            hemisphere_image_url = hemisphere_images_soup.find("img", class_ = "wide-image")["src"]
            hemisphere_image_title = hemisphere_images_soup.find("h2", class_ = "title")
            hemisphere_image_title = hemisphere_image_title.text.strip().split(" Enhanced")[0] 

            # set up a dictionary to store the image url string and the title in a list - one dictionary for each hemisphere
            hemisphere_dict={}
            hemisphere_dict["title"]=hemisphere_image_title
            hemisphere_dict["img_url"]=hemisphere_images_url+hemisphere_image_url
            all_hemisphere_dicts.append(hemisphere_dict)

    except AttributeError as e:
        print(e)
    # add it to our mars data dict
    browser.quit()
    #
    #  Construct the Dictionary to be updated to MongoDB
    #  -------------------------------------------------
    # add Latest News Title & Text to mars data dict
    mars_data["news_title"]=news_title
    mars_data["news_text"]=news_text

    # add Features Image URL to mars data dict
    mars_data["featured_image_src"] = featured_image_url

    # add Mars Hemishere Image Texts and URLS
    for i in range(4):
        mars_data["hemisphere_title"+str(i)]=all_hemisphere_dicts[i-1]["title"]
        mars_data["hemisphere_img_url"+str(i)]=all_hemisphere_dicts[i-1]["img_url"]

    # add Mars Facts table to mars data dict
    #mars_data["facts_table"] = build_report(mars_report)
    mars_data["facts_table"] = mars_facts_data_html

    
    
    return mars_data

