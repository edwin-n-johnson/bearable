import argparse
import csv
import json
import re

TOD_PM = 'pm'
CAT_SYMPTOM = 'Symptom'
CAT_HEALTH = 'Health measurements'

DETAIL_JOINT_PAIN = r"Joint pain"
DETAIL_BACK_LOWER_PAIN = r"Back \(lower\) pain"
DETAIL_WEIGHT = r"Weight"
DETAIL_RESTING_HR = r"Resting heart rate"
DETAIL_VO2MAX = r"VO2 Max"

KEYH_DATE = 'date'
KEYH_DATEFORMAT = 'date formatted'
KEYH_WEEKDAY = 'weekday'
KEYH_TOD = 'time of day'
KEYH_CATEGORY = 'category'
KEYH_AMOUNT = 'rating/amount'
KEYH_DETAIL = 'detail'
KEYH_NOTES = 'notes'

KEYNH_JOINT_PAIN = 'joint pain (n)'
KEYNH_BACK_LOWER_PAIN = 'lower back pain (n)'
KEYNH_WEIGHT = 'weight (n)'
KEYNH_RESTING_HR = 'resting hr (n)'
KEYNH_VO2MAX = 'vo2max (n)'

g_events_d = {}
g_events_l = []
g_headers_to_index = { }

def process_row_helper(date, row, keynh):
    global g_events_d
    global g_headers_to_index

    # get or make the event
    event = { }
    if date in g_events_d:
        event = g_events_d[date]

    # Set the joint pain value
    value = float(row[g_headers_to_index[KEYH_AMOUNT]])
    print(f"{keynh}: {value}")
    event[keynh] = value
    if keynh not in g_headers_to_index:
        g_headers_to_index[keynh] = len(g_headers_to_index)

    # Put the modified event back in the global dict
    g_events_d[date] = event


def process_row_joint_pain(date, row):
    process_row_helper(date, row, KEYNH_JOINT_PAIN)


def process_row_back_lower_pain(date, row):
    process_row_helper(date, row, KEYNH_BACK_LOWER_PAIN)


def process_row_weight(date, row):
    process_row_helper(date, row, KEYNH_WEIGHT)


def process_row_resting_hr(date, row):
    process_row_helper(date, row, KEYNH_RESTING_HR)


def process_row_vo2max(date, row):
    process_row_helper(date, row, KEYNH_VO2MAX)


def process_row(headers_list, row):
    global g_headers_to_index

    # Create a dictionary out of the headers list
    for i in range(len(headers_list)):
        g_headers_to_index[headers_list[i]] = i
    date = row[g_headers_to_index[KEYH_DATEFORMAT]]

    # Check for the various categories and details
    category = row[g_headers_to_index[KEYH_CATEGORY]]
    detail = row[g_headers_to_index[KEYH_DETAIL]]

    if category == CAT_SYMPTOM:
        if re.search(DETAIL_JOINT_PAIN, detail):
            process_row_joint_pain(date, row)
        if re.search(DETAIL_BACK_LOWER_PAIN, detail):
            process_row_back_lower_pain(date, row)
    elif category == CAT_HEALTH:
        if re.search(DETAIL_WEIGHT, detail):
            process_row_weight(date, row)
        if re.search(DETAIL_RESTING_HR, detail):
            process_row_resting_hr(date, row)
        if re.search(DETAIL_VO2MAX, detail):
            process_row_vo2max(date, row)


def flatten_events():
    new_headers_d = {}
    # Find all headers created
    for key,event in g_events_d.items():
        for key2 in event.keys():
            new_headers_d[key2] = True

    new_headers = list(new_headers_d.keys())
    g_events_l.append([KEYH_DATE] + new_headers)

    for key in sorted(g_events_d.keys()):
        event = g_events_d[key]
        row = [ key ]
        for key2 in new_headers:
            if key2 in event:
                row.append(event[key2])
            else:
                row.append('')

        g_events_l.append(row)


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage = "%(prog)s [OPTION] [FILE]",
        description = "Process bearable events from CSV file",
        add_help = True,
    )
    parser.add_argument("-v", "--version", action="version", version="%(prog)s 1.0")
    parser.add_argument('file')

    return parser


def main():
    parser = init_argparse()
    args = parser.parse_args()

    with open("test-data/bearable-export-09-02-2026.csv", encoding='utf-8') as fInput:
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

    flatten_events()

    with open("test-data/bearable-out.csv", 'w', encoding='utf-8', newline='') as fOutput:
        writer = csv.writer(fOutput, delimiter=',')
        writer.writerows(g_events_l)

    with open("test-data/bearable-out.json", 'w') as fOutput:
        json.dump(g_events_d, fOutput, indent=4)

if __name__ == '__main__':
    main()
