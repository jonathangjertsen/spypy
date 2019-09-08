import pickle
import json
import time

import spypy

def perftest_minimal():
    pass

def perftest_ten_lines_one_var():
    a = 1
    a += 1
    a += 1
    a += 1
    a += 1
    a += 1
    a += 1
    a += 1
    a += 1
    a += 1

def perftest_loop(n):
    while n > 0:
        n -= 1

def perftest_list_append(n):
    res = []
    while n > 0:
        n -= 1
        res.append(n)

def perftest_json_dump(iterations, list_size):
    for _ in range(iterations):
        numbers = list(range(list_size))
        string = json.dumps(numbers)

def perftest_numpy(iterations, list_size):
    import numpy as np
    for _ in range(iterations):
        arr = np.array(list(range(list_size)))
        sqrt = np.sqrt(arr)

def run_performance_test(ntimes, func, *args, **kwargs):
    tracer = spypy.Tracer()

    timings_without = []
    timings_with = []

    for _ in range(ntimes):
        t0 = time.perf_counter()

        func(*args, **kwargs)

        t1 = time.perf_counter()
        timings_without.append(t1 - t0)

    for _ in range(ntimes):
        t0 = time.perf_counter()

        tracer.reset_history()
        tracer.trace(func, *args, **kwargs)

        t1 = time.perf_counter()
        timings_with.append(t1 - t0)

    mem_consumption = check_memory_consumption(tracer)

    return timings_without, timings_with, mem_consumption

def check_memory_consumption(tracer):
    return len(pickle.dumps(tracer))

def analyze_timings(timings):
    return {
        "mean": sum(timings) / len(timings),
        "max": max(timings),
        "min": min(timings),
        "max/min": max(timings) / min(timings)
    }

def compare_timings(timings_without, timings_with):
    analysis_without = analyze_timings(timings_without)
    analysis_with = analyze_timings(timings_with)
    return {
        "without": analysis_without,
        "with": analysis_with,
        "penalty_factor_mean": analysis_with["mean"] / analysis_without["mean"],
        "penalty_factor_max": analysis_with["max"] / analysis_without["max"],
        "penalty_factor_min": analysis_with["min"] / analysis_without["min"],
    }

if __name__ == "__main__":
    for name, perftest, iterations, kwargs in (
        ("Do nothing", perftest_minimal, 1000, {}),
        ("Ten lines, one var", perftest_ten_lines_one_var, 1000, {}),
        ("Loop (10 iterations)", perftest_loop, 1000, {"n": 10}),
        ("Loop (10000 iterations)", perftest_loop, 10, {"n": 10000}),
        ("List append (1000 ints)", perftest_list_append, 3, {"n": 1000}),
        ("JSON dump (10 iterations, 1000 ints)", perftest_json_dump, 5, {"iterations": 10, "list_size": 1000}),
        ("Numpy array (10 iterations, 1000 ints)", perftest_numpy, 5, {"iterations": 10, "list_size": 1000})
    ):
        try:
            time_with, time_without, mem_consumption = run_performance_test(iterations, perftest, **kwargs)

            analysis = compare_timings(time_with, time_without)

            max_penalty = max(analysis["penalty_factor_mean"], analysis["penalty_factor_min"], analysis["penalty_factor_max"])
            min_penalty = min(analysis["penalty_factor_mean"], analysis["penalty_factor_min"], analysis["penalty_factor_max"])
            print(
                "{: >40}  ".format(name),
                "{:.0f}-{:.0f} times slower with spying, ".format(min_penalty, max_penalty),
                "Memory: {:.2f} kB".format(mem_consumption / 1024)
            )
        except Exception as exc:
            print("Exception during test '{}': {}".format(name, exc))