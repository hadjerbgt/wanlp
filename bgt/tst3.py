import time
import httpx
import pandas as pd

base_url = 'https://www.reddit.com'
endpoint = '/search/q=سعادة'
category = '/top'

url = base_url + endpoint + category + ".json"
after_post_id = None

dataset = []
for _ in range(5):
    params = {
        'limit': 10,
        't': 'year',  # time unit (hour, day, week, month, year, all)
        # 'after': after_post_id
    }

    try:
        response = httpx.get(url, params=params)
        print(f'fetching "{response.url}"...')

        if response.status_code == 200:
            json_data = response.json()
            dataset.extend([rec['data'] for rec in json_data['data']['children']])
            after_post_id = json_data['data']['after']
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            # Retry after a delay
            time.sleep(5)
            continue  # Skip to the next iteration

        time.sleep(0.5)

    except Exception as e:
        print("An error occurred:", str(e))
        # Retry after a delay
        time.sleep(5)
        continue  # Skip to the next iteration

df = pd.DataFrame(dataset)
df.to_csv('hh.csv', index=False)