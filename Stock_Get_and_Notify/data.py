import requests
import pandas as pd
import datetime as dt
import os
from dotenv import load_dotenv

load_dotenv(verbose=True)

url_data = "https://api.finmindtrade.com/api/v4/data"
url_snapshot = "https://api.finmindtrade.com/api/v4/taiwan_stock_tick_snapshot"

token = os.getenv("TOKEN")


def get_tw_stock_info(token_obtained):
    """Get TW Stocks Information"""
    data_param = {
        "dataset": "TaiwanStockInfo",
        "token": token_obtained,
    }
    tw_stock_data = requests.get(url_data, params=data_param)
    tw_stock_data = pd.DataFrame(tw_stock_data.json()["data"])
    return tw_stock_data


def check_gsheet_stock_id(sheet_stocks_interested, tw_stock_data):
    """Check the stock ids on the Google sheet are correct"""
    # Generate a new list only containing the stock id of stock interested
    stocks_entered = sheet_stocks_interested["Stock Number"].tolist()
    stocks_id_list = tw_stock_data["stock_id"].tolist()
    stocks_name_list = tw_stock_data["stock_name"].tolist()
    stocks_id_name_combined = dict(zip(stocks_id_list, stocks_name_list))

    wrong_stock_id_list = []
    stock_full_name_dic = {}
    for i in range(len(stocks_entered)):
        if stocks_entered[i] not in stocks_id_name_combined.keys():
            wrong_stock_id_list.append(stocks_entered[i])
        else:
            stock_full_name_dic[stocks_entered[i]] = stocks_id_name_combined[
                stocks_entered[i]
            ]
    return wrong_stock_id_list, stock_full_name_dic, stocks_entered


def get_newest_stock_historical_price(
    operating_status: dict, stocks_entered, token_obtained, days=120
):
    """Get the newest stock historical  data and Export a csv file. The default time interval is 120 days"""
    today = dt.date.today()
    specified_date = today - dt.timedelta(days=days)

    df_combined_historical_price = pd.DataFrame(
        columns=[
            "stock_id",
            "date",
            "Trading_Volume",
            "Trading_money",
            "open",
            "close",
            "max",
            "min",
            "spread",
            "Trading_turnover",
        ]
    )
    params = {
        "dataset": "TaiwanStockPrice",
        "start_date": specified_date,
        "end_date": today,
        "token": token_obtained,
    }

    for stock_id in stocks_entered:
        params["data_id"] = stock_id
        stock_historical_data = requests.get(url_data, params=params).json()
        stock_historical_data = pd.DataFrame(stock_historical_data["data"])
        stock_historical_data["stock_id"] = stock_historical_data["stock_id"].astype(
            str
        )
        df_combined_historical_price = pd.concat(
            [df_combined_historical_price, stock_historical_data], ignore_index=True
        )

    df_combined_historical_price["stock_id"] = df_combined_historical_price[
        "stock_id"
    ].astype(str)

    df_combined_historical_price.to_csv("../Data/Historical Price.csv")
    operating_status["get_newest_historical_data"] = "success"

    return operating_status


def get_newest_stock_realtime_price(
    operating_status: dict, stocks_entered, token_obtained
):
    """Get the newest stock realtime data and Export a csv file"""
    today = dt.date.today()
    df_combined_realtime_price = pd.DataFrame(
        columns=[
            "stock_id",
            "date",
            "amount",
            "average_price",
            "high",
            "low",
            "buy_price",
            "buy_volume",
            "sell_price",
            "sell_volume",
            "change_price",
            "change_rate",
            "close",
            "open",
            "total_amount",
            "total_volume",
            "volume",
            "volume_ratio",
            "yesterday_volume",
            "TickType",
        ]
    )
    params = {
        "dataset": "TaiwanStockPrice",
        "start_date": today,
        "data_id": stocks_entered,
        "token": token_obtained,
    }

    stock_realtime_data = requests.get(url_snapshot, params=params).json()
    stock_realtime_data = pd.DataFrame(stock_realtime_data["data"])
    stock_realtime_data["stock_id"] = stock_realtime_data["stock_id"].astype(str)
    df_combined_realtime_price = pd.concat(
        [df_combined_realtime_price, stock_realtime_data], ignore_index=True
    )
    df_combined_realtime_price["stock_id"] = df_combined_realtime_price[
        "stock_id"
    ].astype(str)

    df_combined_realtime_price.to_csv("..Data/Realtime Price.csv")
    operating_status["get_newest_realtime_data"] = "success"

    return operating_status


if __name__ == "__main__":
    pass
