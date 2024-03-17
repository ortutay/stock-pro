import pprint
import requests
import requests_cache

pp = pprint.PrettyPrinter()

requests_cache.install_cache('sec_cache', expire_after=7*24*3600)

def get_submissions(cik, type_filter, pull_documents):
    headers = {'User-Agent': 'test@example.com'}
    url = f'https://data.sec.gov/submissions/CIK{cik:010d}.json'
    print('url', url)
    resp = requests.get(url, headers=headers)
    data = resp.json()

    recent_filings = data['filings']['recent']
    items = []
    for i in range(len(recent_filings['accessionNumber'])):
        item = {}
        for key in recent_filings.keys():
            val = recent_filings[key][i]
            item[key] = val

        if type_filter and item['primaryDocDescription'] not in type_filter:
            continue

        accession_number = int(item['accessionNumber'].replace('-', ''))
        document = item['primaryDocument']
        doc_url = f'https://www.sec.gov/Archives/edgar/data/{cik:d}/{accession_number:018d}/{document}'
        item['url'] = doc_url
        items.append(item)

        if pull_documents:
            resp = requests.get(doc_url, headers=headers)
            print('doc', doc_url, resp)

    for i in range(10):
        print('doc url', items[i]['primaryDocDescription'], items[i]['url'])


def main():
    cik = 320193
    subs = get_submissions(cik, ['10-Q', '10-K'], True)


main()
