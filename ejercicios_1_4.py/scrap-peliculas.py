from config import *
from selenium import webdriver
from selenium.webdriver import ActionChains
from manage_peliculas import getGoogleSheet, gSheetToDf
import argparse
import sys

driver = None

def setFormatMovie(genre, name, description, ranking, download_url_1, download_url_2, download_url_3):
    description = description.replace("\t"," ")
    description = description.replace("\r"," ")
    description = description.replace("\n"," ")
    description = description.replace(","," ")
    name = name.rstrip()
    movie = []
    movie.append(genre)
    movie.append(name)
    movie.append(description)
    movie.append(ranking)
    movie.append(download_url_1)
    movie.append(download_url_2)
    movie.append(download_url_3)

    return movie


def getMovieInfo(movie_url, genre_name):
    actionChains = ActionChains(driver)
    try:
        driver.get(movie_url)
    except:
        driver.execute_script("window.stop();")
    name=DEFAULT_NAME
    description=DEFAULT_DESCRIPTION
    try:
        name = driver.find_element_by_xpath("//div[@class='single_left']/h1").text
    except:
        name=DEFAULT_NAME
        print("No se pudo obtener el nombre de la película")
    try:
        description = driver.find_elements_by_xpath("//div[@class='single_left']/table/tbody/tr/td")[1]
        description = description.find_elements_by_tag_name("p")[0].text
    except:
        description=DEFAULT_NAME
        print("No se pudo obtener la descripción de la película")
    try:
        ranking = driver.find_element_by_xpath("//div[@id='imdb-box']/a").text
    except:
        ranking = DEFAULT_RANK
    get_urls=True
    try:
        download_tags_a = driver.find_elements_by_xpath("//div[@id='panel_descarga']/ul/a")
        for download_tag_a in download_tags_a:
            actionChains.move_to_element(download_tag_a.find_element_by_tag_name("li"))
            actionChains.context_click()
        actionChains.perform()
    except:
        get_urls=False
    download_url_1 = " "
    download_url_2 = " "
    download_url_3 = " "
    if get_urls:
        download_urls = []
        for download_tag_a in download_tags_a:
            download_url = download_tag_a.get_attribute("href")
            download_urls.append(download_url)

        download_url_1 = " "
        download_url_2 = " "
        download_url_3 = " "

        for download_url in download_urls:
            if not download_url.startswith(PAGE_URL_BASE+"protect/") and not download_url.startswith(PAGE_URL_BASE+"vip/"):
                if DOWNLOAD_URL_1 in download_url:
                    download_url_1 = download_url
                elif DOWNLOAD_URL_2 in download_url:
                    download_url_2 = download_url
                elif DOWNLOAD_URL_3 in download_url:
                    download_url_3 = download_url
            elif download_url.startswith(PAGE_URL_BASE+"protect/"):
                try:
                    driver.get(download_url)
                except:
                    driver.execute_script("window.stop();")
                try :
                    download_url_clean = driver.find_element_by_xpath("//div[@id='texto']/div/a").get_attribute("href")
                    if DOWNLOAD_URL_1 in download_url_clean:
                        download_url_1 = download_url_clean
                    elif DOWNLOAD_URL_2 in download_url_clean:
                        download_url_2 = download_url_clean
                    elif DOWNLOAD_URL_3 in download_url_clean:
                        download_url_3 = download_url_clean
                except:
                    print("No hay una url en el link protegido")

    movie = setFormatMovie(genre_name, name, description, ranking, download_url_1, download_url_2, download_url_3)

    return movie


def getMoviesUrls(genre_url):
    try:
        driver.get(genre_url)
    except:
        driver.execute_script("window.stop();")
    last_page = None
    movies_urls = []
    try:
        last_page = driver.find_element_by_xpath("//div[@class='wp-pagenavi']/a[@class='last']")
    except:
        if last_page == None:
            last_page = driver.find_elements_by_xpath("//div[@class='wp-pagenavi']/a[@class='page larger']")[-1]
    last_page = int(last_page.get_attribute("href").split("/")[-2])

    for page in range(last_page):
        get_movies_urls = True
        try:
            movies_in_page = [movie.get_attribute("href") for movie in driver.find_elements_by_xpath("//div[contains(@class, 'home_post_cont')]/a")]
        except:
            get_movies_urls = False
        if get_movies_urls:
            movies_urls.extend(movies_in_page)
        if page < last_page - 1 :
            next_page_url = driver.find_element_by_xpath("//div[@class='wp-pagenavi']/a[@class='nextpostslink']").get_attribute("href")
            try:
                driver.get(next_page_url)
            except:
                driver.execute_script("window.stop();")

    return movies_urls

def getGenresUrls(genres_filename):
    genres_to_scrap = []
    with open(genres_filename, encoding="utf-8") as genres_file:
        genres_to_scrap = [line.rstrip() for line in genres_file]
    try:
        driver.get(PAGE_URL)
    except:
        driver.execute_script("window.stop();")
    all_genres = {genre.text:genre.find_element_by_tag_name("a").get_attribute("href") for genre in driver.find_elements_by_xpath("//ul[@id='menu-menu']/li")}
    genres = {}

    for genre_name,genre_url in all_genres.items():
        if genre_name in genres_to_scrap:
            genres[genre_name] = genre_url

    return genres

def getTop50(g_sheet):
    g_worksheet = g_sheet.sheet1
    movies_df = gSheetToDf(g_worksheet)
    by_genre = movies_df.groupby([GENRE])
    print(" TOP 50 PELICULAS POR GENERO ".center(100,"="))
    try:
        top50_worksheet = g_sheet.worksheet(TOP_50_WS_TITLE)
        g_sheet.del_worksheet(top50_worksheet)
    except:
        print("First Time")
    g_sheet.add_worksheet(TOP_50_WS_TITLE, 1000, 20)
    top50_worksheet = g_sheet.worksheet(TOP_50_WS_TITLE)
    row_header = [NAME,DESCRIPTION,RANKING,DOWNLOAD_SITE_1,DOWNLOAD_SITE_2,DOWNLOAD_SITE_3]
    row_index = HEADER_INDEX
    for key, item in by_genre:
        by_genre_df = by_genre.get_group(key)
        print("\n"+GENRE+": ", key)

        row_genre = [" ",GENRE+":", key, " "]
        top50_worksheet.insert_row(row_genre, row_index)
        row_index+=1
        top50_worksheet.insert_row(row_header, row_index)
        row_index+=1

        by_genre_df=by_genre_df[(by_genre_df[RANKING] != DEFAULT_RANK) & (by_genre_df[RANKING] != NO_VOTES) & (by_genre_df[RANKING].str.contains("/10"))]
        by_genre_df[RANKING_VALUE] = by_genre_df.apply(lambda L: float(L.Ranking.split("/")[0]), axis=1)
        by_genre_df = by_genre_df.nlargest(50, RANKING_VALUE)[[NAME,DESCRIPTION,RANKING,DOWNLOAD_SITE_1,DOWNLOAD_SITE_2,DOWNLOAD_SITE_3]]

        row_index_last=row_index
        row_index+=int(by_genre_df.shape[0])

        cell_list = top50_worksheet.range('A'+str(row_index_last)+':F'+str(row_index))
        cell_index = 0
        for index, row in by_genre_df.iterrows():
            for row_i in range(len(row)):
                if row_i == 0 :
                    cell_list[cell_index].value = row[NAME]
                elif row_i == 1 :
                    cell_list[cell_index].value = row[DESCRIPTION]
                elif row_i == 2 :
                    cell_list[cell_index].value = row[RANKING]
                elif row_i == 3 :
                    cell_list[cell_index].value = row[DOWNLOAD_SITE_1]
                elif row_i == 4 :
                    cell_list[cell_index].value = row[DOWNLOAD_SITE_2]
                elif row_i == 5 :
                    cell_list[cell_index].value = row[DOWNLOAD_SITE_3]
                cell_index+=1

        top50_worksheet.update_cells(cell_list)
        row_index+=1

        print(by_genre_df.to_string(index=False))

        by_genre_df.to_csv("data/"+key+"_"+"top50"+".csv", index=None)

def getTop15DetailedDescription(g_sheet):
    g_worksheet = g_sheet.sheet1
    movies_df = gSheetToDf(g_worksheet)
    try:
        topdescription_worksheet = g_sheet.worksheet(TOP_DETAILED_DESCRIPTION)
        g_sheet.del_worksheet(topdescription_worksheet)
    except:
        print("First Time")
    g_sheet.add_worksheet(TOP_DETAILED_DESCRIPTION, 1000, 20)
    topdescription_worksheet = g_sheet.worksheet(TOP_DETAILED_DESCRIPTION)
    row_title = ["Top 15 Descripcciones Detalladas","",""]
    topdescription_worksheet.insert_row(row_title, 1)
    row_header = [NAME,DESCRIPTION,DESCRIPTION_SIZE]

    movies_df[DESCRIPTION_SIZE] = movies_df.apply(lambda L: int(len(L[DESCRIPTION])), axis=1)
    movies_df = movies_df.nlargest(15, DESCRIPTION_SIZE)[[NAME,DESCRIPTION,DESCRIPTION_SIZE]]
    row_index = HEADER_INDEX+1
    topdescription_worksheet.insert_row(row_header, row_index)
    row_index+=1

    cell_list = topdescription_worksheet.range('A'+str(row_index)+':C'+str(row_index+15))
    cell_index = 0
    for index, row in movies_df.iterrows():
        for row_i in range(len(row)):
            if row_i == 0 :
                cell_list[cell_index].value = row[NAME]
            elif row_i == 1 :
                cell_list[cell_index].value = row[DESCRIPTION]
            elif row_i == 2 :
                cell_list[cell_index].value = row[DESCRIPTION_SIZE]
            cell_index+=1

    topdescription_worksheet.update_cells(cell_list)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Hace scrap de peliculas en la page cinecalidad')
    parser.add_argument('-a', '--action', dest='action', help='Opciones: [scrap, top50, both, top15Detailed]', default="scrap")
    args = parser.parse_args(sys.argv[1:])
    if args.action =="scrap" or args.action =="both":
        driver = webdriver.Chrome(DRIVER_PATH)
        driver.set_page_load_timeout(3)
        try:
            genres = getGenresUrls(DATA_FILENAME)
        except Exception as e:
            print(e)
        genres_movies = {}
        try :
            for genre_name, genre_url in genres.items():
                movies = getMoviesUrls(genre_url)
                genres_movies[genre_name] = movies

            g_sheet = getGoogleSheet(SPREADSHEET_ID)
            g_worksheet = g_sheet.sheet1
            g_worksheet.clear()
            movie_info_header = setFormatMovie(GENRE, NAME, DESCRIPTION, RANKING, DOWNLOAD_SITE_1, DOWNLOAD_SITE_2, DOWNLOAD_SITE_3)
            row_index = HEADER_INDEX
            g_worksheet.insert_row(movie_info_header, row_index)
            for genre_name, movies_urls in genres_movies.items():
                for movie_url in movies_urls:
                    row_index+=1
                    movie_info = getMovieInfo(movie_url, genre_name)
                    g_worksheet.insert_row(movie_info, row_index)

        except Exception as e:
            print(e)
    if args.action == "top50" or args.action == "both":
        g_sheet = getGoogleSheet(SPREADSHEET_ID)
        getTop50(g_sheet)

    if args.action == "top15Detailed":
        g_sheet = getGoogleSheet(SPREADSHEET_ID)
        getTop15DetailedDescription(g_sheet)
