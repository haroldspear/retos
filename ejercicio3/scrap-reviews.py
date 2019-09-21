from config import *
from selenium import webdriver
import csv

driver = None

def formatReview(rate, review_comment, date, user_id, user_about):
    review_comment = review_comment.replace("\t"," ")
    review_comment = review_comment.replace("\r"," ")
    review_comment = review_comment.replace("\n"," ")
    review_comment = review_comment.replace(","," ")
    user_about = user_about.replace("\t"," ")
    user_about = user_about.replace("\r"," ")
    user_about = user_about.replace("\n"," ")
    user_about = user_about.replace(","," ")
    review = {}
    review[RATE] = rate
    review[REVIEW] = review_comment
    review[DATE] = date
    review[USER_ID] = user_id
    review[USER_ABOUT] = user_about

    return review

if __name__ == '__main__':
    driver = webdriver.Chrome(DRIVER_PATH)
    driver.get(SCRAP_URL)
    reviews_url = driver.find_element_by_xpath("//div[@id='reviews-medley-footer']/div/a").get_attribute("href")
    try:
        with open(OUTPUT_FILE, 'w', encoding = "utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=OUTPUT_COLUMNS)
            writer.writeheader()
            last_page = False
            while not last_page:
                driver.get(reviews_url)
                reviews = driver.find_elements_by_xpath("//div[@class='a-section review aok-relative']/div/div")
                reviewId = None
                rates = []
                review_comments = []
                dates = []
                user_ids = []
                users_urls = []

                try:
                    next_page_url = driver.find_element_by_xpath("//li[@class='a-last']/a").get_attribute("href")
                    reviews_url = next_page_url
                except:
                    try:
                        next_page_url = driver.find_element_by_xpath("//li[@class='a-disabled a-last']")
                        last_page = True
                    except:
                        print("Error to get next page")
                get_user = True
                for review in reviews:
                    try:
                        reviewId = review.get_attribute("id")
                        rate = review.find_element_by_xpath("div[@class='a-row']/a[@class='a-link-normal']").get_attribute("title")
                        review_comment = review.find_element_by_xpath("div[@class='a-row a-spacing-small review-data']/span/span").text
                        date = review.find_element_by_xpath("span").text
                        user_url = review.find_element_by_xpath("div[@class='a-row a-spacing-mini']/a[@class='a-profile']").get_attribute("href")
                        user_id = user_url.split("profile/")[1].split("/")[0]

                        users_urls.append(user_url)
                        rates.append(rate)
                        review_comments.append(review_comment)
                        dates.append(date)
                        user_ids.append(user_id)
                    except:
                        get_user=False
                        print("Error obteniendo una review")
                if get_user:
                    for user_url in users_urls:
                        try:
                            driver.get(user_url)
                            user_about = driver.find_element_by_xpath("//div[@class='desktop padded card']/div[@class='a-row']/div[@class='a-section']").text
                            review_data = formatReview(rates.pop(0), review_comments.pop(0), dates.pop(0), user_ids.pop(0), user_about)
                            writer.writerow(review_data)
                        except:
                            print("Error obteniendo info de un usuario")

    except Exception as e:
        print("Error to get a review", reviewId)
        print(e)
