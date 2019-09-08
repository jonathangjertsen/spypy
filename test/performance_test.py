import pickle
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

def perftest_short_loop():
    i = 10
    while i > 0:
        i -= 1

def perftest_long_loop():
    i = 10000
    while i > 0:
        i -= 1

def perftest_list_append():
    i = 1000
    res = []
    while i > 0:
        i -= 1
        res.append(i)



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
    for perftest, iterations in (
        (perftest_minimal, 1000),
        (perftest_ten_lines_one_var, 1000),
        (perftest_short_loop, 1000),
        (perftest_long_loop, 10),
        (perftest_list_append, 3),
    ):
        time_with, time_without, mem_consumption = run_performance_test(iterations, perftest)

        analysis = compare_timings(time_with, time_without)

        max_penalty = max(analysis["penalty_factor_mean"], analysis["penalty_factor_min"], analysis["penalty_factor_max"])
        min_penalty = min(analysis["penalty_factor_mean"], analysis["penalty_factor_min"], analysis["penalty_factor_max"])
        print(
            "{: >40}  ".format(perftest.__name__),
            "{:.0f}-{:.0f} times slower with spying, ".format(min_penalty, max_penalty),
            "Memory: {:.2f} kB".format(mem_consumption / 1024)
        )