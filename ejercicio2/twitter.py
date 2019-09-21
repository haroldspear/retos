from selenium import webdriver
import csv
from config import *
import requests
from requests_toolbelt.adapters import source
from bs4 import BeautifulSoup
from time import *
from selenium.webdriver.common.action_chains import ActionChains

driver = None

def login_twitter(username, password):
    driver.get(LOGIN_URL)

    username_field = driver.find_element_by_class_name("js-username-field")
    password_field = driver.find_element_by_class_name("js-password-field")

    username_field.send_keys(username)
    driver.implicitly_wait(1)

    password_field.send_keys(password)
    driver.implicitly_wait(1)

    driver.find_element_by_class_name("EdgeButtom--medium").click()

def getUsernamesLikesOrRetweetsOrReply(output_filename):
    usernames_list = []
    scroll_times = 0
    if output_filename == RETWEETS_FILENAME or output_filename == LIKES_FILENAME:
        scroll_times = 70
    elif output_filename == REPLIES_FILENAME:
        scroll_times = 500
    for i in range(scroll_times):
        if output_filename == RETWEETS_FILENAME or output_filename == LIKES_FILENAME:
            usernames = driver.find_elements_by_xpath("//div[@class='css-901oao css-bfa6kz r-1re7ezh r-18u37iz r-1qd0xha r-1b43r93 r-16dba41 r-ad9z0x r-bcqeeo r-qvutc0']/span[text()[contains(., '@')]]")
        elif output_filename == REPLIES_FILENAME:
            usernames = driver.find_elements_by_xpath("//div[@class='css-1dbjc4n r-18u37iz r-1wbh5a2 r-1f6r7vd']/div/span")
        for username in usernames:
            try:
                username_text = username.get_attribute("innerHTML")+"\n"
                if ONLY_USERNAME:
                    username_text = username_text.split("@")[1]
                if username_text not in usernames_list:
                    usernames_list.append(username_text)
            except Exception as e:
                print("Error getting an username")
                print(e)
        driver.execute_script("window.scrollBy(0, 83)")
    if ONLY_USERNAME:
        output_filename="simple_"+output_filename
    with open(output_filename,"w") as retweets_file:
        retweets_file.write("Usernames\n")
        retweets_file.writelines(usernames_list)

if __name__ == '__main__':
    driver = webdriver.Chrome(DRIVER_PATH)
    driver.set_window_size(250, 1024)
    login_twitter(USERNAME, PASSWORD)
    driver.get(TWEET_URL)

    getUsernamesLikesOrRetweetsOrReply(REPLIES_FILENAME)


    retweets_url = TWEET_URL+"/"+"retweets"
    driver.get(retweets_url)
    sleep(3)
    getUsernamesLikesOrRetweetsOrReply(RETWEETS_FILENAME)

    retweets_url = TWEET_URL+"/"+"likes"
    driver.get(retweets_url)
    sleep(3)
    getUsernamesLikesOrRetweetsOrReply(LIKES_FILENAME)
