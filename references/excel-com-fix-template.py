"""
教务系统成绩文件格式修复脚本模板
用Excel COM (win32com) 修复已有.xls文件的格式问题。
用法：修改 TARGET_PATH 和修复逻辑，运行 python fix_template.py
"""
import win32com.client
import os

TARGET_PATH = r'D:\BaiduSyncdisk\龙虾文件\成绩\提交成绩\待修复文件.xls'

def fix_grade_file(path):
    excel = win32com.client.Dispatch("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False

    wb = excel.Workbooks.Open(os.path.abspath(path))
    ws = wb.Sheets(1)
    rows = ws.UsedRange.Rows.Count

    # === 1. 修复表头文字 ===
    ws.Cells(1, 5).Value = '平时成绩：60(必填)'  # E列
    ws.Cells(1, 6).Value = '期末成绩：40(必填)'  # F列

    # === 2. 修复E列数据：数字→文本 ===
    # 先读取所有值
    e_values = []
    for r in range(2, rows + 1):
        val = ws.Cells(r, 5).Value
        if val is not None and val != '' and val != ' ':
            e_values.append(str(int(float(val))))
        else:
            e_values.append('')

    # 先设NumberFormat为文本（必须在写值之前！）
    e_range = ws.Range(ws.Cells(2, 5), ws.Cells(rows, 5))
    e_range.NumberFormat = '@'

    # 再写入字符串值
    for i, val in enumerate(e_values):
        if val:
            ws.Cells(i + 2, 5).Value = val

    # === 3. 修复字体（@格式可能重置为Arial/10pt）===
    for r in range(2, rows + 1):
        cell = ws.Cells(r, 5)
        cell.Font.Name = '宋体'
        cell.Font.Size = 13

    # === 4. 验证 ===
    print("=== 验证 ===")
    for r in range(1, min(6, rows + 1)):
        e_cell = ws.Cells(r, 5)
        print(f"Row {r}: val={repr(e_cell.Value)}, type={type(e_cell.Value).__name__}, "
              f"font={e_cell.Font.Name}/{e_cell.Font.Size}, fmt={repr(e_cell.NumberFormat)}")

    wb.Save()
    wb.Close(False)
    excel.Quit()
    print(f"\n文件已保存: {path}")


def inspect_file(path):
    """检查文件格式，用于诊断问题"""
    excel = win32com.client.Dispatch("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False

    wb = excel.Workbooks.Open(os.path.abspath(path))
    ws = wb.Sheets(1)
    rows = ws.UsedRange.Rows.Count

    print(f"=== {os.path.basename(path)} (rows={rows}) ===")
    for r in range(1, min(6, rows + 1)):
        print(f"Row {r}:")
        for c in range(1, 8):
            cell = ws.Cells(r, c)
            print(f"  {chr(64+c)}: val={repr(cell.Value)}, type={type(cell.Value).__name__}, "
                  f"font={cell.Font.Name}/{cell.Font.Size}, fmt={repr(cell.NumberFormat)}, "
                  f"H={cell.HorizontalAlignment}, V={cell.VerticalAlignment}")

    wb.Close(False)
    excel.Quit()


if __name__ == '__main__':
    # 先检查
    inspect_file(TARGET_PATH)
    # 再修复
    fix_grade_file(TARGET_PATH)
