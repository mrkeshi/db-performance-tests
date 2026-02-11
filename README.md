# 🧾 Database Performance Comparison Report

## 🧩 Introduction

The purpose of this report is to **compare the performance characteristics** of four widely used and modern database systems — **Redis**, **MongoDB**, **Cassandra**, and **PostgreSQL** — under controlled, reproducible, and containerized (Docker-based) environments.

The goal of this study is to **evaluate and analyze** key performance metrics that reflect each system’s efficiency and scalability under different workloads.
By testing these databases in a **standardized and isolated Docker environment**, we ensure that each system is subjected to **identical hardware, resource limits, and workload conditions**, thereby maintaining fairness and reproducibility.

---

## ⚖️ Benchmarking Fairness

To achieve fairness and consistency in measurement:

- All tests were conducted on the **same host machine** with **identical CPU, memory, and storage conditions**.
- Each database was **Dockerized** to eliminate environment-specific advantages and ensure isolation.
- **Swap memory was disabled** to prevent the operating system from influencing memory consumption results.
- For databases using internal thread pools, **manual connection pooling** (in PostgreSQL) was applied to match concurrency conditions.

This ensures that performance differences observed are attributed solely to **database design and architecture**, not to environmental or configuration biases.

---

## 📏 Measurement Metrics

The following key metrics were collected and analyzed across all workloads:

| Metric | Description |
|---------|--------------|
| **Throughput** | The number of successful operations or transactions processed per second. |
| **Latency** | The response time experienced by each operation or query (reported as average and percentiles). |
| **CPU Utilization** | The average CPU load (%) during workload execution. |
| **Memory Usage (RAM)** | The average physical memory consumption throughout the test run. |
| **P50 / P95 / P99 Latency** | Percentile-based latency measurements showing the distribution of response times. |

---

By systematically evaluating these metrics across different **read/write-intensive workloads**,
this study aims to identify each system’s **strengths, scalability patterns, and resource efficiency**.
The final goal is to provide **practical, data-driven insights** for selecting the most suitable database for various real-world application scenarios.

# 🧪 Test Environment and Experimental Setup

All experiments were conducted under **controlled and fair conditions** on a dedicated machine running **Ubuntu 24.04.3 LTS**.
The objective was to ensure that performance differences across databases are solely due to internal design and implementation — not due to hardware, OS, or configuration disparities.

---

## 🖥️ System Specifications

| Component | Specification |
|-----------|----------------|
| **Operating System** | Ubuntu 24.04.3 LTS |
| **Kernel Release** | 24.04 |
| **Architecture** | x86_64 |
| **CPU Model** | 11th Gen Intel(R) Core(TM) i5-11260H @ 2.60GHz |
| **Cores / Threads** | 6 cores / 12 threads |
| **CPU Frequency Range** | 800 MHz – 4.4 GHz |
| **Memory (RAM)** | 16 GB |
| **Virtualization Support** | Intel VT-x enabled |
| **Byte Order** | Little Endian |
| **Cache & SIMD Extensions** | SSE, SSE2, AVX, AVX2, AVX512, FMA, AES-NI |
| **Graphics** | NVIDIA GeForce RTX 3050 Ti |
| **Swap Space** | **Disabled** (to ensure fair memory usage across all tests) |

> Swap was disabled to maintain consistent and fair memory allocation conditions among all databases during testing.

---

## 🗄️ Database Versions

| Database | Version |
|-----------|----------|
| **PostgreSQL** | 18.0 |
| **Cassandra** | 5.0.5 |
| **MongoDB** | 8.0.15 |
| **Redis** | 8.2.2 |

---

## 📊 Data Characteristics

- **Data Volume:** 500,000 records
- **Record Structure:** Each record contains 10 fields (`attr0`–`attr4`, `_id`, `client`, `name`, `email`, `phone`, `age`, `country`), with an average record size of **~1 KB**.
- **Unique Key:** `client` + 12 random digits
- **Fields Include:** Name, Email, Phone Number, Age, Country, and 5 random fields (text/number, ~200 bytes each).
- **Access Pattern:** uniform distribution
- **Indexing:** All retrieval operations are indexed on the `_id` field of type **UUID**.
- **Data Output:** Prepared and verified before loading into databases.

---

## ⚙️ Benchmark Methodology

- Each benchmark test is **repeated 5 times**, and results are presented as **mean ± standard deviation** for all measured metrics.
- Benchmarks are executed with **50 concurrent threads** on a dataset of **500,000 records**.
- Since other database drivers use internal thread pools, **PostgreSQL** benchmarks employ manual **connection pooling** and **cursor management** to ensure comparable and fair testing conditions.
- **Swap space is disabled** to prevent OS-level paging and ensure identical memory constraints across systems.
- Metrics collected during experiments include:
  - **Throughput**
  - **Latency**
  - **CPU Utilization**
  - **Memory Usage**

---

## 🧭 Workloads Definition

A total of **six workloads** were defined to represent different operational mixes between read and update operations.

| Workload ID | Description | Operation Mix | Update Behavior |
|--------------|-------------|----------------|-----------------|
| **W1** | Pure Insert | 100% Insert | — |
| **W2** | Pure Load | 100% Read | — |
| **W3** | Read-Major | 90% Read / 10% Update | 3 fields updated per record |
| **W4** | Balanced | 50% Read / 50% Update | 3 fields updated per record |
| **W5** | Write-Major | 10% Read / 90% Update | 3 fields updated per record |
| **W6** | Pure Update | 100% Update | 3 fields updated per record |

All update operations modify **three fields per record**, maintaining data consistency while simulating realistic update workloads.

---

## 📑 Output Report Format

Each workload produces results in the following standardized format, reported as **mean ± standard deviation** over 5 runs:

| Metric | Description |
|---------|--------------|
| **Total Time** | Total execution time of the workload |
| **Avg Latency** | Average latency per operation |
| **Throughput** | Number of operations per second |
| **CPU Usage** | Mean CPU utilization during execution |
| **RAM Usage** | Mean memory usage during execution |
| **P50 Latency** | 50th percentile (median) latency |
| **P95 Latency** | 95th percentile latency |
| **P99 Latency** | 99th percentile latency |

---


# 📈 Performance Results and Analysis

All workloads were executed across four database systems — **Cassandra**, **MongoDB**, **Redis**, and **PostgreSQL** — under identical test conditions.
Each workload result represents the **mean ± standard deviation** of five benchmark runs.

---

## ⚙️ Workload 1 – 100% Insert

| Database | Total Time (s) | Avg Latency (ms) | Throughput (rec/s) | CPU (%) | RAM (%) | P50 | P95 | P99 |
|-----------|----------------|------------------|---------------------|----------|----------|------|------|------|
| **Cassandra** | 89.28 ± 0.53 | 8.84 ± 0.05 | 5600.32 ± 33.31 | 16.28 ± 0.38 | 69.40 ± 0.09 | 8.04 | 13.22 | 22.73 |
| **MongoDB** | 98.02 ± 0.50 | 9.69 ± 0.05 | 5101.06 ± 26.01 | 15.86 ± 0.10 | 19.68 ± 1.00 | 8.91 | 18.72 | 24.10 |
| **Redis** | 65.48 ± 0.99 | 6.43 ± 0.10 | 7637.44 ± 113.51 | 11.90 ± 0.71 | 16.29 ± 0.31 | 4.00 | 19.30 | 30.04 |
| **PostgreSQL** | 89.08 ± 16.07 | 8.71 ± 1.47 | 5751.06 ± 959.45 | 18.22 ± 3.23 | 16.69 ± 0.09 | 6.71 | 16.01 | 32.15 |

**Observation:**
Redis achieved the highest insertion throughput, while Cassandra and PostgreSQL showed similar insertion performance with moderate latency. MongoDB’s insertion rate was slightly lower but with stable resource usage.

---

## ⚙️ Workload 2 – 100% Read (Load)

| Database | Total Time (s) | Avg Latency (ms) | Throughput (rec/s) | CPU (%) | RAM (%) | P50 | P95 | P99 |
|-----------|----------------|------------------|---------------------|----------|----------|------|------|------|
| **Cassandra** | 117.74 ± 0.56 | 11.77 ± 0.06 | 4246.62 ± 20.25 | 14.18 ± 0.49 | 69.33 ± 0.04 | 10.61 | 18.14 | 40.18 |
| **MongoDB** | 65.31 ± 0.07 | 6.51 ± 0.01 | 7655.71 ± 7.68 | 17.45 ± 0.01 | 20.14 ± 0.05 | 6.01 | 12.44 | 15.97 |
| **Redis** | 22.35 ± 0.01 | 2.21 ± 0.00 | 22371.92 ± 14.55 | 16.35 ± 0.05 | 15.74 ± 0.02 | 1.35 | 7.28 | 12.25 |
| **PostgreSQL** | 24.85 ± 0.07 | 2.47 ± 0.01 | 20118.45 ± 60.28 | 53.61 ± 0.39 | 16.59 ± 0.05 | 2.12 | 5.51 | 7.61 |

**Observation:**
Redis and PostgreSQL dominated read-heavy workloads. PostgreSQL achieved near-Redis throughput but at a higher CPU cost. Cassandra showed higher latency due to distributed coordination overhead.

---

## ⚙️ Workload 3 – 90% Read / 10% Update

| Database | Total Time (s) | Avg Latency (ms) | Throughput (rec/s) | CPU (%) | RAM (%) | P50 | P95 | P99 |
|-----------|----------------|------------------|---------------------|----------|----------|------|------|------|
| **Cassandra** | 115.92 ± 0.76 | 11.58 ± 0.08 | 4313.58 ± 27.91 | 15.01 ± 0.36 | 69.53 ± 0.13 | 10.48 | 17.57 | 39.22 |
| **MongoDB** | 68.44 ± 0.04 | 6.82 ± 0.00 | 7306.03 ± 4.16 | 17.29 ± 0.01 | 20.12 ± 0.01 | 6.29 | 13.06 | 16.77 |
| **Redis** | 24.77 ± 0.49 | 2.46 ± 0.05 | 20187.99 ± 401.21 | 15.86 ± 0.13 | 16.12 ± 0.23 | 1.49 | 8.02 | 13.34 |
| **PostgreSQL** | 30.03 ± 5.74 | 2.97 ± 0.55 | 17049.00 ± 2626.96 | 46.75 ± 8.64 | 16.59 ± 0.06 | 2.02 | 7.81 | 20.76 |

**Observation:**
Redis maintained the fastest mixed performance, closely followed by PostgreSQL. MongoDB showed balanced performance, while Cassandra had the highest latency.

---

## ⚙️ Workload 4 – 50% Read / 50% Update

| Database | Total Time (s) | Avg Latency (ms) | Throughput (rec/s) | CPU (%) | RAM (%) | P50 | P95 | P99 |
|-----------|----------------|------------------|---------------------|----------|----------|------|------|------|
| **Cassandra** | 94.41 ± 0.68 | 9.43 ± 0.07 | 5296.07 ± 37.84 | 15.79 ± 0.39 | 69.54 ± 0.02 | 8.66 | 14.20 | 32.28 |
| **MongoDB** | 73.22 ± 0.05 | 7.29 ± 0.01 | 6828.72 ± 5.06 | 17.05 ± 0.03 | 20.12 ± 0.02 | 6.73 | 14.00 | 17.99 |
| **Redis** | 31.06 ± 0.36 | 3.08 ± 0.03 | 16098.12 ± 189.06 | 14.75 ± 0.23 | 17.16 ± 0.24 | 1.88 | 9.88 | 16.10 |
| **PostgreSQL** | 48.79 ± 9.96 | 4.84 ± 1.00 | 10551.76 ± 1885.58 | 30.39 ± 6.72 | 16.55 ± 0.06 | 2.86 | 10.75 | 21.28 |

**Observation:**
Redis led significantly in throughput, while PostgreSQL performed consistently with moderate latency. MongoDB provided balanced results; Cassandra remained steady but slower.

---

## ⚙️ Workload 5 – 10% Read / 90% Update

| Database | Total Time (s) | Avg Latency (ms) | Throughput (rec/s) | CPU (%) | RAM (%) | P50 | P95 | P99 |
|-----------|----------------|------------------|---------------------|----------|----------|------|------|------|
| **Cassandra** | 69.32 ± 0.53 | 6.92 ± 0.05 | 7213.63 ± 54.82 | 16.45 ± 0.15 | 69.62 ± 0.05 | 6.21 | 10.39 | 23.93 |
| **MongoDB** | 72.92 ± 0.04 | 7.26 ± 0.00 | 6857.02 ± 3.50 | 17.18 ± 0.05 | 20.11 ± 0.01 | 6.70 | 13.92 | 17.88 |
| **Redis** | 35.12 ± 0.05 | 3.48 ± 0.01 | 14236.33 ± 22.09 | 14.15 ± 0.23 | 17.52 ± 0.05 | 2.13 | 11.18 | 18.26 |
| **PostgreSQL** | 58.33 ± 9.58 | 5.81 ± 0.95 | 8761.42 ± 1460.27 | 25.83 ± 4.51 | 16.51 ± 0.03 | 3.60 | 12.38 | 30.11 |

**Observation:**
Redis again delivered the highest throughput with low latency. Cassandra scaled efficiently for high write ratios, while PostgreSQL exhibited increased variability.

---

## ⚙️ Workload 6 – 100% Update

| Database | Total Time (s) | Avg Latency (ms) | Throughput (rec/s) | CPU (%) | RAM (%) | P50 | P95 | P99 |
|-----------|----------------|------------------|---------------------|----------|----------|------|------|------|
| **Cassandra** | 58.62 ± 0.35 | 5.85 ± 0.04 | 8529.98 ± 51.27 | 16.23 ± 0.70 | 69.88 ± 0.04 | 5.25 | 8.62 | 19.46 |
| **MongoDB** | 71.21 ± 0.04 | 7.09 ± 0.00 | 7021.43 ± 3.63 | 17.31 ± 0.02 | 20.12 ± 0.01 | 6.55 | 13.57 | 17.41 |
| **Redis** | 35.81 ± 0.03 | 3.55 ± 0.00 | 13962.39 ± 12.45 | 14.02 ± 0.22 | 17.54 ± 0.01 | 2.17 | 11.42 | 18.79 |
| **PostgreSQL** | 63.77 ± 15.78 | 6.36 ± 1.58 | 8175.57 ± 1704.65 | 25.85 ± 5.58 | 17.59 ± 0.63 | 3.88 | 12.98 | 27.78 |

**Observation:**
Redis sustained top update throughput and lowest latency. Cassandra closely followed with stable performance, while MongoDB and PostgreSQL trailed slightly behind in high-write conditions.

---

## 🧠 Overall Insights

- **Redis** consistently achieved the **highest throughput** and **lowest latency** across all workloads, with efficient CPU and memory use.
- **PostgreSQL** showed excellent **read performance**, close to Redis, but at a higher CPU cost.
- **MongoDB** demonstrated **balanced scalability**, maintaining stable latency and moderate resource use.
- **Cassandra** excelled in **write-heavy** scenarios with predictable performance and strong stability.

---

✨ *All systems were tested under identical, Dockerized environments with 50 concurrent threads on 500k records. Results reflect mean ± standard deviation from five independent runs.*
