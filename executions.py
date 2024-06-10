"""
Executes generated completions.
"""
# bounded_subprocess was written for MultiPL-E by Ming-Ho and Arjun.
import bounded_subprocess
import pandas as pd
from pathlib import Path
import yaml
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import tempfile
import csv
import argparse

# Add a program column that has prompt + "\n\n" + print(inputs) + "\n" ...
def assemble_program(row):
    entrypoint = row["entrypoint"]

    def assemble_test(t):
        nonlocal entrypoint
        (input, output) = t
        return f"assert {entrypoint}({input}) == {output}"

    return "\n\n".join(
        [row["prompt"] + row["completion"]] + [assemble_test(t) for t in row["tests"]]
    )


def main():
    args = argparse.ArgumentParser()
    args.add_argument("--completions", type=str, required=True)
    args.add_argument("--executions", type=str, required=True)

    args = args.parse_args()
    with Path("problems.yaml").open() as f:
        tests = yaml.safe_load(f)

    # Data frame mapping problems to a list of input and output pairs.
    tests_df = []
    for (key, value) in tests.items():
        signature = value["signature"].lstrip()
        entrypoint = signature[4:].split("(")[0]
        tests_df.append(
            {
                "problem": key,
                "entrypoint": entrypoint,
                "tests": [(test["input"], test["output"]) for test in value["tests"]],
            }
        )
    tests_df = pd.DataFrame(tests_df)

    completions = pd.read_json(args.completions, lines=True)

    # Data frame with prompt, problem, completion, count. Every row has a unique (prompt, problem, completion).
    completions = (
        completions.groupby(["prompt", "problem", "completion"])
        .size()
        .reset_index(name="count")
    )

    # Data frame with problem, prompt, completion, count, and inputs
    joined = tests_df.merge(completions, on=["problem"], how="inner")

    joined["program"] = joined.apply(assemble_program, axis=1)

    # Set the index of joined to be (prompt, problem, completion)

    def run_assembled_program(row):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py") as f:
            f.write(row["program"])
            f.flush()
            result = bounded_subprocess.run(["python3", f.name])
        return (row["problem"], row["prompt"], row["count"], result.exit_code)

    with ThreadPoolExecutor(max_workers=12) as executor:
        exitcodes = []
        for (i, tuple) in tqdm(
            enumerate(executor.map(run_assembled_program, joined.iloc)),
            total=len(joined),
        ):
            exitcodes.append(tuple)

    exitcodes_df = pd.DataFrame(
        exitcodes, columns=["problem", "prompt", "count", "exit_code"]
    )
    exitcodes_df.to_csv(args.executions, quoting=csv.QUOTE_ALL, escapechar="\\")


if __name__ == "__main__":
    main()
