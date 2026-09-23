<div align="center">

<img src="https://img.shields.io/badge/Python-纯本地_·_零依赖-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />

# metaphysics-toolkit

**排盘不问命 —— 八字排盘 + 六爻纳甲装卦。**

工具只负责把盘排对。断命这事，别赖工具。

![Python](https://img.shields.io/badge/Python_3-3776AB?style=flat-square&logo=python&logoColor=white)
![offline](https://img.shields.io/badge/网络依赖-零-4CAF50?style=flat-square&logo=cloudflare&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square&logo=opensourceinitiative&logoColor=white)

</div>

面向命理学习者与开发者的开源工具集：**八字排盘** 与 **六爻纳甲装卦** 两个独立小工具，纯本地运行，无任何网络依赖。

> 方法论：先排盘核对，再下判断。工具只负责"排"，不负责"断"——断卦断命需要结合日月建、旺衰与具体问题综合分析，本仓库提供的是可靠的底层数据与结构化框架。

## 📦 工具

### 1. bazi/bazi_paipan.py — 八字排盘

公历生日 → 四柱、十神、藏干、五行统计、大运、流年。

```bash
pip install lunar_python

python3 bazi/bazi_paipan.py 1998-07-04 12:00 --gender 男
python3 bazi/bazi_paipan.py 1988-05-20 08:00 --gender 男 --liunian 2026
```

输出示例：

```
    十神    干支    藏干
----------------------------------
年柱  正财    癸酉    辛
月柱  七杀    庚申    庚、壬、戊
日柱  日主    丙戌    戊、辛、丁
时柱  正财    癸巳    丙、庚、戊

五行（干+支本气）：木0  火2  土1  金3  水2

大运（逆排，10 岁起运）：
  10-19岁  己未
  20-29岁  戊午
  ...
```

实现要点：
- 十神判定**手动实现**（`lunar_python` 此版本无 `getTenStar()`），阴阳异同决定正/偏：克我者异性=正官、同性=七杀，以此类推
- 大运方向遵循 阳年男/阴年女顺排、阴年男/阳年女逆排，起运数=出生日到节的÷3（库自动算）
- 经三个已知命例回归校验（含顺排/逆排两种方向）

### 2. liuyao/liuyao_najia.py — 六爻纳甲装卦

手摇六次结果（或卦名）→ 本卦/变卦、卦宫、世应、纳甲地支、六亲、六神、旬空。

```bash
# 六次摇卦结果自下而上（第一次=初爻）
python3 liuyao/liuyao_najia.py 少阳少阴少阴老阳少阴少阳 --date 2026-09-10

# 只记得卦名也行（按静卦处理）
python3 liuyao/liuyao_najia.py 泽天夬 --date 2026-09-10

# 简写：阳/阴/动
python3 liuyao/liuyao_najia.py 阳阳阳阳阳老阴 --date 2026-09-10
```

输出示例（泽天夬，丁亥日起卦）：

```
◆ 泽天夬 （静卦）
  卦宫：坤宫（土）   世爻：5爻   应爻：2爻
  起卦：2026-09-10 12:00   日建：丁亥   月建：酉
  旬空：午、未

  爻  六神  本卦   六亲  地支  世应
  ------------------------------
  上  青龙  阴     兄弟  未
  五  玄武  阳     子孙  酉   世
  四  白虎  阳     妻财  亥
  三  螣蛇  阳     兄弟  辰
  二  勾陈  阳     官鬼  寅   应
  初  朱雀  阳     妻财  子
```

实现要点：
- 内置完整 **京房八宫** 归宫表与世爻位置表（本宫/一世~五世/游魂/归魂）
- 纳甲地支表（乾震纳子寅辰、巽纳丑亥酉……）、六神起例（日干定初爻六神顺排）、旬空表（六十甲子逐旬生成）
- 应爻 = 世爻隔二位：世1应4、世4应1（游魂）、世3应6（归魂）
- **经典校验**：泽天夬（坤宫五世）与水火既济（坎宫三世）两卦的纳甲、六亲、六神、世应、旬空逐项人工核对通过

## 📖 方法论（docs/）

- [八字格局核对清单](docs/bazi-methodology.md) — 排盘之后、下判断之前过一遍
- [六爻断卦框架](docs/liuyao-methodology.md) — 装卦之后的分析路径与常见坑

## ⚠️ 边界声明

- 本工具输出的是**排盘数据**，不构成任何命理结论或人生建议
- 体系基于传统子平术与京房六爻，属于民俗文化范畴，请理性看待
- 没有日月建，不断应期——工具会打印起卦日期干支，但"断"永远在人

## License

MIT

---

<div align="center">
<sub>由 <b>李卓扬 · Aktive</b> 构建 · <a href="https://github.com/zhuangli410-commits">更多项目</a> · <a href="https://li-zhuoyang-ai-product-builder.zhuangli410.chatgpt.site">完整作品集</a></sub>
</div>
