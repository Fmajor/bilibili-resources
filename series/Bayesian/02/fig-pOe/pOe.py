# -*- coding: utf-8 -*-
# @Date     : 2023-09-17
# @Author   : @Fmajor in Bilibili

# 本程序用于绘制 概率(probability,p) vs 发生比(odds,O) vs 证据量(evidence,e)的关系图

import numpy as np
import matplotlib.pyplot as plt

O = np.logspace(-5,5,101)
p = O/(O+1)
E = np.log10(O)

fig1 = plt.figure(figsize=(8,4))
ax1 = fig1.add_subplot(111)
ax1.plot(p, O, ms=1, ls='-', color='red', label='O')
ax1.set_yscale('log')

ax2 = ax1.twinx()
ax2.plot(p, E, ms=1, ls=':', color='green', label="e")
ax1.set_xlim(0,1)
ax1.set_xlabel('p')
ax1.set_ylabel('O (in log scale)')
ax2.set_ylabel('e')

fig1.legend(loc='upper left',bbox_to_anchor=(0.15, 0.85))
ax1.set_title('Probability(p) vs Odds(O) vs Evidence(e)')
fig1.savefig('./pOE.png')
plt.show(block=False)