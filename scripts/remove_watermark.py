#!/usr/bin/env python3
"""
remove_watermark.py — 自动去水印工具（PS 内容识别填充的脚本化替代）

选区（三选一，优先级：--mask > --rect > ROI 自动检测）：
  1. 自动检测：在 --roi 区域内按亮度阈值/颜色距离找出水印像素并膨胀成掩码
  2. --rect x1 y1 x2 y2：手动矩形选区（像素坐标）
  3. --mask mask.png：外部掩码（白=待修复，黑=保留）

修复引擎：
  LaMa 深度学习修复（via IOPaint，纹理/结构区域几乎无痕）
  依赖: pip install iopaint

用法示例：
  python3 remove_watermark.py 图1.jpg 图2.jpg                    # 批量，默认自动检测右下角
  python3 remove_watermark.py 图.jpg --roi 0.85 0.92 1 1 --thresh 120
  python3 remove_watermark.py 图.jpg --color "255,255,255" --thresh 60
  python3 remove_watermark.py 图.jpg --rect 2700 1480 2848 1600
  python3 remove_watermark.py 图.jpg --mask mask.png
  python3 remove_watermark.py 图.jpg --save-mask                 # 只导出掩码供手工微调
"""
import argparse
import os
import sys

import cv2
import numpy as np


def imread_unicode(path: str) -> np.ndarray:
    data = np.fromfile(path, dtype=np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"无法读取图片: {path}")
    return img


def imwrite_unicode(path: str, img: np.ndarray) -> None:
    ext = os.path.splitext(path)[1] or ".png"
    ok, buf = cv2.imencode(ext, img)
    if not ok:
        raise IOError(f"编码失败: {path}")
    buf.tofile(path)


def build_mask(img: np.ndarray, args) -> np.ndarray:
    """优先级：外部 mask > rect > ROI 自动检测"""
    h, w = img.shape[:2]
    mask = np.zeros((h, w), np.uint8)

    if args.mask:
        m = imread_unicode(args.mask)
        if m.ndim == 3:
            m = cv2.cvtColor(m, cv2.COLOR_BGR2GRAY)
        if m.shape[:2] != (h, w):
            m = cv2.resize(m, (w, h))
        _, mask = cv2.threshold(m, 127, 255, cv2.THRESH_BINARY)
        return mask

    if args.rect:
        x1, y1, x2, y2 = args.rect
        mask[max(y1, 0):min(y2, h), max(x1, 0):min(x2, w)] = 255
        return mask

    fx1, fy1, fx2, fy2 = args.roi
    rx1, ry1, rx2, ry2 = int(w * fx1), int(h * fy1), int(w * fx2), int(h * fy2)
    roi = img[ry1:ry2, rx1:rx2]

    if args.color:  # 颜色距离模式: --color B,G,R
        b, g, r = map(float, args.color.split(","))
        dist = np.linalg.norm(roi.astype(np.float32) - np.array([b, g, r]), axis=2)
        m = (dist < args.thresh).astype(np.uint8) * 255
    else:  # 亮度阈值模式（适合浅色/白色水印）
        _, m = cv2.threshold(cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY), args.thresh, 255, cv2.THRESH_BINARY)

    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (args.dilate, args.dilate))
    m = cv2.dilate(m, k, iterations=args.iter)
    mask[ry1:ry2, rx1:rx2] = m

    n = int(np.count_nonzero(mask))
    if n == 0:
        sys.exit("未在 ROI 内检测到水印像素，请调低 --thresh 或改用 --rect / --mask")
    print(f"  掩码像素: {n}（占全图 {100 * n / (h * w):.3f}%）")
    return mask


def make_lama_runner(args):
    try:
        import torch
        from iopaint.model_manager import ModelManager
        from iopaint.schema import HDStrategy, InpaintRequest
    except ImportError:
        sys.exit("未安装 iopaint，无法运行。安装: pip install iopaint（或用 ~/venvs/iopaint/bin/python 运行）")

    device = torch.device("mps" if (args.device == "auto" and torch.backends.mps.is_available())
                          else args.device if args.device != "auto" else "cpu")
    print(f"加载 LaMa 模型（device={device.type}）…")
    model = ModelManager(name="lama", device=device)

    def run(img: np.ndarray, mask: np.ndarray) -> np.ndarray:
        config = InpaintRequest(
            hd_strategy=HDStrategy.CROP,
            hd_strategy_crop_margin=args.crop_margin,
            hd_strategy_crop_trigger_size=args.crop_trigger,
            hd_strategy_resize_limit=args.resize_limit,
        )
        return model(img, mask, config)

    return run


def main() -> None:
    p = argparse.ArgumentParser(description="自动去水印：智能掩码 + LaMa 修复")
    p.add_argument("images", nargs="+", help="输入图片（支持多张批量）")
    p.add_argument("-o", "--out", help="输出路径或目录（默认逐张原名 + _no_watermark.png）")
    p.add_argument("--device", default="auto", choices=["auto", "cpu", "mps", "cuda"], help="lama 运算设备")
    p.add_argument("--roi", nargs=4, type=float, metavar=("FX1", "FY1", "FX2", "FY2"),
                   default=[0.80, 0.90, 1.0, 1.0], help="自动检测区域（比例坐标，默认右下角）")
    p.add_argument("--thresh", type=int, default=140, help="亮度阈值 0-255（或颜色距离模式下为最大色距）")
    p.add_argument("--color", help="按颜色检测: 'B,G,R'（如白色 '255,255,255'）")
    p.add_argument("--rect", nargs=4, type=int, metavar=("X1", "Y1", "X2", "Y2"), help="手动矩形选区（像素坐标）")
    p.add_argument("--mask", help="外部掩码图（白色=待修复），仅单张图片时可用")
    p.add_argument("--save-mask", action="store_true", help="把自动生成的掩码保存到输出旁（_mask.png）")
    p.add_argument("--dilate", type=int, default=7, help="掩码膨胀核大小（默认 7）")
    p.add_argument("--iter", type=int, default=2, help="掩码膨胀迭代次数（默认 2）")
    p.add_argument("--crop-margin", type=int, default=256, help="lama 裁剪策略边距")
    p.add_argument("--crop-trigger", type=int, default=1024, help="lama 裁剪策略触发尺寸")
    p.add_argument("--resize-limit", type=int, default=2048, help="lama resize 策略上限")
    args = p.parse_args()

    if args.mask and len(args.images) > 1:
        sys.exit("--mask 仅支持单张图片；批量请用自动检测 / --rect")

    lama_run = make_lama_runner(args)

    outdir = args.out if (args.out and os.path.isdir(args.out) or (args.out and len(args.images) > 1 and not os.path.splitext(args.out)[1])) else None
    if outdir:
        os.makedirs(outdir, exist_ok=True)

    for path in args.images:
        print(f"处理: {path}")
        img = imread_unicode(path)
        mask = build_mask(img, args)

        base = os.path.splitext(os.path.basename(path))[0]
        if outdir:
            out = os.path.join(outdir, base + "_no_watermark.png")
        elif args.out and len(args.images) == 1:
            out = args.out
        else:
            out = os.path.splitext(path)[0] + "_no_watermark.png"

        if args.save_mask:
            imwrite_unicode(os.path.splitext(out)[0] + "_mask.png", mask)

        result = lama_run(img, mask)

        imwrite_unicode(out, result)
        print(f"  已输出: {out}")


if __name__ == "__main__":
    main()
