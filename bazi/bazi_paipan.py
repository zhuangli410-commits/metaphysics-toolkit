#!/usr/bin/env python3
from __future__ import annotations
"""
bazi_paipan.py — 八字排盘工具（公历/农历生日 → 四柱、十神、大运、流年）

依赖：pip install lunar_python
用途：给出生日期时间，排出完整四柱八字 + 十神 + 大运列表。
     用于命理学习、格局核对、剧本命格设计。

十神速查（以日干为"我"）：
    克我 = 官杀（异性=正官，同性=七杀）
    我克 = 财   （异性=正财，同性=偏财）
    生我 = 印   （异性=正印，同性=偏印）
    我生 = 食伤 （异性=伤官，同性=食神）
    同我 = 比劫

用法：
    python3 bazi_paipan.py 1988-05-20 08:00          # 公历 + 24h制
    python3 bazi_paipan.py 1998-07-04 12:00 --gender 男
    python3 bazi_paipan.py 1988-05-20 08:00 --liunian 2026
"""

import argparse
import sys

try:
    from lunar_python import Solar, Lunar
except ImportError:
    sys.exit("缺少依赖：请先 pip install lunar_python")

GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]  # 阳阳阴阴阳阳阴阴阳阴
ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
ZHI_HIDE = {  # 地支藏干（本气在前）
    "子": ["癸"], "丑": ["己", "癸", "辛"], "寅": ["甲", "丙", "戊"],
    "卯": ["乙"], "辰": ["戊", "乙", "癸"], "巳": ["丙", "庚", "戊"],
    "午": ["丁", "己"], "未": ["己", "丁", "乙"], "申": ["庚", "壬", "戊"],
    "酉": ["辛"], "戌": ["戊", "辛", "丁"], "亥": ["壬", "甲"],
}
SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}   # 我生
KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}     # 我克
GAN_WUXING = {"甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
              "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"}
ZHI_WUXING = {"寅": "木", "卯": "木", "巳": "火", "午": "火", "申": "金", "酉": "金",
              "亥": "水", "子": "水", "辰": "土", "戌": "土", "丑": "土", "未": "土"}
SHICHEN = [  # 时辰 → 小时区间（起点）
    ("子", 23), ("丑", 1), ("寅", 3), ("卯", 5), ("辰", 7), ("巳", 9),
    ("午", 11), ("未", 13), ("申", 15), ("酉", 17), ("戌", 19), ("亥", 21),
]


def shichen_of(hour: int) -> str:
    """小时 → 时辰地支。23-0 点算子时（晚子时归当日，此处简化取就近区间）。"""
    for zhi, start in SHICHEN:
        if start <= hour < start + 2 or (zhi == "子" and hour == 23):
            return zhi
    return "子"


def ten_star(day_gan: str, other_gan: str) -> str:
    """十神：以日干为基准。阴阳异同决定正/偏。"""
    dw, ow = GAN_WUXING[day_gan], GAN_WUXING[other_gan]
    same_yin_yang = (GAN.index(day_gan) % 2) == (GAN.index(other_gan) % 2)
    if dw == ow:
        return "比肩" if same_yin_yang else "劫财"
    if KE[dw] == ow:
        return "七杀" if same_yin_yang else "正官"   # 克我：同性七杀，异性正官
    if SHENG[ow] == dw:
        return "偏印" if same_yin_yang else "正印"   # 生我
    if SHENG[dw] == ow:
        return "食神" if same_yin_yang else "伤官"   # 我生
    if KE[ow] == dw:
        return "偏财" if same_yin_yang else "正财"   # 我克：同性偏财，异性正财
    return "?"


def paipan(y: int, m: int, d: int, hh: int, mm: int, gender: str, liunian: int | None):
    solar = Solar.fromYmdHms(y, m, d, hh, mm, 0)
    lunar = solar.getLunar()
    ec = lunar.getEightChar()
    day_gan = ec.getDayGan()

    pillars = [
        ("年柱", ec.getYear(), ec.getYearGan(), ec.getYearZhi()),
        ("月柱", ec.getMonth(), ec.getMonthGan(), ec.getMonthZhi()),
        ("日柱", ec.getDay(), ec.getDayGan(), ec.getDayZhi()),
        ("时柱", ec.getTime(), ec.getTimeGan(), ec.getTimeZhi()),
    ]

    print(f"\n公历 {y}-{m:02d}-{d:02d} {hh:02d}:{mm:02d}   "
          f"农历 {lunar.toString()}   [{gender}]")
    print(f"生肖 {lunar.getYearShengXiao()}\n")
    print(f"{'':<4}{'十神':<6}{'干支':<6}{'藏干':<14}")
    print("-" * 34)
    for name, gz, gan, zhi in pillars:
        hides = "、".join(ZHI_HIDE[zhi])
        star = "日主" if name == "日柱" else ten_star(day_gan, gan)
        print(f"{name:<4}{star:<6}{gz:<6}{hides:<14}")

    # 五行统计（天干+地支本气）
    count = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
    for _, _, gan, zhi in pillars:
        count[GAN_WUXING[gan]] += 1
        count[ZHI_WUXING[zhi]] += 1
    print("\n五行（干+支本气）：" + "  ".join(f"{k}{v}" for k, v in count.items()))

    # 大运：lunar_python 自动按 阳年男/阴年女顺排、阴年男/阳年女逆排
    try:
        yun = ec.getYun(1 if gender == "男" else 0)   # 1=男 0=女
        dayuns = yun.getDaYun()          # 注意：不带参数才返回全部；带参数返回空 list
        forward = (GAN.index(ec.getYearGan()) % 2 == 0) == (gender == "男")
        print(f"\n大运（{'顺排' if forward else '逆排'}，{dayuns[1].getStartAge()} 岁起运）：")
        for dy in dayuns[1:]:
            print(f"  {dy.getStartAge():>2}-{dy.getEndAge():<2}岁  {dy.getGanZhi()}")
    except Exception as e:
        print(f"\n[大运计算失败：{e}]")

    if liunian:
        ls = Solar.fromYmd(liunian, 6, 15).getLunar()
        lec = ls.getEightChar()
        lzhi = lec.getYearZhi()
        print(f"\n流年 {liunian}：{lec.getYearGan()}{lzhi}（{ten_star(day_gan, lec.getYearGan())}"
              f"+{ZHI_WUXING[lzhi]}），生肖{ls.getYearShengXiao()}")
        print(f"  与日柱关系可查：{day_gan}{ec.getDayZhi()} vs {lec.getYearGan()}{lzhi}")
    print()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="八字排盘：公历生日 → 四柱十神大运")
    ap.add_argument("date", help="公历日期 YYYY-MM-DD")
    ap.add_argument("time", nargs="?", default="12:00", help="时间 HH:MM（默认午时 12:00）")
    ap.add_argument("--gender", choices=["男", "女"], default="男", help="性别（排大运必需）")
    ap.add_argument("--liunian", type=int, help="流年年份，如 2026")
    a = ap.parse_args()
    hh, mm = map(int, a.time.split(":"))
    y, m, d = map(int, a.date.split("-"))
    if not (1 <= hh <= 23 and 0 <= mm <= 59):
        sys.exit("时间不合法")
    paipan(y, m, d, hh, mm, a.gender, a.liunian)
