import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt 
import plotly.graph_objects as go
import requests
import pymysql

# for connection to mysql databse ------------

conn = pymysql.connect(
        host="localhost",
        user="root",
        password = "Vinay@123",
        database="Phonepe"
    )

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="PhonePe Data Analysis",
    layout="wide"
)

# ---------------- SIDEBAR ----------------

st.sidebar.title("Navigation")
page = st.sidebar.radio("", ["Home", "Business Case Study"])

# ---------------- MAIN TITLE ----------------

st.markdown(
    "<h1 style='text-align:center;'>PHONEPE DATA ANALYSIS</h1>",
    unsafe_allow_html=True
)

# ================= HOME PAGE =================

if page == "Home":
    st.subheader("Home Page")

    st.title("🗺️ India Transaction Map")

# --------------FILTERS (YEAR & QUARTER)------ 

    col1, col2 = st.columns(2)

    years_df = pd.read_sql("SELECT DISTINCT Year FROM aggregated_transaction ORDER BY Year;", conn)
    quarters_df = pd.read_sql("SELECT DISTINCT Quarter FROM aggregated_transaction ORDER BY Quarter;", conn)

    years = ["All"] + years_df["Year"].tolist()
    quarters = ["All"] + quarters_df["Quarter"].tolist()

    with col1:
        selected_year = st.selectbox("Select Year", years)

    with col2:
        selected_quarter = st.selectbox("Select Quarter", quarters)

#--------------- DYNAMIC WHERE CLAUSE----------- 

    conditions = []
    if selected_year != "All":
        conditions.append(f"Year = {selected_year}")
    if selected_quarter != "All":
        conditions.append(f"Quarter = '{selected_quarter}'")

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

# -----------------QUERY TO GET DATA--------------

    query = f"""
SELECT
    State,
    SUM(Transaction_count) AS total_transactions,
    SUM(Transaction_amount) AS total_amount
FROM aggregated_transaction
{where_clause}
GROUP BY State
ORDER BY total_transactions DESC;
"""

    df = pd.read_sql(query, conn)

#-------------- LOAD GEOJSON & GET STATES LIST------- 

    geojson_url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
    geojson = requests.get(geojson_url).json()
    geo_states = [feature['properties']['ST_NM'] for feature in geojson['features']]

#--------- FIX STATE NAMES TO MATCH GEOJSON-------- 

    df['State'] = df['State'].str.strip()
    df['State_lower'] = df['State'].str.lower()
    geo_states_lower = [s.strip().lower() for s in geo_states]

    state_mapping = {s_lower: s for s_lower, s in zip(geo_states_lower, geo_states)}
    df['State'] = df['State_lower'].map(state_mapping)
    df = df.drop(columns=['State_lower'])

#--------- MERGE TO INCLUDE ALL STATES (FILL MISSING WITH ZERO)--------

    all_states_df = pd.DataFrame({'State': geo_states})

    df = all_states_df.merge(df, on='State', how='left')
    df['total_transactions'] = df['total_transactions'].fillna(0)
    df['total_amount'] = df['total_amount'].fillna(0)

#------------- PLOT CHOROPLETH WITH BORDER-------  

    fig = px.choropleth(
        df,
        geojson=geojson,
        featureidkey='properties.ST_NM',
        locations='State',
        color='total_transactions',  # Change to 'total_amount' if needed
        color_continuous_scale='Reds',
        labels={'total_transactions': 'Total Transactions'},
        hover_data=['total_amount']
    )

    fig.update_geos(
        fitbounds="locations",
        visible=False,
        showcountries=False,
        showcoastlines=False,
        showframe=False
    )

#------------- Add black border to states-------------- 

    fig.update_traces(marker_line_width=0.8, marker_line_color='black')

    fig.update_layout(
        title_text="🗺️ Total Transactions by State",
        margin={"r":0, "t":30, "l":0, "b":0}
    )

    st.plotly_chart(fig, use_container_width=True)



# ================= BUSINESS CASE STUDY =================

elif page == "Business Case Study":

    st.markdown(
        "<h2 style='text-align:center;'>Business Case Study</h2>",
        unsafe_allow_html=True
    )

    st.markdown("### Select any Question")

    # -------- QUESTION DROPDOWN --------

    question = st.selectbox(
        "Choose a Question",
        [
            "1. Decoding Transaction Dynamics on PhonePe",
            "2. Device Dominance and User Engagement Analysis",
            "3. Insurance Penetration and Growth Potential Analysis",
            "4. Transaction Analysis for Market Expansion",
            "5. User Engagement and Growth Strategy"
        ]
    )

    #======================================================
    # -------------------- QUESTION 1 ---------------------
    #=======================================================  

    if question == "1. Decoding Transaction Dynamics on PhonePe":

        col1, col2 = st.columns(2)

        with col1:
            year = st.selectbox(
                "Year",
                [2018, 2019, 2020, 2021, 2022, 2023, 2024]
            )

        with col2:
            quarter = st.selectbox(
                "Quarter",
                ["Q1", "Q2", "Q3", "Q4"]
            )

        st.divider()

       # -------Convert Quarter--------- 

        quarter_map = {
            "Q1": 1,
            "Q2": 2,
            "Q3": 3,
            "Q4": 4
        }
        qtr = quarter_map[quarter]

        st.markdown(
    "<h1 style='text-align: center; color: red;'>Top 10 State-wise Total Transaction Amount</h1>",
     unsafe_allow_html=True
)


        # -------- SQL Query-----------
 
        query = """
SELECT 
    State,
    SUM(Transaction_amount) AS total_amount
FROM aggregated_transaction
WHERE year = %s AND quarter = %s
GROUP BY State
ORDER BY total_amount DESC
LIMIT 10;
"""

        df = pd.read_sql(query, conn, params=(year, qtr))

        #----------- Convert to Trillions --------------
 
        df["total_amount_trillion"] = df["total_amount"] / 1e12

        # ------------ Plotly Bar Chart-------------- 
 
        fig = px.bar(
            df,
            x="State",
            y="total_amount_trillion",
            text="total_amount_trillion",
            color="State",
            title="Top 10 State-wise Total Transaction Amount",
        )

        fig.update_traces(
            texttemplate='%{text:.2f}T',
            textposition='outside'
        )

        fig.update_layout(
            xaxis_title="State",
            yaxis_title="Transaction Amount (Trillion)",
            showlegend=False,
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

        #========= for payment method popularity using donut chart ===============
 
        st.markdown(
    "<h1 style='text-align: center; color: red;'>Payment Method Popularity</h1>",
     unsafe_allow_html=True
)

       

        # ------------ SQL Query for donut chart ------------ 
 
        query_donut = """
SELECT
    Transaction_type,
    SUM(Transaction_count) AS total_transactions,
    SUM(Transaction_amount) AS total_amount
FROM aggregated_transaction
WHERE year = %s AND quarter = %s
GROUP BY Transaction_type
ORDER BY total_transactions DESC;
"""

        df_donut = pd.read_sql(query_donut, conn, params=(year, qtr))

        #------------ for Fixed Color --------------------
        color_map = {
    "Peer-to-peer payments": "#1f77b4",      # dark blue
    "Merchant payments": "#aec7e8",          # light blue
    "Recharge & bill payments": "#ff4d4d",   # red
    "Others": "#f7b6d2",                      # pink
    "Financial Services": "#2ca02c"           # green
            }

       #------- for leyout -----------
        col1, col2 = st.columns(2)

       # ----Donut Chart: Transaction Count ------------  

        with col1:
            fig_count = px.pie(
                df_donut,
                names="Transaction_type",
                values="total_transactions",
                hole=0.55,
                title="Distribution of Total Transaction Count",
                color="Transaction_type",
                color_discrete_map=color_map
            )

            fig_count.update_traces(
                textinfo="percent",
                textposition="inside"
            )

            fig_count.update_layout(
                title_x=0.5,
                legend_title_text="",
                showlegend=True
            )

            st.plotly_chart(fig_count, use_container_width=True)

       #-------  Donut Chart: Transaction Amount ----------------   

        with col2:
            fig_amount = px.pie(
                df_donut,
                names="Transaction_type",
                values="total_amount",
                hole=0.55,
                title="Distribution of Total Transaction Amount",
                color="Transaction_type",
                color_discrete_map=color_map
            )

            fig_amount.update_traces(
                textinfo="percent",
                textposition="inside"
            )

            fig_amount.update_layout(
                title_x=0.5,
                legend_title_text="",
                showlegend=True
            )

            st.plotly_chart(fig_amount, use_container_width=True)

        #==========Comparing payment category by state===================
        st.markdown(
    "<h1 style='text-align: center; color: red;'>Transactions by State and Payment Category</h1>",
     unsafe_allow_html=True
)    


    # --------------- Get State List using sql -------------  

        state_query = """
SELECT DISTINCT State
FROM aggregated_transaction
WHERE year = %s AND quarter = %s
ORDER BY State;
"""

        state_df = pd.read_sql(state_query, conn, params=(year, qtr))

        selected_state = st.selectbox(
            "Select a State",
            state_df["State"]
        )

    #-------------  SQL Query --------------------------  

        query = """
SELECT
    Transaction_type AS payment_category,
    SUM(Transaction_amount) AS total_amount
FROM aggregated_transaction
WHERE year = %s
  AND quarter = %s
  AND State = %s
GROUP BY Transaction_type
ORDER BY total_amount DESC;
"""

        df = pd.read_sql(query, conn, params=(year, qtr, selected_state))

        #------- Convert to Trillions -------------------

        df["total_amount_trillion"] = df["total_amount"] / 1e12

        #--------------ploting graph --------------------  
 
        fig = px.line(
            df,
            x="payment_category",
            y="total_amount_trillion",
            markers=True,
            title=f"Transaction Distribution in {selected_state} ({year} {quarter})"
        )

        fig.update_layout(
            xaxis_title="Payment Category",
            yaxis_title="Transaction Amount (Trillion)",
            height=500
        )

        fig.update_traces(
            line=dict(width=3),
            marker=dict(size=10)
        )

        st.plotly_chart(fig, use_container_width=True)

    
    #=====================================================
    # ------------------- QUESTION 2 ---------------------
    #===================================================== 

    elif question == "2. Device Dominance and User Engagement Analysis":

        col1, col2 = st.columns(2)

        with col1:
            year = st.selectbox(
                "Year",
                [2018, 2019, 2020, 2021, 2022]
            )

        with col2:
            quarter = st.selectbox(
                "Quarter",
                ["Q1", "Q2", "Q3", "Q4"]
            )

        st.divider()

        quarter_map = {"Q1": 1, "Q2": 2, "Q3": 3, "Q4": 4}
        qtr = quarter_map[quarter]

        #=========== 1️⃣ BRAND-WISE TOTAL USERS ===================

        query_brand = """
SELECT 
    Brand,
    SUM(User_count) AS total_users
FROM aggregated_user
WHERE year = %s AND quarter = %s
GROUP BY Brand
ORDER BY total_users DESC;
"""

        df_brand = pd.read_sql(query_brand, conn, params=(year, qtr))

        st.markdown(
    "<h1 style='text-align: center; color: red;'>Total Users by Brand</h1>",
     unsafe_allow_html=True
)

        fig1, ax1 = plt.subplots(figsize=(10, 6))
        ax1.barh(df_brand["Brand"], df_brand["total_users"], color="steelblue")
        ax1.set_xlabel("Total Users")
        ax1.set_ylabel("Brand")
        ax1.set_title(f"Brand-wise User Distribution ({year} {quarter})")
        ax1.invert_yaxis()

        st.pyplot(fig1)

        st.divider()

        #=========== 2️⃣ STATE-WISE BRAND DISTRIBUTION============================== 

        query_state_brand = """
SELECT 
    State,
    Brand,
    SUM(User_count) AS total_users
FROM aggregated_user
WHERE year = %s AND quarter = %s
GROUP BY State, Brand
ORDER BY State, total_users DESC;
"""

        df_state_brand = pd.read_sql(query_state_brand, conn, params=(year, qtr))
        st.markdown(
    "<h1 style='text-align: center; color: red;'>State-wise Brand Distribution</h1>",
     unsafe_allow_html=True
)


      #----------- Pivot data for stacked bar chart ----------------------   

        pivot_df = df_state_brand.pivot(
            index="State",
            columns="Brand",
            values="total_users"
        ).fillna(0)

        fig2, ax2 = plt.subplots(figsize=(14, 7))
        pivot_df.plot(
            kind="bar",
            stacked=True,
            ax=ax2,
            colormap="tab20"
        )

        ax2.set_xlabel("State")
        ax2.set_ylabel("Total Users")
        ax2.set_title(f"State-wise Brand-wise User Distribution ({year} {quarter})")
        ax2.legend(title="Brand", bbox_to_anchor=(1.05, 1), loc="upper left")

        st.pyplot(fig2)

        st.divider()

       #===============for underutilized brand analysis================= 
        st.markdown(
    "<h1 style='text-align: center; color: red;'>Underutilized Brands Analysis</h1>",
     unsafe_allow_html=True
)

        query_underutilized = """
SELECT 
    Brand,
    SUM(User_count) AS total_users,
    AVG(Percentage) AS avg_percentage
FROM aggregated_user
WHERE year = %s AND quarter = %s
GROUP BY Brand
HAVING SUM(User_count) > 100000
   AND AVG(Percentage) < 5
ORDER BY total_users DESC;
"""

        df_underutilized = pd.read_sql(
            query_underutilized,
            conn,
            params=(year, qtr)
        )

      #---------------- Safety check----------------------      

        if df_underutilized.empty:
            st.info("No underutilized brands found for the selected year and quarter.")
        else:
            fig = px.scatter(
                df_underutilized,
                x="total_users",
                y="avg_percentage",
                size="total_users",
                color="Brand",
                hover_name="Brand",
                title=f"Underutilized Brands ({year} {quarter})",
                size_max=60
            )

            fig.update_layout(
                xaxis_title="Total Users",
                yaxis_title="Average Usage Percentage",
                height=550
            )

            st.plotly_chart(fig, use_container_width=True)


    #==================================================
    # ------------------ QUESTION 3 ------------------- 
    # =================================================   

    elif question == "3. Insurance Penetration and Growth Potential Analysis":

        st.subheader("Insurance Transactions by State (All Years & Quarters)")

        st.divider()

   #------------- Query for Data -------------------

        query = """
SELECT
    State,
    SUM(Transaction_count) AS total_insurance_transactions
FROM aggregated_insurance
WHERE Transaction_type = 'Insurance'
GROUP BY State
ORDER BY total_insurance_transactions DESC;
"""

        df = pd.read_sql(query, conn)


      #----------------- Plot Graph ----------------------

        plot_df = df if not df.empty else pd.DataFrame({
            "State": ["No Data"],
            "total_insurance_transactions": [0]
        })

        fig = px.bar(
            plot_df,
            x="State",
            y="total_insurance_transactions",
            color="total_insurance_transactions",
            color_continuous_scale="Blues",
            text="total_insurance_transactions",
            labels={"total_insurance_transactions": "Total Transactions"}
        )

        fig.update_traces(textposition="outside")
        fig.update_layout(
            xaxis_title="State",
            yaxis_title="Total Insurance Transactions",
            uniformtext_minsize=8
        )

        st.plotly_chart(fig, use_container_width=True)

      #====================for total transaction amount=============
        st.subheader("State-wise Total Insurance Amount")

    #------- SQL Query-----------
        query_amount = """
SELECT
    State,
    SUM(Transaction_amount) AS total_insurance_amount
FROM aggregated_insurance
WHERE Transaction_type = 'Insurance'
GROUP BY State
ORDER BY total_insurance_amount DESC;
"""

# Fetch data
        df_amount = pd.read_sql(query_amount, conn)

# Horizontal Bar Chart
        fig, ax = plt.subplots(figsize=(10, 7))

        ax.barh(
            df_amount["State"],
            df_amount["total_insurance_amount"],
            color="teal"
        )

        ax.set_title("Total Insurance Amount by State")
        ax.set_xlabel("Total Insurance Amount")
        ax.set_ylabel("State")

# Reverse y-axis to show highest value at top
        ax.invert_yaxis()

        st.pyplot(fig)

    #======================== for year wise insurance transaction ======================
        st.markdown(
    "<h1 style='text-align: center; color: red;'>Year-wise Insurance Transactions (State-wise Trend)</h1>",
     unsafe_allow_html=True
) 
 
# Get list of states for dropdown
        state_query = """
SELECT DISTINCT State
FROM aggregated_insurance
ORDER BY State;
"""
        states = pd.read_sql(state_query, conn)["State"].tolist()

# State filter
        selected_state = st.selectbox("Select State", states)

# SQL Query (State filtered)
        query_year_state = f"""
SELECT
    Year,
    SUM(Transaction_count) AS insurance_transactions
FROM aggregated_insurance
WHERE Transaction_type = 'Insurance'
  AND State = '{selected_state}'
GROUP BY Year
ORDER BY Year;
"""

# Fetch data
        df_year_state = pd.read_sql(query_year_state, conn)

# Line Chart
        fig, ax = plt.subplots(figsize=(8, 4))

        ax.plot(
            df_year_state["Year"],
            df_year_state["insurance_transactions"],
            marker="o",
            linestyle="-",
            color="darkorange"
        )

        ax.set_title(f"Year-wise Insurance Transactions in {selected_state}")
        ax.set_xlabel("Year")
        ax.set_ylabel("Total Insurance Transactions")

        ax.grid(True)
        st.pyplot(fig)
    #================================================
   # ----------------- QUESTION 4 -------------------
   #==================================================
    elif question == "4. Transaction Analysis for Market Expansion": 

        st.title("State-wise Transaction Amounts Comparison")
        st.divider()

#  FILTERS 
        col1, col2 = st.columns(2)

        with col1:
            year = st.selectbox(
                "Year",
                options=["All", 2018, 2019, 2020, 2021, 2022, 2023, 2024]
            )

        with col2:
            quarter_label = st.selectbox(
                "Quarter",
                options=["All", "Q1", "Q2", "Q3", "Q4"]
            )

        quarter_map = {
            "All": "All",
            "Q1": 1,
            "Q2": 2,
            "Q3": 3,
            "Q4": 4
        }

        quarter = quarter_map[quarter_label]

#  QUERY 
        query = """
SELECT 
    State,
    SUM(Transaction_amount) AS total_amount
FROM map_transaction
WHERE 1=1
"""

        if year != "All":
            query += f" AND Year = {year}"

        if quarter != "All":
            query += f" AND Quarter = {quarter}"

        query += """
GROUP BY State
ORDER BY total_amount DESC
LIMIT 10;
"""

#  FETCH DATA 
        df = pd.read_sql(query, conn)

        df["total_amount_T"] = df["total_amount"] / 1_000_000_000_000

#  PLOT

        fig = px.bar(
            df,
            x="State",
            y="total_amount_T",
            text=df["total_amount_T"].round(2).astype(str) + "T",
            color="State"
        )

        fig.update_traces(textposition="outside")

        fig.update_layout(
            title=dict(
                text="Top 10 State-wise Total Transaction Amount",
                font=dict(size=36, color="red")
            ),
            xaxis_title="State",
            yaxis_title="Transaction Amount (Trillion)",
            showlegend=False,
            height=550
        )

        st.plotly_chart(fig, use_container_width=True)

      #============= for overall comparison===============
        st.subheader("Overall Transaction Comparison")

        kpi_query = """
SELECT 
    SUM(Transaction_amount) AS total_amount,
    SUM(Transaction_count) AS total_transactions
FROM map_transaction
WHERE 1=1
"""

# Use EXISTING year and quarter variables
        if year != "All":
            kpi_query += f" AND Year = {year}"

        if quarter != "All":
            kpi_query += f" AND Quarter = {quarter}"

        kpi_df = pd.read_sql(kpi_query, conn)

        total_amount = kpi_df["total_amount"][0]
        total_transactions = kpi_df["total_transactions"][0]

# KPI display
        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                label="💰 Total Transaction Amount",
                value=f"₹ {total_amount/1_000_000_000_000:.2f} Trillion"
            )

        with col2:
            st.metric(
                label="🔄 Total Transaction Count",
                value=f"{total_transactions/1_000_000_000:.2f} Billion"
            )

        # ===================== COMPARISON GRAPH =====================
        st.markdown(
    "<h1 style='text-align: center; color: red;'>State wise Comparison(trnasaction count vs transaction amount)</h1>",
     unsafe_allow_html=True
)
# STATE FILTER
        state_query = "SELECT DISTINCT State FROM map_transaction ORDER BY State"
        state_df = pd.read_sql(state_query, conn)

        state_list = ["All"] + state_df["State"].tolist()
        state = st.selectbox("State", state_list)

# QUERY
        compare_query = """
SELECT
    SUM(Transaction_amount) AS total_amount,
    SUM(Transaction_count) AS total_count
FROM map_transaction
WHERE 1=1
"""

        if year != "All":
            compare_query += f" AND Year = {year}"

        if quarter != "All":
            compare_query += f" AND Quarter = {quarter}"

        if state != "All":
            compare_query += f" AND State = '{state}'"

        compare_df = pd.read_sql(compare_query, conn)

# PREPARE DATA
        graph_df = pd.DataFrame({
            "Metric": ["Transaction Amount", "Transaction Count"],
            "Value": [
                compare_df["total_amount"][0] / 1_000_000_000_000,  # Trillion
                compare_df["total_count"][0] / 1_000_000_000        # Billion
            ],
            "Unit": ["₹ Trillion", "Billion"]
        })

# BAR CHART
        fig = px.bar(
            graph_df,
            x="Metric",
            y="Value",
            text=graph_df["Value"].round(2).astype(str) + " " + graph_df["Unit"],
            color="Metric",
            title="Transaction Amount vs Transaction Count"
        )

        fig.update_traces(textposition="outside")

        fig.update_layout(
            xaxis_title="Metric",
            yaxis_title="Value (Different Units)",
            title_font_size=26,
            height=500,
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

        # ===================== LOW TRANSACTION STATES (₹ BILLION) =====================
        st.markdown(
    "<h1 style='text-align: center; color: red;'>States with Lowest Transaction Amount</h1>",
     unsafe_allow_html=True
)

# SQL QUERY (Connected to Year & Quarter)
        low_state_query = """
SELECT 
    State,
    SUM(Transaction_amount) AS total_amount
FROM map_transaction
WHERE 1=1
"""

        if year != "All":
            low_state_query += f" AND Year = {year}"

        if quarter != "All":
            low_state_query += f" AND Quarter = {quarter}"

        low_state_query += """
GROUP BY State
ORDER BY total_amount ASC;
"""

        low_state_df = pd.read_sql(low_state_query, conn)

# Convert to BILLION 
        low_state_df["total_amount_B"] = (
            low_state_df["total_amount"] / 1_000_000_000
        )

# Show Bottom 10 States
        low_state_df = low_state_df.head(10)

# HORIZONTAL BAR CHART
        fig_low = px.bar(
            low_state_df,
            x="total_amount_B",
            y="State",
            orientation="h",
            text=low_state_df["total_amount_B"].round(2).astype(str) + " B",
            title="Bottom 10 States by Transaction Amount"
        )

        fig_low.update_traces(textposition="outside")

        fig_low.update_layout(
            xaxis_title="Transaction Amount (₹ Billion)",
            yaxis_title="State",
            title_font_size=26,
            height=600
        )

        st.plotly_chart(fig_low, use_container_width=True)


    #=============================================
    # --------------- QUESTION 5 ----------------- 
    #============================================= 

    elif question == "5. User Engagement and Growth Strategy": 

        st.title("Registered Users by State")

        st.divider()

# SQL Query without Year & Quarter filters
        query = """
SELECT 
    State,
    SUM(Registered_users) AS total_registered_users
FROM map_user
GROUP BY State
ORDER BY total_registered_users DESC;
"""

        df = pd.read_sql(query, conn)

# Graph
        if df.empty:
            st.warning("No data available.")
        else:
            st.subheader("Registered Users by State (All Years & Quarters)")

    # Horizontal bar chart
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.barh(df["State"], df["total_registered_users"], color='skyblue')
            ax.set_xlabel("Total Registered Users")
            ax.set_ylabel("State")
            ax.invert_yaxis()  # Highest value on top

            st.pyplot(fig)

    #===============for state wise app open=================   

        # SQL Query
        query = """
SELECT 
    State,
    SUM(App_opens) AS total_app_opens
FROM map_user
GROUP BY State
ORDER BY total_app_opens DESC;
"""

# Load data into DataFrame
        df = pd.read_sql(query, conn)

# Streamlit UI
        st.title("📊 State-wise Total App Opens")

# Plotly Horizontal Bar Chart
        fig = px.bar(
            df,
            x="total_app_opens",
            y="State",
            orientation="h",
            title="Total App Opens by State",
            color="total_app_opens",
            color_continuous_scale="Blues"
        )

        fig.update_layout(
            yaxis={'categoryorder':'total ascending'},
            xaxis_title="Total App Opens",
            yaxis_title="State",
            title_font_size=30
        )

# Display chart
        st.plotly_chart(fig, use_container_width=True)

      #=============== Engament analysis ==================   

        st.title("📊 State-wise Engagement Analysis")

# FILTERS (WITH ALL OPTION)
        col1, col2 = st.columns(2)

        years_df = pd.read_sql("SELECT DISTINCT Year FROM map_user ORDER BY Year;", conn)
        quarters_df = pd.read_sql("SELECT DISTINCT Quarter FROM map_user ORDER BY Quarter;", conn)

        years = ["All"] + years_df["Year"].tolist()
        quarters = ["All"] + quarters_df["Quarter"].tolist()

        with col1:
            selected_year = st.selectbox("Select Year", years)

        with col2:
            selected_quarter = st.selectbox("Select Quarter", quarters)

# DYNAMIC WHERE CLAUSE
        conditions = []

        if selected_year != "All":
            conditions.append(f"Year = {selected_year}")

        if selected_quarter != "All":
            conditions.append(f"Quarter = '{selected_quarter}'")

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

# QUERY (RAW ENGAGEMENT RATIO)
        query = f"""
SELECT 
    State,
    (SUM(App_opens) * 1.0 / SUM(Registered_users)) AS engagement_ratio
FROM map_user
{where_clause}
GROUP BY State
ORDER BY engagement_ratio DESC;
"""

        df = pd.read_sql(query, conn)

# KPI METRICS
        top_state = df.iloc[0]
        lowest_state = df.iloc[-1]
        avg_engagement = df["engagement_ratio"].mean()

        k1, k2, k3 = st.columns(3)

        k1.metric(
            "🏆 Highest Engagement",
            top_state["State"],
            f"{top_state['engagement_ratio']:.2f}"
        )

        k2.metric(
            "📊 Average Engagement",
            f"{avg_engagement:.2f}"
        )

        k3.metric(
            "🔻 Lowest Engagement",
            lowest_state["State"],
            f"{lowest_state['engagement_ratio']:.2f}"
        )

        st.divider()


# BAR CHART
        fig = px.bar(
            df,
            x="engagement_ratio",
            y="State",
            orientation="h",
            color="engagement_ratio",
            color_continuous_scale="Viridis",
            title="Average App Opens per User by State"
        )

        fig.update_layout(
            xaxis_title="Average App Opens per User",
            yaxis_title="State",
            yaxis=dict(autorange="reversed"),
            height=900
        )

        st.plotly_chart(fig, use_container_width=True)

# DATA TABLE
        with st.expander("📋 View Data Table"):
            st.dataframe(df)
