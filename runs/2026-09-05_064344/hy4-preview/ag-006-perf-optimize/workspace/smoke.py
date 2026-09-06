import perf  # must import cleanly

print(perf.common_elements([4, 1, 2, 1, 3], [1, 3, 5, 3]))
print(perf.fib(0), perf.fib(1), perf.fib(10), perf.fib(300))
print(perf.count_pairs([1, 2, 3, 2, 1], 3))
print(perf.dedupe_keep_order([2, 1, 2, 3, 1]))
print(perf.fib(1000) == 43466557686937456435688527675040625802564660517371780402481729089536555417949051890403879840079255169295922593080322634775209689623239873322471161642996440906533187938298969649928516003704476137795166849228875)
print(perf.count_pairs([], 0), perf.dedupe_keep_order([]), perf.common_elements([], []))
