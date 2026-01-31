import streamlit as st
st.set_page_config(page_title="Film Budget Feasibility", layout="centered")

st.title("🎬 Film Budget Feasibility")
st.caption("Quick decision tool for producers (SAFE / BORDERLINE / UNSAFE)")

# =====================
# INPUTS
# =====================
shooting_days = st.number_input("Shooting Days", 1, 200, 22)
locations = st.number_input("Locations", 1, 50, 5)
stars = st.number_input("Stars", 1, 10, 3)

travel = st.selectbox("Travel", ["No", "Yes"], index=1)
vfx = st.selectbox("VFX", ["No", "Yes"], index=1)
vfx_complexity = st.slider("VFX Complexity", 0, 3, 1)
director_exp = st.number_input("Director Experience (years)", 0, 40, 3)

daily_cost = st.number_input("Daily Cost (input)", 0.0, 1_000_000.0, 10000.0, step=1000.0)
planned_budget = st.number_input("Planned Budget", 0.0, 100_000_000.0, 1_000_000.0, step=50_000.0)

# =====================
# FAST FEASIBILITY LOGIC
# =====================
travel = 1 if travel == "Yes" else 0
vfx = 1 if vfx == "Yes" else 0

# All-in multiplier (simple & fast)
multiplier = 4.0
multiplier += 1.0 if travel else 0.0
multiplier += 0.5 * max((locations - 3) / 3, 0)
multiplier += 0.7 * max(stars - 2, 0)
if vfx:
    multiplier += 1.0 + 0.5 * vfx_complexity

total_daily = daily_cost * multiplier
base_burn = total_daily * shooting_days

# Overheads
preprod = 0.12 * base_burn
postprod = 0.18 * base_burn
travel_cost = 0.10 * base_burn if travel else 0
stars_cost = 0.06 * base_burn * max(stars - 1, 0)
vfx_cost = (0.25 + 0.1 * vfx_complexity) * base_burn if vfx else 0

# Simple delay proxy
delay_days = int(0.25 * shooting_days + (5 if travel else 0) + (5 if vfx else 0))
delay_cost = delay_days * (0.4 * total_daily)

subtotal = base_burn + preprod + postprod + travel_cost + stars_cost + vfx_cost + delay_cost
contingency = 0.22 * subtotal
expected_cost = subtotal + contingency
p75_estimate = expected_cost * 1.1

# =====================
# STATUS
# =====================
if planned_budget >= p75_estimate:
    status = "SAFE ✅"
    color = "green"
elif planned_budget >= expected_cost:
    status = "BORDERLINE ⚠️"
    color = "orange"
else:
    status = "UNSAFE ❌"
    color = "red"

# =====================
# OUTPUT
# =====================
st.divider()
st.subheader("Result")

st.markdown(
    f"<h2 style='color:{color};'>{status}</h2>",
    unsafe_allow_html=True
)

st.write({
    "All-in Multiplier": round(multiplier, 2),
    "Total Daily Burn": round(total_daily),
    "Expected Cost (P50)": round(expected_cost),
    "Conservative Cost (≈P75)": round(p75_estimate),
    "Planned Budget": round(planned_budget),
    "Estimated Delay (days)": delay_days
})

if status != "SAFE ✅":
    st.warning("To improve feasibility, consider:")
    if travel:
        st.write("• Remove travel")
    if vfx:
        st.write("• Reduce or remove VFX")
    if shooting_days > 10:
        st.write("• Cut shooting days")
    if stars > 2:
        st.write("• Reduce stars")
else:
    st.success("Budget is sufficient with margin.")
