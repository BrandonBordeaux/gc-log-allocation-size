# Humongous Allocations

Parse Java G1 gc.log files that are written with `-XX:+PrintAdaptiveSizePolicy` enabled in the JVM options and identify humongous allocations. Humongous allocations are any allocation that exceeds half of the G1 region size.

## Build (optional)

```
pyinstaller -F humongous_alloc.py
```

## Usage

```
humongous_alloc -h
usage: humongous_alloc [-h] file [file ...]

Find humongous allocations in GC log files. JVM option -XX:+PrintAdaptiveSizePolicy is required.

positional arguments:
  file        gc.log file

optional arguments:
  -h, --help  show this help message and exit
```

## Example

```
Heap Size | G1 Region | 50% of G1 Region | Allocations <= 50% G1 Region
------------------------------------------------------------------------
<4GB        1MB         0.5MB              42
<8GB        2MB         1MB                24
<16GB       4MB         2MB                61
<32GB       8MB         4MB                371
<64GB       16MB        8MB                202224
64GB+       32MB        16MB               70685

Number of Allocations >16MB: 8648

Allocation Percentiles (bytes):
	p50 = 7459136.0
	p75 = 11626040.0
	p90 = 14918248.0
	p99 = 22377104.0
Min Allocation Size: 664 bytes
Max Allocation Size: 22377368 bytes
Total Allocation Count: 282055
```

- The table summarizes how many allocations fit within 50% or less of a G1 region size. The purpose of this is to determine whether increasing the G1 region size would help lessen the number of humongous allocations.
  - In this example, if we had a JVM running with a 31 GB heap (`-Xms` and `-Xmx` = 31g), we have 202,224 humongous allocations we could get rid of by increasing the G1 region size to 16 MB.
  - Increasing the G1 region size can be done by:
    - Increasing `-Xms` and `-Xmx` to between 32 GB and 64 GB.
    - Increase `-XX:G1HeapRegionSize` to 16 MB. However, this approach should be used with caution as you will have fewer G1 regions and that can cause JVM performance issues.
- Percentile statistics are also displayed to identify what portion of the allocation are `n` bytes or larger.
