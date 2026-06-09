import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

st.set_page_config(page_title="Instagram User Analytics", layout="wide")

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data.csv", encoding='latin1', sep=';') 
        df.columns = [str(col).lower().strip() for col in df.columns]
        
        for col in df.columns:
            if df[col].dtype == 'float64':
                df[col] = df[col].astype(np.float32)
            elif df[col].dtype == 'int64':
                df[col] = df[col].astype(np.int32)
                
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

df = load_data()

if df is not None:
    plt.close('all')
    
    st.title("Instagram User Behavior & Health Dashboard")
    st.markdown("Change the filters in the left sidebar to update the metrics for all charts simultaneously.")
    with st.expander("ℹ️ About Instagram User Analysis (Click to expand/collapse)", expanded=True):
        st.markdown("### Instagram User Analysis")
        st.write(
            "Instagram User Analysis is a web-based analytics platform designed to explore and visualize "
            "social media user behavior through interactive dashboards and data-driven insights. The project "
            "uses a large-scale synthetic dataset containing over 1 million users with demographic, lifestyle, "
            "behavioral, and engagement attributes."
        )
        st.write(
            "This website helps users better understand social media trends, audience behavior, and digital "
            "interaction patterns through modern visualizations and analytical tools."
        )
        
        intro_col1, intro_col2 = st.columns(2)
        with intro_col1:
            st.markdown("#### ✨ Key Features")
            st.markdown(
                """
                - Interactive dashboards and charts
                - User demographic analysis
                - Social media engagement insights
                - Lifestyle and behavioral pattern exploration
                - Data filtering and visualization tools
                - Machine learning and statistical analysis support
                """
            )
        with intro_col2:
            st.markdown("#### 🎯 Purpose")
            st.markdown(
                """
                The platform is built for:
                - Data analysis practice
                - Academic and research purposes
                - Machine learning projects
                - Data visualization learning
                - Social media behavior exploration
                """
            )
    st.markdown("---")

    st.sidebar.header("GLOBAL FILTERS")
    st.sidebar.markdown("Select conditions to update the dashboard:")
    
    gender_options = list(df["gender"].dropna().unique())
    filter_gender = st.sidebar.multiselect("👤 1. User Gender:", options=gender_options, default=gender_options)

    children_list = ["All"] + list(df["has_children"].dropna().unique())
    filter_children = st.sidebar.selectbox("🏡 2. Parental Status:", children_list)
    
    diet_options = list(df["diet_quality"].dropna().unique()) if "diet_quality" in df.columns else []
    filter_diet = st.sidebar.multiselect("🥗 3. Diet Quality:", options=diet_options, default=diet_options)
    
    min_steps = int(df["daily_steps_count"].min()) if "daily_steps_count" in df.columns else 0
    max_steps = int(df["daily_steps_count"].max()) if "daily_steps_count" in df.columns else 20000
    filter_steps = st.sidebar.slider("👟 4. Daily Steps Range:", min_steps, max_steps, (min_steps, max_steps))
    
    df_filtered = df.copy()
    
    if filter_gender:
        df_filtered = df_filtered[df_filtered["gender"].isin(filter_gender)]
    else:
        df_filtered = df_filtered.iloc[0:0]
        
    if filter_children != "All":
        df_filtered = df_filtered[df_filtered["has_children"] == filter_children]
        
    if filter_diet and "diet_quality" in df.columns:
        df_filtered = df_filtered[df_filtered["diet_quality"].isin(filter_diet)]
    elif "diet_quality" in df.columns:
        df_filtered = df_filtered.iloc[0:0]

    if "daily_steps_count" in df.columns and not df_filtered.empty:
        df_filtered = df_filtered[
            (df_filtered["daily_steps_count"] >= filter_steps[0]) & 
            (df_filtered["daily_steps_count"] <= filter_steps[1])
        ]

    st.sidebar.metric("Sample Count:", f"{len(df_filtered):,}")
    
    if df_filtered.empty:
        st.warning("No users match the selected filters. Please adjust your criteria.")
    else:
        tab1, tab2, tab3 = st.tabs(["📊 Part 1: Demographics & Family", "🏥 Part 2: Health & Physical Status", "⛺ Part 3: Lifestyle & Habits"])
        
        with tab1:
            st.markdown("## Part 1: Demographics & Family")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### User Distribution by Gender")
                gender_counts = df_filtered["gender"].value_counts()
                if not gender_counts.empty:
                    fig, ax = plt.subplots(figsize=(8, 5))
                    
                    # Tính toán tổng để tự tạo nhãn phần trăm chuẩn xác dưới Legend
                    total_gender = gender_counts.sum()
                    
                    # SỬA TẠI ĐÂY: Loại bỏ autopct để vòng tròn không bị dính chữ lem nhem nữa
                    wedges, texts = ax.pie(
                        gender_counts.values,
                        colors=plt.get_cmap("Pastel1").colors,
                        startangle=90,
                        wedgeprops=dict(width=0.4, edgecolor="white")
                    )
                        
                    # SỬA TẠI ĐÂY: Tích hợp đầy đủ Số lượng + Phần trăm (%) xếp hàng ngay ngắn bên dưới
                    ax.legend(
                        wedges, 
                        [f"{g}: {n:,} ({n/total_gender*100:.1f}%)" for g, n in zip(gender_counts.index, gender_counts.values)],
                        title="Gender Groups",
                        loc="upper center",
                        bbox_to_anchor=(0.5, -0.05),
                        ncol=2,
                        frameon=False
                    )
                    ax.axis('equal')  
                    st.pyplot(fig)
                    plt.close(fig)
                else:
                    st.info("No data available for Gender chart.")

            with col2:
                st.markdown("#### Proportion of Users with Children")
                counts_child = df_filtered["has_children"].value_counts()
                if not counts_child.empty:
                    fig, ax = plt.subplots(figsize=(8, 5))
                    
                    total_child = counts_child.sum()
                    
                    # SỬA TẠI ĐÂY: Áp dụng đồng bộ giải pháp làm sạch cho cả biểu đồ trạng thái con cái
                    wedges, texts = ax.pie(
                        counts_child.values, 
                        colors=["#87C5FF", "#F8EBA3"], 
                        startangle=90,
                        wedgeprops=dict(width=0.4, edgecolor="white")
                    )
                        
                    ax.legend(
                        wedges,
                        [f"{k}: {v:,} ({v/total_child*100:.1f}%)" for k, v in zip(counts_child.index, counts_child.values)],
                        title="Parental Status",
                        loc="upper center",
                        bbox_to_anchor=(0.5, -0.05),
                        ncol=2,
                        frameon=False
                    )
                    ax.axis('equal')  
                    st.pyplot(fig)
                    plt.close(fig)
                else:
                    st.info("No data available for Parental Status chart.")

        with tab2:
            st.markdown("## Part 2: Health & Physical Status")
            col3, col4 = st.columns(2)
            
            with col3:
                st.markdown("#### Distribution of Daily Steps Count")
                fig, ax = plt.subplots(figsize=(8, 5))
                ax.hist(df_filtered["daily_steps_count"].dropna(), bins=25, color="#B2E2F2", edgecolor="white")
                ax.set_xlabel("Daily Steps")
                ax.set_ylabel("Number of Users")
                st.pyplot(fig)
                plt.close(fig)

                st.markdown("#### Distribution of Body Mass Index (BMI)")
                bmi = df_filtered["body_mass_index"].dropna()
                if not bmi.empty:
                    counts, edges = np.histogram(bmi, bins=40)
                    centers = (edges[:-1] + edges[1:]) / 2
                    fig, ax = plt.subplots(figsize=(8, 5))
                    ax.fill_between(centers, counts, color="#B2E2F2", alpha=0.6)
                    ax.plot(centers, counts, color="#82C0D1", linewidth=2)
                    ax.set_xlabel("BMI Value")
                    st.pyplot(fig)
                    plt.close(fig)

            with col4:
                st.markdown("#### Comparison of Systolic Blood Pressure by Gender")
                avg_bp = df_filtered.groupby("gender")["blood_pressure_systolic"].mean()
                if not avg_bp.empty:
                    fig, ax = plt.subplots(figsize=(8, 4.5))
                    ax.hlines(y=avg_bp.index, xmin=0, xmax=avg_bp.values, color="lightgray", linewidth=4)
                    ax.plot(avg_bp.values, avg_bp.index, "o", markersize=12, color="salmon")
                    ax.axvline(x=120, linestyle='--', color="gray", label="Normal Threshold (120 mmHg)")
                    ax.set_xlabel("Blood Pressure (mmHg)")
                    ax.legend()
                    st.pyplot(fig)
                    plt.close(fig)
                else:
                    st.caption("Insufficient data to analyze blood pressure splits.")

                st.markdown("#### Distribution of Diet Quality")
                if "diet_quality" in df_filtered.columns:
                    order = ["Average", "Good", "Excellent", "Poor", "Very poor"]
                    counts_diet = df_filtered["diet_quality"].value_counts().reindex(order).fillna(0)
                    colors = ["#669DD7", "#FFC285", "#FA9192", "#87EAE1", "#9DD895"]
                    fig, ax = plt.subplots(figsize=(8, 5))
                    ax.vlines(counts_diet.index, 0, counts_diet.values, colors=colors, linewidth=3)
                    ax.scatter(counts_diet.index, counts_diet.values, s=200, color=colors)
                    
                    diet_vals = counts_diet.values
                    for i, val in enumerate(diet_vals):
                        ax.text(i, val + (max(diet_vals) * 0.03), f'{int(val):,}', 
                                va='bottom', 
                                ha='center', 
                                fontsize=10, 
                                fontweight='bold', 
                                color='#4a4a4a')
                    st.pyplot(fig)
                    plt.close(fig)

        with tab3:
            st.markdown("## Part 3: Lifestyle & Habits")
            col5, col6 = st.columns(2)
            
            with col5:
                st.markdown("#### Sleep Hours Per Night Distribution")
                sleep_data = df_filtered["sleep_hours_per_night"].dropna()
                if not sleep_data.empty:
                    bins = np.arange(2, 11, 0.5)
                    counts, edges = np.histogram(sleep_data, bins=bins)
                    centers = (edges[:-1] + edges[1:]) / 2
                    fig, ax = plt.subplots(figsize=(8, 5))
                    ax.plot(centers, counts, color="steelblue", linewidth=2.5)
                    ax.set_xlabel("Sleep Hours")
                    st.pyplot(fig)
                    plt.close(fig)

                st.markdown("#### Annual Travel Frequency Analysis")
                df_travel = df_filtered["travel_frequency_per_year"].value_counts().sort_index()
                if not df_travel.empty:
                    fig, ax = plt.subplots(figsize=(8, 5))
                    ax.plot(df_travel.index, df_travel.values, marker='o', color="#FBB4AE", linewidth=2)
                    ax.fill_between(df_travel.index, df_travel.values, alpha=0.1, color="#FBB4AE")
                    ax.set_xlabel("Trips per Year")
                    st.pyplot(fig)
                    plt.close(fig)

            with col6:
                st.markdown("#### Distribution of Books Read Per Year")
                fig, ax = plt.subplots(figsize=(8, 5))
                ax.hist(df_filtered["books_read_per_year"].dropna(), bins=20, color="#D2B7EA", edgecolor="white")
                ax.set_xlabel("Books Read")
                st.pyplot(fig)
                plt.close(fig)

                st.markdown("#### Distribution of Volunteer Hours")
                v_hours = df_filtered["volunteer_hours_per_month"].dropna()
                if not v_hours.empty:
                    fig, ax = plt.subplots(figsize=(8, 5))
                    sns.histplot(v_hours, bins=25, kde=True, color="firebrick", ax=ax)
                    ax.set_xlabel("Hours per Month")
                    st.pyplot(fig)
                    plt.close(fig)
else:
    st.warning("Please check if 'data.csv' exists in your project folder.")

st.markdown("""
    <style>
        .main {
            background-color: #fcf8f5;
            color: #4A4A4A;
        }
        [data-testid="stSidebar"] {
            background-color: #e8f5e9;
            border-right: 2px solid #c8e6c9;
        }
        h1 {
            color: #2E5A61 !important;
            font-size: 2.5rem !important;
            border-bottom: 3px solid #ffccd5;
            padding-bottom: 10px;
        }
        h2, h3 {
            color: #3A6B74 !important;
            background: linear-gradient(90s, #fff0f3, transparent);
            padding: 5px 10px;
            border-left: 5px solid #ffb3c1;
        }
        [data-testid="stSidebar"] .stSelectbox, [data-testid="stSidebar"] .stMultiSelect {
            background-color: #ffffff !important;
            border: 2px solid #b3e5fc !important;
            border-radius: 12px !important;
            transition: all 0.3s ease-in-out !important;
            padding: 5px !important;
        }
        [data-testid="stSidebar"] .stSelectbox:hover, [data-testid="stSidebar"] .stMultiSelect:hover {
            border-color: #ffb3c1 !important;
            background-color: #fff9fa !important;
            box-shadow: 0 0 15px rgba(255, 179, 193, 0.8), 0 0 5px rgba(179, 229, 252, 0.5) !important;
            transform: scale(1.02) !important;
        }
        div[role="slider"] {
            background-color: #ff718a !important;
            border: 2px solid #ffffff !important;
        }
        [data-testid="stSidebar"] div[data-testid="stMetric"] {
            background-color: #e0f7fa !important;
            padding: 18px !important;
            border-radius: 16px !important;
            text-align: center !important;
            box-shadow: 0 4px 15px rgba(0, 229, 255, 0.2) !important;
            border: 2px dashed #00e5ff !important;
            transition: all 0.3s ease-in-out !important;
        }
        [data-testid="stSidebar"] div[data-testid="stMetric"]:hover {
            transform: translateY(-3px) scale(1.03) !important;
            background-color: #b2ebf2 !important;
            box-shadow: 0 0 20px rgba(0, 229, 255, 0.6), 0 0 8px rgba(179, 229, 252, 0.4) !important;
        }
        [data-testid="stSidebar"] div[data-testid="stMetric"] label {
            color: #00838f !important;
            font-weight: bold !important;
            font-size: 1.1rem !important;
        }
        [data-testid="stSidebar"] div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            color: #00b8d4 !important;
            font-weight: 800 !important;
            font-size: 2.2rem !important;
        }
        .stDetails {
            border: 2px solid #ffd6ff !important;
            border-radius: 12px !important;
            background-color: #fff0f3 !important;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;600;700&family=Quicksand:wght@500;700&display=swap" rel="stylesheet">

    <style>
        html, body, [data-testid="stAppViewContainer"], .main {
            font-family: 'Be Vietnam Pro', sans-serif !important;
            background-color: #fff9f6 !important;
        }
        [data-testid="stSidebar"] {
            background-color: #f0f7f4 !important;
            border-right: 2px solid #e1efe6 !important;
        }
        [data-testid="stSidebar"] .stMarkdown h1, [data-testid="stSidebar"] .stMarkdown h2 {
            font-family: 'Quicksand', sans-serif !important;
            color: #2E5A61 !important;
        }
        div[data-testid="stSelectbox"], div[data-testid="stMultiSelect"] {
            background-color: #ffffff !important;
            padding: 8px 12px !important;
            border-radius: 16px !important;
            border: 1px solid #e1efe6 !important;
            box-shadow: 0 4px 10px rgba(46, 90, 97, 0.05) !important;
            margin-bottom: 10px !important;
        }
        h1 {
            font-family: 'Quicksand', sans-serif !important;
            font-weight: 700 !important;
            color: #1e464d !important;
            font-size: 2.8rem !important;
            letter-spacing: -0.5px;
        }
        .stMarkdown hr {
            border: none !important;
            height: 4px !important;
            background: linear-gradient(90deg, #ffb3c1, #ffe5ec, transparent) !important;
            border-radius: 10px !important;
            margin-top: -10px !important;
            margin-bottom: 25px !important;
        }
        h2, h3 {
            font-family: 'Quicksand', sans-serif !important;
            color: #2c5259 !important;
            font-weight: 700 !important;
            border-left: 6px solid #ffb3c1 !important;
            padding-left: 12px !important;
            margin-top: 30px !important;
        }
        div[data-testid="stExpander"] {
            background-color: #ffffff !important;
            border: 1px solid #ffe5ec !important;
            border-radius: 16px !important;
            box-shadow: 0 6px 15px rgba(255, 179, 193, 0.1) !important;
            overflow: hidden !important;
            padding: 5px !important;
        }
        div[data-testid="stExpander"] details summary p {
            font-family: 'Quicksand', sans-serif !important;
            font-weight: 700 !important;
            color: #2c5259 !important;
            font-size: 1.1rem !important;
        }
        [data-testid="stImage"], [data-testid="stElementToolbar"] + div {
            border-radius: 16px !important;
            overflow: hidden !important;
        }
        button[data-baseweb="tab"] {
            font-family: 'Quicksand', sans-serif !important;
            font-weight: bold !important;
            font-size: 1.05rem !important;
            color: #7da1a6 !important;
            border: none !important;
            background-color: transparent !important;
            padding: 10px 20px !important;
            transition: all 0.2s ease !important;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            color: #1e464d !important;
            border-bottom: 3px solid #ffb3c1 !important;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
        div[data-baseweb="select"] {
            border: 2px solid #b3e5fc !important;
            border-radius: 12px !important;
            background-color: #ffffff !important;
            transition: all 0.2s ease-in-out;
        }
        div[data-baseweb="select"]:hover {
            border-color: #ffb3c1 !important;
            box-shadow: 0 4px 10px rgba(255, 179, 193, 0.2) !important;
        }
        div[data-baseweb="slider"] > div {
            background-color: #ffe5ec !important;
        }
        div[role="slider"] {
            background-color: #ff718a !important;
            border: 2px solid #ffffff !important;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2) !important;
        }
        div[data-testid="stExpander"] {
            border: 1px solid #ffe5ec !important;
            border-radius: 12px !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.02) !important;
            background-color: #ffffff !important;
        }
    </style>
""", unsafe_allow_html=True)