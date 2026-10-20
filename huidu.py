# import cv2
# import numpy as np
#
# img = cv2.imread("image/11.png")
# gray_cv = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#
# b, g, r = cv2.split(img)
# gray_manual = (0.114 * b + 0.587 * g + 0.299 * r).astype(np.uint8)
#
# diff = cv2.absdiff(gray_cv, gray_manual)
# print("最大差异:", diff.max())   # 通常是 0 或 1（浮点舍入）



# ... existing code ...

# import cv2
# import numpy as np
# import matplotlib.pyplot as plt
#
# # 设置中文，防止乱码
# plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
# plt.rcParams["axes.unicode_minus"] = False
#
# # 1. 读取原图并转为灰度图
# img = cv2.imread("image/part_dark.png")
# gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#
# # ---------- 核心改动：使用 OpenCV 的 Otsu 自动计算全局最优阈值 ----------
# # cv2.threshold 返回两个值：retval（计算出的Otsu阈值）和 dst（二值化图像）
# otsu_thresh, _ = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
# print(f"【自动计算】原图的 Otsu 全局最优阈值: {otsu_thresh:.2f}")
#
# x = np.arange(256, dtype=np.float64)                  # 输入灰度值 0~255
#
# # ---------- 映射参数（基于 Otsu 动态生成） ----------
# T = otsu_thresh                                       # 使用 Otsu 阈值替代固定的 127
# band_width = 35                                       # 规则3/4的区间半宽度
# T1 = max(0, int(T - band_width))                      # 自适应区间左边界
# T2 = min(255, int(T + band_width))                    # 自适应区间右边界
# gamma = 0.5                                           # 伽马校正系数（<1 提亮暗部）
#
# # ---------- 5 种自适应像素映射规则（输出均为 0 或 255）----------
# # 规则1：阶跃映射（正向）- 使用 Otsu 阈值
# lut1 = np.where(x >= T, 255, 0)
#
# # 规则2：阶跃映射（反相）- 使用 Otsu 阈值
# lut2 = np.where(x < T, 255, 0)
#
# # 规则3：区间带通映射 - 以 Otsu 阈值为中心的自适应区间
# lut3 = np.where((x >= T1) & (x <= T2), 255, 0)
#
# # 规则4：区间带阻映射 - 剔除以 Otsu 阈值为中心的区间
# lut4 = np.where((x >= T1) & (x <= T2), 0, 255)
#
# # 规则5：伽马校正 + 动态 Otsu 阶跃映射
# # 先对灰度图做伽马校正
# gray_gamma = np.clip((gray / 255.0) ** gamma * 255, 0, 255).astype(np.uint8)
# # 对校正后的图像重新计算 Otsu 阈值，实现非线性空间的自适应
# otsu_thresh_gamma, _ = cv2.threshold(gray_gamma, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
# print(f"【自动计算】伽马校正后的 Otsu 阈值: {otsu_thresh_gamma:.2f}")
#
# x_gamma = (x / 255.0) ** gamma * 255
# lut5 = np.where(x_gamma >= otsu_thresh_gamma, 255, 0)
#
# luts = [lut.astype(np.uint8) for lut in [lut1, lut2, lut3, lut4, lut5]]
#
# # ---------- 逐像素查表映射 ----------
# bins = [cv2.LUT(gray, lut) for lut in luts]
#
# names = [
#     f"规则1 Otsu阶跃正向 (T={otsu_thresh:.1f})",
#     f"规则2 Otsu阶跃反相 (T={otsu_thresh:.1f})",
#     f"规则3 自适应区间带通 ({T1}~{T2})",
#     f"规则4 自适应区间带阻 ({T1}~{T2})",
#     f"规则5 伽马+动态Otsu (γ={gamma}, T={otsu_thresh_gamma:.1f})",
# ]
# files = ["otsu_map_1_step.png", "otsu_map_2_inv.png", "otsu_map_3_band.png",
#          "otsu_map_4_bandstop.png", "otsu_map_5_gamma.png"]
#
# # ---------- 打印白色像素占比，辅助定性分析 ----------
# for name, binary, f in zip(names, bins, files):
#     ratio = (binary == 255).mean() * 100
#     print(f"{name}: 白色像素占比 {ratio:.2f}%")
#     cv2.imwrite(f, binary)
#
# # ---------- 2x3 并排展示 ----------
# fig, axes = plt.subplots(2, 3, figsize=(15, 9), dpi=100)
# axes = axes.ravel()
#
# axes[0].imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
# axes[0].set_title("原图", fontsize=12)
#
# for i, (name, binary) in enumerate(zip(names, bins), start=1):
#     axes[i].imshow(binary, cmap="gray", vmin=0, vmax=255)
#     axes[i].set_title(name, fontsize=10)
#
# for ax in axes:
#     ax.axis("off")
#
# plt.suptitle("基于 Otsu 自适应规则的五种像素映射对比", fontsize=15)
# plt.tight_layout()
# plt.savefig("Otsu自适应像素映射五规则对比.png", bbox_inches="tight")
# print("对比图已保存到: Otsu自适应像素映射五规则对比.png")
# plt.show()
#
# # ---------- 映射函数曲线图 ----------
# plt.figure(figsize=(10, 6), dpi=100)
# colors = ["#1f77b4", "#d62728", "#2ca02c", "#ff7f0e", "#9467bd"]
# for lut, name, c in zip(luts, names, colors):
#     plt.plot(np.arange(256), lut, color=c, linewidth=2, label=name)
#
# plt.title("基于 Otsu 的 5 种像素映射函数曲线", fontsize=14)
# plt.xlabel("输入灰度值", fontsize=12)
# plt.ylabel("输出灰度值", fontsize=12)
# plt.xlim(0, 255)
# plt.ylim(-10, 265)
# plt.grid(alpha=0.3)
# plt.legend(fontsize=9)
# plt.tight_layout()
# plt.savefig("Otsu像素映射函数曲线.png")
# print("映射曲线图已保存到: Otsu像素映射函数曲线.png")
# plt.show()


import cv2
import numpy as np
import matplotlib.pyplot as plt

# 设置中文，防止乱码
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
plt.rcParams["axes.unicode_minus"] = False

# 1. 直接读取彩色图像（BGR 3 通道）
image_path = "image/part_raw.png"
img = cv2.imread(image_path)  # 保持彩色

if img is None:
    print("错误：未能成功读取图片，请检查路径！")
else:
    # 2. 定义彩色图像添加椒盐噪声的函数
    def add_color_salt_and_pepper(image, prob=0.05):
        """
        prob: 噪声总比例（如 0.05 代表约 5% 的像素会变成白点或黑点）
        """
        noisy = image.copy()
        # 针对每个像素位置生成随机数
        rand = np.random.rand(image.shape[0], image.shape[1])

        # 盐噪声：设为纯白 [255, 255, 255]
        noisy[rand < prob / 2] = [255, 255, 255]
        # 椒噪声：设为纯黑 [0, 0, 0]
        noisy[rand > 1 - prob / 2] = [0, 0, 0]
        return noisy


    # 3. 添加彩色椒盐噪声
    noisy_img = add_color_salt_and_pepper(img, prob=0.05)
    cv2.imwrite("color_noisy_image.png", noisy_img)
    print("已成功添加彩色椒盐噪声，保存为 color_noisy_image.png")

    # 4. 对彩色图像分别使用 3x3, 5x5, 7x7 进行中值滤波
    # cv2.medianBlur 会对 B、G、R 三通道分别独立滤波，完好保留色彩
    filtered_3 = cv2.medianBlur(noisy_img, 3)
    filtered_5 = cv2.medianBlur(noisy_img, 5)
    filtered_7 = cv2.medianBlur(noisy_img, 7)

    # 保存处理后的彩色图像
    cv2.imwrite("color_median_3x3.png", filtered_3)
    cv2.imwrite("color_median_5x5.png", filtered_5)
    cv2.imwrite("color_median_7x7.png", filtered_7)
    print("三种不同 ksize 的彩色中值滤波结果已成功保存！")

    # 5. 使用 Matplotlib 展示对比结果
    # 注意：OpenCV 读取的是 BGR 格式，Matplotlib 需要转换成 RGB 才能正确显示颜色
    titles = ["原图", "加彩色椒盐噪声 (5%)", "中值滤波 (3x3)", "中值滤波 (5x5)", "中值滤波 (7x7)"]
    images = [img, noisy_img, filtered_3, filtered_5, filtered_7]

    plt.figure(figsize=(16, 5), dpi=100)
    for i in range(5):
        plt.subplot(1, 5, i + 1)
        # BGR -> RGB 转色彩通道
        rgb_img = cv2.cvtColor(images[i], cv2.COLOR_BGR2RGB)
        plt.imshow(rgb_img)
        plt.title(titles[i], fontsize=11)
        plt.axis("off")

    plt.tight_layout()
    plt.savefig("彩色中值滤波ksize对比实验.png", bbox_inches="tight")
    print("对比图已保存为: 彩色中值滤波ksize对比实验.png")
    plt.show()
