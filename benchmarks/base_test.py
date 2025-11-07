import random
import time
import statistics
import uuid

import psutil
from concurrent.futures import ThreadPoolExecutor

class BaseLoadTest:
    def __init__(self, db_connector, num_records=500_000):
        self.db = db_connector
        self.num_records = num_records

    def generate_record(self, i):
        raise NotImplementedError("generate_record must be implemented in subclass.")


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
        total_time = end_total - start_total
        avg_latency = sum(latencies) / len(latencies)
        throughput = self.num_records / total_time
        cpu_percent = psutil.cpu_percent(interval=1)
        ram_percent = psutil.virtual_memory().percent

        return total_time, avg_latency, throughput, cpu_percent, ram_percent

    def run_repeats_insert_concurrent(self, repeats=5, num_threads=50):
        total_times, avg_latencies, throughputs, cpu_usages, ram_usages = [], [], [], [], []

        for run in range(repeats):
            print(f"\n--- Run Insert {run + 1} ({num_threads} threads) ---")
            total_time, avg_latency, throughput, cpu, ram = self.run_insert_test_concurrent(num_threads)
            print(f"Run {run + 1}: Total time = {total_time:.2f}s, "
                  f"Avg latency = {avg_latency*1000:.2f}ms, "
                  f"Throughput = {throughput:.2f} rec/s, "
                  f"CPU = {cpu:.1f}%, RAM = {ram:.1f}%")

            total_times.append(total_time)
            avg_latencies.append(avg_latency*1000)
            throughputs.append(throughput)
            cpu_usages.append(cpu)
            ram_usages.append(ram)

        print("\n--- Insert Summary ---")
        print(f"Total time: {statistics.mean(total_times):.2f} ± {statistics.stdev(total_times):.2f} s")
        print(f"Avg latency: {statistics.mean(avg_latencies):.2f} ± {statistics.stdev(avg_latencies):.2f} ms")
        print(f"Throughput: {statistics.mean(throughputs):.2f} ± {statistics.stdev(throughputs):.2f} rec/s")
        print(f"CPU usage: {statistics.mean(cpu_usages):.2f} ± {statistics.stdev(cpu_usages):.2f} %")
        print(f"RAM usage: {statistics.mean(ram_usages):.2f} ± {statistics.stdev(ram_usages):.2f} %")


    def _read_chunk(self, start, end):
        latencies = []
        for i in range(start, end):
            start_t = time.time()
            record_id = uuid.UUID(int=i)
            record = self.db.read_user_by_id("users", record_id)
            end_t = time.time()
            latencies.append(end_t - start_t)
        return latencies

    def run_read_test_concurrent(self, num_threads=50):
        latencies = []
        chunk_size = self.num_records // num_threads
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
        total_time = end_total - start_total
        avg_latency = sum(latencies) / len(latencies)
        throughput = self.num_records / total_time
        cpu_percent = psutil.cpu_percent(interval=1)
        ram_percent = psutil.virtual_memory().percent

        return total_time, avg_latency, throughput, cpu_percent, ram_percent

    def run_read_repeats_concurrent(self, repeats=5, num_threads=50):
        total_times, avg_latencies, throughputs, cpu_usages, ram_usages = [], [], [], [], []

        for run in range(repeats):
            print(f"\n--- READ Run {run + 1} ({num_threads} threads) ---")
            total_time, avg_latency, throughput, cpu, ram = self.run_read_test_concurrent(num_threads)
            print(f"READ Run {run + 1}: Total time = {total_time:.2f}s, "
                  f"Avg latency = {avg_latency*1000:.2f}ms, "
                  f"Throughput = {throughput:.2f} rec/s, "
                  f"CPU = {cpu:.1f}%, RAM = {ram:.1f}%")

            total_times.append(total_time)
            avg_latencies.append(avg_latency*1000)
            throughputs.append(throughput)
            cpu_usages.append(cpu)
            ram_usages.append(ram)

    def mixed_chunk(self, start, end, read_ratio=0.1):
        """عملیات خواندن و به‌روزرسانی ترکیبی روی رکوردها"""
        import string

        def random_string(n=100):
            return ''.join(random.choices(string.ascii_letters + string.digits, k=n))

        local_latencies = []
        for i in range(start, end):
            start_t = time.time()
            key = str(uuid.UUID(int=i))  # کلید همیشه str
            if random.random() < read_ratio:
                self.db.read_user_by_id(key)
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
        start_total = time.time()

        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = []
            for t in range(num_threads):
                start_idx = t * chunk_size
                end_idx = (t + 1) * chunk_size if t < num_threads - 1 else self.num_records
                # فراخوانی متد mixed_chunk
                futures.append(executor.submit(self.mixed_chunk, start_idx, end_idx, read_ratio))

            for future in futures:
                latencies.extend(future.result())

        end_total = time.time()
        total_time = end_total - start_total
        avg_latency = sum(latencies) / len(latencies)
        throughput = self.num_records / total_time

        import psutil
        cpu_percent = psutil.cpu_percent(interval=None)
        ram_percent = psutil.virtual_memory().percent

        return total_time, avg_latency, throughput, cpu_percent, ram_percent

    def run_mixed_repeats_concurrent(self, read_ratio=0.1, repeats=5, num_threads=50):
        import statistics
        total_times, avg_latencies, throughputs, cpu_usages, ram_usages = [], [], [], [], []

        for run in range(repeats):
            print(f"\n--- Mixed Run {run + 1}: READ {read_ratio * 100:.0f}% / UPDATE {(1 - read_ratio) * 100:.0f}% ---")
            total_time, avg_latency, throughput, cpu, ram = self.run_mixed_test_concurrent(read_ratio, num_threads)

            print(f"Run {run + 1}: Total time = {total_time:.2f}s, "
                  f"Avg latency = {avg_latency * 1000:.2f}ms, "
                  f"Throughput = {throughput:.2f} rec/s, "
                  f"CPU = {cpu:.1f}%, RAM = {ram:.1f}%")

            total_times.append(total_time)
            avg_latencies.append(avg_latency * 1000)
            throughputs.append(throughput)
            cpu_usages.append(cpu)
            ram_usages.append(ram)

        print("\n--- Mixed Summary ---")
        print(f"Total time: {statistics.mean(total_times):.2f} ± {statistics.stdev(total_times):.2f} s")
        print(f"Avg latency: {statistics.mean(avg_latencies):.2f} ± {statistics.stdev(avg_latencies):.2f} ms")
        print(f"Throughput: {statistics.mean(throughputs):.2f} ± {statistics.stdev(throughputs):.2f} rec/s")
        print(f"CPU usage: {statistics.mean(cpu_usages):.2f} ± {statistics.stdev(cpu_usages):.2f} %")
        print(f"RAM usage: {statistics.mean(ram_usages):.2f} ± {statistics.stdev(ram_usages):.2f} %")
