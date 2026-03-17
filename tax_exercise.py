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
    return a - b * P

def supply_curve(P, c=10, d=0.8):
    return c + d * P

def find_equilibrium(a, b, c, d):
    P = (a - c) / (b + d)
    Q = a - b * P
    return P, Q

def find_tax_equilibrium(a, b, c, d, t, tax_on='supplier'):
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
    a = st.number_input("截距 a", min_value=50, max_value=200, value=150, step=5)
    b = st.number_input("斜率 b (价格敏感度)", min_value=0.1, max_value=2.0, value=0.8, step=0.1)
    st.divider()
    st.subheader("供给曲线 (Qs = c + d·P)")
    c = st.number_input("截距 c", min_value=0, max_value=50, value=20, step=5)
    d = st.number_input("斜率 d (供给对价格的敏感度)", min_value=0.1, max_value=2.0, value=0.6, step=0.1)
    st.divider()
    st.subheader("税收设置")
    t = st.number_input("从量税 t (单位税额)", min_value=0.0, max_value=100.0, value=30.0, step=2.0)
    tax_on = st.radio("向谁征税？", options=["supplier", "consumer"],
                      format_func=lambda x: "卖方" if x == "supplier" else "买方",
                      index=0, horizontal=True)

# ---------------------- 计算均衡与弹性 ----------------------
P0, Q0 = find_equilibrium(a, b, c, d)
if Q0 <= 0:
    st.error("税前均衡数量为零或负，请调整参数使供需曲线在正价格有正交点。")
    st.stop()
Pc, Pp, Q1 = find_tax_equilibrium(a, b, c, d, t, tax_on)
if Q1 < 0:
    st.error("税后均衡数量为负，请降低税额或调整曲线参数。")
    st.stop()
Ed_abs, Es = calculate_elasticities(a, b, c, d, P0, Q0)
tax_consumer = Pc - P0
tax_producer = P0 - Pp

# ---------------------- 绘图 ----------------------
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

# 设置坐标轴范围（提前计算偏移用）
xlim_max = max(Q0, Q1) * 1.5
ylim_max = max(P0, Pc, Pp) * 1.5
ax.set_xlim(0, xlim_max)
ax.set_ylim(0, ylim_max)

# 动态偏移量（基于坐标轴范围的5%）
x_offset = xlim_max * 0.05
y_offset = ylim_max * 0.05

# 绘制税前均衡点（带箭头文本框）
ax.scatter(Q0, P0, s=100, color='green', zorder=5, label='税前均衡')
if tax_on == 'supplier':
    xytext_pre = (Q0 + x_offset, P0 - y_offset) if Pc > P0 else (Q0 + x_offset, P0 + y_offset)
else:
    xytext_pre = (Q0 + x_offset, P0 - y_offset) if Pp > P0 else (Q0 + x_offset, P0 + y_offset)
ax.annotate(f'税前\nP={P0:.1f}\nQ={Q0:.1f}', (Q0, P0), xytext=xytext_pre,
            arrowprops=dict(arrowstyle='->', color='green'), fontsize=9)

# 绘制税后均衡点
if tax_on == 'supplier':
    ax.scatter(Q1, Pc, s=100, color='purple', zorder=5, label='税后市场价')
    # 避免与税前点重叠
    if abs(Pc - P0) < y_offset and abs(Q1 - Q0) < x_offset:
        xytext_post = (Q1 - x_offset, Pc + y_offset) if Pc > P0 else (Q1 - x_offset, Pc - y_offset)
    else:
        xytext_post = (Q1 + x_offset, Pc + y_offset)
    ax.annotate(f'税后市场价\nPc={Pc:.1f}\nQ={Q1:.1f}', (Q1, Pc), xytext=xytext_post,
                arrowprops=dict(arrowstyle='->', color='purple'), fontsize=9)
    ax.axhline(Pp, color='gray', linestyle=':', alpha=0.5, label=f'生产者价格 Pp={Pp:.1f}')
else:
    ax.scatter(Q1, Pp, s=100, color='purple', zorder=5, label='税后生产者价')
    if abs(Pp - P0) < y_offset and abs(Q1 - Q0) < x_offset:
        xytext_post = (Q1 - x_offset, Pp + y_offset) if Pp > P0 else (Q1 - x_offset, Pp - y_offset)
    else:
        xytext_post = (Q1 + x_offset, Pp + y_offset)
    ax.annotate(f'税后生产者价\nPp={Pp:.1f}\nQ={Q1:.1f}', (Q1, Pp), xytext=xytext_post,
                arrowprops=dict(arrowstyle='->', color='purple'), fontsize=9)
    ax.axhline(Pc, color='orange', linestyle=':', alpha=0.5, label=f'消费者价格 Pc={Pc:.1f}')

# ---------- 新增：从均衡点向坐标轴绘制垂直和水平虚线 ----------
# 税前均衡点
ax.axvline(x=Q0, ymax=P0/ylim_max, linestyle='--', color='green', alpha=0.5, linewidth=1)
ax.axhline(y=P0, xmax=Q0/xlim_max, linestyle='--', color='green', alpha=0.5, linewidth=1)
# 税后市场均衡点（根据征税对象选择对应的价格）
if tax_on == 'supplier':
    ax.axvline(x=Q1, ymax=Pc/ylim_max, linestyle='--', color='purple', alpha=0.5, linewidth=1)
    ax.axhline(y=Pc, xmax=Q1/xlim_max, linestyle='--', color='purple', alpha=0.5, linewidth=1)
else:
    ax.axvline(x=Q1, ymax=Pp/ylim_max, linestyle='--', color='purple', alpha=0.5, linewidth=1)
    ax.axhline(y=Pp, xmax=Q1/xlim_max, linestyle='--', color='purple', alpha=0.5, linewidth=1)

# 税收收入矩形
if t > 0:
    rect = plt.Rectangle((0, Pp), Q1, t, facecolor='gold', alpha=0.2, label='税收收入')
    ax.add_patch(rect)

# 在轴外侧标注价格和数量的具体数值
ax.text(Q0, -0.05, f'{Q0:.1f}', transform=ax.get_xaxis_transform(),
        ha='center', va='top', color='green', fontsize=9)
ax.text(-0.05, P0, f'{P0:.1f}', transform=ax.get_yaxis_transform(),
        ha='right', va='center', color='green', fontsize=9)
ax.text(Q1, -0.05, f'{Q1:.1f}', transform=ax.get_xaxis_transform(),
        ha='center', va='top', color='purple', fontsize=9)
if tax_on == 'supplier':
    ax.text(-0.05, Pc, f'{Pc:.1f}', transform=ax.get_yaxis_transform(),
            ha='right', va='center', color='purple', fontsize=9)
    ax.text(-0.05, Pp, f'{Pp:.1f}', transform=ax.get_yaxis_transform(),
            ha='right', va='center', color='gray', fontsize=9)
else:
    ax.text(-0.05, Pp, f'{Pp:.1f}', transform=ax.get_yaxis_transform(),
            ha='right', va='center', color='purple', fontsize=9)
    ax.text(-0.05, Pc, f'{Pc:.1f}', transform=ax.get_yaxis_transform(),
            ha='right', va='center', color='orange', fontsize=9)

# 设置标签和标题
ax.set_xlabel('Quantity (Q) 数量')
ax.set_ylabel('Price (P) 价格')
ax.set_title('从量税：消费者与生产者承担的价格变化')
ax.legend(loc='upper right', fontsize=9)
ax.grid(True, alpha=0.3)

# 调整边距，确保外侧标签不被裁剪
plt.subplots_adjust(left=0.15, bottom=0.15)

st.pyplot(fig)

# ---------------------- 结果展示（含总税负，学生填写验证）---------------------
# ---------------------- 结果展示（学生练习：填写所有关键变量）---------------------
st.divider()
st.subheader("📝 学生练习：计算税收相关数值")
st.markdown("请根据图表中的信息，填写以下所有数值（保留两位小数），然后点击验证按钮。")

# 真实计算值（保留两位小数供比较）
true_Q1 = round(Q1, 2)
true_tax_consumer = round(tax_consumer, 2)
true_tax_producer = round(tax_producer, 2)
true_total_revenue = round(t * Q1, 2)
true_consumer_total = round(tax_consumer * Q1, 2)
true_producer_total = round(tax_producer * Q1, 2)

# 已知条件展示（帮助学生理解）
col_info1, col_info2, col_info3 = st.columns(3)
with col_info1:
    st.info(f"税前价格 P0: {P0:.2f}")
    st.info(f"税前数量 Q0: {Q0:.2f}")
with col_info2:
    st.info(f"税率 t: {t:.2f}")
    st.info(f"需求弹性 |Ed|: {Ed_abs:.3f}")
with col_info3:
    st.info(f"供给弹性 Es: {Es:.3f}")
    st.info(f"征税对象: {'卖方' if tax_on == 'supplier' else '买方'}")

st.markdown("---")

# 学生输入区域（分两行布局）
col_input1, col_input2, col_input3 = st.columns(3)
with col_input1:
    student_Q1 = st.number_input(
        "税后数量 Q₁", value=None, placeholder="请输入",
        step=0.01, format="%.2f", key="Q1_input"
    )
with col_input2:
    student_tax_consumer = st.number_input(
        "消费者多付 (ΔPc)", value=None, placeholder="请输入",
        step=0.01, format="%.2f", key="tax_consumer_input"
    )
with col_input3:
    student_tax_producer = st.number_input(
        "生产者少得 (ΔPp)", value=None, placeholder="请输入",
        step=0.01, format="%.2f", key="tax_producer_input"
    )

col_input4, col_input5, col_input6 = st.columns(3)
with col_input4:
    student_total_revenue = st.number_input(
        "税收总收入", value=None, placeholder="请输入",
        step=0.01, format="%.2f", key="revenue_input"
    )
with col_input5:
    student_consumer_total = st.number_input(
        "消费者总税负", value=None, placeholder="请输入",
        step=0.01, format="%.2f", key="consumer_total_input"
    )
with col_input6:
    student_producer_total = st.number_input(
        "生产者总税负", value=None, placeholder="请输入",
        step=0.01, format="%.2f", key="producer_total_input"
    )

# 验证按钮
if st.button("✅ 验证答案", type="primary"):
    # 检查是否全部填写
    inputs = [student_Q1, student_tax_consumer, student_tax_producer,
              student_total_revenue, student_consumer_total, student_producer_total]
    if any(v is None for v in inputs):
        st.warning("请先填写所有六个数值。")
    else:
        # 判断每个输入的正确性（允许浮点误差 0.01）
        correct_Q1 = abs(student_Q1 - true_Q1) < 0.01
        correct_tax_consumer = abs(student_tax_consumer - true_tax_consumer) < 0.01
        correct_tax_producer = abs(student_tax_producer - true_tax_producer) < 0.01
        correct_total_revenue = abs(student_total_revenue - true_total_revenue) < 0.01
        correct_consumer_total = abs(student_consumer_total - true_consumer_total) < 0.01
        correct_producer_total = abs(student_producer_total - true_producer_total) < 0.01

        if (correct_Q1 and correct_tax_consumer and correct_tax_producer and
            correct_total_revenue and correct_consumer_total and correct_producer_total):
            st.success("🎉 完全正确！你的计算结果与系统一致。")
        else:
            st.error("❌ 部分答案不正确，请检查计算。")
            # 列出错误项并给出正确答案
            if not correct_Q1:
                st.markdown(f"- 税后数量 Q₁ 错误（正确答案：{true_Q1:.2f}）")
            if not correct_tax_consumer:
                st.markdown(f"- 消费者多付 ΔPc 错误（正确答案：{true_tax_consumer:.2f}）")
            if not correct_tax_producer:
                st.markdown(f"- 生产者少得 ΔPp 错误（正确答案：{true_tax_producer:.2f}）")
            if not correct_total_revenue:
                st.markdown(f"- 税收总收入错误（正确答案：{true_total_revenue:.2f}）")
            if not correct_consumer_total:
                st.markdown(f"- 消费者总税负错误（正确答案：{true_consumer_total:.2f}）")
            if not correct_producer_total:
                st.markdown(f"- 生产者总税负错误（正确答案：{true_producer_total:.2f}）")

# 注意：不再直接显示任何正确答案，只有验证后才会在错误提示中显示。
# 这样满足“只有学生填了之后才能显示正确答案”的要求。
    - 税收总收入：**{true_total_revenue:.2f}**
    - 消费者总税负：**{true_consumer_total:.2f}**
    - 生产者总税负：**{true_producer_total:.2f}**
    """)
