from Stock_Get_and_Notify.data import (
    check_gsheet_stock_id,
    get_tw_stock_info,
    get_newest_stock_historical_price,
    get_newest_stock_realtime_price,
)
from Stock_Get_and_Notify.login_auth import login_finmind, connect_gsheets
from Stock_Get_and_Notify.analysis import compute_historical_data, compute_realtime_data
from Stock_Get_and_Notify.notify import notify


def stock_main():
    # ToDo - Step 1: Login
    login_result = login_finmind()
    current_operating_status = login_result[0]
    token_obtained = login_result[1]["token"]

    # ToDo - Step 2: Access gsheets
    google_sheets = connect_gsheets(operating_status=current_operating_status)
    current_operating_status = google_sheets[0]

    # ToDo - Step 2-1: Check whether data entered on gsheets are correct
    tw_stock_info = get_tw_stock_info(token_obtained)
    wrong_stock_id_list, stock_full_name_dic, stocks_entered = check_gsheet_stock_id(
        sheet_stocks_interested=google_sheets[1], tw_stock_data=tw_stock_info
    )

    if len(wrong_stock_id_list) != 0:
        print(
            f"The following stock id(s) entered is wrong. Please double-check.\n {wrong_stock_id_list}"
        )

    # ToDo - Step 3: Get the newest stocks' historical and real-time data
    if len(wrong_stock_id_list) == 0:
        current_operating_status = get_newest_stock_historical_price(
            operating_status=current_operating_status,
            stocks_entered=stocks_entered,
            token_obtained=token_obtained,
        )

        current_operating_status = get_newest_stock_realtime_price(
            operating_status=current_operating_status,
            stocks_entered=stocks_entered,
            token_obtained=token_obtained,
        )

    # ToDo - Step 4-1: Calculate and Update stock historical price
    current_operating_status = compute_historical_data(current_operating_status)

    # ToDo - Step 4-2: Calculate and Compare stock realtime price
    current_operating_status, df_report = compute_realtime_data(
        current_operating_status
    )

    # ToDo - Step 5: Send emails
    current_operating_status = notify(df_report, current_operating_status)

    return current_operating_status


if __name__ == "__main__":
    operating_result = stock_main()
    print(operating_result)
