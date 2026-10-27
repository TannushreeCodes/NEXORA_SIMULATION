import streamlit as st
import pandas as pd

st.set_page_config(page_title="NEXORA Simulator", layout="wide")
st.title("NEXORA — What-If Simulator")

drain_df = pd.read_csv("data/drain.csv")
occupancy_df = pd.read_csv("data/occupancy.csv")
parking_df = pd.read_csv("data/parking_spots.csv")
scenario = st.selectbox(
    "Choose scenario",
    ["Energy", "Drain", "Parking"]
)
if scenario == "Energy":
    st.subheader("Energy — fan use reduction")

    building = st.selectbox(
        "Choose building",
        sorted(occupancy_df["building_id"].unique())
    )

    # # Get the latest reading for each zone
    building_data = occupancy_df[
        occupancy_df["building_id"] == building
    ].copy()
    building_data["timestamp"] = pd.to_datetime(building_data["timestamp"])
    latest_zones = (
        building_data.sort_values("timestamp")
        .drop_duplicates("zone_id", keep="last")
    )

    current_energy = latest_zones["estimated_power_kwh"].sum()
    reduction = st.slider("Simulated energy reduction (%)", 0, 50, 10)

    saved_energy = current_energy * reduction / 100
    energy_after = current_energy - saved_energy

    st.metric("Current estimated energy", f"{current_energy:.3f} kWh")
    st.metric("Estimated energy saved", f"{saved_energy:.3f} kWh")
    st.metric("After intervention", f"{energy_after:.3f} kWh")

    st.caption(
        "Estimate uses the latest zone readings. It represents the latest "
        "sensor interval, not a full day."
    )


elif scenario == "Drain":
    st.subheader("Drain — simulate clearing")

    building = st.selectbox(
        "Choose building",
        sorted(drain_df["building_id"].unique())
    )

    building_data = drain_df[
        drain_df["building_id"] == building
    ].copy()
    building_data["timestamp"] = pd.to_datetime(building_data["timestamp"])

    latest_drains = (
        building_data.sort_values("timestamp")
        .drop_duplicates("drain_id", keep="last")
    )

    drain_id = st.selectbox(
        "Choose drain",
        sorted(latest_drains["drain_id"].unique())
    )
    current = latest_drains[latest_drains["drain_id"] == drain_id].iloc[0]

    current_distance = float(current["distance_to_water_cm"])
    clearing = st.slider("Simulated clearing (%)", 0, 100, 50)

    drain_history = drain_df[drain_df["drain_id"] == drain_id].copy()
    drain_history["is_choking"] = (
        drain_history["is_choking"].astype(str).str.lower() == "true"
    )
    healthy = drain_history[~drain_history["is_choking"]]

    if healthy.empty:
        st.warning("No non-choking history found for this drain.")
    else:
        normal_distance = float(healthy["distance_to_water_cm"].median())
        after_distance = current_distance + (
            normal_distance - current_distance
        ) * clearing / 100

        status = str(current["is_choking"]).lower() == "true"
        st.metric("Current status", "Choking" if status else "Not choking")
        st.metric("Current distance to water", f"{current_distance:.1f} cm")
        st.metric("Simulated distance", f"{after_distance:.1f} cm")

        st.caption(
            "Simulated distance moves toward this drain's historical "
            "non-choking median. It does not predict flow rate."
        )


else:
    st.subheader("Parking — smart parking guidance")

    lot = st.selectbox(
        "Choose parking lot",
        sorted(parking_df["lot_id"].unique())
    )

    lot_data = parking_df[parking_df["lot_id"] == lot].copy()
    lot_data["timestamp"] = pd.to_datetime(lot_data["timestamp"])
    lot_data["occupied"] = (
        lot_data["occupied"].astype(str).str.lower() == "true"
    )

    latest_spots = (
        lot_data.sort_values("timestamp")
        .drop_duplicates("spot_id", keep="last")
    )

    capacity = latest_spots["spot_id"].nunique()
    occupied_now = int(latest_spots["occupied"].sum())

    target_pct = st.slider("Target lot occupancy (%)", 50, 100, 90)
    arrivals = st.number_input(
        "Assumed incoming vehicles",
        min_value=0,
        max_value=100,
        value=5
    )

    target_spots = int(capacity * target_pct / 100)
    route_elsewhere = min(
        arrivals,
        max(0, occupied_now + arrivals - target_spots)
    )
    projected_occupied = occupied_now + arrivals - route_elsewhere

    st.metric("Occupied spots now", f"{occupied_now} / {capacity}")
    st.metric("Vehicles to guide to another lot", route_elsewhere)
    st.metric(
        "Projected occupancy after guidance",
        f"{projected_occupied} / {capacity}"
    )

    st.caption(
        "Incoming vehicle count is a scenario assumption because the CSV "
        "contains parking spot readings, not arrival counts."
    )