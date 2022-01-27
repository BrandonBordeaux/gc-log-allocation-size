import argparse
import os
import re

import numpy


def main():
    parser = argparse.ArgumentParser(description='Find humongous allocations in GC log files. JVM option '
                                                 '-XX:+PrintAdaptiveSizePolicy is required.')
    parser.add_argument('file', nargs='+', help='gc.log file')
    args = parser.parse_args()

    allocations = list()

    for file in args.file:
        if os.path.isfile(file):
            allocations.extend(parse_file(file))

    print_results(allocations)


def parse_file(file):
    regex = "allocation request: ([0-9])+"
    allocations = list()

    open_file = open(file, "r")

    # Parse file for regex match
    for line in open_file:
        match = re.search(regex, line)

        if match is not None:
            match_str = match.group(0)

            # Split string and add allocation request size to list
            # Ignore 0 Byte allocations
            split_str = match_str.split(': ')
            allocation = int(split_str[1])
            if allocation != 0:
                allocations.append(allocation)

    return allocations


def print_results(allocations):
    # Aggregate allocations by 50% G1 region size
    allocation_512kb = 0
    allocation_1mb = 0
    allocation_2mb = 0
    allocation_4mb = 0
    allocation_8mb = 0
    allocation_16mb = 0
    allocation_gt16mb = 0

    for alloc in allocations:
        if alloc <= 524288:
            allocation_512kb += 1
        elif alloc <= 1048576:
            allocation_1mb += 1
        elif alloc <= 2097152:
            allocation_2mb += 1
        elif alloc <= 4194304:
            allocation_4mb += 1
        elif alloc <= 8388608:
            allocation_8mb += 1
        elif alloc <= 16777216:
            allocation_16mb += 1
        else:
            allocation_gt16mb += 1

    print('{0:<9} | {1:<9} | {2:<16} | {3:<}'.format("Heap Size", "G1 Region", "50% of G1 Region",
                                                     "Allocations <= 50% G1 Region"))
    print("------------------------------------------------------------------------")
    print('{0:<9}   {1:<9}   {2:<16}   {3:<}'.format("<4GB", "1MB", "0.5MB", allocation_512kb))
    print('{0:<9}   {1:<9}   {2:<16}   {3:<}'.format("<8GB", "2MB", "1MB", allocation_1mb))
    print('{0:<9}   {1:<9}   {2:<16}   {3:<}'.format("<16GB", "4MB", "2MB", allocation_2mb))
    print('{0:<9}   {1:<9}   {2:<16}   {3:<}'.format("<32GB", "8MB", "4MB", allocation_4mb))
    print('{0:<9}   {1:<9}   {2:<16}   {3:<}'.format("<64GB", "16MB", "8MB", allocation_8mb))
    print('{0:<9}   {1:<9}   {2:<16}   {3:<}'.format("64GB+", "32MB", "16MB", allocation_16mb))
    print('\nNumber of Allocations >16MB: {0}\n'.format(allocation_gt16mb))

    # Statistics
    if len(allocations) != 0:
        p50 = numpy.percentile(allocations, 50)
        p75 = numpy.percentile(allocations, 75)
        p90 = numpy.percentile(allocations, 90)
        p99 = numpy.percentile(allocations, 99)
        min_allocation = numpy.min(allocations)
        max_allocation = numpy.max(allocations)

        print('Allocation Percentiles (bytes):\n\tp50 = {}\n\tp75 = {}\n\tp90 = {}\n\tp99 = {}'
              .format(p50, p75, p90, p99))
        print('Min Allocation Size: {} bytes'.format(min_allocation))
        print('Max Allocation Size: {} bytes'.format(max_allocation))

    print('Total Allocation Count: {0}'.format(len(allocations)))


if __name__ == "__main__":
    main()
