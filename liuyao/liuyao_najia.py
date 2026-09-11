#!/usr/bin/env python3
"""
liuyao_najia.py — 六爻纳甲装卦工具

输入：手摇六次结果（从下往上，第一次=初爻），如"少阳 少阴 少阴 少阳 少阴 少阳"
输出：本卦+变卦、卦宫、世应、纳甲地支、六亲、六神（按起卦日干）、旬空

装卦规则：
  1. 六爻自下而上：少阳=阳静，少阴=阴静，老阳=阳动变阴，老阴=阴动变阳
  2. 上卦+下卦 → 卦名（八经卦组合查表）
  3. 定卦宫：本卦在八宫中的归属（京房八宫）
  4. 世应：按本卦在宫中的位置（第几世）定世爻，世隔二位为应爻
  5. 纳甲：按卦宫装地支（乾纳甲壬子寅辰…），内外卦分装
  6. 六亲：以卦宫五行为"我"，按地支五行定兄弟/父母/子孙/妻财/官鬼
  7. 六神：按起卦日天干起，自初爻向上排：青龙朱雀勾陈螣蛇白虎玄武
  8. 旬空：按起卦日干支定旬，旬内所缺二支为空

用法：
    python3 liuyao_najia.py 少阳少阴少阴少阳少阴少阳 --date 2026-09-10
    python3 liuyao_najia.py 阳阴阳阴阳阳 --date 2026-09-10 --time 14:30
    python3 liuyao_najia.cpp 泽天夬 --date 2026-09-10        # 也可以直接给卦名
"""

from __future__ import annotations
import argparse
import sys

try:
    from lunar_python import Solar
except ImportError:
    sys.exit("缺少依赖：请先 pip install lunar_python")

GAN = "甲乙丙丁戊己庚辛壬癸"
ZHI = "子丑寅卯辰巳午未申酉戌亥"

# ── 八经卦：二进制自下而上，1=阳 ──
TRIGRAMS = {
    "乾": (1, 1, 1), "兑": (1, 1, 0), "离": (1, 0, 1), "震": (1, 0, 0),
    "巽": (0, 1, 1), "坎": (0, 1, 0), "艮": (0, 0, 1), "坤": (0, 0, 0),
}
TRI_WUXING = {"乾": "金", "兑": "金", "离": "火", "震": "木",
              "巽": "木", "坎": "水", "艮": "土", "坤": "土"}

# ── 64卦名表：(上卦,下卦) → 卦名（(坤,乾)=地天泰：上坤下乾）──
HEX_NAMES = {
    ("乾","乾"):"乾为天", ("坤","乾"):"地天泰", ("震","乾"):"雷天大壮", ("巽","乾"):"风天小畜",
    ("坎","乾"):"水天需", ("离","乾"):"火天大有", ("艮","乾"):"山天大畜", ("兑","乾"):"泽天夬",
    ("乾","坤"):"天地否", ("坤","坤"):"坤为地", ("震","坤"):"雷地豫", ("巽","坤"):"风地观",
    ("坎","坤"):"水地比", ("离","坤"):"火地晋", ("艮","坤"):"山地剥", ("兑","坤"):"泽地萃",
    ("乾","震"):"天雷无妄", ("坤","震"):"地雷复", ("震","震"):"震为雷", ("巽","震"):"风雷益",
    ("坎","震"):"水雷屯", ("离","震"):"火雷噬嗑", ("艮","震"):"山雷颐", ("兑","震"):"泽雷随",
    ("乾","巽"):"天风姤", ("坤","巽"):"地风升", ("震","巽"):"雷风恒", ("巽","巽"):"巽为风",
    ("坎","巽"):"水风井", ("离","巽"):"火风鼎", ("艮","巽"):"山风蛊", ("兑","巽"):"泽风大过",
    ("乾","坎"):"天水讼", ("坤","坎"):"地水师", ("震","坎"):"雷水解", ("巽","坎"):"风水涣",
    ("坎","坎"):"坎为水", ("离","坎"):"火水未济", ("艮","坎"):"山水蒙", ("兑","坎"):"泽水困",
    ("乾","离"):"天火同人", ("坤","离"):"地火明夷", ("震","离"):"雷火丰", ("巽","离"):"风火家人",
    ("坎","离"):"水火既济", ("离","离"):"离为火", ("艮","离"):"山火贲", ("兑","离"):"泽火革",
    ("乾","艮"):"天山遁", ("坤","艮"):"地山谦", ("震","艮"):"雷山小过", ("巽","艮"):"风山渐",
    ("坎","艮"):"水山蹇", ("离","艮"):"火山旅", ("艮","艮"):"艮为山", ("兑","艮"):"泽山咸",
    ("乾","兑"):"天泽履", ("坤","兑"):"地泽临", ("震","兑"):"雷泽归妹", ("巽","兑"):"风泽中孚",
    ("坎","兑"):"水泽节", ("离","兑"):"火泽睽", ("艮","兑"):"山泽损", ("兑","兑"):"兑为泽",
}

# ── 京房八宫：宫名 → [八卦按一世~归魂顺序]，首位为本宫卦(六世/上世) ──
PALACES = {
    "乾": ["乾为天", "天风姤", "天山遁", "天地否", "风地观", "山地剥", "火地晋", "火天大有"],
    "兑": ["兑为泽", "泽水困", "泽地萃", "泽山咸", "水山蹇", "地山谦", "雷山小过", "雷泽归妹"],
    "离": ["离为火", "火山旅", "火风鼎", "火水未济", "山水蒙", "风水涣", "天水讼", "天火同人"],
    "震": ["震为雷", "雷地豫", "雷水解", "雷风恒", "地风升", "水风井", "泽风大过", "泽雷随"],
    "巽": ["巽为风", "风天小畜", "风火家人", "风雷益", "天雷无妄", "火雷噬嗑", "山雷颐", "山风蛊"],
    "坎": ["坎为水", "水泽节", "水雷屯", "水火既济", "泽火革", "雷火丰", "地火明夷", "地水师"],
    "艮": ["艮为山", "山火贲", "山天大畜", "山泽损", "火泽睽", "天泽履", "风泽中孚", "风山渐"],
    "坤": ["坤为地", "地雷复", "地泽临", "地天泰", "雷天大壮", "泽天夬", "水天需", "水地比"],
}
# 世爻位置：本宫卦世在上爻(6)，一世卦世在初爻……五世卦世在五爻，游魂世在四爻，归魂世在三爻
SHI_POS = [6, 1, 2, 3, 4, 5, 4, 3]

# ── 纳甲：内卦(初二三爻)与外卦(四五上爻)地支，自下而上 ──
NAJIA_IN  = {"乾": ["子","寅","辰"], "坎": ["寅","辰","午"], "艮": ["辰","午","申"],
             "震": ["子","寅","辰"], "巽": ["丑","亥","酉"], "离": ["卯","丑","亥"],
             "坤": ["未","巳","卯"], "兑": ["巳","卯","丑"]}
NAJIA_OUT = {"乾": ["午","申","戌"], "坎": ["申","戌","子"], "艮": ["戌","子","寅"],
             "震": ["午","申","戌"], "巽": ["未","巳","卯"], "离": ["酉","未","巳"],
             "坤": ["丑","亥","酉"], "兑": ["亥","酉","未"]}
# 乾宫纳甲：内卦纳甲(子寅辰)，外卦纳壬(午申戌)。断卦时干支以支为主，干用于六神起例与旬空。

ZHI_WUXING = {"子":"水","丑":"土","寅":"木","卯":"木","辰":"土","巳":"火",
              "午":"火","未":"土","申":"金","酉":"金","戌":"土","亥":"水"}
SHENG = {"木":"火","火":"土","土":"金","金":"水","水":"木"}
KE = {"木":"土","土":"水","水":"火","火":"金","金":"木"}

# 六神起例：日干 → 初爻六神，自下而上顺排
LIUSHEN_SEQ = ["青龙","朱雀","勾陈","螣蛇","白虎","玄武"]
LIUSHEN_START = {"甲":"青龙","乙":"青龙","丙":"朱雀","丁":"朱雀","戊":"勾陈",
                 "己":"勾陈","庚":"白虎","辛":"白虎","壬":"玄武","癸":"玄武"}

# 旬空表：日干支所在旬 → 旬空二支
XUN_TABLE = {}  # 生成：甲子旬起，60甲子每旬
for xun_start in range(0, 60, 10):
    gz = [GAN[(xun_start+i) % 10] + ZHI[(xun_start+i) % 12] for i in range(10)]
    kong1, kong2 = ZHI[(xun_start+10) % 12], ZHI[(xun_start+11) % 12]
    for g in gz:
        XUN_TABLE[g] = [kong1, kong2]


def lines_to_hexagram(lines):
    """lines: 自下而上6个元素，'少阳'/'少阴'/'老阳'/'老阴' 或 '阳'/'阴'/'动阳'/'动阴'
    返回 (下卦名, 上卦名, 卦名, 变卦lines)"""
    def tri(bits):
        for name, pat in TRIGRAMS.items():
            if pat == tuple(bits):
                return name
        raise ValueError(f"非法卦象: {bits}")
    lower = tri([1 if l in ("少阳","老阳","阳","动阳") else 0 for l in lines[:3]])
    upper = tri([1 if l in ("少阳","老阳","阳","动阳") else 0 for l in lines[3:]])
    name = HEX_NAMES.get((upper, lower))  # 表key约定为(上卦,下卦)，如(坤,乾)=地天泰
    if not name:
        raise ValueError(f"未收录卦象: {lower}+{upper}")
    changed = ["动阴" if l == "老阳" else "动阳" if l == "老阴" else l for l in lines]
    return lower, upper, name, changed


def changed_hex_name(changed):
    lower = [1 if l in ("少阳","老阳","阳","动阳") else 0 for l in changed[:3]]
    upper = [1 if l in ("少阳","老阳","阳","动阳") else 0 for l in changed[3:]]
    def tri(bits):
        for name, pat in TRIGRAMS.items():
            if pat == tuple(bits):
                return name
    return HEX_NAMES.get((tri(upper), tri(lower)), "（变卦名待查）")


def palace_info(hex_name):
    """返回 (卦宫, 世爻位1-6, 应爻位, 宫五行)"""
    for palace, members in PALACES.items():
        for idx, hn in enumerate(members):
            if hn == hex_name:
                shi = SHI_POS[idx]
                ying = ((shi - 1 + 3) % 6) + 1  # 世隔二位为应：世1应4、世4应1（游魂）、世3应6（归魂）
                return palace, shi, ying, TRI_WUXING[palace]
    raise ValueError(f"卦 {hex_name} 未在八宫表中")


def liuqin(gong_wx, zhi_wx):
    if zhi_wx == gong_wx: return "兄弟"
    if SHENG[gong_wx] == zhi_wx: return "子孙"
    if KE[gong_wx] == zhi_wx: return "妻财"
    if SHENG[zhi_wx] == gong_wx: return "父母"
    if KE[zhi_wx] == gong_wx: return "官鬼"
    return "?"


def najia_for(lower, upper):
    """内卦+外卦 → 六爻地支（自下而上）"""
    return NAJIA_IN[lower] + NAJIA_OUT[upper]


def zhuanggua(lines, date_str, time_str="12:00"):
    lower, upper, name, changed = lines_to_hexagram(lines)
    palace, shi, ying, gong_wx = palace_info(name)
    y, m, d = map(int, date_str.split("-"))
    hh, mm = map(int, time_str.split(":"))
    solar = Solar.fromYmdHms(y, m, d, hh, mm, 0)
    lunar = solar.getLunar()
    day_gz = lunar.getDayInGanZhi()
    day_gan, day_zhi = day_gz[0], day_gz[1:]
    month_zhi = lunar.getMonthInGanZhi()[1:]
    kong = XUN_TABLE[day_gz]

    zhis = najia_for(lower, upper)
    shens = [LIUSHEN_START[day_gan] if i == 0 else "" for i in range(6)]
    for i in range(1, 6):
        shens[i] = LIUSHEN_SEQ[(LIUSHEN_SEQ.index(shens[0]) + i) % 6]

    is_static = all(l in ("少阳","少阴","阳","阴") for l in lines)
    chg_name = None if is_static else changed_hex_name(changed)

    print(f"\n◆ {name} {'（静卦）' if is_static else '→ 变卦 ' + chg_name}")
    print(f"  卦宫：{palace}宫（{gong_wx}）   世爻：{shi}爻   应爻：{ying}爻")
    print(f"  起卦：{date_str} {time_str}   日建：{day_gz}   月建：{month_zhi}")
    print(f"  旬空：{'、'.join(kong)}\n")
    print(f"  {'爻':<3}{'六神':<4}{'本卦':<8}{'六亲':<4}{'地支':<4}{'世应':<4}")
    print("  " + "-" * 30)
    labels = {6: "上", 5: "五", 4: "四", 3: "三", 2: "二", 1: "初"}  # pos → 爻位名
    for pos in range(6, 0, -1):
        i = pos - 1  # lines/zhis 索引（自下而上）
        yao = "阳" if lines[i] in ("少阳","老阳","阳","动阳") else "阴"
        move = ""
        if lines[i] in ("老阳","老阴"):
            move = "○动" if lines[i] == "老阳" else "×动"
        shi_ying = "世" if pos == shi else ("应" if pos == ying else "")
        lq = liuqin(gong_wx, ZHI_WUXING[zhis[i]])
        print(f"  {labels[pos]:<3}{shens[i]:<4}{yao+move:<6}{lq:<4}{zhis[i]:<4}{shi_ying:<4}")

    if not is_static:
        print(f"\n  变卦 {chg_name}（动爻已标，变卦装卦从略）")
    print(f"\n【断卦提醒】静卦先看卦名卦辞；旬空之爻断'有但未到'，出空应事；")
    print(f"应期必须结合日月建旺衰。无日月建不断应期。\n")


def parse_lines(s):
    """'少阳少阴少阴老阳少阴少阳' 或 '阳阴阴阳阴阴' → list 自下而上"""
    tokens, i = [], 0
    words = sorted(["少阳","少阴","老阳","老阴","动阳","动阴"], key=len, reverse=True)
    while i < len(s):
        for w in words:
            if s.startswith(w, i):
                tokens.append(w); i += len(w); break
        else:
            tokens.append(s[i]); i += 1
    if len(tokens) != 6:
        raise ValueError(f"需要6爻，解析出{len(tokens)}爻: {tokens}")
    return tokens


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="六爻纳甲装卦")
    ap.add_argument("input", help="六爻结果，自下而上。如 '少阳少阴少阴老阳少阴少阳'、'阳阴阴阳阴阴' 或卦名'泽天夬'")
    ap.add_argument("--date", required=True, help="起卦日期 YYYY-MM-DD")
    ap.add_argument("--time", default="12:00", help="起卦时间 HH:MM（默认12:00）")
    a = ap.parse_args()
    if a.input in HEX_NAMES.values():
        # 直接给卦名：全部按静卦处理
        tri_bits = {name: list(bits) for name, bits in TRIGRAMS.items()}
        for (up, lo), nm in HEX_NAMES.items():  # 表key=(上卦,下卦)，lo=下卦=第二个
            if nm == a.input:
                lines = []
                for b in tri_bits[lo] + tri_bits[up]:  # 爻序自下而上：先下卦后上卦
                    lines.append("少阳" if b else "少阴")
                zhuanggua(lines, a.date, a.time)
                break
    else:
        zhuanggua(parse_lines(a.input), a.date, a.time)
