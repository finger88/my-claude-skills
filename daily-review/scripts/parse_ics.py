#!/usr/bin/env python
"""飞书日历 ICS 解析器。提取指定日期（或日期范围/整月）的事件，输出 JSON。

用法:
  python parse_ics.py <ics_file> <date>           # 单日: 2025-09-01
  python parse_ics.py <ics_file> <start>~<end>     # 范围: 2025-09-01~2025-09-07
  python parse_ics.py <ics_file> --month           # 整月（从文件名推断）
  python parse_ics.py <folder> --month 2025-09     # 整月指定

输出 JSON 数组，每个元素:
  { "date": "2025-09-01", "start": "08:30", "end": "11:45",
    "summary": "...", "description": "...", "tags": ["#工作"] }
"""
import re
import sys
import json
import os
from datetime import datetime, timedelta


def parse_ics(file_path):
    """解析 ICS 文件，返回所有事件列表。"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 折行处理: 以空格或tab开头的行拼接到上一行
    lines = content.split("\n")
    processed = []
    for line in lines:
        if line and (line.startswith(" ") or line.startswith("\t")):
            if processed:
                processed[-1] += line[1:]
        else:
            processed.append(line)

    processed_content = "\n".join(processed)

    # 提取 VEVENT 块
    raw_events = re.findall(
        r"BEGIN:VEVENT\n(.*?)\nEND:VEVENT", processed_content, re.DOTALL
    )

    events = []
    for ev in raw_events:
        fields = {}
        for line in ev.split("\n"):
            if ":" in line:
                key, val = line.split(":", 1)
                fields[key] = val

        dtstart = fields.get("DTSTART", "")
        dtend = fields.get("DTEND", "")
        summary = fields.get("SUMMARY", "")
        description = fields.get("DESCRIPTION", "")

        # 转义处理
        description = (
            description.replace("\\n", "\n")
            .replace("\\,", ",")
            .replace("\\;", ";")
        )

        # 提取 SUMMARY 中的标签 (#工作, #学习, #生活, #育儿 等)
        tags = re.findall(r"#\S+", summary)

        # 解析时间
        if len(dtstart) >= 15:
            date_str = f"{dtstart[:4]}-{dtstart[4:6]}-{dtstart[6:8]}"
            start_time = f"{dtstart[9:11]}:{dtstart[11:13]}"
        else:
            date_str = dtstart
            start_time = ""

        if len(dtend) >= 15:
            end_time = f"{dtend[9:11]}:{dtend[11:13]}"
        else:
            end_time = ""

        events.append(
            {
                "date": date_str,
                "start": start_time,
                "end": end_time,
                "summary": summary,
                "description": description.strip(),
                "tags": tags,
            }
        )

    # 按日期+开始时间排序
    events.sort(key=lambda x: (x["date"], x["start"]))
    return events


def filter_by_date(events, target_date):
    """筛选单日事件。target_date 格式: YYYY-MM-DD"""
    return [e for e in events if e["date"] == target_date]


def filter_by_range(events, start_date, end_date):
    """筛选日期范围内的事件。"""
    return [e for e in events if start_date <= e["date"] <= end_date]


def get_month_range(year_month):
    """从 YYYY-MM 返回该月的起止日期。"""
    year, month = int(year_month[:4]), int(year_month[5:7])
    start = f"{year:04d}-{month:02d}-01"
    if month == 12:
        end = f"{year + 1:04d}-01-01"
    else:
        end = f"{year:04d}-{month + 1:02d}-01"
    # end 减一天
    end_dt = datetime.strptime(end, "%Y-%m-%d") - timedelta(days=1)
    end = end_dt.strftime("%Y-%m-%d")
    return start, end


def infer_month_from_filename(file_path):
    """从文件名推断月份: calendar_2025_09.ics -> 2025-09"""
    basename = os.path.basename(file_path)
    m = re.search(r"(\d{4})_(\d{2})", basename)
    if m:
        return f"{m.group(1)}-{m.group(2)}"
    return None


def main():
    if len(sys.argv) < 3:
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]
    date_arg = sys.argv[2]

    # 如果第一个参数是目录，按月份找文件
    if os.path.isdir(file_path) and date_arg.startswith("--month"):
        folder = file_path
        if len(sys.argv) > 3:
            year_month = sys.argv[3]
        else:
            print("需要指定月份，如: --month 2025-09", file=sys.stderr)
            sys.exit(1)
        ym = year_month.replace("-", "_")
        file_path = os.path.join(folder, f"calendar_{ym}.ics")
        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}", file=sys.stderr)
            sys.exit(1)
        start, end = get_month_range(year_month)
        events = parse_ics(file_path)
        result = filter_by_range(events, start, end)
    elif date_arg == "--month":
        year_month = infer_month_from_filename(file_path)
        if not year_month:
            if len(sys.argv) > 3:
                year_month = sys.argv[3]
            else:
                print("无法从文件名推断月份，请指定: --month 2025-09", file=sys.stderr)
                sys.exit(1)
        start, end = get_month_range(year_month)
        events = parse_ics(file_path)
        result = filter_by_range(events, start, end)
    elif "~" in date_arg:
        start, end = date_arg.split("~", 1)
        events = parse_ics(file_path)
        result = filter_by_range(events, start.strip(), end.strip())
    else:
        events = parse_ics(file_path)
        result = filter_by_date(events, date_arg)

    # Windows 终端强制 UTF-8 输出
    sys.stdout.reconfigure(encoding="utf-8")
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
