# -*- coding: utf-8 -*-
# @Date     : 2023-09-17
# @Author   : @Fmajor in Bilibili

# 本程序用于计算给定 先验概率、灵敏度和特异性参数
#   在得到疾病检测 阳性/阴性 数据之后
# 后验概率/置信的数值

# 此外还有四个人对于网红事件概率认知更新的表格
# 数据用于制作ppt使用

import numpy as np
import pprint

def cal(*, data, prior, sens, spec):
  def evidence(p):
    return 10*np.log10(p/(1-p))
  result_p = []
  result_e = []
  p = prior
  result_p.append(f"{p:.3f}")
  result_e.append(f"{evidence(p):.3f}")
  for each in data:
    if each:
      p = (p*sens)/(p*sens + (1-p)*(1-spec))
    else:
      p = (p*(1-sens))/(p*(1-sens) + (1-p)*spec)
    result_p.append(f"{p:.3f}")
    result_e.append(f"{evidence(p):.3f}")
  bayes_p = 10*np.log10(sens/(1-spec))
  bayes_n = 10*np.log10(spec/(1-sens))
  #diff_e = np.diff(np.array(list(map(float,result_e))))
  #diff_e_expected = np.array([bayes_p if _ else bayes_n for _ in data])
  #errors = (diff_e-diff_e_expected)/diff_e_expected
  #assert np.all(errors<0.01), errors
  # [sens, spec, f"{bayes_p:.3f}", f"{bayes_n:.3f}"], result_p, result_e
  print(f"prior:{prior:.3f} sens:{sens:.3f} {spec:.3f} | delta_e: +{bayes_p:.3f}-{bayes_n:.3f}")
  print("p: ", end="")
  for each in result_p:
    print(each+" ",end="")
  print()
  print("e: ", end="")
  for each in result_e:
    print(each+" ",end="")
  print("\n")



data = [1,1,1,0]
cal(data=data, prior=0.1, sens=0.99, spec=0.75)
cal(data=data, prior=0.01, sens=0.99, spec=0.75)
cal(data=data, prior=0.001, sens=0.99, spec=0.95)
cal(data=[0], prior=0.5, sens=0.90, spec=0.75)
cal(data=[1], prior=0.5, sens=0.90, spec=0.75)

print("张三")
cal(data=[1], prior=0.1, sens=0.99, spec=0.99)
print("李四")
cal(data=[1], prior=0.9, sens=0.99, spec=0.3)
print("王五")
cal(data=[1], prior=0.1, sens=0.99, spec=0.01)
print("赵六")
cal(data=[1], prior=0.6, sens=0.10, spec=0.01)