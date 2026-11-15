# 切换班级后导入静默失败 — 计网24-3 案例（2026-06-18）

## 场景

连续导入两个班级的成绩：
1. ✅ **物联网24-1;物联网24-2**（高等数学4）— 91人，导入成功
2. ❌ **计网24-3**（高等数学4）— 51人，导入完全失败

## 操作过程

```
物联网24-1 导入成功 → 点击保存
→ goto(LIST_URL) 回到课程列表
→ jqGrid 查找"计网24-3"（单独班级，非合并）
→ setSelection + btn_qd 进入详情页
→ btn_dr 打开导入弹窗
→ 选择覆盖模式（drfs=2）
→ #cjFile.first.set_input_files(计网24-3_最终模板格式.xlsx)
→ #btn_success 点击确认导入
→ 等待8s
→ 无任何弹窗出现（无successModal，无alertModal）
→ 清理遮罩后点击 btn_bc 保存
→ 保存成功？未确认（无"保存成功"文本）
→ 核查成绩：0/51 人有平时、期末、总评（全部为空）
```

## 关键差异

| 项目 | 物联网24-1（成功） | 计网24-3（失败） |
|------|:---:|:---:|
| 班级类型 | 合并班（分号连接） | 独立班级 |
| 导入时机 | 首次进入页面后导入 | 切换班级后导入 |
| 导入弹窗状态 | 显示 importModal + successModal | 无任何弹窗 |
| 成绩结果 | 91/91 全部正确 | 0/51 全部为空 |
| 页面刷新 | 否 | 否（仅goto回列表页） |

## 可能根因

### 1. 页面状态残留（最可能）

`goto(LIST_URL)` 回到列表页时，jqGrid 重新加载了列表，但之前的详情视图状态（DOM缓存、JS数据绑定）未完全清除。进入新的详情页后，部分前端事件监听器绑定到了旧的 view state 上。

**证据**：
- 第二次导入没有产生任何弹窗（无 import success/fail 反馈）
- 这说明 `#btn_success.click()` 虽然执行了，但后端导入请求可能没有被正确路由

### 2. 详情页加载时序

首次进入某个班级的详情页时，页面有一个明显的加载过程（初始显示0人，几秒后加载完成）。切换到另一个班级后，这个加载过程可能被缓存或跳过，导致数据绑定出错。

**建议等待时间**：切换到新班级后，等待至少10秒让详情页完全初始化。

### 3. 合并班级 vs 独立班级

物联网24-1是合并班（`物联网24-1;物联网24-2`），计网24-3是独立班级。教务系统内部可能对这两种班级的处理逻辑不同。

## 预防措施

### ✅ 每次都刷新页面
```python
# 切换班级时：先 goto 到列表页，再强制 reload
grade_page.goto(LIST_URL)
time.sleep(5)
grade_page.reload()
time.sleep(8)

# 然后才操作 jqGrid
row = grade_page.evaluate("...")
grade_page.evaluate("jQuery('#jxrwGrid').jqGrid('setSelection', '" + row['id'] + "')")
time.sleep(2)
grade_page.evaluate("document.getElementById('btn_qd').click()")
time.sleep(10)  # 详情页加载
```

### ✅ 导入后立即验证
导入 + 关闭弹窗后，不要急着保存，先验证数据是否确实进入了 input 字段：
```python
scores = grade_page.evaluate("""() => {
    const t = document.getElementById('cjlrTable_right');
    if (!t) return {error: 'no table'};
    const rows = t.querySelectorAll('tr');
    let hasData = false;
    for (let i = 1; i < Math.min(rows.length, 5); i++) {
        const cells = rows[i].querySelectorAll('td');
        if (cells.length >= 3) {
            const ps = cells[0].querySelector('input');
            const qm = cells[1].querySelector('input');
            if (ps && ps.value) hasData = true;
        }
    }
    return {totalRows: rows.length, hasData: hasData};
}""")
if not scores.get('hasData'):
    print("⚠️ 导入后数据为空！请检查页面状态后重试")
```

### ✅ 多班导入时用独立脚本
每个班级的导入用独立的 Python 脚本运行，不要在同一个浏览器会话中连续操作。脚本结束后浏览器保持打开供用户检查，再运行下一个班级的脚本。

## 启示

**成绩导入操作有状态性**：教务系统前端在单次会话中操作多个班级时，会累积页面状态。最安全的方式是每个班级独立启动脚本，不要在同一个浏览器页面中连续切换班级导入。
