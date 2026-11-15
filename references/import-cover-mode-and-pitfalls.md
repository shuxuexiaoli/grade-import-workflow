# 覆盖模式导入 + 2026-06-18 关键发现

## 场景
物联网24-1/2 高等数学4 成绩导入。原有数据只有总评，缺少平时和期末分项。用 `物联网24-12_最终模板格式.xlsx` 覆盖导入成功。

## 覆盖模式完整流程

```python
# 1. 打开导入弹窗
page.evaluate('document.getElementById("btn_dr").click()')
time.sleep(3)

# 2. 选择覆盖模式（radio button value="2"）
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

# 3. 选择文件（必须用 .first）
page.locator("#cjFile").first.set_input_files(grade_file_path)
time.sleep(2)

# 4. 点击导入确定（弹窗内的btn_success）
page.evaluate("""() => {
    const modal = document.getElementById('importModal');
    if (modal) {
        const btn = modal.querySelector('#btn_success');
        if (btn) btn.click();
    }
}""")
time.sleep(8)  # 等待导入完成

# 5. 关闭successModal（如果有）
page.evaluate("""() => {
    var sm = document.getElementById('successModal');
    if (sm && sm.offsetParent !== null) {
        var btn = sm.querySelector('.btn-primary');
        if (btn) btn.click();
    }
}""")
time.sleep(2)

# 6. 隐藏importModal + 清理遮罩
page.evaluate("""() => {
    var im = document.getElementById('importModal');
    if (im) { im.style.display = 'none'; }
    document.querySelectorAll('.modal-backdrop').forEach(b => b.remove());
    document.body.classList.remove('modal-open');
    document.body.style.overflow = 'auto';
    if (typeof bootbox !== 'undefined' && bootbox.hideAll) bootbox.hideAll();
}""")
time.sleep(3)

# 7. 检查保存按钮状态
btn_state = page.evaluate("""() => {
    const btn = document.getElementById('btn_bc');
    if (!btn) return {exists: false};
    return {exists: true, disabled: btn.disabled, visible: btn.offsetParent !== null};
}""")

# 8. 保存
page.evaluate('document.getElementById("btn_bc").click()')
time.sleep(6)

# 9. 验证保存成功
text = page.evaluate("() => document.body.innerText")
saved = "保存成功" in text
```

## 关键观察

### 1. 覆盖模式导入后成绩存在但显示方式不同
- 平时和期末成绩存在于 `<input name="xmcj">` 元素中
- 单元格 `textContent` 为空字符串（input元素不贡献文本内容）
- 必须通过 `input.querySelector('input').value` 获取
- 总评列是纯文本显示，用 `textContent` 读取即可

### 2. 总评可能未自动重算
覆盖导入后：
- 平时成绩：正确写入 ✅
- 期末成绩：正确写入 ✅
- 总评：显示旧值（不触发自动重算）⚠️

源文件数据示例：
- 江春: 平时=85, 期末=34, 加权=64.6
- 系统显示: 平时=85 ✅, 期末=34 ✅, 但总评=34 ❌（旧值）

大部分学生总评计算正确（四舍五入到整数），个别数据需要手动核实。

### 3. 弹窗状态检查方法
```python
modals = page.evaluate("""() => {
    var result = [];
    document.querySelectorAll('.bootbox.modal.in, #successModal, #alertModal')
        .forEach(function(m) {
            if (m.offsetParent !== null) {
                result.push({id: m.id, text: m.innerText.substring(0, 120)});
            }
        });
    return result;
}""")
```

### 4. "请求正在处理中" 处理流程
```
症状：点击 btn_dr 后没有反应，页面出现 bootbox alert
内容："警告提示\n请求正在处理中，请勿重复提交!"
解决：关闭 alertModal → 清理 backdrop → 等待3秒 → 重新点击 btn_dr
```

### 5. 首次导入后"追加"模式未生效
第一次用 .xls 文件（列名 `平时(必填)`，数据只有期末列）追加导入 → 提示"成绩追加成功"但数据未出现在表格中。
第二次用 _最终模板格式.xlsx 文件覆盖导入 → 成功。
推测：追加模式在列名不匹配时不会报错但静默失败。

## 文件对比

| 文件 | 表头 | 数据 |
|------|------|------|
| `物联网24-12.xls` | `平时(必填)` / `期末(必填)` | 平时=空, 期末=49... |
| `物联网24-12_最终模板格式.xlsx` | `平时成绩：60(必填)` / `期末成绩：40(必填)` | 平时=87, 期末=49... |

**结论**：必须使用列名完全匹配教务系统预期的文件格式导入。