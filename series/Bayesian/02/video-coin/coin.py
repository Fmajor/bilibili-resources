# -*- coding: utf-8 -*-
# @Date     : 2023-09-17
# @Author   : @Fmajor in Bilibili

# 本程序用于模拟投硬币时后验概率的变化过程
# 程序会在./figs和./figs1文件中生成若干png图片，并最后使用ffmpeg合成视频

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import os
import subprocess
from scipy.stats import beta as Beta
from pathlib import Path
from matplotlib.font_manager import FontProperties,FontManager,findSystemFonts
from scipy.special import beta as fBeta
from scipy.interpolate import interp1d
import ipdb
matplotlib.rc('font', size=12)

if "functions":
  # 抛硬币函数
  def toss_coin(n, p, seed):
    np.random.seed(seed)
    return np.random.choice([0, 1], size=n, p=[1-p, p])

  def E(p):
    return 10*np.log10(p/(1-p))
  # 绘制后验分布图像
  def plot_posterior(alpha, beta, toss_count, heads_count, frame, this_coin, confidence=0.95):
    x = np.linspace(0, 1, 9999)
    y = Beta.pdf(x, heads_count + alpha, toss_count - heads_count + beta)
    first_flag = this_coin==-1
    if not first_flag:
      if this_coin: # before / after
        # h--, t--
        beta_ratio = fBeta(heads_count  , toss_count-heads_count+1)     / fBeta(heads_count+1, toss_count-heads_count+1)
      else:
        # h==, t--
        beta_ratio = fBeta(heads_count+1, toss_count-heads_count+1-1) / fBeta(heads_count+1, toss_count-heads_count+1)
      likely_ratio = x**this_coin * (1-x)**(1-this_coin) / beta_ratio

    if "plot in linear scale":
      ymax = max(y)
      if not first_flag:
        p = heads_count/toss_count
        xlow, xhigh,ymid = find_confidence_interval(x,y, confidence=confidence)
      else:
        p = 0.5
        xlow  = p - confidence/2
        xhigh = p + confidence/2
        ymid = ymax

      ax0.plot(x, y)
      ax0.plot([p,p],[0,ymax], ls='--', color='black')
      ax0.plot([xlow,xlow],[0,ymid], ls='--', color='black')
      ax0.plot([xhigh,xhigh],[0,ymid], ls='--', color='black')
      if not first_flag:
        ax1.plot(x, likely_ratio, ls=':', color="green")
        ax1.set_ylim(ymin=0)
        ax1.set_ylabel('似然比',fontproperties=FONT)
        ax1.yaxis.set_label_position("right")
        yticks = ax1.get_yticks()
        ax1.set_yticklabels(list(map(lambda _:f"{_:.3f}", yticks)))

      rstr = f" 95%可信区间:${p:.3f}^{{+{xhigh-p:.3f}}}_{{-{p-xlow:.3f}}} ({xhigh-xlow:.3f})$"
      this_coin = "正" if this_coin else "反"
      ax0.set_title(f'后验分布 本次数据:{this_coin}({heads_count:4d}正/{toss_count-heads_count:4d}反/{toss_count:4d}总)' + rstr,fontproperties=FONT)
      ax0.set_xlim([0, 1])
      ax0.set_ylim([0, max(y) + 1])
      ax0.set_xlabel('正面朝上概率',fontproperties=FONT)
      ax0.set_ylabel('后验分布概率密度',fontproperties=FONT)
      filename = FIGDIR / f'frame_{frame:04}.png'
      fig.savefig(filename,dpi=200)
      #plt.pause(0.2)
      ax0.clear()
      if not first_flag:
        ax1.clear()
    #ipdb.set_trace()
    if "plot in normal log scale (db)":
      x = 10*np.log10(x/(1-x))

      ax01.plot(x, y)
      ax01.plot([E(p),E(p)],[0,ymax], ls='--', color='black')
      ax01.plot([E(xlow),E(xlow)],[0,ymid], ls='--', color='black')
      ax01.plot([E(xhigh),E(xhigh)],[0,ymid], ls='--', color='black')
      if not first_flag:
        ax11.plot(x, likely_ratio, ls=':', color="green")
        ax11.set_ylim(ymin=0)
        ax11.set_ylabel('似然比',fontproperties=FONT)
        ax11.yaxis.set_label_position("right")
        yticks = ax11.get_yticks()
        ax11.set_yticklabels(list(map(lambda _:f"{_:.3f}", yticks)))

      rstr = f" 95%可信证据量区间(db):${E(p):.3f}^{{+{E(xhigh)-E(p):.3f}}}_{{-{E(p)-E(xlow):.3f}}} ({E(xhigh)-E(xlow):.3f})$"
      this_coin = "正" if this_coin else "反"
      ax01.set_title(f'后验分布 本次数据:{this_coin}({heads_count:4d}正/{toss_count-heads_count:4d}反/{toss_count:4d}总)' + rstr,fontproperties=FONT)
      ax01.set_xlim([-30, 30])
      ax01.set_ylim([0, max(y) + 1])
      ax01.set_xlabel('正面朝上证据量(db)',fontproperties=FONT)
      ax01.set_ylabel('后验分布概率密度',fontproperties=FONT)
      filename = FIGDIR1 / f'frame_{frame:04}.png'
      fig1.savefig(filename,dpi=200)
      #plt.pause(0.2)
      ax01.clear()
      if not first_flag:
        ax11.clear()
    #ipdb.set_trace()

  def find_confidence_interval(x, y, confidence=0.95, tol=1e-5, N=9999):
    # 使用样条插值进行插值
    f = interp1d(x, y, kind='cubic')
    # 生成更细的网格以进行数值积分
    x_fine = np.linspace(min(x), max(x), N)
    y_fine = f(x_fine)
    ymax = np.max(y_fine)
    ymin = 0
    integral_x = x_fine
    threshold = 1
    last_ymax = ymax
    last_ymin = ymin
    while threshold > tol:
      ymid = (ymax + ymin) / 2
      mask = y_fine >= ymid
      integral_y = y_fine[mask]
      integral_x = x_fine[mask]
      # 计算面积
      A = np.trapz(integral_y, integral_x)
      if A > confidence:
        ymin = ymid
      else:
        ymax = ymid
      threshold = np.abs(A - confidence)
      if np.abs(ymin-ymax)<tol:
        break
      if last_ymax==ymax and last_ymin==ymin:
        break
      else:
        last_ymin = ymin
        last_ymax = ymax
      #ipdb.set_trace()
      #print(integral_x[0], integral_x[-1], ymin, ymax, threshold)
    return integral_x[0], integral_x[-1], (ymin+ymax)/2

if "constants":
  # 参数设置
  p = 0.6     # 成功（正面）概率
  n = 1000    # 投掷次数
  seed = 23333  # 随机数种子

if "main":
  GENERATE = 1 # 重新生成所有png图片

  FIGDIR  = Path('./figs')
  FIGDIR1 = Path('./figs1')
  os.makedirs(FIGDIR, exist_ok=True)
  os.makedirs(FIGDIR1, exist_ok=True)
  font_path = '../../../../resources/SourceHanSansCN-Bold.otf'  # 或者是 .otf 字体的路径
  FONT = FontProperties(fname=font_path)
  #plt.rcParams['font.serif'] = ["Source Han Sans CN"] + plt.rcParams['font.serif']
  #plt.rcParams['font.family'] = "serif"

  # 初始化参数
  alpha, beta = 1, 1
  frame = 0

  # 抛硬币
  coin_tosses = toss_coin(n, p, seed)

  if GENERATE:
    __ = 2
    fig = plt.figure(figsize=(16/__,9/__))
    ax0 = fig.add_subplot(111)
    fig1 = plt.figure(figsize=(16/__,9/__))
    ax01 = fig1.add_subplot(111)
    last_head_count = 0
    # 先画先验分布
    plot_posterior(alpha, beta, 0, 0, frame, -1)
    # 然后才有似然比坐标轴
    ax1 = ax0.twinx()
    ax11 = ax01.twinx()
    # 主循环：绘制后验分布
    for toss_count, heads_count in enumerate(np.cumsum(coin_tosses), 1):
      frame += 1
      if heads_count != last_head_count:
        this_coin = 1
      else:
        this_coin = 0
      plot_posterior(alpha, beta, toss_count, heads_count, frame, this_coin)
      last_head_count = heads_count
      print(f'生成视频帧:{frame}')

  # generate duration
  concat_content = []
  durations = []
  max_frames = 30

  frame = 0
  fname = f"frame_{frame:04d}.png"
  concat_content.append(f"file {fname}")
  concat_content.append(f"duration 5")
  for frame in range(1,n+1):
    fname = f"frame_{frame:04d}.png"
    __ = frame
    if __<=5:
      dframe = max_frames
    elif __<=15:
      dframe = int(max_frames * (1-(__-5)/(15-5)))
      if dframe<1:
        dframe = 1
    elif n+1-__<=10:
      dframe = int(max_frames/(n+1-__))
    else:
      dframe = 1
    duration = dframe/max_frames
    durations.append(duration)
    concat_content.append(f"file {fname}")
    concat_content.append(f"duration {duration}")
  concat_content.append(f"file {fname}")
  concat_content.append(f"duration 5")
  concat_content.append(f"file {fname}")
  concat_content.append(f"duration 5")
  concat_content.append(f"file {fname}")
  concat_content.append(f"duration 10")
  # 生成帧参数文件,控制每张图片的停留时间
  with open(FIGDIR/"frame_list.txt", "w") as f:
    f.write("\n".join(concat_content))
  with open(FIGDIR1/"frame_list.txt", "w") as f:
    f.write("\n".join(concat_content))
  # 使用 FFmpeg 生成 MP4 视频
  subprocess.run([
    'ffmpeg',
    '-f', "concat",
    '-i', 'frame_list.txt',
    '-vf', f'fps={max_frames},format=yuv420p',
    'output.mp4'
  ], cwd=FIGDIR)
  subprocess.run([
    'ffmpeg',
    '-f', "concat",
    '-i', 'frame_list.txt',
    '-vf', f'fps={max_frames},format=yuv420p',
    'output.mp4'
  ], cwd=FIGDIR1)
