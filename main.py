import re

import numpy


def main():
    filename = "gc.log"
    regex = "allocation request: ([0-9])+"
    allocations = list()

    file = open(filename, "r")

    # Parse file for regex match
    for line in file:
        match = re.search(regex, line)

        if match is not None:
            match_str = match.group(0)

            # Split string and add allocation request size to list
            # Ignore 0 Byte allocations
            split_str = match_str.split(': ')
            if int(split_str[1]) is not 0:
                allocations.append(int(split_str[1]))

    # Aggregate allocations by 50% G1 region size
    humongous_object_512kb = 0
    humongous_object_1mb = 0
    humongous_object_2mb = 0
    humongous_object_4mb = 0
    humongous_object_8mb = 0
    humongous_object_16mb = 0
    humongous_object_gt16mb = 0

    for alloc in allocations:
        if alloc <= 524288:
            humongous_object_512kb += 1
        elif alloc <= 1048576:
            humongous_object_1mb += 1
        elif alloc <= 2097152:
            humongous_object_2mb += 1
        elif alloc <= 4194304:
            humongous_object_4mb += 1
        elif alloc <= 8388608:
            humongous_object_8mb += 1
        elif alloc <= 16777216:
            humongous_object_16mb += 1
        else:
            humongous_object_gt16mb += 1

    print('{0:<9} | {1:<9} | {2:<16} | {3:<}'.format("Heap Size", "G1 Region", "50% of G1 Region",
                                                     "Humongous Allocations <= 50% G1 Region"))
    print("---------------------------------------------------------------------------------")
    print('{0:<9}   {1:<9}   {2:<16}   {3:<}'.format("<4GB", "1MB", "0.5MB", humongous_object_512kb))
    print('{0:<9}   {1:<9}   {2:<16}   {3:<}'.format("<8GB", "2MB", "1MB", humongous_object_1mb))
    print('{0:<9}   {1:<9}   {2:<16}   {3:<}'.format("<16GB", "4MB", "2MB", humongous_object_2mb))
    print('{0:<9}   {1:<9}   {2:<16}   {3:<}'.format("<32GB", "8MB", "4MB", humongous_object_4mb))
    print('{0:<9}   {1:<9}   {2:<16}   {3:<}'.format("<64GB", "16MB", "8MB", humongous_object_8mb))
    print('{0:<9}   {1:<9}   {2:<16}   {3:<}'.format("64GB+", "32MB", "16MB", humongous_object_16mb))
    print('\nNumber of Humongous Objects >16MB: {0}'.format(humongous_object_gt16mb))

    # Statistics
    p50 = numpy.percentile(allocations, 50)
    p75 = numpy.percentile(allocations, 75)
    p90 = numpy.percentile(allocations, 90)
    p99 = numpy.percentile(allocations, 99)
    min_allocation = numpy.min(allocations)
    max_allocation = numpy.max(allocations)

    print('\nHumongous Allocation Percentiles:\n\tp50 = {}\n\tp75 = {}\n\tp90 = {}\n\tp99 = {}'
          .format(p50, p75, p90, p99))
    print('Min Humongous Allocation Size: {}'.format(min_allocation))
    print('Max Humongous Allocation Size: {}'.format(max_allocation))
    print('Total Humongous Allocation Count: {0}'.format(len(allocations)))


if __name__ == "__main__":
    main()
