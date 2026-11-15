# 成绩录入模板格式规范

> 从`高等数学4学生成绩录入模板[李盘润].xls`和`电梯24-12模板.xls`交叉验证提取（2026-06-05/06-06）

## 表头行（行0）

| 列 | 内容 | 字体 | 字号 | 对齐 | 边框 |
|:---|:---|:---|:---|:---|:---|
| A | 序号 | 宋体 | 23pt | 居中 | 四边细线 |
| B | 班级 | 宋体 | 23pt | 居中 | 四边细线 |
| C | 学号 | 宋体 | 23pt | 居中 | 四边细线 |
| D | 姓名 | 宋体 | 23pt | 居中 | 四边细线 |
| E | 平时成绩：60(必填) | **黑体** | **15pt** | 居中 | 四边细线 |
| F | 期末成绩：40(必填) | **黑体** | **15pt** | 居中 | 四边细线 |
| G | 备注 | 宋体 | 23pt | 居中 | 四边细线 |

## 数据行（行1-92）

| 列 | 内容示例 | 字体 | 字号 | 对齐 | 边框 | 类型 |
|:---|:---|:---|:---|:---|:---|:---|
| A | "1" | 宋体 | 13pt | 居中 | 四边细线 | 文本 |
| B | "电梯24-1" | 宋体 | 13pt | 居中 | 四边细线 | 文本 |
| C | "24502003" | 宋体 | 13pt | 居中 | 四边细线 | 文本 |
| D | "曹瑞" | 宋体 | 13pt | 居中 | 四边细线 | 文本 |
| E | "97" 或 " " | 宋体 | 13pt | 居中 | 四边细线 | 文本 |
| F | " " (空格) | 宋体 | 13pt | 居中 | 四边细线 | 文本 |
| G | "" | 宋体 | 13pt | 居中 | 四边细线 | 文本 |

## xlwt样式代码

```python
import xlwt

# 表头样式（序号、班级、学号、姓名、备注）
header_style = xlwt.easyxf(
    'font: name 宋体, height 460;'  # 23pt = 460 twips
    'alignment: horiz centre;'
    'borders: left thin, right thin, top thin, bottom thin;'
)

# 平时/期末表头：黑体 15pt
header_score_style = xlwt.easyxf(
    'font: name 黑体, height 300;'  # 15pt = 300 twips
    'alignment: horiz centre;'
    'borders: left thin, right thin, top thin, bottom thin;'
)

# 数据行：宋体 13pt
data_style = xlwt.easyxf(
    'font: name 宋体, height 260;'  # 13pt = 260 twips
    'alignment: horiz centre;'
    'borders: left thin, right thin, top thin, bottom thin;'
)
```

## 常见格式不匹配问题

| 问题 | 模板要求 | 常见错误格式 |
|:---|:---|:---|
| 平时列名 | `平时成绩：60(必填)` | `平时(必填)` |
| 期末列名 | `期末成绩：40(必填)` | `期末(必填)` |
| 表头字体 | 宋体 23pt / 黑体 15pt | Arial 10pt |
| 数据字体 | 宋体 13pt | Arial 10pt |
| 对齐 | 居中 | 左对齐 |
| 边框 | 四边细线 | 无 |
| 分数类型 | 文本("97") | 数值(97.0) |

## 列宽（xls内部单位，1单位≈1/256字符宽）

| 列 | 宽度 | 说明 |
|:---|:---|:---|
| A 序号 | 5120 | 约20字符 |
| B 班级 | 5120 | |
| C 学号 | 5120 | |
| D 姓名 | 5120 | |
| E 平时成绩 | 7168 | 约28字符，较宽 |
| F 期末成绩 | 7168 | 同上 |
| G 备注 | 5120 | |

## 工作表名

必须为 `学生成绩录入模板`（教务系统按此名识别）。

## Excel COM格式值参考

| 属性 | 值 | 含义 |
|:---|:---|:---|
| NumberFormat='@' | 文本格式 | 存字符串，不会被Excel转为数字 |
| NumberFormat='General' | 常规格式 | Excel自动判断类型 |
| HorizontalAlignment=-4108 | xlCenter | 水平居中 |
| VerticalAlignment=-4108 | xlCenter | 垂直居中（表头） |
| VerticalAlignment=-4107 | xlBottom | 底部对齐（数据行E列） |

**注意**：用户要求所有数据列格式一致。A-D列数据行也应为底部对齐(ver=-4107)，与E列相同。修复方法：
```python
for r in range(2, rows + 1):
    for c in range(1, 5):
        ws.Cells(r, c).VerticalAlignment = ws.Cells(r, 5).VerticalAlignment
```
