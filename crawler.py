import collections
import os

import pandas as pd

# num_letter = [str(n) for n in range(9)]
num_letter = '0123456789'
thres = 10000

def get_num(f_string, start_index):
    space_index = f_string.find(" ", start_index)
    
    num_string = f_string[start_index: space_index]
    num_string = filter(lambda ch: ch in num_letter, num_string)
    try:
        num = int(num_string)
    except:
        num = -1

    if num < thres:
        return -1
    else:
        return num

def parse_file(fname):
    with open(fname, 'r') as f_h:
        f_string = f_h.read()
        a_index = f_string.find('affiliate')
        if a_index == -1:
            print(" ".join((fname, ": affiliate cannot be found")))
            return -1

        dollar_index = f_string.find("$", a_index)
        if dollar_index == -1:
            print(" ".join((fname, ": dollar cannot be found")))
            return -1

        num = get_num(f_string, dollar_index + 1)
        if num == -1:
            return -1

        company_name = find_fields(f_string, 'COMPANY CONFORMED NAME')
        if company_name == -1:
            return -1

        report = find_fields(f_string, 'CONFORMED PERIOD OF REPORT')
        if report == -1:
            return -1

        date = find_fields(f_string, "FILED AS OF DATE")
        if date == -1:
            return -1

        return [num, company_name, report, date]


def find_fields(f_string, var_name):
    s_index = f_string.find(var_name)
    if (s_index == -1):
        return -1
    colon_index = f_string.find(":", s_index)
    if (colon_index == -1):
        return -1
    end_line = f_string.find('\n', colon_index)
    if (end_line == -1):
        return -1
    field_s = f_string[colon_index + 1: end_line].replace("\t", "").replace("\r", "")
    return field_s

def filter_file(fname):
    if fname.find('10-K') != -1:
        return True
    else:
        return False

def parse_file_name(fname):
    _, ftype, _, _, cik = fname.split("_")[:5]
    cik = "%010d"%int(cik)
    return ftype, cik

if __name__ == "__main__":
    file_dir = "file_list/"
    year_name_list = os.listdir(file_dir)
    save_dict = collections.defaultdict(list)
    for year_dir in year_name_list:
        qtr_list = os.listdir(os.path.join(file_dir, year_dir))
        for qtr_name in qtr_list:
            file_name_list = os.listdir(os.path.join(file_dir, year_dir, qtr_name))
            for fname in file_name_list:
                if filter_file(fname):
                    return_val = parse_file(os.path.join(file_dir, year_dir, qtr_name, fname))
                    if isinstance(return_val, list):
                        num = return_val[0]
                        company_name = return_val[1]
                        report = return_val[2]
                        date = return_val[3]

                        ftype, cik = parse_file_name(fname)
                        save_dict['file_type'].append(ftype)
                        save_dict['CIK'].append(cik)
                        save_dict['num'].append(num)
                        save_dict['COMPANY NAME'].append(company_name)
                        save_dict['CONFORMED PERIOD OF REPORT'].append(report)
                        save_dict['FILED AS OF DATE'].append(date)
                        save_dict['YEAR'].append(year_dir)


    df = pd.DataFrame(save_dict)
    filename = 'data.csv'
    df.to_csv(filename, index=['file_type', 'CIK', 'num', 'COMPANY NAME', 'CONFORMED PERIOD OF REPORT','FILED AS OF DATE', 'YEAR'], encoding='utf-8')
