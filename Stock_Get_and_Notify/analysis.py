import pandas as pd
import numpy as np
import pygsheets
import os
from dotenv import load_dotenv

load_dotenv(verbose=True)

url_sheet = os.getenv("URL_SHEET")


def compute_historical_data(operating_status: dict):
    """Use the newest stock historical data to compute additional information and then export a csv file"""
    all_historical_data = pd.read_csv(
        "..Data/Historical Price.csv",
        converters={"stock_id": lambda x: str(x)},
        index_col=0,
    )

    # ToDo - 1: Computing
    historical_computed = (
        all_historical_data.groupby("stock_id")
        .agg(
            historical_max_price=("max", max),
            historical_min_price=("min", min),
            historical_close_price_mean=("close", "mean"),
            historical_close_price_median=("close", "median"),
            historical_close_price_std=("close", "std"),
        )
        .reset_index(drop=False)
    )

    columns_need_rounding = [
        "historical_close_price_mean",
        "historical_close_price_median",
        "historical_close_price_std",
    ]

    historical_computed[columns_need_rounding] = historical_computed[
        columns_need_rounding
    ].apply(lambda x: pd.Series.round(x, 2))
    historical_computed.rename(
        columns={
            "stock_id": "Stock Number",
            "historical_max_price": "Historical Highest Price",
            "historical_min_price": "Historical Lowest Price",
            "historical_close_price_mean": "Closed Price Mean",
            "historical_close_price_median": "Closed Price Median",
            "historical_close_price_std": "Closed Price Std",
        }
    )
    historical_computed.to_csv("..Data/Historical Price_summarized.csv")

    # ToDo - 2: Updating
    gc = pygsheets.authorize(service_account_file=os.getenv("JSON_FILE_PATH"))
    sh = gc.open_by_url(url_sheet)
    sheet_stock_historical_price = sh.worksheet_by_title("Historical Price")
    sheet_stock_historical_price.clear(start="A1")
    sheet_stock_historical_price.set_dataframe(
        df=historical_computed,
        start="A1",
        copy_index=False,
        copy_head=True,
        extend=True,
        fit=False,
    )
    operating_status["compute_historical_data"] = "success"
    return operating_status


def compute_realtime_data(operating_status: dict):
    sheet_interested_stock_list = pd.read_csv(
        "..Data/Google Sheet - Stocks Interested.csv",
        converters={"Stock Number": lambda x: str(x)},
        index_col=0,
    )

    all_realtime_data = pd.read_csv(
        "..Data/Realtime Price.csv",
        converters={"stock_id": lambda x: str(x)},
        index_col=0,
    )

    # Update copy if Realtime data is not null
    if all_realtime_data.shape[0] != 0:
        all_realtime_data_copy = all_realtime_data.copy()

    df = all_realtime_data.join(sheet_interested_stock_list).reset_index(drop=True)
    df.to_csv("..Data/test.csv")

    df_new = df.loc[
        :,
        [
            "stock_id",
            "Full Name",
            "date",
            "buy_price",
            "sell_price",
            "close",
            "Buy Price",
            "Buy Percent",
            "Sell Price",
            "Sell Percent",
        ],
    ]
    df_new["buy_price_change"] = round(
        abs(df_new["buy_price"] - df_new["close"]) / df_new["close"] * 100, 2
    )
    df_new["sell_price_change"] = round(
        abs(df_new["sell_price"] - df_new["close"]) / df_new["close"] * 100, 2
    )

    report_conditions = [
        (df_new["buy_price"] <= df_new["Buy Price"]),
        (df_new["buy_price_change"] >= df_new["Buy Percent"]),
        (df_new["sell_price"] >= df_new["Sell Price"]),
        (df_new["sell_price_change"] >= df_new["Sell Percent"]),
    ]

    report_choices = [1, 1, 1, 1]
    report_suggestions = ["Buy", "Buy", "Sell", "Sell"]

    df_new["report"] = np.select(report_conditions, report_choices, default=0)
    df_new["suggestion"] = np.select(report_conditions, report_suggestions, default=0)

    df_report = df_new[df_new["report"] == 1]
    df_report = df_report.drop(columns=["report"])
    df_report = df_report.rename(
        columns={
            "stock_id": "股票代號",
            "Full Name": "股票名稱",
            "date": "更新時間",
            "close": "收盤價",
            "buy_price": "即時買價",
            "buy_price_change": "即時買比例",
            "Buy Price": "設定買價",
            "Buy Percent": "設定買比例",
            "sell_price": "即時賣價",
            "sell_price_change": "即時賣比例",
            "Sell Price": "設定賣價",
            "Sell Percent": "設定賣比例",
            "suggestion": "建議",
        }
    )

    cols = [
        "股票代號",
        "股票名稱",
        "更新時間",
        "建議",
        "收盤價",
        "即時買價",
        "設定買價",
        "即時買比例",
        "設定買比例",
        "即時賣價",
        "設定賣價",
        "即時賣比例",
        "設定賣比例",
    ]

    df_report = df_report[cols]
    df_report.loc[df_report["建議"] == "Buy", ["即時賣價", "設定賣價", "即時賣比例", "設定賣比例"]] = ""
    df_report.loc[df_report["建議"] == "Sell", ["即時買價", "設定買價", "即時買比例", "設定買比例"]] = ""

    operating_status["compute_realtime_data"] = "success"
    return operating_status, df_report
