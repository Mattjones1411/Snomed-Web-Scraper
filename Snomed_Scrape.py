from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from time import sleep
import pandas as pd
import tqdm
import os
import csv

term = 'Diabetes'
driver = webdriver.Chrome()

driver.get('https://termbrowser.nhs.uk/?')
sleep(4)
driver.find_element_by_id('accept-license-button-modal').click()
driver.find_element_by_xpath('//*[@id="welcome-perspective"]/div/p[6]/a[1]').click()
driver.find_element_by_xpath('//a[@href="#fh-search_canvas"]').click()

WebDriverWait(driver, 10).until(
    ec.visibility_of_element_located((By.XPATH, '//*[@id="fh-search_canvas-searchConfigBar"]/div[2]/button'))).click()
driver.find_element_by_id('fh-search_canvas-activeInactiveButton').click()

driver.find_element_by_xpath('//input[@id="fh-search_canvas-searchBox"]').send_keys(term)

driver.find_element_by_id('fh-cd1_canvas-configButton').click()
checkbox_one = WebDriverWait(driver, 10).until(
    ec.visibility_of_element_located((By.ID, 'fh-cd1_canvas-displayIdsOption')))
if not checkbox_one.is_selected():
    checkbox_one.click()

driver.find_element_by_id('fh-cd1_canvas-apply-button').click()

checkbox_two = WebDriverWait(driver, 10).until(
    ec.visibility_of_element_located((By.ID, 'fh-search_canvas-groupConcept')))
if not checkbox_two.is_selected():
    checkbox_two.click()

while True:
    try:
        men_menu = WebDriverWait(driver, 10).until(
            ec.visibility_of_element_located((By.ID, 'fh-search_canvas-more')))
        ActionChains(driver).move_to_element(men_menu).perform()
        men_menu.click()
    except TimeoutException:
        break

if type(term) == list:
    file_name = input('What would you like the file to be/is the file called? ')
    table = driver.find_element_by_id('fh-search_canvas-resultsTable')
    results = table.find_elements(By.TAG_NAME, "tr")
    output = []
    start_index = 0
    internal_index = 0
    csv_file_name = f'{file_name}.csv'
    write_mode = 'w'

    if os.path.isfile(f'{file_name}.csv'):
        file = pd.read_csv(f'{file_name}.csv', encoding='latin1')
        df = pd.DataFrame(file.iloc[-1:, -1:].values)
        start_index = df.iat[-1, 4] + 1
        internal_index = df.iat[-1, 6]
        write_mode = 'a'

    with tqdm.tqdm(total=len(term) - start_index - 1) as pbar, open(csv_file_name, write_mode, newline='') as file:
        writer = csv.writer(file)
        for item in term[start_index:-1]:
            for result in results[internal_index]:
                result.find_element_by_xpath('.//td[1]/div/a').click()
                while True:
                    try:
                        concept_id = result.find_element_by_xpath('.//td[1]/div').get_attribute('data-concept-id')
                        details = WebDriverWait(driver, 10).until(
                            ec.visibility_of_element_located((By.XPATH, '//*[@href="#details-fh-cd1_canvas"]')))
                        ActionChains(driver).move_to_element(details).perform()
                        details.click()
                        while True:
                            try:
                                result_pane = WebDriverWait(driver, 10).until(
                                    ec.visibility_of_element_located(
                                        (By.XPATH, '//*[@id="fh-cd1_canvas-descriptions-panel"]')))
                                result_tables = result_pane.find_elements(By.TAG_NAME, "table")
                                for table in result_tables:
                                    rows = table.find_elements_by_xpath('.//tbody/tr')
                                    for row in rows:
                                        description_name = row.find_element_by_xpath('.//td[1]').text.replace('&nbsp;',
                                                                                                              '')[
                                                           4:].lstrip()
                                        description_id = row.find_element_by_xpath('.//td[2]').text
                                        preferred = row.find_element_by_xpath('.//td[3]').text.replace('&nbsp;',
                                                                                                       '').lstrip()
                                        index = term.index(item)
                                        item_index = results.index(result)
                                        output = [concept_id, description_name, description_id, preferred, index, term,
                                                  item_index]
                                        writer.writerow(output)
                                break
                            except TimeoutException:
                                sleep(60)
                                details.click()
                        break
                    except TimeoutException:
                        sleep(60)
                        result.find_element_by_xpath('.//td[1]/div/a').click()
            pbar.update()
        driver.close()
        file.close()

else:
    table = driver.find_element_by_id('fh-search_canvas-resultsTable')
    results = table.find_elements(By.TAG_NAME, "tr")
    output = []
    start_index = 0
    csv_file_name = f'{term}.csv'
    write_mode = 'w'

    if os.path.isfile(f'{term}.csv'):
        file = pd.read_csv(f'{term}.csv', encoding='latin1')
        df = pd.DataFrame(file.iloc[-1:, -1:].values)
        start_index = df.iat[0, 0] + 1
        write_mode = 'a'

    with tqdm.tqdm(total=len(results) - start_index - 1) as pbar, open(csv_file_name, write_mode, newline='') as file:
        writer = csv.writer(file)
        for result in results[start_index:-1]:
            result.find_element_by_xpath('.//td[1]/div/a').click()
            while True:
                try:
                    concept_id = result.find_element_by_xpath('.//td[1]/div').get_attribute('data-concept-id')
                    details = WebDriverWait(driver, 10).until(
                        ec.visibility_of_element_located((By.XPATH, '//*[@href="#details-fh-cd1_canvas"]')))
                    ActionChains(driver).move_to_element(details).perform()
                    details.click()
                    while True:
                        try:
                            result_pane = WebDriverWait(driver, 10).until(
                                ec.visibility_of_element_located((By.XPATH, '//*[@id="fh-cd1_canvas-descriptions'
                                                                            '-panel"]')))
                            result_tables = result_pane.find_elements(By.TAG_NAME, "table")
                            for table in result_tables:
                                rows = table.find_elements_by_xpath('.//tbody/tr')
                                for row in rows:
                                    description_name = row.find_element_by_xpath('.//td[1]').text.replace('&nbsp;', '')[
                                                       4:].lstrip()
                                    description_id = row.find_element_by_xpath('.//td[2]').text
                                    preferred = row.find_element_by_xpath('.//td[3]').text.replace('&nbsp;', '').lstrip(
                                    )
                                    index = results.index(result)
                                    output = [concept_id, description_name, description_id, preferred, index]
                                    writer.writerow(output)
                            break
                        except TimeoutException:
                            sleep(60)
                            details.click()
                    break
                except TimeoutException:
                    sleep(60)
                    result.find_element_by_xpath('.//td[1]/div/a').click()
            pbar.update()
        driver.close()
        file.close()
