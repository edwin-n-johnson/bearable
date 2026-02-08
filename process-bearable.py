import csv
import json
import re

TOD_PM = 'pm'
CAT_SYMPTOM = 'Symptom'
KEYH_DATE = 'date'
KEYH_DATEFORMAT = 'date formatted'
KEYH_WEEKDAY = 'weekday'
KEYH_TOD = 'time of day'
KEYH_CATEGORY = 'category'
KEYH_AMOUNT = 'rating/amount'
KEYH_DETAIL = 'detail'
KEYH_NOTES = 'notes'
g_events_d = {}
g_events_l = []

def process_row(headers_list, row):
    headers_to_index = {}

    #key_joint_pain = 'Joint pain'
    #key_back_pain = 'Back (lower) pain'

    # Create a dictionary out of the headers list
    for i in range(len(headers_list)):
        headers_to_index[headers_list[i]] = i
    date = row[headers_to_index[KEYH_DATEFORMAT]]
    print()
    print(date)
    print(headers_to_index)

    # Create the new event
    event = {}
    # But if we have one, use that one
    if date in g_events_d:
        event = g_events_d[date]

    # Copy values into the event
    print(row)
    for key in [KEYH_DATE, KEYH_DATEFORMAT, KEYH_WEEKDAY, KEYH_TOD, KEYH_CATEGORY, KEYH_AMOUNT, KEYH_DETAIL, KEYH_NOTES]:
        #if key in event and event[key] != row[headers_to_index[key]]:
            #print("ERROR: {} has duplicate entries for {} | {} | {}".format(date, key, event[key],
            #                                                                row[headers_to_index[key]]))
        if headers_to_index[key] >= len(row):
            event[key] = ''
        else:
            event[key] = row[headers_to_index[key]]
    category = row[headers_to_index[KEYH_CATEGORY]]
    detail = row[headers_to_index[KEYH_DETAIL]]
    tod = row[headers_to_index[KEYH_TOD]]
    amount = row[headers_to_index[KEYH_AMOUNT]]

    key2 = None
    value2 = None
    # Category Symptom
    if category == CAT_SYMPTOM and (not tod or tod == TOD_PM):
        symptom = row[headers_to_index[KEYH_DETAIL]]
        symptom = re.sub(r'(.*) \(.+\)', r'\1', symptom)
        key2 = symptom
        value2 = amount
        # Clear TOD
        event[KEYH_TOD] = TOD_PM

    # Category

    # Insert the sub-key (key2)
    if key2 in event and event[key2] != value2:
        print("ERROR: {} has duplicate entries for {} | {} | {}".format(date, key2, event[key2], value2))
    else:
        event[key2] = value2

    # Check for duplicates
    #print(event[keyh_category])
    #print(row[headers_to_index[keyh_category]])

    # Insert the event
    g_events_d[date] = event


def flatten_events(headers):
    new_headers = ['Joint pain', 'Back (lower) pain']

    for key_primary in sorted(g_events_d.keys()):
        event = g_events_d[key_primary]
        row = []
        for header in headers:
            row.append(event[header])
        for header in new_headers:
            if header in event:
                row.append(event[header])
            else:
                row.append('')

        g_events_l.append(row)
    return headers + new_headers

def main():
    with open("bearable.csv", encoding='utf-8') as fInput:
        csv_reader = csv.reader(fInput, delimiter=',')
        line_num = 0
        for row in csv_reader:
            if line_num == 0:
                headers = row
                print(headers)
                print("==============================")
            else:
                process_row(headers, row)
            #print(row)
            line_num += 1
    print("==============================")

    new_headers = flatten_events(headers)

    with open("bearable-out.csv", 'w', encoding='utf-8', newline='') as fOutput:
        writer = csv.writer(fOutput, delimiter=',')
        writer.writerow(new_headers)
        writer.writerows(g_events_l)

    with open("bearable-out.json", 'w') as fOutput:
        json.dump(g_events_d, fOutput, indent=4)

if __name__ == '__main__':
    main()
