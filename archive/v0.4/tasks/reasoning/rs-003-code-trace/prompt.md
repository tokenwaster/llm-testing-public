Predict the exact output of this Python program without running it. Explain what
happens at each step, paying attention to which operations alias and which copy.

```python
x = [1, 2, 3]
y = x
y += [4]
z = y[1:]
z[0] = 99
print(len(x), x[1], z[0])
```

Give the printed line exactly as it appears (numbers separated by single spaces).
