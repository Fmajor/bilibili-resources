# -*- coding: utf-8 -*-
# @Date     : 2023-12-17
# @Author   : @Fmajor in Bilibili
# 本程序用于绘制视频中的若干示意图
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from matplotlib.font_manager import FontProperties,FontManager,findSystemFonts

if "constants":
  font_path = '../../../../resources/SourceHanSansCN-Bold.otf'  # 开源中文字体
  FONT = FontProperties(fname=font_path)

if "functions":
  def get_ratio(fig, ax):
    left, bottom, width_rel, height_rel = ax.get_position().bounds
    fig_width, fig_height = fig.get_size_inches()
    actual_aspect = (width_rel * fig_width) / (height_rel * fig_height)
    return actual_aspect
  def adjust_fig_size(fig, size, vspace, hspace):
    # 获取子图列表
    axes = fig.get_axes()
    if not axes:
      raise ValueError("No axes found in the figure.")

    # 获取行数和列数
    nrow, ncol = fig.axes[0].get_subplotspec().get_gridspec().get_geometry()

    # 使用第一个子图的aspect和position bounds
    ax = axes[0]

    # 使用fig.subplotpars中的所有参数
    sp = fig.subplotpars
    left_margin, right_margin = sp.left, 1 - sp.right
    bottom_margin, top_margin = sp.bottom, 1 - sp.top

    actual_aspect = get_ratio(fig, ax)
    axis_total_width_with_space  = size * ncol + vspace * (ncol-1)
    axis_total_height_with_space = size / actual_aspect  * nrow + hspace * (nrow-1)

    axis_total_width_rel  = 1 - left_margin - right_margin
    axis_total_height_rel = 1 - top_margin - bottom_margin

    # 计算整个图形的绝对宽度和高度
    fig_width = axis_total_width_with_space / axis_total_width_rel
    fig_height = axis_total_height_with_space / axis_total_height_rel

    vspace_ratio = vspace / fig_width
    hspace_ratio = hspace / fig_height * actual_aspect

    fig.set_size_inches(fig_width, fig_height)
    fig.subplots_adjust(wspace=vspace_ratio, hspace=hspace_ratio)

    print(f'updated: {fig_width:.2f},{fig_height:.2f}')
    fig_width, fig_height = fig.get_size_inches()
    print(f'get: {fig_width:.5f},{fig_height:.5f}')
    left, bottom, width_rel, height_rel = ax.get_position().bounds
    print(left_margin, right_margin, bottom_margin, top_margin)
    print(f'{left:.5f}, {bottom:.5f}')
    actual_aspect = get_ratio(fig, ax)
    print(f'ratio: {actual_aspect}')

  def draw_doors(*, ax, data, height, width, space):
    N = len(data)
    total_height = height
    total_width = (N+1) * space + N * width
    Y = - total_height / 2
    X = - total_width  / 2

    for i, each in enumerate(data):
      color = each.get('c', 'green')
      text  = each.get('t', '')
      star  = each.get('s', False)
      # matplotlib.patches.Rectangle(xy, width, height)
      # :                +------------------+
      # :                |                  |
      # :              height               |
      # :                |                  |
      # :               (xy)---- width -----+
      x = X + i * (width + space)
      y = Y
      rect = patches.Rectangle((x, y), width, height, linewidth=1, edgecolor='black', facecolor=color, alpha=0.5)
      ax.add_patch(rect)
      if text:
        ax.text(x + width / 2, y + height * 2 / 3, text, ha='center', fontsize=10, fontweight='bold', font=FONT)
      if star:
        ax.plot(x + width / 2, y + height / 3, marker='*', color='yellow', markersize=10)

    ax.set_xlim(X, -X)
    ax.set_ylim(Y, -Y)
    ax.axis('off')  # Turn off the axis
    ax.set_aspect('equal')

  def draw_fig(*, data, vspace, hspace, size):
    ndata = np.array(data)
    shape = ndata.shape
    fig, axs = plt.subplots(shape[0], shape[1])
    for row in range(shape[0]):
      for col in range(shape[1]):
        ddata = data[row][col]
        if shape[0] == 1:
          if shape[1] == 1:
            ax = axs
          else:
            ax = axs[col] 
        elif shape[1] == 1:
          ax = axs[row] 
        else:
          ax = axs[row, col] 
        draw_doors(ax=ax, data=ddata, height=DOOR_HEIGHT, width=DOOR_WIDTH, space=DOOR_SPACE)
    fig.subplots_adjust(left=0.02, bottom=0.02, right=0.98, top=0.98)
    adjust_fig_size(fig, size, vspace, hspace)

    plt.show(block=False)
    return fig, axs

# relative size in axis
DOOR_WIDTH  = 1
DOOR_HEIGHT = 2.2
DOOR_SPACE  = 0.1
# relative size of fig
FIG_VSPACE = 0.5
FIG_HSPACE = 0.5
SIZE = 0.5

if "data":
  data_step_one = []
  for car_id in range(3):
    each_doors = []
    for door_id in range(3):
      each_doors.append({
        "c": 'green',
        "t": '',
        "s": door_id == car_id
      })
    data_step_one.append([each_doors])

  data_step_two = []
  for car_id in range(3):
    each_row = []
    for you_id in range(3):
      each_doors = []
      for door_id in range(3):
        each_doors.append({
          "c": 'green' if door_id == you_id else "#5b9bd5",
          "t": '你' if door_id == you_id else '',
          "s": door_id == car_id
        })
      each_row.append(each_doors)
    data_step_two.append(each_row)

  data_step_three = []
  for car_id in range(3):
    each_row = []
    for you_id in range(3):
      for host_id in range(3):
        if host_id == you_id: continue
        each_doors = []
        for door_id in range(3):
          if door_id == you_id:
            color = 'green'
            text = '你'
          elif door_id == host_id:
            color = 'gray'
            text = '主'
          else:
            color = "#5b9bd5"
            text = '剩'
          each_doors.append({
            "c": color, 
            "t": text,
            "s": door_id == car_id
          })
        each_row.append(each_doors)
    data_step_three.append(each_row)

fig, axs = draw_fig(data=data_step_one,   size=SIZE, vspace=FIG_VSPACE, hspace=FIG_HSPACE)
fig, axs = draw_fig(data=data_step_two,   size=SIZE, vspace=FIG_VSPACE, hspace=FIG_HSPACE)
fig, axs = draw_fig(data=data_step_three, size=SIZE, vspace=FIG_VSPACE, hspace=FIG_HSPACE)