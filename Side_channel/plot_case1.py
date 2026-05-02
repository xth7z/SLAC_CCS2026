import matplotlib.pyplot as plt
import numpy as np

def sample(arr, sca, cache_size):
    l0 = len(arr)
    l1 = l0 // sca
    arr_sca = []
    for i in range(l1):
        arr_sca.append(cache_size - np.max(arr[i * sca:(i + 1) * sca]))
    return arr_sca

def sample2(arr, sca):
    l0 = len(arr)
    l1 = l0 // sca
    arr_sca = []
    for i in range(l1):
        arr_sca.append(np.sum(arr[i * sca:(i + 1) * sca]))
    return arr_sca


arr = np.loadtxt("trace.txt", dtype=int)
print(arr.shape)
arr0 = np.zeros([arr.shape[0] // 2, arr.shape[1]])
arr1 = np.zeros([arr.shape[0] // 2, arr.shape[1]])

c = 0
for i in range(arr.shape[0]):
    if i % 2 == 0:
        arr0[i // 2] = arr[i + c]
    else:
        arr1[i // 2] = arr[i + c]

result = np.mean(arr0, axis=0) - np.mean(arr1, axis=0)

# 将 result 近似到最接近的整数
result_int = np.rint(result).astype(int)

# 如果 result 表示 cache-line count，一般不应该为负，可以裁剪到 0
# result_int = np.clip(result_int, 0, None)

# plt.plot(result_int, label="rounded result")
plt.plot(result, label="rounded result")
# plt.plot(np.mean(arr0, axis=0))


real_trace = np.zeros(4096, dtype=int)
with open("Target_address.txt", "r") as f:
    for line in f:
        line = line.strip()
        if line:
            real_trace[int(line)] += 1

plt.plot(real_trace, label="real trace")
plt.show()


# 检查长度是否一致
if len(result_int) != len(real_trace):
    raise ValueError(
        f"Length mismatch: result_int has length {len(result_int)}, "
        f"but real_trace has length {len(real_trace)}"
    )

# undercount: result_int 比 real_trace 小的部分
undercount = np.maximum(real_trace - result_int, 0)

# overcount: result_int 比 real_trace 大的部分
overcount = np.maximum(result_int - real_trace, 0)

total_real = np.sum(real_trace)

undercount_rate = np.sum(undercount) / total_real if total_real > 0 else 0
overcount_rate = np.sum(overcount) / total_real if total_real > 0 else 0

print("Total real count:", total_real)
print("Total predicted count:", np.sum(result_int))

print("Total undercount:", np.sum(undercount))
print("Total overcount:", np.sum(overcount))

print("Undercount rate:", undercount_rate)
print("Overcount rate:", overcount_rate)

# 也可以看有多少个 cache set 发生了 undercount / overcount
num_undercount_sets = np.sum(result_int < real_trace)
num_overcount_sets = np.sum(result_int > real_trace)
num_equal_sets = np.sum(result_int == real_trace)

print("Undercount sets:", num_undercount_sets)
print("Overcount sets:", num_overcount_sets)
print("Equal sets:", num_equal_sets)