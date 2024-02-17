import pandas as pd
from flask import send_from_directory
from flask import Flask, render_template, jsonify
from financetoolkit import Toolkit
from mezmorize import Cache
cache = Cache(CACHE_TYPE='filesystem', CACHE_DIR='cache',
              CACHE_DEFAULT_TIMEOUT=999999999, CACHE_THRESHOLD=99999999)


# surpress e notation


def format_numbers(value):
    if value == 0:
        return "0"
    return '{:.2f}B'.format(value)
    if abs(value) >= 1e9:
        return '{:.2f}B'.format(value / 1e9)
    if abs(value) >= 1e6:
        return '{:.2f}M'.format(value / 1e6)
    elif abs(value) >= 1e3:
        return '{:.2f}K'.format(value / 1e3)
    else:
        return '{:.2f}'.format(value)


@cache.memoize()
def cached_statements(ticker, start_date):
    company = Toolkit(
        ticker, api_key="8c15789517adf7282a6d99201c122625", start_date=start_date)
    income = company.get_income_statement()
    cashflow = company.get_cash_flow_statement()
    balance = company.get_balance_sheet_statement()
    return (income, cashflow, balance)


app = Flask(__name__)


@app.route('/static/<path:path>')
def send_static_file(path):
    return send_from_directory('static', path)


@app.route('/stock/<ticker>')
def stock_ui(ticker):
    return render_template("stock.html", ticker=ticker)


@app.route('/json/<ticker>')
def send_stock_json(ticker):
    (income, cashflow, balance) = cached_statements(ticker, "2010-12-31")
    fin_dic = {"income": income, "cashflow": cashflow, "balance": balance}
    print(fin_dic["income"].to_csv(header=None, index=True))
    print(fin_dic["cashflow"].to_csv(header=None, index=True))
    print(fin_dic["balance"].to_csv(header=None, index=True))
    pd.set_option('display.float_format', format_numbers)
    # TODO json = jsonify(fin_dic)
    # print(json)
    json = """
{
"nodes":[
{"node":0,"name":"node0"},
{"node":1,"name":"node1"},
{"node":2,"name":"node2"},
{"node":3,"name":"node3"},
{"node":4,"name":"node4"}
],
"links":[
{"source":0,"target":2,"value":2},
{"source":1,"target":2,"value":2},
{"source":1,"target":3,"value":2},
{"source":0,"target":4,"value":2},
{"source":2,"target":3,"value":2},
{"source":2,"target":4,"value":2},
{"source":3,"target":4,"value":4}
]}
 """
    return json


if __name__ == "__main__":
    app.run()
