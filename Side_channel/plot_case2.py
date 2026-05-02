import matplotlib.pyplot as plt
import numpy as np

def sample2(arr, sca):
    l0 = len(arr)
    l1 = l0 // sca
    arr_sca = []
    for i in range(l1):
        arr_sca.append(np.sum(arr[i * sca:(i + 1) * sca]))
    return np.array(arr_sca)


TRACE_FILE = "trace.txt"
TARGET_FILE = "Target_address.txt"

SUPERSET_SIZE = 64
THRESHOLD = 32


# ======================
# Load all traces
# ======================
all_arr = np.loadtxt(TRACE_FILE, dtype=int)
print("all_arr shape:", all_arr.shape)

if all_arr.shape[0] % 2 != 0:
    raise ValueError("trace.txt must contain an even number of rows because every two rows form one trace pair.")


arr = all_arr[0:2, :]
print("plot arr shape:", arr.shape)

arr0 = np.zeros([arr.shape[0] // 2, arr.shape[1]])
arr1 = np.zeros([arr.shape[0] // 2, arr.shape[1]])

c = 0
for i in range(arr.shape[0]):
    if i % 2 == 0:
        arr0[i // 2] = arr[i + c]
    else:
        arr1[i // 2] = arr[i + c]

result = np.mean(arr0, axis=0) - np.mean(arr1, axis=0)
result = sample2(result, SUPERSET_SIZE)

plt.plot(result)


# ======================
# Generate the real trace from target addresses
# ======================
real_trace = np.zeros(all_arr.shape[1], dtype=int)

with open(TARGET_FILE, "r") as f:
    for line in f:
        line = line.strip()
        if line:
            real_trace[int(line)] += 1

real_trace = sample2(real_trace, SUPERSET_SIZE)

plt.plot(real_trace, label="real trace")
plt.show()

print("First pair exact value accuracy:", np.sum(real_trace == result) / len(real_trace))


# ======================
# Compute average FNR and FPR over all trace pairs
# ======================
real_binary = real_trace >= THRESHOLD

num_pairs = all_arr.shape[0] // 2

fnr_list = []
fpr_list = []

for pair_idx in range(num_pairs):
    # Each trace pair consists of one even row and one odd row.
    even_trace = all_arr[2 * pair_idx]
    odd_trace = all_arr[2 * pair_idx + 1]

    # Compute the pair-level difference trace.
    pair_result = even_trace - odd_trace

    # Aggregate cache sets into supersets.
    pair_result = sample2(pair_result, SUPERSET_SIZE)

    # Convert the superset trace into a binary prediction.
    pred_binary = pair_result >= THRESHOLD

    # Compute confusion matrix entries.
    TP = np.sum((pred_binary == 1) & (real_binary == 1))
    TN = np.sum((pred_binary == 0) & (real_binary == 0))
    FP = np.sum((pred_binary == 1) & (real_binary == 0))
    FN = np.sum((pred_binary == 0) & (real_binary == 1))

    # False Negative Rate: missed true active supersets.
    fnr = FN / (FN + TP) if (FN + TP) > 0 else 0

    # False Positive Rate: inactive supersets incorrectly predicted as active.
    fpr = FP / (FP + TN) if (FP + TN) > 0 else 0

    fnr_list.append(fnr)
    fpr_list.append(fpr)

fnr_list = np.array(fnr_list)
fpr_list = np.array(fpr_list)

print("Number of trace pairs:", num_pairs)
print("Average FNR:", np.mean(fnr_list))
print("Average FPR:", np.mean(fpr_list))