def days_in_month(self, month, day):
    if month < 1 or month > 12:
        raise ValueError("Invalid month")
    if day < 1 or day > 31:
        raise ValueError("Invalid day")

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

def days_in_month(self, month, day):
    if month < 1 or month > 12:
        raise ValueError("Invalid month")
    if day < 1 or day > 31:
        raise ValueError("Invalid day")

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


def mean(self, data):
    if len(data) < 2:
        raise ValueError("Need at least two numbers")
    
    total = sum(data)
    count = len(data)
    return total / count
