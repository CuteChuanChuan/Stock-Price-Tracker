import requests
import pygsheets
import os
from dotenv import load_dotenv

load_dotenv(verbose=True)

FINMIND_ACCOUNT = os.getenv("FINMIND_ACCOUNT")
FINMIND_PASSWORD = os.getenv("FINMIND_PASSWORD")

url_sheet = os.getenv("URL_SHEET")
url_login = "https://api.finmindtrade.com/api/v4/login"

login_param = {
    "user_id": FINMIND_ACCOUNT,
    "password": FINMIND_PASSWORD,
}


def login_finmind():
    """Login FinMind and Get Token for Further Using"""
    operating_status = {}
    connection = requests.post(url_login, data=login_param).json()
    operating_status["login_finmind"] = connection["msg"]
    return [operating_status, connection]


def connect_gsheets(operating_status: dict):
    """Login Google and Access the Sheets Containing Stocks Interested and Historical Price"""
    gc = pygsheets.authorize(service_account_file=os.getenv("JSON_FILE_PATH"))
    sh = gc.open_by_url(url_sheet)

    sheet_interested_stock_list = sh.worksheet_by_title("Setting")
    df_stocks_interested = sheet_interested_stock_list.get_as_df(
        has_header=True, index_column=False, numerize=False
    )
    df_stocks_interested.to_csv("..Data/Google Sheet - Stocks Interested.csv")
    operating_status["gsheet_interested_list"] = "success"

    sheet_stock_historical_price = sh.worksheet_by_title("Historical Price")
    df_stock_historical_price = sheet_stock_historical_price.get_as_df(
        has_header=True, index_column=False, numerize=False
    )
    operating_status["gsheet_historical_price"] = "success"

    return [operating_status, df_stocks_interested, df_stock_historical_price]


if __name__ == "__main__":
    login_results = login_finmind()
    connect_results = connect_gsheets(login_results[0])
