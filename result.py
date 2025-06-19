data = {
    "Implementation": ['mycat2', 'mycat3', 'mycat4', 'mycat5', 'mycat6', 'system cat'],
    "Time (ms)": [289.3, 282.7, 280.7, 171.1, 174.1, 150.0],
    "Speedup": [1.0, 1.02, 1.03, 1.69, 1.66, 1.93]
}

base_time = data["Time (ms)"][0]
data["Speedup"] = [base_time / t for t in data["Time (ms)"]]

print("\ncat实现性能比较")
print("=" * 65)
print(f"{'实现':<12} | {'时间 (ms)':>10} | {'相对性能':>12} | {'提升倍数':>12} | {'性能柱状图'}")
print("-" * 65)

for i in range(len(data["Implementation"])):
    impl = data["Implementation"][i]
    time_val = data["Time (ms)"][i]
    speedup = data["Speedup"][i]
    
    bar_length = int(speedup * 20)
    bar = '█' * bar_length
    
    print(f"{impl:<12} | {time_val:>10.1f} | {speedup:>12.2f}x | {speedup:>12.2f}x | {bar}")

print("=" * 65)
print("注：相对性能和提升倍数均基于mycat2作为基准")