# -*- coding: utf-8 -*-
# @Date     : 2023-09-17
# @Author   : @Fmajor in Bilibili

# 本程序用于生成给定 先验概率、灵敏度和特异性 实验参数(假设他们都服从Beta分布)
#   以及疾病检测得到 阳性/阴性 数据之后
# 后验概率密度分布变化的图像
# 图像用于制作ppt使用

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import os
import pickle
import subprocess
from scipy.stats import beta as Beta
from pathlib import Path
from matplotlib.font_manager import FontProperties,FontManager,findSystemFonts
from scipy.special import beta as fBeta
from scipy.interpolate import interp1d
import ipdb
import time
import os
matplotlib.rc('font', size=12)

if "functions":
  def E(p):
    return 10*np.log10(p/(1-p))
  # 绘制后验分布图像
  def plot_posterior(*,
      alpha, beta,
      prior_good, prior_total,
      sens_good, sens_total,
      spec_good, spec_total,
      cache_path=Path('./cache/'),
      fig_path=Path('./figs/'),
      n_sample=99999,
      seed=23333,
      rerun=False,
      n_bins=10001,
      elimit=30,
      ylimit=None,
      prefix="",
      **kwargs
    ):
    np.random.seed(seed)
    os.makedirs(cache_path, exist_ok=True)
    os.makedirs(fig_path, exist_ok=True)

    t0 = time.time()
    __ = 2
    fig = plt.figure(figsize=(16/__,9/__))
    ax0 = fig.add_subplot(111)
    fig1 = plt.figure(figsize=(16/__,9/__))
    ax1 = fig1.add_subplot(111)
    x = np.linspace(0, 1, n_bins)

    fname = f"{prefix}-{alpha}-{beta}-{prior_good}-{prior_total}-{sens_good}-{sens_total}-{spec_good}-{spec_total}-{n_sample}-{seed}-{n_bins}"
    cache_file = cache_path / f"{fname}.npy"

    B_0 = lambda x:Beta.pdf(x, prior_good + alpha, prior_total-prior_good + beta)
    B_1 = lambda x:Beta.pdf(x, sens_good + alpha,  sens_total-sens_good + beta)
    B_2 = lambda x:Beta.pdf(x, spec_good + alpha,  spec_total-spec_good + beta)

    # 使用蒙特卡罗模拟方式来计算后验分布
    if not cache_file.exists() or rerun:
      pdata = {}
      y_prior = B_0(x)
      xlow, xhigh, ymid = find_confidence_interval(x,y_prior); xcen = prior_good/prior_total
      pdata['prior'] = {
        'x':x,
        'y':y_prior,
        'xcen': xcen,
        'xlow': xlow,
        'xhigh': xhigh,
        'ymid': ymid,
      }

      y_sens  = B_1(x)
      xlow, xhigh, ymid = find_confidence_interval(x,y_sens);  xcen = sens_good/sens_total
      pdata['sens'] = {
        'x':x,
        'y':y_sens,
        'xcen': xcen,
        'xlow': xlow,
        'xhigh': xhigh,
        'ymid': ymid,
      }

      y_spec  = B_2(x)
      xlow, xhigh, ymid = find_confidence_interval(x,y_spec);  xcen = spec_good/spec_total
      pdata['spec'] = {
        'x':x,
        'y':y_spec,
        'xcen': xcen,
        'xlow': xlow,
        'xhigh': xhigh,
        'ymid': ymid,
      }

      deltat = time.time() - t0; t0 = time.time(); print(f'cal y_prior in {deltat:.1f}s')

      xx = samples_prior = Beta.rvs(prior_good+alpha, prior_total-prior_good+beta, size=n_sample)
      yy = samples_sens  = Beta.rvs(sens_good+alpha,  sens_total-sens_good+beta,   size=n_sample)
      zz = samples_spec  = Beta.rvs(spec_good+alpha,  spec_total-spec_good+beta,   size=n_sample)
      deltat = time.time() - t0; t0 = time.time(); print(f'do sample in {deltat:.1f}s')

      post_pos = xx*yy/(xx*yy+(1-xx)*(1-zz))
      post_neg = xx*(1-yy)/(xx*(1-yy)+zz*(1-xx))

      hist, bin_edges = np.histogram(post_pos, bins=x, density=True)
      bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
      post_x = bin_centers
      post_y = hist
      xlow, xhigh, ymid = find_confidence_interval(post_x,post_y)
      ymax_ind = np.argmax(post_y); xcen = post_x[ymax_ind]
      pdata['post_pos'] = {
        'x': bin_centers,
        'y': hist,
        'xcen': xcen,
        'xlow': xlow,
        'xhigh': xhigh,
        'ymid': ymid,
      }

      hist, bin_edges = np.histogram(post_neg, bins=x, density=True)
      bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
      post_x = bin_centers
      post_y = hist
      xlow, xhigh, ymid = find_confidence_interval(post_x,post_y)
      ymax_ind = np.argmax(post_y); xcen = post_x[ymax_ind]
      pdata['post_neg'] = {
        'x': bin_centers,
        'y': hist,
        'xcen': xcen,
        'xlow': xlow,
        'xhigh': xhigh,
        'ymid': ymid,
      }
      deltat = time.time() - t0; t0 = time.time(); print(f'do statistic in {deltat:.1f}s')
      with open(cache_file, 'wb') as f:
        pickle.dump(pdata, f)
    else:
      with open(cache_file, 'rb') as f:
        pdata = pickle.load(f)

    if "plot prior":
      color = 'black'
      d = pdata['prior']
      x = d['x'];y=d['y'];xcen=d['xcen'];xlow=d['xlow'];xhigh=d['xhigh'];ymid=d['ymid'];ymax=np.max(y)

      ax0.plot(x, y, color=color)
      ax0.plot([xcen, xcen],[0,ymax], ls='--', color=color)
      ax0.plot([xlow,xlow],[0,ymid], ls='--', color=color)
      ax0.plot([xhigh,xhigh],[0,ymid], ls='--', color=color)
      ax1.plot(E(x), y, color=color)
      ax1.plot([E(xcen), E(xcen)],[0,ymax], ls='--', color=color)
      ax1.plot([E(xlow), E(xlow)],[0,ymid], ls='--', color=color)
      ax1.plot([E(xhigh),E(xhigh)],[0,ymid], ls='--', color=color)

      d = pdata['sens'];xcen=d['xcen'];xhigh=d['xhigh'];xlow=d['xlow']
      p_prior_str  = f"灵敏度分布({sens_good}/{sens_total}):${{{xcen:.5f}^{{+{xhigh-xcen:.5f}}}_{{-{xcen-xlow:.5f}}}}}({xhigh-xlow:.5f})$"
      ep_prior_str  = f"灵敏度分布({sens_good}/{sens_total}):${{{E(xcen):.5f}^{{+{E(xhigh)-E(xcen):.5f}}}_{{-{E(xcen)-E(xlow):.5f}}}}}({E(xhigh)-E(xlow):.5f})$"
      d = pdata['spec'];xcen=d['xcen'];xhigh=d['xhigh'];xlow=d['xlow']
      p_prior_str += f"|特异性分布({spec_good}/{spec_total}):${{{xcen:.5f}^{{+{xhigh-xcen:.5f}}}_{{-{xcen-xlow:.5f}}}}}({xhigh-xlow:.5f})$"
      ep_prior_str += f"|特异性分布({spec_good}/{spec_total}):${{{E(xcen):.5f}^{{+{E(xhigh)-E(xcen):.5f}}}_{{-{E(xcen)-E(xlow):.5f}}}}}({E(xhigh)-E(xlow):.5f})$"
      d = pdata['prior'];xcen=d['xcen'];xhigh=d['xhigh'];xlow=d['xlow']
      p_prior_str += f"\n先验分布({prior_good}/{prior_total}):${{{xcen:.5f}^{{+{xhigh-xcen:.5f}}}_{{-{xcen-xlow:.5f}}}}}({xhigh-xlow:.5f})$"
      ep_prior_str += f"\n先验分布({prior_good}/{prior_total}):${{{E(xcen):.5f}^{{+{E(xhigh)-E(xcen):.5f}}}_{{-{E(xcen)-E(xlow):.5f}}}}}({E(xhigh)-E(xlow):.5f})$"
    if "plot sens":
      color = 'gray'
      lw = 0.75
      d = pdata['sens']
      x = d['x'];y=d['y'];xcen=d['xcen'];xlow=d['xlow'];xhigh=d['xhigh'];ymid=d['ymid'];ymax=np.max(y)
      ax0.plot(x, y, color=color, ls=':', lw=lw)
      ax0.plot([xcen, xcen],[0,ymax], ls=':', color=color, lw=lw)
      ax0.plot([xlow,xlow],[0,ymid], ls=':', color=color, lw=lw)
      ax0.plot([xhigh,xhigh],[0,ymid], ls=':', color=color, lw=lw)
      ax1.plot(E(x), y, color=color, ls=":", lw=lw)
      ax1.plot([E(xcen), E(xcen)],[0,ymax], ls=':', color=color, lw=lw)
      ax1.plot([E(xlow), E(xlow)],[0,ymid], ls=':', color=color, lw=lw)
      ax1.plot([E(xhigh),E(xhigh)],[0,ymid], ls=':', color=color, lw=lw)

      ax0.plot(1-x, y, color=color, ls=':', lw=lw)
      ax0.plot([1-xcen, 1-xcen],[0,ymax], ls=':', color=color, lw=lw)
      ax0.plot([1-xlow,1-xlow],[0,ymid], ls=':', color=color, lw=lw)
      ax0.plot([1-xhigh,1-xhigh],[0,ymid], ls=':', color=color, lw=lw)
      ax1.plot(-E(x), y, color=color, ls=":", lw=lw)
      ax1.plot([-E(xcen), -E(xcen)],[0,ymax], ls=':', color=color, lw=lw)
      ax1.plot([-E(xlow), -E(xlow)],[0,ymid], ls=':', color=color, lw=lw)
      ax1.plot([-E(xhigh),-E(xhigh)],[0,ymid], ls=':', color=color, lw=lw)
    if "plot spec":
      color = 'gray'
      d = pdata['spec']
      x = d['x'];y=d['y'];xcen=d['xcen'];xlow=d['xlow'];xhigh=d['xhigh'];ymid=d['ymid'];ymax=np.max(y)
      ax0.plot(x, y, color=color, ls=":", lw=lw)
      ax0.plot([xcen, xcen],[0,ymax], ls=':', color=color, lw=lw)
      ax0.plot([xlow,xlow],[0,ymid], ls=':', color=color, lw=lw)
      ax0.plot([xhigh,xhigh],[0,ymid], ls=':', color=color, lw=lw)
      ax1.plot(E(x), y, color=color, ls=":", lw=lw)
      ax1.plot([E(xcen), E(xcen)],[0,ymax], ls=':', color=color, lw=lw)
      ax1.plot([E(xlow), E(xlow)],[0,ymid], ls=':', color=color, lw=lw)
      ax1.plot([E(xhigh),E(xhigh)],[0,ymid], ls=':', color=color, lw=lw)

      ax0.plot(1-x, y, color=color, ls=":", lw=lw)
      ax0.plot([1-xcen, 1-xcen],[0,ymax], ls=':', color=color, lw=lw)
      ax0.plot([1-xlow, 1-xlow],[0,ymid], ls=':', color=color, lw=lw)
      ax0.plot([1-xhigh,1-xhigh],[0,ymid], ls=':', color=color, lw=lw)
      ax1.plot(-E(x), y, color=color, ls=":", lw=lw)
      ax1.plot([-E(xcen), -E(xcen)],[0,ymax], ls=':', color=color, lw=lw)
      ax1.plot([-E(xlow), -E(xlow)],[0,ymid], ls=':', color=color, lw=lw)
      ax1.plot([-E(xhigh),-E(xhigh)],[0,ymid], ls=':', color=color, lw=lw)

    if "plot post pos data":
      color = 'blue'
      d = pdata['post_pos']
      x = d['x'];y=d['y'];xcen=d['xcen'];xlow=d['xlow'];xhigh=d['xhigh'];ymid=d['ymid'];ymax=np.max(y)

      ax0.plot(x, y, color=color)
      ax0.plot([xcen, xcen],[0,ymax], ls='--', color=color)
      ax0.plot([xlow,xlow],[0,ymid], ls='--', color=color)
      ax0.plot([xhigh,xhigh],[0,ymid], ls='--', color=color)
      p_post_pos_str = f"右:后验分布(阳):${{{xcen:.5f}^{{+{xhigh-xcen:.5f}}}_{{-{xcen-xlow:.5f}}}}}({xhigh-xlow:.5f})$"

      ax1.plot(E(x), y, color=color)
      ax1.plot([E(xcen), E(xcen)],[0,ymax], ls='--', color=color)
      ax1.plot([E(xlow), E(xlow)],[0,ymid], ls='--', color=color)
      ax1.plot([E(xhigh),E(xhigh)],[0,ymid], ls='--', color=color)
      ep_post_pos_str = f"右:后验分布(阳):${{{E(xcen):.5f}^{{+{E(xhigh)-E(xcen):.5f}}}_{{-{E(xcen)-E(xlow):.5f}}}}}({E(xhigh)-E(xlow):.5f})$"
    if "plot post neg data":
      color = 'blue'
      d = pdata['post_neg']
      x = d['x'];y=d['y'];xcen=d['xcen'];xlow=d['xlow'];xhigh=d['xhigh'];ymid=d['ymid'];ymax=np.max(y)

      ax0.plot(x, y, color=color)
      ax0.plot([xcen, xcen],[0,ymax], ls='--', color=color)
      ax0.plot([xlow,xlow],[0,ymid], ls='--', color=color)
      ax0.plot([xhigh,xhigh],[0,ymid], ls='--', color=color)
      p_post_neg_str = f"左:后验分布(阴):${{{xcen:.5f}^{{+{xhigh-xcen:.5f}}}_{{-{xcen-xlow:.5f}}}}}({xhigh-xlow:.5f})$"

      ax1.plot(E(x), y, color=color)
      ax1.plot([E(xcen), E(xcen)],[0,ymax], ls='--', color=color)
      ax1.plot([E(xlow), E(xlow)],[0,ymid], ls='--', color=color)
      ax1.plot([E(xhigh),E(xhigh)],[0,ymid], ls='--', color=color)
      ep_post_neg_str = f"左:后验分布(阴):${{{E(xcen):.5f}^{{+{E(xhigh)-E(xcen):.5f}}}_{{-{E(xcen)-E(xlow):.5f}}}}}({E(xhigh)-E(xlow):.5f})$"

    rstr = f"{p_prior_str}\n{p_post_neg_str}|{p_post_pos_str}"
    ax0.set_title(rstr,fontproperties=FONT)
    ax0.set_xlim([0, 1])
    if ylimit is not None:
      ax0.set_ylim([0, ylimit])
    #ax0.set_ylim([0, max(y) + 1])
    ax0.set_xlabel('患病概率',fontproperties=FONT)
    ax0.set_ylabel('概率密度',fontproperties=FONT)
    fig.subplots_adjust(top=0.82)
    fig.savefig(fig_path/f"{fname}.png",dpi=250)

    erstr = f"{ep_prior_str}\n{ep_post_neg_str}|{ep_post_pos_str}"
    ax1.set_title(erstr,fontproperties=FONT)
    ax1.set_xlim([-elimit, elimit])
    if ylimit is not None:
      ax1.set_ylim([0, ylimit])
    #ax0.set_ylim([0, max(y) + 1])
    ax1.set_xlabel('患病证据量(db)',fontproperties=FONT)
    ax1.set_ylabel('概率密度',fontproperties=FONT)
    fig1.subplots_adjust(top=0.82)
    fig1.savefig(fig_path/f"{fname}-evidence.png",dpi=250)

    plt.show(block=False)
    #plt.savefig(filename,dpi=200)

  def find_confidence_interval(x, y, confidence=0.95, tol=1e-6, N=99999):
    mask = np.isfinite(np.isnan(x))
    xx = x[mask]
    yy = y[mask]
    # 使用样条插值进行插值
    f = interp1d(xx, yy, kind='cubic')
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
  font_path = '../../../../resources/SourceHanSansCN-Bold.otf'  # 开源中文字体
  FONT = FontProperties(fname=font_path)

if "main":
  n_sample=999999999 # 默认参数需要大内存,对于普通笔记本建议使用n_sample=9999999
  n_bins = 10001
  seed = 23333
  rerun = False

  if "group1":
    elimit=20
    ylimit=25
    prefix="0.90-0.75"

    prior_good, prior_total = 50, 100
    sens_good, sens_total   = 90, 100
    spec_good, spec_total   = 75, 100
    plot_posterior(alpha=1, beta=1, **locals())

    prior_good, prior_total = 500, 1000
    sens_good, sens_total   = 90, 100
    spec_good, spec_total   = 75, 100
    plot_posterior(alpha=1, beta=1, **locals())

    prior_good, prior_total = 50, 100
    sens_good, sens_total   = 90, 100
    spec_good, spec_total   = 750, 1000
    plot_posterior(alpha=1, beta=1, **locals())

    prior_good, prior_total = 50, 100
    sens_good, sens_total   = 900, 1000
    spec_good, spec_total   = 75, 100
    plot_posterior(alpha=1, beta=1, **locals())

    prior_good, prior_total = 50, 100
    sens_good, sens_total   = 900, 1000
    spec_good, spec_total   = 750, 1000
    plot_posterior(alpha=1, beta=1, **locals())
  if "group2":
    elimit=30
    ylimit=85
    prefix="0.99-0.75"

    prior_good, prior_total = 50, 100
    sens_good, sens_total   = 99, 100
    spec_good, spec_total   = 75, 100
    plot_posterior(alpha=1, beta=1, **locals())

    prior_good, prior_total = 500, 1000
    sens_good, sens_total   = 99, 100
    spec_good, spec_total   = 75, 100
    plot_posterior(alpha=1, beta=1, **locals())

    prior_good, prior_total = 50, 100
    sens_good, sens_total   = 99, 100
    spec_good, spec_total   = 750, 1000
    plot_posterior(alpha=1, beta=1, **locals())

    prior_good, prior_total = 50, 100
    sens_good, sens_total   = 990, 1000
    spec_good, spec_total   = 75, 100
    plot_posterior(alpha=1, beta=1, **locals())

    prior_good, prior_total = 50, 100
    sens_good, sens_total   = 990, 1000
    spec_good, spec_total   = 750, 1000
    plot_posterior(alpha=1, beta=1, **locals())
  if "group3":
    elimit=30
    ylimit=85
    prefix="0.75-0.99"

    prior_good, prior_total = 50, 100
    sens_good, sens_total   = 75, 100
    spec_good, spec_total   = 99, 100
    plot_posterior(alpha=1, beta=1, **locals())

    prior_good, prior_total = 50, 100
    sens_good, sens_total   = 750, 1000
    spec_good, spec_total   = 990, 1000
    plot_posterior(alpha=1, beta=1, **locals())