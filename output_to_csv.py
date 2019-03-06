import csv


def output_to_csv(output):
    for d in output:
        keys = output[d][0].keys()
        with open(d + '.csv', 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(output[d])
