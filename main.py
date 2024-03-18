import chat
import fetch

def make_time_series(question, ticker, mode='claude'):
    cik = fetch.symbol_to_cik(ticker)
    items = fetch.fetch_submissions(cik, ['10-K'], True)
    time_series = {}
    for item in items:
        if mode =='claude':
            result = chat.call_claude(question + ' The file content follows ' + item['text'])
            json_result = chat.extract_json(result[0].text)
        else:
            print("Parsing file that originated from", item['url'])
            json_result = chat.call_chatgpt(question, item['text'])
        print("Appending ", json_result, " to time series")
        if json_result["found"]:
            time_series[json_result['date']] = json_result['value']
    print(time_series)

if __name__ == '__main__':
    make_time_series('Extract the unit sales of iPhones expressed in millions', 'AAPL', 'chatgpt')
