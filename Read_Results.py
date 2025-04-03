import argparse
import json
import os

data_dict = {
    'CF1': 5,
    'CF2': 6,
    'CF3': 0,
    'CS1': 0,
    'CS2': 0,
    'CS3': 0,
    'I3': 8,
    'P3': 5,
    'S1': 8,
    'S2': 6,
    'SS2': 5,
    'SS3': 10,
    'VZ1': 5,
    'VZ2': 5,
    'VZ3': 5
}

def calc(answer, num):
    if num == 0:
        return answer[-1] * 100 / len(answer)
    base = 0
    count = 0
    now = 0
    for i in range(len(answer)):
        if i % num == 0:
            if now - base == num:
                count += 1
            base = now
        now = answer[i]

    return count * 100 / (len(answer) / num)

def Read_results(test_meta, test_prefix, test_mode, test_id):
    answer = []
    num = data_dict[test_id]
    if test_mode == 'Split' and "Split" not in test_meta.keys():
        return

    for i, (q, a) in enumerate(zip(test_meta[test_mode]["Questions"], test_meta[test_mode]["Answers"])):
        output_path = f"{test_prefix}-{i}.json"
        output_path = output_path.replace("Results_read", "Results")

        # Check if the output file exists before trying to read it
        txt_file_path = f"{output_path[:-5]}.txt"
        if not os.path.isfile(txt_file_path):
            continue

        with open(txt_file_path, 'r') as f:
            all_count, gpt_correct, gpt_invalid = [int(_) for _ in f.read().splitlines()[2][5:].split(',')]
        
        answer.append(gpt_correct)
    if len(answer) == 0:
        return 
    print(test_id, ' ', calc(answer, num))
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--flag",
                        type=str,
                        default="gpt4o-example-cot-group-0",
                        help="name of this run",
                        )
    opt = parser.parse_args()
    with open("meta.json", 'r') as f:
        data = json.load(f)
    
    for test_id, test in data.items():
        test_prefix = f"Results_read/{test_id}-{test['Name']}"

        if not os.path.isdir(test_prefix):
            os.makedirs(test_prefix)

        test_prefix += f'/{opt.flag}'

        Read_results(
                test_meta=data[test_id],
                test_prefix=test_prefix,
                test_mode='Group',
                test_id=test_id
        )
