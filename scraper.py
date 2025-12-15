import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time


def get_data(contest_id: int):

    """

    Function that scrapes https://sports.yahoo.com/dailyfantasy/ to obtain the required information for lineup optimization.

    NB:

    :param contest_id: see contests here https://sports.yahoo.com/dailyfantasy/
    :return: a dataframe with the following columns:
                                                   - FullName
                                                   - Position
                                                   - Salary
                                                   - FPPG (average number of fantasy points)
                                                   - SD (standard deviation of fantasy points)
                                                   - Injury Status
    """

    # Obtain list of avaliable players as csv and save the meaningful columns

    columns_to_keep = ["ID", "First Name", "Last Name", "Position", "Salary", "FPPG", "Injury Status"]
    players_table = pd.read_csv(f'https://dfyql-ro.sports.yahoo.com/v2/export/contestPlayers?contestId={contest_id}')[columns_to_keep]
    players_table["SD"] = np.nan # create an empty column for the standard deviation



    while players_table["SD"].isnull().values.any() is True:

        url = f'https://sports.yahoo.com/dailyfantasy/contest/{contest_id}/setlineup'
        driver = webdriver.Chrome()
        driver.get(url)

        accept_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button"))
        )
        accept_button.click()

        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')

        time.sleep(10)

        table = driver.find_element(By.XPATH, '//*[@id="lineupSelection"]/div/div/div/table')

        time.sleep(10)

        rows = table.find_elements(By.CSS_SELECTOR, 'tr[data-tst^="player-row"]')

        time.sleep(10)

        for row in rows:
            player_id = row.get_attribute('data-tst-player-id')

            stddev = row.find_element(By.CSS_SELECTOR, 'span[data-tst="player-stddev"]').text

            players_table.loc[players_table["ID"] == player_id, "SD"] = float(
                stddev)  # match the correct SD to the correct player

    players_table['FullName'] = players_table['First Name'] + ' ' + players_table['Last Name']

    players_table.drop(['First Name', 'Last Name'], axis=1, inplace=True)


    players_table = players_table[(players_table['Injury Status'] != "INJ") & (players_table['Injury Status'] != "GTD") & (players_table['Injury Status'] != "O")].reset_index(drop=True)


    # players_table.to_csv(f'{contest_id}.csv', index=False) # going to add option to save it

    return players_table
