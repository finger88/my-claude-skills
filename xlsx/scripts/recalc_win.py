# -*- coding: utf-8 -*-
"""
Windows 版 Excel 公式验证脚本
替代官方 recalc.py，使用本地 Excel COM 接口
"""

import win32com.client
import json
import sys
from pathlib import Path


def verify_excel(filepath, timeout=30):
    """
    打开 Excel 文件，强制重算所有公式，检查错误
    返回详细的错误报告
    """
    excel = None
    workbook = None

    try:
        # 启动 Excel（不可见）
        excel = win32com.client.Dispatch("Excel.Application")
        excel.Visible = False
        excel.DisplayAlerts = False
        excel.EnableEvents = False

        # 打开文件
        workbook = excel.Workbooks.Open(str(Path(filepath).resolve()))

        # 强制重算所有公式
        excel.CalculateFullRebuild()

        # 收集所有公式和错误
        total_formulas = 0
        error_count = 0
        error_summary = {}
        sheet_details = []

        for sheet in workbook.Sheets:
            sheet_errors = []
            used_range = sheet.UsedRange

            for row in range(1, used_range.Rows.Count + 1):
                for col in range(1, used_range.Columns.Count + 1):
                    cell = sheet.Cells(row, col)

                    # 检查是否有公式
                    if cell.HasFormula:
                        total_formulas += 1
                        value = cell.Value

                        # 检查错误值
                        if isinstance(value, int) and value in range(-2146826281, -2146826242):
                            # COM 错误码范围
                            error_count += 1
                            error_text = str(cell.Text)
                            cell_ref = f"{sheet.Name}!{cell.Address.replace('$', '')}"

                            if error_text not in error_summary:
                                error_summary[error_text] = {
                                    "count": 0,
                                    "locations": []
                                }
                            error_summary[error_text]["count"] += 1
                            error_summary[error_text]["locations"].append(cell_ref)
                            sheet_errors.append({
                                "cell": cell_ref,
                                "formula": cell.Formula,
                                "error": error_text
                            })

            sheet_details.append({
                "sheet": sheet.Name,
                "errors": sheet_errors
            })

        # 保存（确保重算后的值被写入）
        workbook.Save()

        result = {
            "status": "success" if error_count == 0 else "errors_found",
            "file": filepath,
            "total_formulas": total_formulas,
            "total_errors": error_count,
        }

        if error_count > 0:
            result["error_summary"] = error_summary
            result["details"] = sheet_details

        return result

    except Exception as e:
        return {
            "status": "error",
            "file": filepath,
            "error": str(e)
        }

    finally:
        if workbook:
            workbook.Close(SaveChanges=False)
        if excel:
            excel.Quit()


def main():
    if len(sys.argv) < 2:
        print("用法: python recalc_win.py <excel_file> [timeout_seconds]", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]
    timeout = int(sys.argv[2]) if len(sys.argv) > 2 else 30

    result = verify_excel(filepath, timeout)
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # 返回退出码
    sys.exit(0 if result.get("status") == "success" else 1)


if __name__ == "__main__":
    main()
