import random
import time
import statistics
import uuid
import psutil
from concurrent.futures import ThreadPoolExecutor
import string
import threading
import numpy as np

class BaseLoadTest:
    uuid_as_str = True

    def __init__(self, db_connector, num_records=500_000):
        self.db = db_connector
        self.num_records = num_records

    def generate_record(self, i):
        random_fields = [
            "".join(random.choices(string.ascii_letters + string.digits, k=200))
            for _ in range(5)
        ]
        record_id = str(uuid.UUID(int=i)) if self.uuid_as_str else uuid.UUID(int=i)
        return {
            "id": record_id,
            "client": f"client{i:06d}{random.randint(100000000000, 999999999999)}",
            "name": f"user{i}",
            "email": f"user{i}@example.com",
            "phone": f"+1{random.randint(1000000000, 9999999999)}",
            "age": 20 + i % 50,
            "country": random.choice(["US", "UK", "DE", "FR", "IN"]),
            "attr0": random_fields[0],
            "attr1": random_fields[1],
            "attr2": random_fields[2],
            "attr3": random_fields[3],
            "attr4": random_fields[4],
        }

    def _insert_chunk(self, start, end):
        latencies = []
        for i in range(start, end):
            record = self.generate_record(i)
            start_t = time.time()
            self.db.insert("users", record)
            end_t = time.time()
            latencies.append(end_t - start_t)
        return latencies

    def run_insert_test_concurrent(self, num_threads=50):
        self.db.truncate_table("users")
        latencies = []
        chunk_size = self.num_records // num_threads
        stop_event = threading.Event()
        cpu_samples, ram_samples = [], []

        def sample_resources():
            while not stop_event.is_set():
                cpu_samples.append(psutil.cpu_percent(interval=0.1))
                ram_samples.append(psutil.virtual_memory().percent)

        sampler_thread = threading.Thread(target=sample_resources)
        sampler_thread.start()
        start_total = time.time()

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = []
            for t in range(num_threads):
                start_idx = t * chunk_size
                end_idx = (t + 1) * chunk_size if t < num_threads - 1 else self.num_records
                futures.append(executor.submit(self._insert_chunk, start_idx, end_idx))

            for future in futures:
                latencies.extend(future.result())

        end_total = time.time()
        stop_event.set()
        sampler_thread.join()

        total_time = end_total - start_total
        avg_latency = sum(latencies) / len(latencies)
        throughput = self.num_records / total_time
        cpu_percent = sum(cpu_samples) / len(cpu_samples)
        ram_percent = sum(ram_samples) / len(ram_samples)
        latencies_ms = [l * 1000 for l in latencies]
        p50, p95, p99 = np.percentile(latencies_ms, [50, 95, 99])
        return total_time, avg_latency, throughput, cpu_percent, ram_percent, p50, p95, p99

    def run_repeats_insert_concurrent(self, repeats=5, num_threads=50):
        total_times, avg_latencies, throughputs, cpu_usages, ram_usages = [], [], [], [], []
        p50_list, p95_list, p99_list = [], [], []

        for run in range(repeats):
            print(f"\n--- Run Insert {run + 1} ({num_threads} threads) ---")
            total_time, avg_latency, throughput, cpu, ram, p50, p95, p99 = self.run_insert_test_concurrent(num_threads)
            print(f"Run {run + 1}: Total time = {total_time:.2f}s, "
                  f"Avg latency = {avg_latency*1000:.2f}ms, "
                  f"Throughput = {throughput:.2f} rec/s, "
                  f"CPU = {cpu:.1f}%, RAM = {ram:.1f}%, "
                  f"P50 = {p50:.2f}ms, P95 = {p95:.2f}ms, P99 = {p99:.2f}ms")

            total_times.append(total_time)
            avg_latencies.append(avg_latency*1000)
            throughputs.append(throughput)
            cpu_usages.append(cpu)
            ram_usages.append(ram)
            p50_list.append(p50)
            p95_list.append(p95)
            p99_list.append(p99)

        print("\n--- Insert Summary ---")
        print(f"Total time: {statistics.mean(total_times):.2f} ± {statistics.stdev(total_times):.2f} s")
        print(f"Avg latency: {statistics.mean(avg_latencies):.2f} ± {statistics.stdev(avg_latencies):.2f} ms")
        print(f"Throughput: {statistics.mean(throughputs):.2f} ± {statistics.stdev(throughputs):.2f} rec/s")
        print(f"CPU usage: {statistics.mean(cpu_usages):.2f} ± {statistics.stdev(cpu_usages):.2f} %")
        print(f"RAM usage: {statistics.mean(ram_usages):.2f} ± {statistics.stdev(ram_usages):.2f} %")
        print(f"P50 latency: {statistics.mean(p50_list):.2f} ms")
        print(f"P95 latency: {statistics.mean(p95_list):.2f} ms")
        print(f"P99 latency: {statistics.mean(p99_list):.2f} ms")

    def _read_chunk(self, start, end):
        latencies = []
        for i in range(start, end):
            start_t = time.time()
            record_id = str(uuid.UUID(int=i)) if self.uuid_as_str else uuid.UUID(int=i)
            self.db.read_user_by_id("users", record_id)
            end_t = time.time()
            latencies.append(end_t - start_t)
        return latencies

    def run_read_test_concurrent(self, num_threads=50):
        latencies = []
        chunk_size = self.num_records // num_threads
        stop_event = threading.Event()
        cpu_samples, ram_samples = [], []

        def sample_resources():
            while not stop_event.is_set():
                cpu_samples.append(psutil.cpu_percent(interval=0.1))
                ram_samples.append(psutil.virtual_memory().percent)

        sampler_thread = threading.Thread(target=sample_resources)
        sampler_thread.start()
        start_total = time.time()

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = []
            for t in range(num_threads):
                start_idx = t * chunk_size
                end_idx = (t + 1) * chunk_size if t < num_threads - 1 else self.num_records
                futures.append(executor.submit(self._read_chunk, start_idx, end_idx))

            for future in futures:
                latencies.extend(future.result())

        end_total = time.time()
        stop_event.set()
        sampler_thread.join()

        total_time = end_total - start_total
        avg_latency = sum(latencies) / len(latencies)
        throughput = self.num_records / total_time
        cpu_percent = sum(cpu_samples) / len(cpu_samples)
        ram_percent = sum(ram_samples) / len(ram_samples)
        latencies_ms = [l * 1000 for l in latencies]
        p50, p95, p99 = np.percentile(latencies_ms, [50, 95, 99])
        return total_time, avg_latency, throughput, cpu_percent, ram_percent, p50, p95, p99

    def run_read_repeats_concurrent(self, repeats=5, num_threads=50):
        total_times, avg_latencies, throughputs, cpu_usages, ram_usages = [], [], [], [], []
        p50_list, p95_list, p99_list = [], [], []

        for run in range(repeats):
            print(f"\n--- READ Run {run + 1} ({num_threads} threads) ---")
            total_time, avg_latency, throughput, cpu, ram, p50, p95, p99 = self.run_read_test_concurrent(num_threads)
            print(f"READ Run {run + 1}: Total time = {total_time:.2f}s, "
                  f"Avg latency = {avg_latency*1000:.2f}ms, "
                  f"Throughput = {throughput:.2f} rec/s, "
                  f"CPU = {cpu:.1f}%, RAM = {ram:.1f}%, "
                  f"P50 = {p50:.2f}ms, P95 = {p95:.2f}ms, P99 = {p99:.2f}ms")

            total_times.append(total_time)
            avg_latencies.append(avg_latency*1000)
            throughputs.append(throughput)
            cpu_usages.append(cpu)
            ram_usages.append(ram)
            p50_list.append(p50)
            p95_list.append(p95)
            p99_list.append(p99)

        print("\n--- READ Summary ---")
        print(f"Total time: {statistics.mean(total_times):.2f} ± {statistics.stdev(total_times):.2f} s")
        print(f"Avg latency: {statistics.mean(avg_latencies):.2f} ± {statistics.stdev(avg_latencies):.2f} ms")
        print(f"Throughput: {statistics.mean(throughputs):.2f} ± {statistics.stdev(throughputs):.2f} rec/s")
        print(f"CPU usage: {statistics.mean(cpu_usages):.2f} ± {statistics.stdev(cpu_usages):.2f} %")
        print(f"RAM usage: {statistics.mean(ram_usages):.2f} ± {statistics.stdev(ram_usages):.2f} %")
        print(f"P50 latency: {statistics.mean(p50_list):.2f} ms")
        print(f"P95 latency: {statistics.mean(p95_list):.2f} ms")
        print(f"P99 latency: {statistics.mean(p99_list):.2f} ms")

    def mixed_chunk(self, start, end, read_ratio=0.1):
        def random_string(n=100):
            return ''.join(random.choices(string.ascii_letters + string.digits, k=n))
        local_latencies = []
        for i in range(start, end):
            start_t = time.time()
            key = str(uuid.UUID(int=i)) if self.uuid_as_str else uuid.UUID(int=i)
            if random.random() < read_ratio:
                self.db.read_user_by_id("users", key)
            else:
                updates = {
                    "attr0": random_string(100),
                    "attr1": random_string(100),
                    "attr2": random_string(100)
                }
                self.db.update_user_fields("users", key, updates)
            end_t = time.time()
            local_latencies.append(end_t - start_t)
        return local_latencies

    def run_mixed_test_concurrent(self, read_ratio=0.1, num_threads=50):
        latencies = []
        chunk_size = self.num_records // num_threads
        stop_event = threading.Event()
        cpu_samples, ram_samples = [], []

        def sample_resources():
            while not stop_event.is_set():
                cpu_samples.append(psutil.cpu_percent(interval=0.1))
                ram_samples.append(psutil.virtual_memory().percent)

        sampler_thread = threading.Thread(target=sample_resources)
        sampler_thread.start()
        start_total = time.time()

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = []
            for t in range(num_threads):
                start_idx = t * chunk_size
                end_idx = (t + 1) * chunk_size if t < num_threads - 1 else self.num_records
                futures.append(executor.submit(self.mixed_chunk, start_idx, end_idx, read_ratio))

            for future in futures:
                latencies.extend(future.result())

        end_total = time.time()
        stop_event.set()
        sampler_thread.join()

        total_time = end_total - start_total
        avg_latency = sum(latencies) / len(latencies)
        throughput = self.num_records / total_time
        cpu_percent = sum(cpu_samples) / len(cpu_samples)
        ram_percent = sum(ram_samples) / len(ram_samples)
        latencies_ms = [l*1000 for l in latencies]
        p50, p95, p99 = np.percentile(latencies_ms, [50, 95, 99])
        return total_time, avg_latency, throughput, cpu_percent, ram_percent, p50, p95, p99

    def run_mixed_repeats_concurrent(self, read_ratio=0.1, repeats=5, num_threads=50):
        total_times, avg_latencies, throughputs, cpu_usages, ram_usages = [], [], [], [], []
        p50_list, p95_list, p99_list = [], [], []

        for run in range(repeats):
            print(f"\n--- Mixed Run {run + 1}: Threads {num_threads}, READ {read_ratio*100:.0f}% / UPDATE {(1-read_ratio)*100:.0f}% ---")
            total_time, avg_latency, throughput, cpu, ram, p50, p95, p99 = self.run_mixed_test_concurrent(read_ratio, num_threads)
            print(f"Run {run + 1}: Total time = {total_time:.2f}s, "
                  f"Avg latency = {avg_latency*1000:.2f}ms, "
                  f"Throughput = {throughput:.2f} rec/s, "
                  f"CPU = {cpu:.1f}%, RAM = {ram:.1f}%, "
                  f"P50 = {p50:.2f}ms, P95 = {p95:.2f}ms, P99 = {p99:.2f}ms")

            total_times.append(total_time)
            avg_latencies.append(avg_latency*1000)
            throughputs.append(throughput)
            cpu_usages.append(cpu)
            ram_usages.append(ram)
            p50_list.append(p50)
            p95_list.append(p95)
            p99_list.append(p99)

        print("\n--- Mixed Summary ---")
        print(f"Total time: {statistics.mean(total_times):.2f} ± {statistics.stdev(total_times):.2f} s")
        print(f"Avg latency: {statistics.mean(avg_latencies):.2f} ± {statistics.stdev(avg_latencies):.2f} ms")
        print(f"Throughput: {statistics.mean(throughputs):.2f} ± {statistics.stdev(throughputs):.2f} rec/s")
        print(f"CPU usage: {statistics.mean(cpu_usages):.2f} ± {statistics.stdev(cpu_usages):.2f} %")
        print(f"RAM usage: {statistics.mean(ram_usages):.2f} ± {statistics.stdev(ram_usages):.2f} %")
        print(f"P50 latency: {statistics.mean(p50_list):.2f} ms")
        print(f"P95 latency: {statistics.mean(p95_list):.2f} ms")
        print(f"P99 latency: {statistics.mean(p99_list):.2f} ms")
