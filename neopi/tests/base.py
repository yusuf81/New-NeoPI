"""Base test class definition."""

import math

class Test:
    """Base class for all tests"""
    def __init__(self):
        # high_is_bad means the higher the metric, the more suspicious it is
        self.high_is_bad = True
        self.results = []
        self.mean = 0
        self.stddev = 0
    def calculate(self, input_data, filepath):
        """Calculate metric for given data. Should be overridden by child classes."""
        raise NotImplementedError("Calculate method must be implemented by child class")

    def block_calculate(self, block_size, input_data, filepath):
        """Calculate metric for blocks of data of given size."""
        if not input_data:
            return {"value": 0, "position": 0}
        num_blocks = int(math.ceil(len(input_data) / block_size))
        max_entropy = float('-inf')
        min_entropy = float('inf')
        pos = 0
        for i in range(num_blocks):
            start = i * block_size
            block_data = input_data[start:start + block_size]
            calc_result = self.calculate(block_data, filepath)
            
            if self.high_is_bad:
                if max_entropy <= calc_result:
                    max_entropy = calc_result
                    pos = start
            elif min_entropy > calc_result:
                min_entropy = calc_result
                pos = start
        result = {
            "value": max_entropy if self.high_is_bad else min_entropy,
            "position": pos
        }
        self.results.append({"filename": filepath, **result})
        return result

    def calc_mean(self):
        """Calculate mean of all results."""
        if not self.results:
            return 0
        return sum(r["value"] for r in self.results) / len(self.results)

    def calc_std_dev(self):
        """Calculate standard deviation of results."""
        if not self.results:
            return 0
        self.mean = self.calc_mean()
        square_diffs = sum((r["value"] - self.mean) ** 2 for r in self.results)
        return math.sqrt(square_diffs / len(self.results))

    def flag_alarm(self, deviation_thresh=1.5):
        """Flag suspicious files based on deviation from mean."""
        self.mean = self.calc_mean()
        self.stddev = self.calc_std_dev()

        flag_list = []
        for res in self.results:
            distance = abs(res["value"] - self.mean)
            if distance > (deviation_thresh * self.stddev):
                if ((self.high_is_bad and res["value"] > self.mean) or
                        (not self.high_is_bad and res["value"] < self.mean)):
                    percentage = distance / self.stddev if self.stddev > 0 else float('inf')
                    res["percentage"] = percentage
                    flag_list.append(res)

        return sorted(flag_list, key=lambda x: x["percentage"])

    def sort(self):
        """Sort results by value and add ranking."""
        # Filter out results with None values
        self.results = [r for r in self.results if r["value"] is not None]
        
        if not self.results:
            return
        self.results.sort(
            key=lambda x: x["value"],
            reverse=self.high_is_bad
        )
        
        rank = 1
        prev_value = None
        for i, result in enumerate(self.results, 1):
            if prev_value is not None and prev_value != result["value"]:
                rank = i
            result["rank"] = rank
            prev_value = result["value"]

    def printer(self, result_count, block_mode=False):
        """Print top results."""
        test_name = self.__class__.__name__
        print(f"\n[[ Top {result_count} {test_name} results ]]")
        
        if not self.results:
            print(" No results found")
            return
        
        result_count = min(result_count, len(self.results))
        
        # Print header
        if block_mode:
            print(" Value      Position           Filename")
            print(" -----      --------           --------")
        else:
            print(" Value           Filename")
            print(" -----           --------")
        for result in self.results[:result_count]:
            if block_mode:
                print(
                    f' {result["value"]:>7.4f}   '
                    f'at byte {result["position"]:<8}     '
                    f'{result["filename"]}'
                )
            else:
                print(f' {result["value"]:>7.4f}        {result["filename"]}')
