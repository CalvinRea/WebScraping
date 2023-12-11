from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common import exceptions as ex
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import copy

# The code below should be used to reset the system if the state.json gets messed up
# [[], 2, 2, [3], "https://www.takealot.com/all"]


with open("WebScrapper/categories.json", "r") as f:
    data = json.load(f)

with open("WebScrapper/state.json", "r") as f:
    state = json.load(f)
    categoriser = state[0]
    max_depth = state[1]
    depth = state[2]
    rows = state[3]
    link = state[4]

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument(
    '--blink-settings=imagesEnabled=false')  # disables image loading
chrome_options
driver = webdriver.Chrome(
    ChromeDriverManager().install(), chrome_options=chrome_options)
driver.get(link)
driver.fullscreen_window()

time.sleep(1)

# clicks accept cookies
driver.find_element(
    By.XPATH, "/html/body/div[1]/div[1]/div/div/button").click()


def click_see_more(location):

    try:
        driver.find_element(By.XPATH, location).click()

    except ex.NoSuchElementException:
        pass

    except ex.ElementClickInterceptedException:
        pass

    except ex. StaleElementReferenceException:
        time.sleep(2)

        try:
            driver.find_element(By.XPATH, location).click()
        except ex.NoSuchElementException:
            pass


# The code below performs a DFS through all of takealot's product catalogue except the book section
while (True):

    see_more_location = "/html/body/div[1]/div[4]/div[3]/div[1]/div/div[1]/div[3]/button"
    general_location = "/html/body/div[1]/div[4]/div[3]/div[1]/div/div[1]/div[2]/div/div/div/a"

    if (depth == 2):
        general_location = "/html/body/div[1]/div[4]/div[2]/div[1]/div/div[1]/div[2]/div/div/div/a"
        see_more_location = "/html/body/div[1]/div[4]/div[2]/div[1]/div/div[1]/div[3]/button"

    click_see_more(see_more_location)
    time.sleep(0.3)

    try:
        if (depth > max_depth):
            max_depth = depth
            rows.append(depth)

        current_elem = driver.find_element(
            By.XPATH, general_location+"["+str(rows[depth-2])+"]")
        href = current_elem.get_attribute("href")
        name = current_elem.text

        categoriser.append(name)

        data.update({name: (copy.deepcopy(categoriser), href)})

        rows[depth-2] += 1

        try:
            current_elem.click()
        except ex.StaleElementReferenceException:
            time.sleep(2)
            current_elem = driver.find_element(
                By.XPATH, general_location+"["+str(rows[depth-2])+"]")
            current_elem.click()
        except ex.ElementClickInterceptedException:
            time.sleep(2)
            click_see_more(see_more_location)
            time.sleep(0.3)
            current_elem = driver.find_element(
                By.XPATH, general_location+"["+str(rows[depth-2])+"]")
            current_elem.click()

        time.sleep(2)
        depth += 1

        with open('WebScrapper/categories.json', 'w') as json_file:
            json.dump(data, json_file)

        with open('WebScrapper/state.json', 'w') as json_file:
            json.dump([categoriser, max_depth,
                      depth, rows, href], json_file)

    except ex.NoSuchElementException:
        if (depth == 2):  # breaks if no element is found on first level, hence last element has been clicked
            break

        categoriser.pop()
        max_depth -= 1
        rows.pop()

        back_one_elem = driver.find_element(
            By.XPATH, general_location+"["+str(depth-2)+"]")

        try:
            back_one_elem.click()
        except ex.StaleElementReferenceException:
            time.sleep(2)
            back_one_elem = driver.find_element(
                By.XPATH, general_location+"["+str(depth-2)+"]")
            back_one_elem.click()
        except ex.ElementClickInterceptedException:
            time.sleep(2)
            click_see_more(see_more_location)
            time.sleep(0.3)
            back_one_elem = driver.find_element(
                By.XPATH, general_location+"["+str(depth-2)+"]")
            back_one_elem.click()

        time.sleep(2)
        depth -= 1
