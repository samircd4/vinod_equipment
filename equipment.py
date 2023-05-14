from sendmail import send_mail
import requests, json
import pandas as pd


def get_data(current):
    print('Scraping data!')
    url = "https://jwxkwap.miit.gov.cn/dev-api-50/mobile/certificateQuery"

    payload = {
        "licenseNo": "",
        "equipmentCategoryCode": "002",
        "type": "1"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    data = json.loads(response.text)['data']
    models = []

    for d in data:
        model = {}
        acceptid = d['acceptid']
        licenseNo = d['licenseNo']
        equipmentModel = d['equipmentModel']
        url = f'https://jwxkwap.miit.gov.cn/licenseNoQuery?licenseNo={licenseNo}&acceptid={acceptid}'
        model['acceptid'] = acceptid
        model['licenseNo'] = licenseNo
        model['equipmentModel'] = equipmentModel
        model['url'] = url
        models.append(model)
        print(model)
    df = pd.DataFrame(models)
    df.to_csv(current, index=False)
    print('Scraping data completed!')

def compare_data(master, current):
        
    master_df = pd.read_csv(master)
    current_df = pd.read_csv(current)
    
    
    
    
    compared_df = current_df.merge(master_df, indicator=True, how='outer')
    compared_df = compared_df.loc[lambda x : x['_merge'] == 'left_only']
    
    isEmpty = len(compared_df)==0
    print(f'Equipment Model Data compared!')
    if not isEmpty:
        new_df = compared_df.iloc[:, [0, 1, 2, 3]]
        print(f'{len(new_df)} New data found! \n{compared_df["equipmentModel"]}')
        new_df.to_csv(master, index=False)
        update_master_df = pd.concat([master_df, new_df])
        update_master_df.to_csv(master, index=False)
        send_mail(new_df, 'Equipment Model Data Updated')
    else:
        print(f'Equipment Model Data is up to date!')



def main():
    master = 'master.csv'
    current = 'current.csv'
    get_data(current)
    compare_data(master, current)

if __name__=="__main__":
    main()
