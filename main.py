import requests
from bs4 import BeautifulSoup
import pandas as pd


def main():
    # the page rejects GET requests if requests does not identify as a User-Agent
    header = {'User-Agent': '...'}
    abv = ['atl']
    # URL FOR THE FIRST TEAM
    url = 'https://www.espn.com/nba/team/stats/_/name/' + abv[0]
    request = requests.get(url, headers=header).text
    soup = BeautifulSoup(request, 'html.parser')
    # OBTAIN THE ABBREVIATION VALUE FOR THE OTHER TEAM TO THEN WEBSCRAPE
    for option in soup.find_all('option', class_='dropdown__option')[:30]:
        if 'data-param-value' in option.attrs:
            # print("Abv: ", option['data-param-value'])
            abv.append(option['data-param-value'])
    # INITIALIZE A LIST TO STORE PLAYER STATISTICS DATAFRAMES
    df_player_list = []
    # INITIALIZE A LIST TO STORE SHOOTING STATISTICS DATAFRAMES
    df_shooting_list = []
    # LOOP THROUGH EACH TEAM ABBREVIATION TO SCRAPE DATA
    for x in abv:
        url = 'https://www.espn.com/nba/team/stats/_/name/' + x
        request = requests.get(url, headers=header).text
        soup = BeautifulSoup(request, 'html.parser')
        # USE TABLE TO FIND NAMES AND STATS
        # INDEX [0] FOR NAMES ON TABLE 1 ----- INDEX [1] FOR STATS ON TABLE 1
        # INDEX [3] FOR STATS ON TABLE 2
        names_table_1 = soup.find_all('table')[0]
        stats_table_1 = soup.find_all('table')[1]
        stats_table_2 = soup.find_all('table')[3]
        # EXTRACT TITLES AND DATA FROM TABLES
        titles_data_1 = stats_table_1.find_all('th')
        titles_1 = [t.text for t in titles_data_1]

        names_data_1 = names_table_1.find_all('td')[:-1]
        position_data = names_table_1.find_all('span', class_="font10")
        player_position = [pos.text for pos in position_data]
        names = [n.text.rsplit(' ', 1)[0] for n in names_data_1]
        titles_data_2 = stats_table_2.find_all('th')
        titles_2 = [t.text for t in titles_data_2]

        team_name = soup.find_all('h1')[1].text.split('Stats')[0]
        # CREATE DICTIONARY FOR PLAYER STATS
        df_dict_player = {}
        column_data = stats_table_1.find_all('tr')
        for row in column_data[1:-1]:
            row_data = row.find_all('td')
            in_row_data = [r.text for r in row_data]
            for index, key in enumerate(titles_1):
                if key in df_dict_player:
                    df_dict_player[key].append(in_row_data[index])
                else:
                    df_dict_player[key] = [in_row_data[index]]
        # CONVERT DICTIONARY TO DATAFRAMES
        df_player_stats = pd.DataFrame.from_dict(df_dict_player)
        df_player_stats['PLAYERS'] = names
        df_player_stats['POS'] = player_position
        df_player_stats.insert(0, 'TEAM', team_name)
        df_player_list.append(df_player_stats)
        # CREATE DICTIONARY FOR SHOOTING STATS
        df_dict_shooting = {}
        column_data = stats_table_2.find_all('tr')
        for row in column_data[1:-1]:
            row_data = row.find_all('td')
            in_row_data = [r.text for r in row_data]
            for index, key in enumerate(titles_2):
                if key in df_dict_shooting:
                    df_dict_shooting[key].append(in_row_data[index])
                else:
                    df_dict_shooting[key] = [in_row_data[index]]
        # CONVERT DICTIONARY TO DATAFRAME
        df_shooting_stats = pd.DataFrame.from_dict(df_dict_shooting)
        df_shooting_stats['PLAYERS'] = names
        df_shooting_stats.insert(0, 'TEAM', team_name)
        df_shooting_list.append(df_shooting_stats)
    # COMBINE PLAYER STATISTICS DATAFRAMES
    df_combined_player = pd.concat(df_player_list)
    print(df_combined_player)
    # COMBINE SHOOTING STATISTICS DATAFRAMES
    df_combined_shooter = pd.concat(df_shooting_list)
    print(df_combined_shooter)

    # SAVE DATAFRAME TO CSV FILE
    df_combined_player.to_csv(r'E:\csvOutput\NBA_2023_2024_player_stats_df.csv', index=False)
    df_combined_shooter.to_csv(r'E:\csvOutput\NBA_2023_2024_shooting_stats_df.csv', index=False)


main()
