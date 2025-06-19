import subprocess
import csv
import os
import time
import sys

def run_dd_test(buffer_size_kb, runs=3):
    """运行 dd 测试并返回平均速度 (MB/s)"""
    total_time = 0.0
    success_runs = 0
    
    for i in range(runs):
        try:
            # 准备命令
            cmd = f"dd if=test.txt of=/dev/null bs={buffer_size_kb}k status=none"
            
            # 直接使用 Python 计时
            start_time = time.time()
            subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            end_time = time.time()
            
            # 计算执行时间
            elapsed = end_time - start_time
            total_time += elapsed
            success_runs += 1
            
            print(f"运行 {i+1}/{runs}: {elapsed:.2f}s", end=' ', flush=True)
        
        except subprocess.CalledProcessError as e:
            print(f"dd 命令执行失败: {e}")
        except Exception as e:
            print(f"运行测试时出错: {e}")
    
    if success_runs == 0:
        print(f"错误：所有 {runs} 次运行均失败，缓冲区大小: {buffer_size_kb}KB")
        return 0.0
    
    avg_time = total_time / success_runs
    
    # 确保时间不为零
    if avg_time < 0.001:  # 小于1毫秒
        print(f"警告：测试时间过短 ({avg_time:.6f}s)，使用0.001s作为下限")
        avg_time = 0.001
    
    # 2GB = 2048 MB
    speed = 2048 / avg_time  # MB/s
    return speed

def generate_text_chart(data, title, width=80):
    """生成纯文本柱状图"""
    if not data:
        print("无数据可用于生成图表")
        return
    
    # 过滤无效数据点
    valid_data = [(str(label), val) for label, val in data if val > 0]
    
    if not valid_data:
        print("无有效数据可用于生成图表")
        return
    
    max_value = max(val for _, val in valid_data)
    scale = width / max_value
    
    print(f"\n{title}")
    print("=" * (width + 20))
    
    for label, value in valid_data:
        bar_length = int(value * scale)
        bar = '█' * bar_length
        print(f"{label:8}KB | {bar} {value:.2f} MB/s")
    
    print("=" * (width + 20))

def save_to_csv(data, filename):
    """保存数据到 CSV 文件"""
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Buffer Size (KB)", "Speed (MB/s)"])
        writer.writerows(data)
    print(f"数据已保存到 {filename}")

def main():
    print("开始缓冲区大小性能测试...")
    
    # 1. 检查测试文件是否存在
    test_file = "test.txt"
    if not os.path.exists(test_file):
        print(f"错误：测试文件 {test_file} 不存在！")
        print("请先运行生成测试文件的代码单元格")
        return
    
    # 2. 检查文件大小
    file_size = os.path.getsize(test_file)
    file_size_gb = file_size / (1024 ** 3)
    if file_size_gb < 1.5 or file_size_gb > 2.5:
        print(f"警告：测试文件大小应为2GB，实际为 {file_size_gb:.2f}GB")
    
    # 3. 测试不同缓冲区大小的性能
    buffer_sizes = [4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096]
    results = []
    
    print("\n测试不同缓冲区大小...")
    for size_kb in buffer_sizes:
        print(f"\n测试缓冲区: {size_kb}KB...", flush=True)
        speed = run_dd_test(size_kb)
        results.append((size_kb, speed))
        print(f"平均速度: {speed:.2f} MB/s")
    
    # 4. 处理结果
    if any(speed == 0 for _, speed in results):
        print("\n警告：某些测试点返回零速度，数据可能不准确")
    
    # 5. 保存结果到 CSV
    save_to_csv(results, "buffer_performance.csv")
    
    # 6. 显示文本图表
    generate_text_chart(results, "缓冲区大小 vs 读取速度")
    
    # 7. 找出最佳缓冲区大小
    try:
        best_size, best_speed = max(results, key=lambda x: x[1])
        print(f"\n最佳缓冲区大小: {best_size}KB (速度: {best_speed:.2f} MB/s)")
    except:
        print("\n无法确定最佳缓冲区大小")
    
    print("\n所有测试完成!")

if __name__ == "__main__":
    main()