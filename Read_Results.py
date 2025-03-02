import argparse
import json
import os
import pickle

def Read_results(test_meta, test_prefix, test_mode, test_name):
    if test_mode == 'Split' and "Split" not in test_meta.keys():
        return
    for i, (q, a) in enumerate(zip(test_meta[test_mode]["Questions"], test_meta[test_mode]["Answers"])):
        output_path_R = f"{test_prefix}_summary.txt"
        output_path = f"{test_prefix}-{i}.json"
        output_path = output_path.replace("Results_read","Results")
        if(not os.path.exists(output_path)):
            break
        if i == 0:
            with open(output_path_R, 'w') as file:
                file.write('')
        if os.path.isfile(output_path_R):
            with open(f"{output_path[:-5]}.txt", 'r') as f:
                all_count, gpt_correct, gpt_invalid = [int(_) for _ in f.read().splitlines()[2][5:].split(',')]
            with open(f"{output_path[:-5]}", "rb") as f:
                gpt_answers = pickle.load(f)
            output = f"{i + 1},{gpt_correct},{gpt_invalid},\n"
            print(output)
            with open(f"{output_path_R}", 'a') as file:
                file.write(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--flag",
                        type=str,
                        default="gpt4o-example-cot-group-0",
                        help="name of this run",
                        )
    parser.add_argument("--mode",
                        type=str,
                        choices=['Split', 'Group'],
                        default="Split",
                        help="Split or Group",
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
            test_mode=opt.mode,
            test_name=test['Name']
        )

