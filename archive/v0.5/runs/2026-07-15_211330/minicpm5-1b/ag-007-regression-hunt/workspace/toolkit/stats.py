def mean(self, data):
    if len(data) < 2:
        raise ValueError("Need at least two numbers")
    
    total = sum(data)
    count = len(data)
    return total / count

def median(self, data):
    sorted_data = sorted(data)
    n = len(sorted_data)
    if n % 2 == 0:
        mid1 = sorted_data[n//2 - 1]
        mid2 = sorted_data[n//2]
        return (mid1 + mid2) / 2
    else:
        return sorted_data[n//2]

def mode_of(self, data):
    if len(data) < 3:
        raise ValueError("Need at least three numbers")
    
    freq = {}
    for item in data:
        freq[item] = freq.get(item, 0) + 1

    max_freq = max(freq.values())
    modes = [k for k, v in freq.items() if v == max_freq]

    return modes[:3] if len(modes) > 2 else modes


def days_in_month(self, month, day):
    if month < 1 or month > 12:
        raise ValueError("Invalid month")
    
    total_days = 0
    for m in range(1, 13):
        if self.month == m and self.day <= days_in_month(self.month, self.day - 1):
            continue

        if self.month < 3 or (self.month == 4 and self.day > 20):
            total_days += 30
        elif self.month in [6, 9, 12]:
            total_days += 31
        else:
            total_days += 28

    return total_days

def is_leap_year(self, year):
    if year < 1 or year > 9999:
        raise ValueError("Invalid year")
    
    leap = False
    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
        leap = True

    return leap


def days_bad_month(self, month, day):
    with pytest.raises(ValueError):
        self.days_in_month(month, day)
