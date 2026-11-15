# 批量导入成绩的完整模式

## 概述
当需要对多个班级执行相同的"导入→保存"操作时，使用以下批量模式。

## 批量导入脚本模板

```python
import sys
sys.stdout.reconfigure(encoding='utf-8')

from playwright.sync_api import sync_playwright
import time
import os

# 连接到已运行的浏览器
p = sync_playwright().start()
browser = p.chromium.connect_over_cdp("http://localhost:9222")

# 查找成绩录入页面
page = None
for pg in browser.contexts[0].pages:
    if "cjlrgl" in pg.url:
        page = pg
        break

# 定义导入任务
import_tasks = [
    {"class_name": "计网24-1", "file_name": "计网24-1_最终模板格式.xlsx"},
    {"class_name": "计网24-2", "file_name": "计网24-2_最终模板格式.xlsx"},
    {"class_name": "物联网24-1;物联网24-2", "file_name": "物联网24-12_最终模板格式.xlsx"},
    {"class_name": "电梯24-1;电梯24-2", "file_name": "电梯24-12_最终模板格式.xlsx"},
]

base_dir = r"D:\BaiduSyncdisk\学校事情\上课相关\成绩\2026年春成绩\2026年春大二成绩\大二成绩"

for task in import_tasks:
    target_class = task["class_name"]
    file_name = task["file_name"]
    
    # 1. 返回课程列表
    page.goto("https://jw.scitc.edu.cn/cjlrgl/jscjlr_cxJscjlrIndex.html?gnmkdm=N302505&layout=default")
    time.sleep(8)
    
    # 2. 检查jqGrid是否有数据（Pitfall 10）
    rows = page.evaluate("jQuery('#jxrwGrid').jqGrid('getDataIDs')")
    if not rows:
        page.reload()
        time.sleep(8)
    
    # 3. 查找目标班级
    row_info = page.evaluate("""(targetClass) => {
        const grid = jQuery('#jxrwGrid');
        const ids = grid.jqGrid('getDataIDs');
        for (let i = 0; i < ids.length; i++) {
            const r = grid.jqGrid('getRowData', ids[i]);
            if (r.jxbzc === targetClass) {
                return {id: ids[i], jxbzc: r.jxbzc, kcmc: r.kcmc, lrztmc: r.lrztmc};
            }
        }
        return null;
    }""", target_class)
    
    if not row_info:
        print(f"未找到班级: {target_class}")
        continue
    
    # 4. 选中行并进入详情
    page.evaluate(f"jQuery('#jxrwGrid').jqGrid('setSelection', '{row_info['id']}')")
    time.sleep(1)
    page.evaluate("document.getElementById('btn_qd').click()")
    time.sleep(8)
    
    # 5. 导入文件
    page.evaluate("document.getElementById('btn_dr').click()")
    time.sleep(3)
    page.locator("#cjFile").set_input_files(os.path.join(base_dir, file_name))
    time.sleep(2)
    
    # 6. 点击导入确定
    page.evaluate("""() => {
        const modal = document.getElementById('importModal');
        if (modal) {
            const btn = modal.querySelector('#btn_success');
            if (btn) { btn.click(); }
        }
    }""")
    time.sleep(8)
    
    # 7. 关闭所有弹窗（关键！）
    page.evaluate("""() => {
        const modals = document.querySelectorAll('.bootbox.modal.in, .modal[style*="display: block"]');
        for (const m of modals) {
            const btn = m.querySelector('.bootbox-close-button, .btn-primary, button');
            if (btn) { btn.click(); }
        }
    }""")
    time.sleep(2)
    
    # 8. 清理遮罩（关键！）
    page.evaluate("""() => {
        document.querySelectorAll('.modal-backdrop').forEach(b => b.remove());
        document.body.classList.remove('modal-open');
        document.body.style.overflow = 'auto';
        document.body.style.paddingRight = '';
        if (typeof bootbox !== 'undefined' && bootbox.hideAll) bootbox.hideAll();
    }""")
    time.sleep(2)
    
    # 9. 检查保存按钮状态
    save_btn_info = page.evaluate("""() => {
        const btn = document.getElementById('btn_bc');
        if (!btn) return null;
        return {disabled: btn.disabled, visible: btn.offsetParent !== null};
    }""")
    
    if save_btn_info and not save_btn_info['disabled']:
        # 10. 点击保存
        page.evaluate("document.getElementById('btn_bc').click()")
        time.sleep(8)
        
        # 11. 验证保存成功（关键！）
        success = page.evaluate("""() => {
            const text = document.body ? document.body.innerText : '';
            return text.includes('保存成功') || text.includes('保存');
        }""")
        
        if success:
            print(f"✅ {target_class} 导入并保存成功")
        else:
            print(f"⚠️ {target_class} 保存可能未成功")
    else:
        print(f"❌ {target_class} 保存按钮不可用")
```

## 关键时序

每个班级的完整操作耗时约50秒：
- 返回列表页: 8s
- jqGrid查找+选行: 2s
- 进入详情页: 8s
- 导入按钮+选文件: 5s
- 导入确定: 8s
- 关闭弹窗+清理遮罩: 4s
- 点击保存+验证: 8s

## 合并班级文件映射

教务系统中的合并班级与文件名的对应关系：

| 教务系统班级名 | 成绩文件名 | 说明 |
|:---|:---|:---|
| 计网24-1 | 计网24-1_最终模板格式.xlsx | 单独班级 |
| 计网24-2 | 计网24-2_最终模板格式.xlsx | 单独班级 |
| 计网24-3 | 计网24-3_最终模板格式.xlsx | 单独班级 |
| 物联网24-1;物联网24-2 | 物联网24-12_最终模板格式.xlsx | 合并班级，文件包含两个班学生 |
| 电梯24-1;电梯24-2 | 电梯24-12_最终模板格式.xlsx | 合并班级，文件包含两个班学生 |
