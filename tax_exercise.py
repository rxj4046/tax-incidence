# 导入依赖
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.font_manager as fm
import urllib.request
import os
import tempfile

# ---------------------- 配置Matplotlib中文字体（增强版）---------------------
def setup_chinese_font():
    """尝试设置中文字体，若系统无则下载SimHei.ttf"""
    chinese_fonts = ['SimHei', 'Microsoft YaHei', 'WenQuanYi Zen Hei',
                     'Noto Sans CJK SC', 'Droid Sans Fallback', 'PingFang SC',
                     'Hiragino Sans GB']

    for font_name in chinese_fonts:
        try:
            font_path = fm.findfont(font_name, fallback_to_default=False)
            default_font = fm.findfont('DejaVu Sans', fallback_to_default=True)
            if font_path != default_font:
                plt.rcParams['font.sans-serif'] = [font_name]
                plt.rcParams['axes.unicode_minus'] = False
                return True
        except:
            continue

    # 尝试下载SimHei.ttf
    font_url = "https://raw.githubusercontent.com/StellarCN/scp_zh/master/fonts/SimHei.ttf"
    temp_dir = tempfile.gettempdir()
    font_path = os.path.join(temp_dir, "SimHei.ttf")

    if not os.path.exists(font_path):
        try:
            urllib.request.urlretrieve(font_url, font_path)
        except:
            plt.rcParams['axes.unicode_minus'] = False
            return False

    try:
        fm.fontManager.addfont(font_path)
        plt.rcParams['font.sans-serif'] = [fm.FontProperties(fname=font_path).get_name()]
        plt.rcParams['axes.unicode_minus'] = False
        return True
    except:
        plt.rcParams['axes.unicode_minus'] = False
        return False

font_ok = setup_chinese_font()
if not font_ok:
    st.warning("⚠️ 未找到中文字体，图表中的中文可能无法正常显示，但英文标签仍可使用。")

# ---------------------- 核心函数定义 ----------------------
def demand_curve(P, a=100, b=0.5):
    """需求曲线：Qd = a - b*P"""
    return a - b * P

def supply_curve(P, c=10, d=0.8):
    """供给曲线：Qs = c + d*P"""
    return c + d * P

def find_equilibrium(a, b, c, d):
    """税前均衡价格和数量"""
    P = (a - c) / (b + d)
    Q = a - b * P
    return P, Q

def find_tax_equilibrium(a, b, c, d, t, tax_on='supplier'):
    """
    税后均衡（从量税）
    tax_on: 'supplier' 对卖方征税，'consumer' 对买方征税
    返回：消费者支付价格 Pc，生产者得到价格 Pp，数量 Q
    """
    if tax_on == 'supplier':
        Pc = (a - c + d * t) / (b + d)
        Pp = Pc - t
        Q = a - b * Pc
    else:
        Pp = (a - c - b * t) / (b + d)
        Pc = Pp + t
        Q = a - b * Pc
    return Pc, Pp, Q

def calculate_elasticities(a, b, c, d, P0, Q0):
    """
    计算税前均衡点的点弹性
    需求价格弹性 Ed = (dQ/dP) * (P/Q) = -b * (P/Q) → 取绝对值
    供给价格弹性 Es = d * (P/Q)
    """
    if Q0 <= 0:
        return 0, 0
    Ed_abs = b * (P0 / Q0)
    Es = d * (P0 / Q0)
    return Ed_abs, Es

# ---------------------- Streamlit 界面 ----------------------
st.set_page_config(page_title="税收效应分析（弹性与税负）", layout="wide")
st.title("💰 税收效应分析：弹性如何决定税负分配")
st.markdown("### 调整参数，观察需求弹性和供给弹性如何影响消费者与生产者承担的价格变化")

with st.sidebar:
    st.header("⚙️ 市场参数")

    st.subheader("需求曲线 (Qd = a - b·P)")
    a = st.number_input("截距 a", min_value=50, max_value=200, value=150, step=5,
                        help="需求曲线在价格为零时的需求量")
    b = st.number_input("斜率 b (价格敏感度)", min_value=0.1, max_value=2.0, value=0.8, step=0.1,
                        help="价格每上升1单位，需求量减少b单位 → 需求弹性与b成正比")

    st.divider()
    st.subheader("供给曲线 (Qs = c + d·P)")
    c = st.number_input("截距 c", min_value=0, max_value=50, value=20, step=5,
                        help="价格为零时的供给量")
    d = st.number_input("斜率 d (供给对价格的敏感度)", min_value=0.1, max_value=2.0, value=0.6, step=0.1,
                        help="价格每上升1单位，供给量增加d单位 → 供给弹性与d成正比")

    st.divider()
    st.subheader("税收设置")
    t = st.number_input("从量税 t (单位税额)", min_value=0.0, max_value=100.0, value=30.0, step=2.0,
                        help="每单位商品征收的税额")
    tax_on = st.radio("向谁征税？", options=["supplier", "consumer"],
                      format_func=lambda x: "卖方" if x == "supplier" else "买方",
                      index=0, horizontal=True)

# ---------------------- 计算均衡与弹性 ----------------------
P0, Q0 = find_equilibrium(a, b, c, d)                # 税前均衡
if Q0 <= 0:
    st.error("税前均衡数量为零或负，请调整参数使供需曲线在正价格有正交点。")
    st.stop()

Pc, Pp, Q1 = find_tax_equilibrium(a, b, c, d, t, tax_on)   # 税后均衡
if Q1 < 0:
    st.error("税后均衡数量为负，请降低税额或调整曲线参数。")
    st.stop()

# 计算弹性
Ed_abs, Es = calculate_elasticities(a, b, c, d, P0, Q0)

# 实际承担的税额变化
tax_consumer = Pc - P0   # 消费者多付的部分
tax_producer = P0 - Pp   # 生产者少得的部分


# ---------------------- 核心绘图逻辑 ----------------------
fig, ax = plt.subplots(figsize=(10, 6))
price_range = np.linspace(0, 200, 500)

# 税前曲线
Qd_pre = demand_curve(price_range, a, b)
Qs_pre = supply_curve(price_range, c, d)
Qd_pre = np.where(Qd_pre >= 0, Qd_pre, np.nan)
Qs_pre = np.where(Qs_pre >= 0, Qs_pre, np.nan)

ax.plot(Qd_pre, price_range, 'r-', label='需求曲线 (税前)', linewidth=2)
ax.plot(Qs_pre, price_range, 'b-', label='供给曲线 (税前)', linewidth=2)

# 税后曲线
if tax_on == 'supplier':
    Qs_tax = supply_curve(price_range - t, c, d)
    Qs_tax = np.where((price_range >= t) & (Qs_tax >= 0), Qs_tax, np.nan)
    ax.plot(Qs_tax, price_range, 'b--', label='供给曲线 (税后)', linewidth=2, alpha=0.7)
else:
    Qd_tax = demand_curve(price_range + t, a, b)
    Qd_tax = np.where(Qd_tax >= 0, Qd_tax, np.nan)
    ax.plot(Qd_tax, price_range, 'r--', label='需求曲线 (税后)', linewidth=2, alpha=0.7)

# 设置坐标轴范围（提前到标注之前，以便计算动态偏移）
xlim_max = max(Q0, Q1) * 1.5
ylim_max = max(P0, Pc, Pp) * 1.5
ax.set_xlim(0, xlim_max)
ax.set_ylim(0, ylim_max)

# 计算动态偏移量（基于坐标轴范围的5%）
x_offset = xlim_max * 0.05
y_offset = ylim_max * 0.05

# 标注税前均衡点
ax.scatter(Q0, P0, s=100, color='green', zorder=5, label='税前均衡')
# 根据税后价格与税前价格的关系决定标注的垂直方向
if tax_on == 'supplier':
    if Pc > P0:
        xytext_pre = (Q0 + x_offset, P0 - y_offset)
    else:
        xytext_pre = (Q0 + x_offset, P0 + y_offset)
else:
    if Pp > P0:
        xytext_pre = (Q0 + x_offset, P0 - y_offset)
    else:
        xytext_pre = (Q0 + x_offset, P0 + y_offset)

ax.annotate(f'税前\nP={P0:.1f}\nQ={Q0:.1f}',
            (Q0, P0), xytext=xytext_pre,
            arrowprops=dict(arrowstyle='->', color='green'), fontsize=9)

# 标注税后均衡点
if tax_on == 'supplier':
    ax.scatter(Q1, Pc, s=100, color='purple', zorder=5, label='税后市场价')
    # 如果与税前点太近，将税后标注放在相反方向
    if abs(Pc - P0) < y_offset and abs(Q1 - Q0) < x_offset:
        if Pc > P0:
            xytext_post = (Q1 - x_offset, Pc + y_offset)
        else:
            xytext_post = (Q1 - x_offset, Pc - y_offset)
    else:
        xytext_post = (Q1 + x_offset, Pc + y_offset)
    ax.annotate(f'税后市场价\nPc={Pc:.1f}\nQ={Q1:.1f}',
                (Q1, Pc), xytext=xytext_post,
                arrowprops=dict(arrowstyle='->', color='purple'), fontsize=9)
    ax.axhline(Pp, color='gray', linestyle=':', alpha=0.5, label=f'生产者价格 Pp={Pp:.1f}')
else:
    ax.scatter(Q1, Pp, s=100, color='purple', zorder=5, label='税后生产者价')
    if abs(Pp - P0) < y_offset and abs(Q1 - Q0) < x_offset:
        if Pp > P0:
            xytext_post = (Q1 - x_offset, Pp + y_offset)
        else:
            xytext_post = (Q1 - x_offset, Pp - y_offset)
    else:
        xytext_post = (Q1 + x_offset, Pp + y_offset)
    ax.annotate(f'税后生产者价\nPp={Pp:.1f}\nQ={Q1:.1f}',
                (Q1, Pp), xytext=xytext_post,
                arrowprops=dict(arrowstyle='->', color='purple'), fontsize=9)
    ax.axhline(Pc, color='orange', linestyle=':', alpha=0.5, label=f'消费者价格 Pc={Pc:.1f}')

# 税收收入矩形
if t > 0:
    rect = plt.Rectangle((0, Pp), Q1, t, facecolor='gold', alpha=0.2, label='税收收入')
    ax.add_patch(rect)

ax.set_xlabel('Quantity (Q) 数量')
ax.set_ylabel('Price (P) 价格')
ax.set_title('从量税：消费者与生产者承担的价格变化')
ax.legend(loc='upper right', fontsize=9)
ax.grid(True, alpha=0.3)

plt.tight_layout()
st.pyplot(fig)

# ---------------------- 结果展示（增加总税负）---------------------
st.divider()
st.subheader("📊 弹性与税负变化（含总税负）")

# 计算总税负
total_tax_revenue = t * Q1          # 税收总收入
consumer_total_tax = tax_consumer * Q1   # 消费者总税负
producer_total_tax = tax_producer * Q1   # 生产者总税负

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("税前均衡价格", f"{P0:.2f}")
    st.metric("税前均衡数量", f"{Q0:.2f}")
with col2:
    st.metric("需求价格弹性 (绝对值)", f"{Ed_abs:.3f}")
    st.metric("供给价格弹性", f"{Es:.3f}")
with col3:
    st.metric("消费者多付 (单位)", f"{tax_consumer:.2f}")
    st.metric("生产者少得 (单位)", f"{tax_producer:.2f}")

# 第二行：总税负相关指标
col4, col5, col6 = st.columns(3)
with col4:
    st.metric("税收总收入", f"{total_tax_revenue:.2f}")
with col5:
    st.metric("消费者总税负", f"{consumer_total_tax:.2f}")
with col6:
    st.metric("生产者总税负", f"{producer_total_tax:.2f}")

st.markdown(f"""
#### 弹性如何影响税负？
- 消费者价格从 **{P0:.2f}** 变为 **{Pc:.2f}**，上升了 **{tax_consumer:.2f}**（每单位）
- 生产者价格从 **{P0:.2f}** 变为 **{Pp:.2f}**，下降了 **{abs(tax_producer):.2f}**（每单位）
- 数量从 **{Q0:.2f}** 减少到 **{Q1:.2f}**，减少了 **{Q0-Q1:.2f}**

**总税负含义**：
- 税收总收入 = 税率 × 税后数量 = {t:.2f} × {Q1:.2f} = **{total_tax_revenue:.2f}**
- 消费者总税负 = 消费者单位多付 × 税后数量 = {tax_consumer:.2f} × {Q1:.2f} = **{consumer_total_tax:.2f}**
- 生产者总税负 = 生产者单位少得 × 税后数量 = {tax_producer:.2f} × {Q1:.2f} = **{producer_total_tax:.2f}**

**规律**：弹性越大的一方，单位税负越小，但总税负还取决于税后数量。您可以通过调整斜率参数（b 和 d）观察弹性变化如何同时影响单位税负和总税负。
""")
