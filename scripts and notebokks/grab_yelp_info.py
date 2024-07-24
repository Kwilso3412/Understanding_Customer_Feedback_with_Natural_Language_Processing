import json
import pandas as pd

# need to process Json file line by line
keys_of_intrest = ['stars', 'text']
data_list = []

'''
# If you want a random sample of the first set values

with open('yelp_academic_dataset_review.json', 'r', encoding='utf-8') as file:
    item_counter = 10000
    for line in file:
        if item_counter <= 0:
            break
        # json 'loads' if for string
        # json 'load' is for json file like object
        item = json.loads(line)
        filterd_item ={key: item[key] for key in keys_of_intrest if key in item}
        data_list.append(filterd_item)
        item_counter -= 1
        print(f'grabbed item {item_counter} left to grab')
        
json_data =pd.DataFrame(data_list)

json_data.to_csv("yelp_reveiw_data.csv")
'''



with open('yelp_academic_dataset_review.json', 'r', encoding='utf-8') as file:
    neg_item_counter = 7000
    neu_item_counter = 7000
    pos_item_counter = 7000

    for line in file:
        if neg_item_counter != 0:
            # json 'loads' if for string
            # json 'load' is for json file like object
            item = json.loads(line)
            if item['stars'] == 3:
                if neg_item_counter <= 0:
                    break 
                else: 
                    filterd_item ={key: item[key] for key in keys_of_intrest if key in item}
                    data_list.append(filterd_item)
                    neg_item_counter -= 1
                    print(f'grabbed item negative Item {neg_item_counter} left to grab')
        else:
            continue
        if neu_item_counter != 0:
            if item['stars'] < 3:
                if neu_item_counter <= 0:
                    break
                else:
                    filterd_item ={key: item[key] for key in keys_of_intrest if key in item}
                    data_list.append(filterd_item)
                    neu_item_counter -= 1
                    print(f'grabbed item neutral {neu_item_counter} left to grab')
        else:
            continue
        if pos_item_counter != 0:
            if item['stars'] > 3:
                if pos_item_counter <= 0:
                    break
                else:
                    filterd_item ={key: item[key] for key in keys_of_intrest if key in item}
                    data_list.append(filterd_item)
                    pos_item_counter -= 1
                    print(f'grabbed item positive {pos_item_counter} left to grab')
        else:
            continue

json_data =pd.DataFrame(data_list)
# clean the data for training

for index, row in json_data.iterrows():
    if row['stars'] > 3:
        json_data.at[index, 'rating'] = "{'positive': 1.0, 'negative': 0.0, 'neutral': 0.0}"
    elif row['stars'] < 3:
        json_data.at[index, 'rating'] = "{'positive': 0.0, 'negative': 1.0, 'neutral': 0.0}"
    else:
        json_data.at[index, 'rating'] = "{'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}"

json_data = json_data.drop(columns='stars')

json_data.to_csv("yelp_reveiw_data.csv", index=False)