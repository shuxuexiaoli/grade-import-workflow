---
name: grade-import-workflow
description: 教务系统成绩导入操作流程。登录门户→SSO进教务→成绩录入→jqGrid选班级→导入文件→保存。
triggers:
  - 成绩导入
  - 导入成绩
  - 上传成绩
  - 提交成绩
  - grade import
---

# 教务系统成绩导入流程

> 适用场景：将已准备好的成绩Excel文件导入教务系统成绩录入页面并保存。

## 前置条件

- 浏览器已启动（CDP端口9222可用）
- 已登录信息门户（或教务系统已打开）
- 成绩文件已准备好（.xls/.xlsx）

## 完整流程（6步）

### 1. 登录门户（如未登录）

参考 `scitc-portal` 技能的登录流程。登录状态检测用页面文本，不用URL。

### 2. 通过SSO进入教务系统

```python
# 从门户提取SSO URL
onclick = page.evaluate("""(() => {
    const links = document.querySelectorAll('a');
    for (const a of links) {
        if (a.textContent.trim() === '教务系统') {
            return a.getAttribute('onclick');
        }
    }
    return null;
}""")
import re
match = re.search(r"openURL\('([^']+)'", onclick)
sso_url = match.group(1)
page.goto(sso_url)
time.sleep(8)
```

⚠️ 不能直接 `page.goto("https://jw.scitc.edu.cn/...")`，必须通过SSO。

### 3. 进入成绩录入页面

```python
# 方式A：菜单点击
page.evaluate("""() => {
    document.querySelectorAll('a').forEach(a => {
        if (a.textContent.trim() === '成绩') a.click();
    });
}""")
time.sleep(3)
page.evaluate("""() => {
    document.querySelectorAll('a').forEach(a => {
        if (a.textContent.includes('成绩录入') && a.textContent.includes('教师')) a.click();
    });
}""")
time.sleep(8)
# 找新标签页
for ctx in browser.contexts:
    for pg in ctx.pages:
        if "jscjlr_cxJscjlrIndex" in pg.url:
            page = pg
            break
```

### 4. jqGrid选中目标班级

```python
# 查找班级（精确匹配jxbzc）
row = page.evaluate("""(() => {
    const grid = jQuery('#jxrwGrid');
    const ids = grid.jqGrid('getDataIDs');
    for (let i = 0; i < ids.length; i++) {
        const r = grid.jqGrid('getRowData', ids[i]);
        if (r.jxbzc === '电梯24-1;电梯24-2') {
            return {id: ids[i], jxb_id: r.jxb_id, kcmc: r.kcmc};
        }
    }
    return null;
})""")

# 选中行
page.evaluate(f"jQuery('#jxrwGrid').jqGrid('setSelection', '{row['id']}')")
time.sleep(1)

# 点确定进入详情
page.evaluate("document.getElementById('btn_qd').click()")
time.sleep(8)
```

⚠️ jxb_id 必须在 `btn_qd` 之前获取（之后jqGrid不可用）。
⚠️ 班级名匹配用 `===` 精确匹配，不要用 `includes()`。

### 5. 导入成绩文件

```python
# 5a. 点击导入按钮
page.evaluate("document.getElementById('btn_dr').click()")
time.sleep(3)

# 5b. 【可选】选择导入模式（追加/覆盖）
# 导入弹窗中有两个radio: drfs=1(追加,默认) / drfs=2(覆盖)
# 覆盖模式会完全替换已有成绩数据，追加模式在已有数据上叠加
page.evaluate("""() => {
    const radios = document.querySelectorAll('#importModal input[name="drfs"]');
    for (let i = 0; i < radios.length; i++) {
        if (radios[i].value === '2') {  // 2=覆盖, 1=追加
            radios[i].checked = true;
            radios[i].dispatchEvent(new Event('change', {bubbles: true}));
            break;
        }
    }
}""")
time.sleep(1)

# 5c. 选择文件（⚠️ 必须用 .first — 页面有两个 #cjFile 元素！）
page.locator("#cjFile").first.set_input_files(r"D:\BaiduSyncdisk\龙虾文件\成绩\提交成绩\电梯24-12.xls")
time.sleep(2)

# 5d. 点击导入弹窗的确定按钮（不是页面的提交按钮！）
page.evaluate("""() => {
    const modal = document.getElementById('importModal');
    if (modal) {
        const btn = modal.querySelector('#btn_success');
        if (btn) { btn.click(); }
    }
}""")
time.sleep(8)
```

⚠️ **导入弹窗的确定按钮** (`#btn_success` in `#importModal`) ≠ **页面提交按钮** (`#btn_tj`)。
⚠️ 导入成功后会弹出"成绩追加成功"或无提示；需要检查弹窗状态并关闭。
⚠️ 导入时选择"覆盖"模式后，平时/期末数据会写入 `<input>` 字段，但总评可能不自动重新计算，需手动核实。

### 6. 关闭弹窗并保存

```python
# 关闭成功提示弹窗
page.evaluate("""() => {
    const modals = document.querySelectorAll('.bootbox.modal.in, .modal[style*="display: block"]');
    for (const m of modals) {
        const btn = m.querySelector('.bootbox-close-button, .btn-primary, button');
        if (btn) { btn.click(); }
    }
}""")
time.sleep(2)

# 强制清理残留弹窗和遮罩
page.evaluate("""() => {
    document.querySelectorAll('.modal-backdrop').forEach(b => b.remove());
    document.body.classList.remove('modal-open');
    document.body.style.overflow = 'auto';
    document.body.style.paddingRight = '';
    if (typeof bootbox !== 'undefined' && bootbox.hideAll) bootbox.hideAll();
}""")
time.sleep(1)

# 点击保存按钮
page.evaluate("document.getElementById('btn_bc').click()")
time.sleep(8)
```

⚠️ 导入后必须**先关闭所有弹窗和遮罩**，再点保存。否则保存按钮点击会被阻塞。
⚠️ `modal-backdrop` 会遮挡页面按钮，必须移除。
⚠️ **必须验证保存成功**：点击保存按钮后，必须检测页面文本是否包含"保存成功"。如果未检测到，说明点击被遮挡或未生效，需要重新清理弹窗后再次点击。用户多次反馈"没有点保存按钮"，根因是弹窗遮罩未完全清除导致点击无效。

## 关键按钮ID

| 按钮 | ID | 位置 | 说明 |
|------|-----|------|------|
| 导入 | `btn_dr` | 成绩详情页 | 打开导入弹窗 |
| 保存 | `btn_bc` | 成绩详情页 | 保存已录入/导入的成绩 |
| 提交 | `btn_tj` | 成绩详情页 | ⚠️ 提交后不可修改 |
| 确定 | `btn_qd` | 课程列表页 | 进入详情页 |
| 返回 | `btn_fh` | 成绩详情页 | 返回列表页 |
| 下载模板 | `btn_xzmb` | 成绩详情页 | 下载空白模板 |
| 导入确定 | `btn_success` | 导入弹窗内 | 确认导入 |
| 导入关闭 | `btn_cancel` | 导入弹窗内 | 取消导入 |

## 关键Pitfalls

### Pitfall 0: 区分成绩模板文件格式（⚠️ 2026-06-17）

教务系统存在两种成绩模板格式，必须确认使用正确的模板：

| 模板文件 | 列名 | 数据行字体 | 数据行对齐 |
|:---|:---|:---|:---|
| **成绩最终模板.xls** | `平时成绩：60(必填)` / `期末成绩：40(必填)` | 全部宋体13pt | 垂直居中 |
| **高等数学1学生成绩录入模板[李盘润].xls** | `平时(必填)` / `期末(必填)` | 平时成绩列：Arial 10pt | 平时成绩列：垂直底部对齐 |

**操作前必须确认用户要求使用哪个模板**。格式差异会导致教务系统导入失败。

### Pitfall 1: 弹窗遮罩导致按钮不可点击（⚠️ 2026-06-17 高频问题）
导入完成后有两层弹窗（导入弹窗 + 成功提示），加上 `.modal-backdrop` 遮罩，会导致页面上的保存按钮点击无反应。
**症状**：脚本显示"已点击保存按钮"，但教务系统中成绩实际未保存。
**根因**：`page.evaluate("document.getElementById('btn_bc').click()")` 被遮罩拦截，JavaScript执行成功但浏览器不响应点击事件。
**解决**：
1. 先关闭所有弹窗（bootbox + modal）
2. 移除 `.modal-backdrop`
3. 移除 `modal-open` class
4. **等待2秒**让DOM更新
5. 检查保存按钮状态（`disabled: false`, `visible: true`）
6. 点击保存按钮
7. **验证保存成功**：检测页面文本包含"保存成功"
```python
# 验证保存成功
success_message = page.evaluate("""() => {
    const text = document.body ? document.body.innerText : '';
    return text.includes('保存成功') || text.includes('保存');
}""")
if not success_message:
    print("WARNING: 保存可能未成功，请手动检查！")
```
**关键**：如果未检测到保存成功提示，必须重新清理弹窗后再次点击保存按钮。

### Pitfall 2: 导入确定 ≠ 页面提交
`#btn_success`（导入弹窗内确定）只关闭弹窗。`#btn_tj`（页面提交按钮）才是正式提交成绩，提交后不可修改。
**用户可能只要导入不提交**，操作前必须确认。

### Pitfall 3: jqGrid精确匹配
班级名必须用 `===` 精确匹配。合并班级（如"电梯24-1;电梯24-2"）是一个完整字符串，不是分开的。
**查找示例**：`r.jxbzc === '电梯24-1;电梯24-2'`

### Pitfall 11: 导入模式选择 — 追加 vs 覆盖（⚠️ 2026-06-18）

导入弹窗中有两个隐藏的 radio 按钮，控制导入方式：

| 模式 | value | 标签 | 默认 | 行为 |
|------|-------|------|------|------|
| 追加 | `1` | 追加 | 是 | 在已有成绩上叠加导入 |
| 覆盖 | `2` | 覆盖 | 否 | 替换已有成绩数据 |

**选择覆盖模式的正确方法**：
```python
page.evaluate("""() => {
    const radios = document.querySelectorAll('#importModal input[name="drfs"]');
    for (let i = 0; i < radios.length; i++) {
        if (radios[i].value === '2') {
            radios[i].checked = true;
            radios[i].dispatchEvent(new Event('change', {bubbles: true}));
            break;
        }
    }
}""")
time.sleep(1)
```

⚠️ 覆盖模式导入后，平时和期末成绩会写入input字段，但总评可能显示旧值（不自动重新计算）。需要手动核实总评是否正确。

### Pitfall 12: 导入弹窗存在两个 #cjFile 元素（⚠️ 2026-06-18）

成绩详情页面和导入弹窗中各有一个 `#cjFile` 文件选择框。Playwright 的 `page.locator("#cjFile")` 会匹配到两个元素并报 `strict mode violation`。

**解决**：使用 `.first` 限定为第一个元素：
```python
page.locator("#cjFile").first.set_input_files(filepath)
```

### Pitfall 13: "请求正在处理中" 阻塞弹窗（⚠️ 2026-06-18）

如果前一次导入请求尚未完成，再次点击导入按钮会弹出 bootbox alert 提示"请求正在处理中，请勿重复提交!"。该弹窗会阻塞后续所有操作。

**症状**：
- `btn_dr` 点击后不打开导入弹窗
- 页面显示 bootbox alert: "请求正在处理中，请勿重复提交!"

**解决**：
```python
# 关闭阻塞弹窗
page.evaluate("""() => {
    const alert = document.getElementById('alertModal');
    if (alert && alert.offsetParent !== null) {
        const btn = alert.querySelector('.btn-primary');
        if (btn) btn.click();
    }
    document.querySelectorAll('.modal-backdrop').forEach(b => b.remove());
    document.body.classList.remove('modal-open');
}""")
time.sleep(3)
# 然后重试导入
page.evaluate("document.getElementById('btn_dr').click()")
```

### Pitfall 14: 验证导入成绩需检查 input.value 而非 textContent（⚠️ 2026-06-18）

导入后，平时和期末成绩存储在 `<input name="xmcj">` 元素的 `value` 属性中，而不是直接显示为单元格文本。使用 `cells[0].textContent` 读取会返回空字符串。

**正确验证方法**：
```python
# ✅ 正确：检查input的value属性
scores = page.evaluate("""() => {
    const table = document.getElementById('cjlrTable_right');
    const rows = table.querySelectorAll('tr');
    const data = [];
    for (let i = 1; i < Math.min(rows.length, 6); i++) {
        const cells = rows[i].querySelectorAll('td');
        const psInput = cells[0].querySelector('input');
        const qmInput = cells[1].querySelector('input');
        data.push({
            daily: psInput ? psInput.value : '',
            final: qmInput ? qmInput.value : '',
            total: (cells[2].textContent || '').trim()
        });
    }
    return data;
}""")

# ❌ 错误：textContent对input元素返回空字符串
wrong = page.evaluate("cells[0].textContent")  # 空字符串！
```

### Pitfall 15: 成绩录入页面可能已在详情视图（⚠️ 2026-06-18）

通过菜单进入成绩录入时，如果之前操作过该页面，浏览器可能直接打开详情视图（URL 含 `doType=details`）。此时 jqGrid 不可用，无法选择班级。

**检测与解决**：
```python
url = grade_page.url
if "doType=details" in url:
    # 先回到列表视图
    grade_page.goto("https://jw.scitc.edu.cn/cjlrgl/jscjlr_cxJscjlrIndex.html?gnmkdm=N302505&layout=default")
    time.sleep(8)
```
从详情页返回课程列表页面后，`jQuery('#jxrwGrid').getDataIDs()` 可能返回空数组，导致找不到目标班级。
**症状**：`jqGrid('getDataIDs')` 返回 `[]`，但页面上实际有班级列表。
**根因**：页面导航后jqGrid需要时间初始化，或者页面状态不一致。
**解决**：返回列表页后，如果jqGrid返回空数据，执行 `page.reload()` 刷新页面，等待8秒后再查询。
```python
page.goto("https://jw.scitc.edu.cn/cjlrgl/jscjlr_cxJscjlrIndex.html?gnmkdm=N302505&layout=default")
time.sleep(8)
# 检查jqGrid是否有数据
rows = page.evaluate("jQuery('#jxrwGrid').jqGrid('getDataIDs')")
if not rows:
    page.reload()
    time.sleep(8)
```

### Pitfall 16: 切换班级后导入可能静默失败（⚠️ 2026-06-18）

成功导入一个班级（如物联网24-1）后，**直接返回列表再导入另一个班级（如计网24-3）可能导致静默失败**：导入流程无报错，但所有学生成绩为空。

**症状**：
- 上一个班级导入成功（91人全部有数据）
- 返回列表→选新班→进入详情→导入→保存
- 导入无报错弹窗（无"成绩追加成功"）
- 保存后成绩全部为空（0/51人）

**可能根因**：
1. 页面状态在课程切换时未完全重置（jqGrid的详情视图缓存未清除）
2. 新的详情页接收了上一个课程的视图状态，导入操作作用到了错误的绑定
3. `page.goto(LIST_URL)` 后导航到详情页可能未等到页面的完全初始化

**预防措施**：
```python
# 切换班级时，强制刷新页面以确保状态干净
grade_page.goto("https://jw.scitc.edu.cn/cjlrgl/jscjlr_cxJscjlrIndex.html?gnmkdm=N302505&layout=default")
time.sleep(5)
grade_page.reload()  # 强制刷新
time.sleep(8)

# 然后才选新班级、进入详情
row = grade_page.evaluate("...find target class...")
grade_page.evaluate("jQuery('#jxrwGrid').jqGrid('setSelection', '" + row['id'] + "')")
time.sleep(2)  # 多等一点
grade_page.evaluate("document.getElementById('btn_qd').click()")
time.sleep(10)  # 给详情页足够时间加载
```

**特别提醒**：切换班级时宁可多等几秒也不要赶时间。详情页加载完成后的特征是 `#btn_xzmb` 按钮从 disabled 变为 enabled。

### Pitfall 4: bootbox弹窗需用bootbox API关闭
bootbox创建的弹窗用 `.bootbox-close-button` 或 `bootbox.hideAll()` 关闭，普通 `.modal` 的 close 方法可能无效。

### Pitfall 5: 成绩文件路径用Windows原生路径
`set_input_files()` 接受 Windows 原生路径：`r"D:\BaiduSyncdisk\龙虾文件\成绩\提交成绩\电梯24-12.xls"`

### Pitfall 6: 成绩文件格式必须匹配教务系统模板（⚠️ 2026-06-05, updated 2026-06-06）

教务系统导入对Excel格式有严格要求。格式不匹配可能导致导入失败或数据错乱。

**模板格式要求**（从`高等数学4学生成绩录入模板[李盘润].xls`提取）：

| 项目 | 表头行（序号/班级/学号/姓名/备注） | 平时/期末列表头 | 数据行 |
|:---|:---|:---|:---|
| 字体 | 宋体 23pt | 黑体 15pt | 宋体 13pt |
| 对齐 | 居中 | 居中 | 居中 |
| 边框 | 四边细线 | 四边细线 | 四边细线 |
| 列名 | 序号/班级/学号/姓名/备注 | `平时成绩：60(必填)` / `期末成绩：40(必填)` | — |

**常见格式问题**：
- 下载的模板表头可能是`平时(必填)`/`期末(必填)`，需改为`平时成绩：60(必填)`/`期末成绩：40(必填)`
- 字体可能是Arial 10pt，需改为宋体/黑体
- 可能没有边框和居中对齐
- 数值类型的分数（如97.0）应转为文本（"97"）

**修复方法**：用Excel COM自动化（win32com）打开模板文件，替换数据行，保存。xlrd+xlwt方案会丢失format_key（0→164）和cell_locked属性，不能用于精确复刻。参考 `references/excel-com-template-replication.md`。模板文件：`D:\BaiduSyncdisk\龙虾文件\成绩\提交成绩\高等数学4学生成绩录入模板[李盘润] (1).xls`。

### Pitfall 7: Excel COM修复格式的正确顺序（⚠️ 2026-06-06）

用Excel COM修复已有文件的格式时，**顺序至关重要**：

```python
# ✅ 正确顺序：先设格式，再写值
# 1. 先设NumberFormat为文本
ws.Range(ws.Cells(2, 5), ws.Cells(rows, 5)).NumberFormat = '@'
# 2. 再写入字符串值
for i, val in enumerate(values):
    ws.Cells(i + 2, 5).Value = str(int(float(val)))

# ❌ 错误：先Clear()再设值 — Clear()会重置NumberFormat
cell.Clear()           # 这会把刚设的@格式清掉！
cell.Value = '95'      # 又变回General格式

# ❌ 错误：只设值不设格式 — Excel COM把'95'当数字处理
cell.Value = '95'      # 实际存为95.0 (float)
```

### Pitfall 8: NumberFormat='@'会重置字体为Arial/10pt

Excel COM对单元格设`NumberFormat='@'`后，字体可能被重置为Arial 10pt（而非宋体13pt）。
**解决**：设完NumberFormat后，必须重新设置字体：

```python
for r in range(2, rows + 1):
    cell = ws.Cells(r, 5)
    cell.Font.Name = '宋体'
    cell.Font.Size = 13
```

### Pitfall 9: 表头文字必须精确匹配

教务系统按表头文字识别列。常见错误：
- `平时(必填)` → 应为 `平时成绩：60(必填)`
- `期末(必填)` → 应为 `期末成绩：40(必填)`

修复时先改表头文字，再改数据格式。

## 格式修复快速检查清单

从教务系统下载的模板/已有文件，按此顺序检查和修复：

1. **表头E列**：值必须为 `平时成绩：60(必填)`（不是`平时(必填)`）
2. **表头F列**：值必须为 `期末成绩：40(必填)`（不是`期末(必填)`）
3. **E列数据类型**：必须为文本(str)，不是数字(float)
4. **E列字体**：宋体 13pt（不是Arial 10pt）
5. **垂直对齐**：E列数据行应为底部对齐(ver=-4107)

参考 `references/excel-com-fix-template.py` 获取完整的格式修复脚本模板。

## 成绩文件位置

| 目录 | 内容 |
|------|------|
| `D:\\BaiduSyncdisk\\龙虾文件\\成绩\\提交成绩\\` | 待导入的成绩文件 |
| `D:\\BaiduSyncdisk\\龙虾文件\\成绩\\` | 成绩册和分析表 |

## 参考文件

- `references/import-cover-mode-and-pitfalls.md` — 覆盖模式导入完整流程、弹窗处理、成绩验证方法（2026-06-18）
