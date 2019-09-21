import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from config import *

def getGoogleSheet(spreadsheet_id):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPES)
    client = gspread.authorize(credentials)
    g_sheet = client.open_by_key(spreadsheet_id)
    return g_sheet


def gSheetToDf(g_worksheet):
    all_values = g_worksheet.get_all_values()
    header = all_values[0]
    values = all_values[1:]
    if not values:
        print('No han sido almacenados los datos de las peliculas en la Google Sheet')
    else:
        all_data = []
        for col_id, col_name in enumerate(header):
            column_data = []
            for row in values:
                column_data.append(row[col_id])
            series = pd.Series(data=column_data, name=col_name)
            all_data.append(series)
        df = pd.concat(all_data, axis=1)
        return df
