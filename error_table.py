
import os
import sys
import json
import numpy as np
import pandas as pd

order = ["logmse", "mse", "qlike"]

# order_model =

formats = ["{:1.8f}", "{:1.8f}", "{:1.8f}"]


def write_table(template_path, target_path, e, step=1, name_addition="Fixed"):

    with open(template_path, "r") as f:
        lines = f.readlines()

    c = 1

    for i, line in enumerate(lines):
        if "+++" in line:
            insert_lines = [
                k.replace("_", " ") + " & " + " & ".join([formats[i].format(e[k][v]) for i, v in enumerate(order)]) + "\\\\ \n"
                for k in e.keys()
            ]
            for j, i_line in enumerate(insert_lines):
                i_line = i_line.replace(f" {step}step", "")
                insert_lines[j] = i_line
            lines = lines[:i] + insert_lines + lines[i+1:]
            lines[i-1] = f"{name_addition}{step}-step ahead " + lines[i-1]
            break

    with open(target_path, "w") as f:
        f.writelines(lines)

    return e


template = os.path.abspath("Table_template.tex")

with open("/Users/lucasburger/Github/pyRC/errors.json", "r") as f:
    errors = json.load(f)

for model, e in errors.items():
    for k2, v2 in e.items():
        if k2 == "mse":
            e[k2] = v2*(10**5)
    errors[model] = e


steps = [1, 2, 5, 10]

filter_and_names = [
    (lambda x: True, "Table_sigma_all_{}step.tex", lambda x: x, ""),
    (lambda x: "rolling" not in x, "Table_sigma_{}step.tex", lambda x: x, "Fixed "),
    (lambda x: "rolling" in x and ("Middle" not in x and "Low" not in x), "Table_sigma_rolling_{}step.tex", lambda x: x.replace("_rolling", ""), "Rolling "),
    (lambda x: "rolling" in x and "Plasticity" in x, "Table_sigma2_rolling_{}step.tex",
     lambda x: x.replace("_rolling", ""), "Rolling ")
]

for step in steps:
    e = {k: v for k, v in errors.items() if "{}step".format(step) in k}
    for filt, name, new_keys, name_addition in filter_and_names:
        local_e = {new_keys(k): v for k, v in e.items() if filt(k)}
        target = os.path.abspath(name.format(step))
        write_table(template, target, local_e, step=step, name_addition=name_addition)
