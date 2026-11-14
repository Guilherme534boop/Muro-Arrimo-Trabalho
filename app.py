import math
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="Cálculo de Muro de Arrimo", layout="wide")

st.title("Dimensionamento de Muro de Arrimo de Flexão")
st.markdown(
    "**Universidade Estadual de Maringá (UEM)** | Estruturas de Concreto III"
)

# --- BARRA LATERAL: DADOS DE ENTRADA ---
st.sidebar.header("1. Geometria do Muro")
h_parede = st.sidebar.number_input(
    "Altura livre da parede (m)", value=4.00, step=0.10
)
e_topo = st.sidebar.number_input(
    "Espessura no topo (m)", value=0.10, step=0.05
)
e_base = st.sidebar.number_input(
    "Espessura na base (m)", value=0.30, step=0.05
)
b_ponta = st.sidebar.number_input(
    "Largura da ponta (m)", value=0.80, step=0.10
)
b_talao = st.sidebar.number_input(
    "Largura do talão (m)", value=0.80, step=0.10
)
h_b = st.sidebar.number_input("Espessura da sapata (m)", value=0.30, step=0.05)
h_d = st.sidebar.number_input(
    "Altura do dente (m) [0 = sem dente]", value=0.50, step=0.05
)

st.sidebar.header("2. Solo e Carregamento")
gamma_s = st.sidebar.number_input(
    "Peso específico do solo (kN/m³)", value=18.0, step=0.5
)
phi = st.sidebar.number_input(
    "Ângulo de atrito interno (°)", value=30.0, step=1.0
)
sigma_adm = st.sidebar.number_input(
    "Tensão admissível do solo (kN/m²)", value=150.0, step=10.0
)
mi = st.sidebar.number_input(
    "Coeficiente de atrito base-solo (µ)", value=0.55, step=0.05
)
q = st.sidebar.number_input(
    "Sobrecarga distribuída q (kN/m²)", value=0.0, step=5.0
)

st.sidebar.header("3. Materiais e Bitolas")
fck = st.sidebar.number_input("fck do concreto (MPa)", value=20.0, step=5.0)
fyk = st.sidebar.number_input("fyk do aço (MPa)", value=500.0, step=50.0)
c_nom = st.sidebar.number_input("Cobrimento nominal (cm)", value=3.0, step=0.5)
gamma_c = 25.0

bitola_n1 = st.sidebar.selectbox(
    "Bitola N1 - Parede (mm)", [8.0, 10.0, 12.5, 16.0], index=1
)
bitola_n2 = st.sidebar.selectbox(
    "Bitola N2 - Sapata (mm)", [6.3, 8.0, 10.0, 12.5], index=1
)
bitola_n3 = st.sidebar.selectbox(
    "Bitola N3 - Construtiva (mm)", [5.0, 6.3, 8.0], index=1
)

# --- CÁLCULOS (PROCEDIMENTO AULA 04) ---
B = b_ponta + e_base + b_talao
h_total = h_parede + h_b

# 1. Empuxos
Ka = (math.tan(math.radians(45 - phi / 2))) ** 2
Kp = 1 / Ka
Ea_solo = 0.5 * Ka * gamma_s * (h_total**2)
Ea_sobr = Ka * q * h_total
Ea_total = Ea_solo + Ea_sobr
Ep = 0.5 * Kp * gamma_s * ((h_b + h_d) ** 2) if h_d > 0 else 0.0

# 2. Pesos e Braços de Alavanca (Ponto A)
P1 = e_topo * h_parede * gamma_c
x1 = b_ponta + e_topo / 2
P2 = ((e_base - e_topo) * h_parede / 2) * gamma_c
x2 = b_ponta + e_topo + (e_base - e_topo) / 3
P3 = h_b * B * gamma_c
x3 = B / 2
P4 = ((e_base - e_topo) * h_parede / 2) * gamma_s
x4 = b_ponta + e_topo + 2 * (e_base - e_topo) / 3
P5 = b_talao * h_parede * gamma_s
x5 = b_ponta + e_base + b_talao / 2
P_sobr = q * (b_talao + (e_base - e_topo))
x_sobr = b_ponta + e_topo + (b_talao + (e_base - e_topo)) / 2

N = P1 + P2 + P3 + P4 + P5 + P_sobr
M_rest = (P1 * x1) + (P2 * x2) + (P3 * x3) + (P4 * x4) + (P5 * x5) + (P_sobr * x_sobr)

# 3. Estabilidade
M_tomb = (Ea_solo * (h_total / 3)) + (Ea_sobr * (h_total / 2))
FS_tomb = M_rest / M_tomb
Fa = mi * N
FS_desl = (Fa + Ep) / Ea_total

# 4. Tensões no Solo
Mc = M_tomb - M_rest + N * (B / 2)
sigma_max = (N / B) + (6 * Mc / (B**2))
sigma_min = (N / B) - (6 * Mc / (B**2))

if sigma_min < 0:
    d_comp = 3 * ((B / 2) - (Mc / N))
    sigma_final = (2 * N) / d_comp
else:
    d_comp = B
    sigma_final = sigma_max

# 5. Momentos Fletores e Armaduras
MA = (1 / 6) * Ka * gamma_s * (h_parede**3) + 0.5 * Ka * q * (h_parede**2)
MB = (P5 + (h_b * b_talao * gamma_c) + (q * b_talao)) * (b_talao / 2)

if sigma_min < 0:
    sigma_2 = sigma_final * (d_comp - b_ponta) / d_comp
else:
    sigma_2 = sigma_min + (sigma_max - sigma_min) * (B - b_ponta) / B

MC = ((sigma_final + sigma_2) / 2) * b_ponta * ((b_ponta / 3) * ((2 * sigma_final + sigma_2) / (sigma_final + sigma_2)))
M_sapata = max(MB, MC)


def dimensionar_aco(Mk, h_secao, bitola):
    d = (h_secao * 100 - c_nom - (bitola / 20)) / 100
    fcd = (fck * 1000) / 1.4
    fyd = fyk / 1.15
    KMD = (1.4 * Mk) / (1.0 * (d**2) * fcd)
    KX = (1 - math.sqrt(1 - 2 * KMD)) / 0.8
    KZ = 1 - 0.4 * KX
    As = (1.4 * Mk * 10) / (KZ * d * fyd)
    area_1_barra_cm2 = math.pi * ((bitola / 20) ** 2)
    espacamento = math.floor((area_1_barra_cm2 / As) * 100)
    return As, espacamento


As_N1, esp_N1 = dimensionar_aco(MA, e_base, bitola_n1)
As_N2, esp_N2 = dimensionar_aco(M_sapata, h_b, bitola_n2)
As_N3 = 0.20 * max(As_N1, As_N2)
area_1_n3_cm2 = math.pi * ((bitola_n3 / 20) ** 2)
esp_N3 = math.floor((area_1_n3_cm2 / As_N3) * 100)


# --- QUADRO RESUMO ---
st.header("Quadro-Resumo das Verificações")
col1, col2, col3 = st.columns(3)
status_tomb = "ATENDE" if FS_tomb >= 1.5 else "NÃO ATENDE"
status_desl = "ATENDE" if FS_desl >= 1.5 else "NÃO ATENDE"
status_solo = "ATENDE" if sigma_final <= sigma_adm else "NÃO ATENDE"

col1.metric("Tombamento (FS >= 1,50)", f"{FS_tomb:.2f}", status_tomb)
col2.metric("Deslizamento (FS >= 1,50)", f"{FS_desl:.2f}", status_desl)
col3.metric(
    "Tensão no Solo (<= σ_adm)", f"{sigma_final:.1f} kN/m²", status_solo
)

st.divider()

# --- DESENHO ESQUEMÁTICO E DETALHAMENTO ---
col_esq, col_dir = st.columns([1, 1.2])

with col_esq:
    st.subheader("Esquema da Seção e Armaduras")
    fig, ax = plt.subplots(figsize=(4.2, 5.2))

    pts = [
        (0, 0),
        (b_ponta, 0),
        (b_ponta, -h_d),
        (b_ponta + e_topo, -h_d),
        (b_ponta + e_base, 0),
        (B, 0),
        (B, h_b),
        (b_ponta + e_base, h_b),
        (b_ponta + e_topo, h_b + h_parede),
        (b_ponta, h_b + h_parede),
        (b_ponta, h_b),
        (0, h_b),
    ]
    muro_poly = patches.Polygon(
        pts, closed=True, facecolor="#E0E0E0", edgecolor="black", linewidth=1.5
    )
    ax.add_patch(muro_poly)

    solo_pts = [
        (b_ponta + e_base, h_b),
        (B + 0.4, h_b),
        (B + 0.4, h_b + h_parede),
        (b_ponta + e_topo, h_b + h_parede),
    ]
    solo_poly = patches.Polygon(
        solo_pts, closed=True, facecolor="#F5DEB3", alpha=0.45, edgecolor="none"
    )
    ax.add_patch(solo_poly)
    ax.plot(
        [b_ponta + e_topo, B + 0.4],
        [h_b + h_parede, h_b + h_parede],
        color="#8B4513",
        linewidth=1.5,
    )

    cob = c_nom / 100.0
    ax.plot(
        [
            b_ponta + e_topo - cob,
            b_ponta + e_base - cob,
            b_ponta + e_base - cob,
        ],
        [h_b + h_parede - cob, h_b, cob],
        color="red",
        linewidth=2.0,
        label=f"N1: Ø{bitola_n1} c/{esp_N1}cm",
    )
    ax.plot(
        [cob, B - cob],
        [cob, cob],
        color="blue",
        linewidth=2.0,
        label=f"N2: Ø{bitola_n2} c/{esp_N2}cm",
    )
    ax.plot(
        [b_ponta + e_base - 0.15, B - cob],
        [h_b - cob, h_b - cob],
        color="blue",
        linewidth=2.0,
    )
    ax.plot(
        [b_ponta + cob, b_ponta + cob],
        [cob, h_b + h_parede - cob],
        color="green",
        linestyle="--",
        linewidth=1.6,
        label=f"N3: Ø{bitola_n3} c/{esp_N3}cm",
    )

    ax.annotate(
        f"B = {B:.2f} m",
        xy=(B / 2, -h_d - 0.35),
        ha="center",
        fontsize=8,
        fontweight="bold",
    )
    ax.annotate(
        f"H = {h_parede:.2f} m",
        xy=(b_ponta - 0.45, h_b + h_parede / 2),
        va="center",
        rotation=90,
        fontsize=8,
        fontweight="bold",
    )
    if h_d > 0:
        ax.annotate(
            f"hd={h_d:.2f}m",
            xy=(b_ponta + e_base + 0.05, -h_d / 2),
            fontsize=7.5,
        )

    ax.set_xlim(-0.7, B + 0.5)
    ax.set_ylim(-h_d - 0.6, h_b + h_parede + 0.4)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.legend(loc="upper left", fontsize=7.5, frameon=True)
    st.pyplot(fig, use_container_width=False)

with col_dir:
    st.subheader("Memorial de Cálculo")
    st.write(f"**1. Empuxos e Esforços:**")
    st.write(f"- Ka = {Ka:.3f} | Kp = {Kp:.2f}")
    st.write(
        f"- Empuxo ativo total (Ea) = {Ea_total:.2f} kN/m | Passivo (Ep) = {Ep:.2f} kN/m"
    )
    st.write(f"- Resultante vertical (N) = {N:.2f} kN/m")
    st.write(
        f"- M_resistente = {M_rest:.2f} kN·m/m | M_tombamento = {M_tomb:.2f} kN·m/m"
    )

    st.write(f"**2. Tensões no Solo:**")
    st.write(
        f"- Inicial: σ_máx = {sigma_max:.1f} kN/m² | σ_mín = {sigma_min:.1f} kN/m²"
    )
    if sigma_min < 0:
        st.warning(
            f"Tração detectada (σ_mín < 0). Zona comprimida d = {d_comp:.2f} m -> σ'A = {sigma_final:.1f} kN/m²."
        )

    st.write(f"**3. Momentos Fletores:**")
    st.write(
        f"- Parede (MA) = {MA:.2f} kN·m/m | Talão (MB) = {MB:.2f} kN·m/m | Ponta (MC) = {MC:.2f} kN·m/m"
    )

    st.write(f"**4. Quadro de Armaduras:**")
    st.table({
        "Barra": ["N1 (Parede)", "N2 (Sapata)", "N3 (Constr.)"],
        "As (cm²/m)": [f"{As_N1:.2f}", f"{As_N2:.2f}", f"{As_N3:.2f}"],
        "Detalhe": [
            f"Ø{bitola_n1} c/{esp_N1}cm",
            f"Ø{bitola_n2} c/{esp_N2}cm",
            f"Ø{bitola_n3} c/{esp_N3}cm",
        ],
    })
