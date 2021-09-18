# This is a sample Python script.
# Importing the module
import json
import pandas as pd
import os
import glob
from bs4 import BeautifulSoup


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

filename = 'data/Evaluation Grid Evaluation1.html'
def scrape_player_page(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'lxml')
    all_t = soup.find_all("table")
    # table 1 is headers I think
    # table 2 is the data
    header_table = all_t[0]
    data_table = all_t[1]

    table_rows = header_table.find_all('th')
    l_h = []
    for th in table_rows:
        # for now I'm adding the table headers as data rows
        row = th.text.replace("\n", " ").strip()
        l_h.append(row)

    table_rows = data_table.find_all('tr')
    l = []
    for tr in table_rows:
        # for now I'm adding the table headers as data rows
        row = []
        td = tr.find_all('td')
        row = row + [tr.text.replace("\n", " ").strip() for tr in td]
        l.append(row)

    df = pd.DataFrame(l)
    df.columns = l_h[0:len(df.columns)]

    return df


def scrape_evaluation_grid(filename, group_text="Group"):
    with open(filename, 'r', encoding='utf-8') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'lxml')
    all_t = soup.find_all("table")

    table_rows = all_t[0].find_all('th')
    l_h = []
    for th in table_rows:
        # for now I'm adding the table headers as data rows
        row = th.text.replace("\n", " ").strip()
        l_h.append(row)


    dfs = []
    for tab in all_t:
        table_rows = tab.find_all('tr')
        l = []
        for tr in table_rows:
            row = []
            tds = tr.find_all('td')
            for td in tds:
                span = td.find_all("span")
                val = td.text.replace("\n", " ").strip()
                if len(val) == 0:
                    if not span:
                        row.append("")
                    else:
                        row.append(span[0].text)
                else:
                    val = td.text.replace("\n", " ").strip()
                    row.append(val)

            # row = row + [td.text.replace("\n", " ").strip() for td in tds]
            l.append(row)

        df = pd.DataFrame(l)
        df.columns = l_h[0:len(df.columns)]

        if "Player" in df.columns:
            f1 = df.Player.str.find("Skating") == -1
            df = df[f1].copy()

        x = tab.find_previous()
        index = 0

        while x.text.find(group_text) == -1:
            x = x.find_previous()
            if x is None:
                break
            index += 1
        df['skate_group'] = x.text
        dfs.append(df.copy())

    # collist = [list(df.columns)[-1]] + list(df.columns)[0:-1]
    return pd.concat(dfs)


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/


# walk a string and get the players

def get_quadrant_team_playersU15(input_str):
    input_list = input_str.split(" ")
    index = 0
    team_list = []
    for entry in input_list:

        if entry.isnumeric():
            _num = int(entry)
            _first = input_list[index + 1]
            _last = input_list[index + 2]
            _position = input_list[index + 3]

            if _first == "NWCAA":
                break

            if _first.isnumeric():
                pass
            else:
                team_list.append({'num': _num, 'firstname': _first, 'lastname': _last, 'position': _position})
        index += 1
    return pd.DataFrame(team_list)

filename = 'data/U15.xlsx'
quadrant_team_sheet = 'Sheet1'
master_sheet = 'U15 Raw'
master_quadrant_list = 'U15 Quadrants'
previous_team_sheet = 'Previous Team 2020'
df_u13_quad_sheet = 'U13 AA Teams'

df_quadrant_teams = pd.read_excel(filename, sheet_name=quadrant_team_sheet)
df_master = pd.read_excel(filename, sheet_name=master_sheet)
df_mquad = pd.read_excel(filename, sheet_name=master_quadrant_list)
df_previous = pd.read_excel(filename, sheet_name=previous_team_sheet)

df_quad_u13 = pd.read_excel(filename, sheet_name=df_u13_quad_sheet)

dfs = []
for index, row in df_quadrant_teams.iterrows():
    team = row['team']
    df = get_quadrant_team_playersU15(row['players'])
    df['team'] = team
    dfs.append(df)
df_all = pd.concat(dfs, axis=0)

left_columns = ['first', 'last']
right_columns = ['firstname', 'lastname']
df_quad_smha = df_mquad.merge(df_all, left_on=left_columns, right_on=right_columns, how='left')
f1 = df_quad_smha.team.isna()
collist = ['first', 'last', 'position', 'team']
df_quad_smha = df_quad_smha[~f1][collist].reset_index().copy()

df_master = df_master.merge(df_quad_smha[['first', 'last', 'team']], on=['first', 'last'], how='left')


def get_quadrant_team_playersU13(input_str):
    x = input_str
    index = 0
    list_x = x.split(" ")
    index = 0
    player_list = []
    while 1 == 1:
        # need to detect a space in their names
        _first = list_x[index]
        _last = list_x[index + 1]

        for t in range(2, 5):
            _position = list_x[index + t]
            if _position in ['Goaltender', 'Defensemen', 'Forward']:
                break
        if t != 2:
            _last = _last + " " + list_x[index + 2]
            index += 4
        else:
            index += 3

        player_list.append({"first": _first, "last": _last, "position": _position})
        if (list_x[index] == 'NWCAA') or (index > len(list_x) -3):
            break
    return pd.DataFrame(player_list)

dfs = []
for index, row in df_quad_u13.iterrows():
    team = row['team']
    df = get_quadrant_team_playersU13(row['players'])
    df['team'] = team
    dfs.append(df)
df_all_u13_quad = pd.concat(dfs, axis=0)

filename = 'data/U13.xlsx'
quadrant_team_sheet = 'U13 AA Teams'
master_sheet = 'U13 Raw'
master_quadrant_list = 'U13 Quadrants'
previous_team_sheet = 'Previous Team 2020'
df_u13_quad_sheet = 'U13 AA Teams'

df_quadrant_teams = pd.read_excel(filename, sheet_name=quadrant_team_sheet)
df_master = pd.read_excel(filename, sheet_name=master_sheet)
df_mquad = pd.read_excel(filename, sheet_name=master_quadrant_list)
df_previous = pd.read_excel(filename, sheet_name=previous_team_sheet)

df_quad_u13 = pd.read_excel(filename, sheet_name=df_u13_quad_sheet)



dfs = []
for index, row in df_quad_u13.iterrows():
    team = row['team']
    df = get_quadrant_team_playersU13(row['players'])
    df['team'] = team
    dfs.append(df)
df_all_u13_quad = pd.concat(dfs, axis=0)



left_columns = ['first', 'last']
right_columns = ['first', 'last']
df_quad_smha = df_mquad.merge(df_all_u13_quad, left_on=left_columns, right_on=right_columns, how='left')
f1 = df_quad_smha.team.isna()
collist = ['first', 'last', 'position', 'team']
df_quad_smha = df_quad_smha[~f1][collist].reset_index().copy()

df_master = df_master.merge(df_quad_smha[['first', 'last', 'team', 'position']], on=['first', 'last'], how='left')
f_quad = df_master.team.isna()
collist = ['first', 'last', 'team', 'position']
df_master[~f_quad][collist].to_csv('data/still_in_quadrants.csv', index=False)

