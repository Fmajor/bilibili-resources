# -*- coding: utf-8 -*-
# @Date     : 2023-12-17
# @Author   : @Fmajor in Bilibili
# 本程序用于模拟三门问题和其变种问题
import numpy as np
from textwrap import dedent

if 'functions':
  def fix_float(f, n=6):
    return int(f * 10**n) / (10**n)
  def monty_hall(*, N, seed, random_select=False):
    """
      not random_select is the origin rule of the monty hall problem
      if random_select, the host will select door randomly and we may see goat behind door
    """
    n = 3 # 三门问题
    counts_worlds = {
      'worlds total': N,
      'worlds used': 0,
      'worlds host with car': 0,
      'worlds used (ratio)': 0,
      'worlds host with car (ratio)': 0,
      'win of change': 0,
    }
    counts = {
      'car':  [0] * n,
      'you':  [0] * n,
      'host': [0] * n,
      'left': [0] * n,
    }
    countsT = {
      'car':  [0] * n,
      'you':  [0] * n,
      'host': [0] * n,
      'left': [0] * n,
      #'host|car-1': [0] * n,
      #'host|car-2': [0] * n,
      #'host|car-3': [0] * n,
    }
    if 'alias 使用中文进行变量名替换，让读者阅读更容易':
      随机整数 = np.random.randint
      class 生成位置集合(set):
        def __init__(self, count):
          super().__init__(range(count))
        def 去掉(self, *args, **kwargs):
          super().remove(*args, **kwargs)
          return self
      原版三门问题 = not random_select
      def 集合中随机选取位置(pos_set:set):
        index = np.random.randint(len(pos_set))
        return list(pos_set)[index]
      def 去掉后面的位置(pos_in, pos_out):
        out = pos_in - pos_out
        assert len(out) == 1
        return list(out)[0]
      使用的世界个数 = 0
      被抛弃的世界个数 = 0
      换门后得奖的世界个数 = 0
      个数为三 = n

    np.random.seed(seed) # 设定世界随机数种子，保证结果可重复
    for i in range(N):   # 开始模拟，生成N个赛博平行世界
      所有位置 = 生成位置集合(个数为三)   # 所有位置 {0,1,2}
      车位置 = 集合中随机选取位置(所有位置) # 第1步: 放置奖品
      你位置 = 集合中随机选取位置(所有位置) # 第2步: 你选位置
      # 第3步: 主持人从 所有位置{0,1,2}去掉你位置后 剩下的位置中选
      给主持人剩下的位置 = 生成位置集合(个数为三).去掉(你位置)
      if 原版三门问题: # 主持人只会选择没有车的门去打开,所以从待选位置去掉车位置
        if 车位置 in 给主持人剩下的位置: 给主持人剩下的位置.去掉(车位置)
      # 如果不是原版三门问题，则不进行上一步, 给主持人剩下的位置就可能有车
      主持人位置 = 集合中随机选取位置(给主持人剩下的位置)
      剩下的位置 = 去掉后面的位置(所有位置, {你位置, 主持人位置})
      if 主持人位置 == 车位置: # 只在 非原版三门问题中存在(Q2)
        被抛弃的世界个数 += 1; continue # 不记录此世界, 直接前往下一个世界
      if 主持人位置 != 车位置: 使用的世界个数 += 1
      if 剩下的位置 == 车位置: 换门后得奖的世界个数 += 1
      # ...接下来记录下所有位置，作为日后统计比例使用...

      ## origin code without chinese..
      ## car = np.random.randint(n)
      ## you = np.random.randint(n)
      ## pos_left_for_host = set(range(n))
      ## pos_left_for_host.remove(you)
      ## if not random_select: # the origin monty hall problem
      ##   if car in pos_left_for_host: pos_left_for_host.remove(car)
      ## host_index_left = np.random.randint(len(pos_left_for_host))
      ## host = list(pos_left_for_host)[host_index_left]
      ## pos_of_left = set(range(n))
      ## pos_of_left.remove(you)
      ## pos_of_left.remove(host)
      ## assert len(pos_of_left)==1
      ## left = list(pos_of_left)[0]

      car = 车位置
      you = 你位置
      host = 主持人位置
      left = 剩下的位置

      # 这里我尝试进行 ppt中的 标签转换方法，并完成了统计，但是结果并没有在ppt中列出
      # 有兴趣的同学可以尝试自行分析这个数据, t 的含义为 transformed 
      t_you = 0
      t_car  = (car - you)  % n 
      t_host = (host - you) % n 
      t_left = (left - you) % n 

      win_of_change = left == car

      counts['car' ][car]  += 1
      counts['you' ][you]  += 1
      counts['host'][host] += 1
      counts['left'][left] += 1

      countsT['car' ][t_car]  += 1
      countsT['you' ][t_you]  += 1
      countsT['host'][t_host] += 1
      countsT['left'][t_left] += 1

      # countsT[f'host|car-{t_car+1}'][t_host] += 1

      # counts_worlds['win of change'] += win_of_change
    
    counts_worlds['worlds used'] = 使用的世界个数
    counts_worlds['worlds host with car'] = 被抛弃的世界个数
    counts_worlds['win of change'] = 换门后得奖的世界个数

    total_world_used = counts_worlds['worlds used']
    counts_worlds['win of change'] /= total_world_used
    counts_worlds['worlds used (ratio)'] = counts_worlds['worlds used'] / N
    counts_worlds['worlds host with car (ratio)'] = counts_worlds['worlds host with car'] / N

    counts_worlds['win of change'] = fix_float(counts_worlds['win of change'])
    counts_worlds['worlds used (ratio)'] = fix_float(counts_worlds['worlds used (ratio)'])
    counts_worlds['worlds host with car (ratio)'] = fix_float(counts_worlds['worlds host with car (ratio)'])

    for each in ['car', 'you', 'host', 'left']:
      for i in range(n):
        counts[each][i]  /= total_world_used
        countsT[each][i] /= total_world_used
        counts[each][i] = fix_float( counts[each][i] )
        countsT[each][i] = fix_float( countsT[each][i] )
    # for i in range(3):
    #   for j in range(3):
    #     countsT[f'host|car-{i+1}'][j] = fix_float(countsT[f'host|car-{i+1}'][j]/sum(countsT[f'host|car-{i+1}']))

    return {
      'counts_worlds': counts_worlds,
      'counts': counts,
      'countsT': countsT,
    }

  def print_results(*, N, seed):
    r0 = monty_hall(N=N, seed=seed, random_select=False)
    r1 = monty_hall(N=N, seed=seed, random_select=True)
    t1 = dedent("""
    =========================
    原版三门问题:
      主持人打开不存在车的那个门
    生成世界的个数: {N}
      使用的世界个数: {N_used}
      抛弃的世界个数: {N_drop}
    换门后获奖概率: {win}""")
    t2 = dedent("""
    =========================
    变种三门问题:
      主持人随机打开剩下的门
      且门内没有奖
    生成世界的个数: {N}
      使用的世界个数: {N_used}
      抛弃的世界个数: {N_drop}
    换门后获奖概率: {win}""")
    print(t1.format(
      N     =r0['counts_worlds']['worlds total'],
      N_used=r0['counts_worlds']['worlds used'],
      N_drop=r0['counts_worlds']['worlds host with car'],
      win=r0['counts_worlds']['win of change'],
      ), end="")
    print(t2.format(
      N     =r1['counts_worlds']['worlds total'],
      N_used=r1['counts_worlds']['worlds used'],
      N_drop=r1['counts_worlds']['worlds host with car'],
      win=r1['counts_worlds']['win of change'],
      ))

seed = 42
N = 10000
r0 = monty_hall(N=N, seed=seed, random_select=False)
r1 = monty_hall(N=N, seed=seed, random_select=True)
print_results(N=N, seed=seed)