import pickle
import pprint
import requests
import requests_cache
from bs4 import BeautifulSoup

pp = pprint.PrettyPrinter()

session = requests_cache.CachedSession('sec')


def symbol_to_cik(query):
    headers = {'User-Agent': 'test@example.com'}
    data = {
        'keysTyped': 'apple',
        'narrow': True,
    }
    resp = requests.post(
        'https://efts.sec.gov/LATEST/search-index',
        headers=headers,
        json=data)
    # print(resp)
    data = resp.json()
    pp.pprint(data['hits']['hits'])
    print('=' * 10)
    pp.pprint(data['hits']['hits'][0])
    for hit in data['hits']['hits']:
        if hit['_source']['tickers'] == query:
            return int(hit['_id'])


def fetch_submissions(cik, type_filter, pull_documents, read_if_cached=True):
    file_key = 'data/%010d-%s-%s.pkl' % (cik, ':'.join(type_filter), pull_documents)
    print("Checking for cached file in ", file_key)
    if read_if_cached:
        print("Checking for cached file in ", file_key)
        try:
            print("Found, reading from", file_key)
            with open(file_key, 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            pass

    headers = {'User-Agent': 'test@example.com'}
    url = f'https://data.sec.gov/submissions/CIK{cik:010d}.json'
    print('url', url)
    resp = session.get(url, headers=headers)
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

        if pull_documents:
            resp = session.get(doc_url, headers=headers)
            print('doc', doc_url, resp)
            soup = BeautifulSoup(resp.content, 'html.parser')
            text = soup.get_text()
            item['html'] = resp.content
            item['text'] = text

        items.append(item)

    with open(file_key, 'wb') as f:
        print("Saving to ", file_key)
        pickle.dump(items, f)

    return items


def load_submissions(cik, type_filter, pull_documents):
    key = 'data/%010d-%s-%s.pkl' % (cik, ':'.join(type_filter), pull_documents)
    with open(key, 'rb') as f:
        return pickle.load(f)


def main():
    # cik = 320193
    cik = symbol_to_cik('AAPL')

    fetch_submissions(cik, ['10-Q', '10-K'], True)
    items = load_submissions(cik, ['10-Q', '10-K'], True)
    import pdb
    pdb.set_trace()
    pp.pprint(items[0])


if __name__ == '__main__':
    main()
