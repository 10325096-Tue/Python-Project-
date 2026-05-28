import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import requests
import io

# 1. CẤU HÌNH TRANG WEB
st.set_page_config(page_title="Instagram User Analytics", layout="wide")

# 2. HÀM TẢI DATA TỪ DRIVE (ÉP CHỮ THƯỜNG CHỐNG LỖI KEYERROR)
@st.cache_data
def load_data():
    try:
        file_id = "1n_9kA8BPrZpuDxdZrGHGoXZ7KUi9cUVJ"
        url = f"https://drive.google.com/uc?export=download&id={file_id}"
        
        response = requests.get(url)
        response.raise_for_status()
        
        # Đọc dữ liệu phân tách bằng dấu chấm phẩy
        df = pd.read_csv(io.BytesIO(response.content), encoding='latin1', sep=';')
        
        # Ép tất cả tên cột thành chữ thường và xóa khoảng trắng thừa
        df.columns = [str(col).lower().strip() for col in df.columns]
        return df
    except Exception as e:
        st.error(f"Lỗi tải dữ liệu từ Google Drive: {e}")
        return None

df = load_data()

# 3. NẾU CÓ DATA THÌ CHẠY GIAO DIỆN
if df is not None:
    plt.close('all')
    
    st.title("Instagram User Behavior & Health Dashboard")
    st.markdown("Change the filters in the left sidebar to update the metrics for all charts simultaneously.")
    
    # Hộp giới thiệu thông tin nhóm
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
            st.markdown("- Interactive dashboards and charts\n- User demographic analysis\n- Social media engagement insights\n- Lifestyle and behavioral pattern exploration\n- Data filtering and visualization tools\n- Machine learning and statistical analysis support")
        with intro_col2:
            st.markdown("#### 🎯 Purpose")
            st.markdown("The platform is built for:\n- Data analysis practice\n- Academic and research purposes\n- Machine learning projects\n- Data visualization learning\n- Social media behavior exploration")
            
    st.markdown("---")

    # 4. TẠO THANH BỘ LỌC AN TOÀN TRÊN SIDEBAR
    st.sidebar.header("GLOBAL FILTERS")
    st.sidebar.markdown("Select conditions to update the dashboard:")
    
    gender_list = ["All"] + list(df["gender"].dropna().unique()) if "gender" in df.columns else ["All"]
    filter_gender = st.sidebar.selectbox("👤 1. User Gender:", gender_list)

    children_list = ["All"] + list(df["has_children"].dropna().unique()) if "has_children" in df.columns else ["All"]
    filter_children = st.sidebar.selectbox("🏡 2. Parental Status:", children_list)
    
    diet_list = ["All"] + list(df["diet_quality"].dropna().unique()) if "diet_quality" in df.columns else ["All"]
    filter_diet = st.sidebar.selectbox("🥗 3. Diet Quality:", diet_list)
    
    min_steps = int(df["daily_steps_count"].min()) if "daily_steps_count" in df.columns else 0
    max_steps = int(df["daily_steps_count"].max()) if "daily_steps_count" in df.columns else 20000
    filter_steps = st.sidebar.slider("👟 4. Daily Steps Range:", min_steps, max_steps, (min_steps, max_steps))
    
    # Thực hiện lọc dữ liệu dựa theo sidebar
    df_filtered = df.copy()
    if filter_gender != "All" and "gender" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["gender"] == filter_gender]
    if filter_children != "All" and "has_children" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["has_children"] == filter_children]
    if filter_diet != "All" and "diet_quality" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["diet_quality"] == filter_diet]
    if "daily_steps_count" in df_filtered.columns:
        df_filtered = df_filtered[(df_filtered["daily_steps_count"] >= filter_steps[0]) & (df_filtered["daily_steps_count"] <= filter_steps[1])]

    st.sidebar.metric("Sample Count:", f"{len(df_filtered):,}")
    
    # 5. VẼ CÁC BIỂU ĐỒ
    if df_filtered.empty:
        st.warning("No users match the selected filters. Please adjust your criteria.")
    else:
        # ---- PART 1 ----
        st.markdown("## Part 1: Demographics & Family")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### User Distribution by Gender")
            if "gender" in df_filtered.columns and not df_filtered["gender"].value_counts().empty:
                gender_counts = df_filtered["gender"].value_counts()
                fig, ax = plt.subplots(figsize=(8, 5))
                ax.pie(gender_counts.values, colors=plt.get_cmap("Pastel1").colors, startangle=90, wedgeprops=dict(width=0.4, edgecolor="white"), autopct='%1.1f%%')
                ax.legend([f"{g} ({n:,})" for g, n in zip(gender_counts.index, gender_counts.values)], loc="center left", bbox_to_anchor=(1, 0.5))
                st.pyplot(fig)
                plt.close(fig)
            else:
                st.info("Gender chart is stationary because a single gender filter is active.")

        with col2:
            st.markdown("#### Proportion of Users with Children")
            if "has_children" in df_filtered.columns and not df_filtered["has_children"].value_counts().empty:
                counts_child = df_filtered["has_children"].value_counts()
                fig, ax = plt.subplots(figsize=(8, 5))
                ax.pie(counts_child.values, autopct='%1.0f%%', colors=["#87C5FF", "#F8EBA3"], startangle=90)
                ax.legend(counts_child.index.astype(str), title="Has Children?", loc="center left", bbox_to_anchor=(1, 0.5))
                st.pyplot(fig)
                plt.close(fig)
            else:
                st.info("Children chart is stationary because a single status filter is active.")

        st.markdown("---")

        # ---- PART 2 ----
        st.markdown("## Part 2: Health & Physical Status")
        col3, col4 = st.columns(2)
        
        with col3:
            st.markdown("#### Distribution of Daily Steps Count")
            if "daily_steps_count" in df_filtered.columns:
                fig, ax = plt.subplots(figsize=(8, 5))
                ax.hist(df_filtered["daily_steps_count"].dropna(), bins=25, color="#B2E2F2", edgecolor="white")
                ax.set_xlabel("Daily Steps")
                ax.set_ylabel("Number of Users")
                st.pyplot(fig)
                plt.close(fig)

            st.markdown("#### Distribution of Body Mass Index (BMI)")
            if "body_mass_index" in df_filtered.columns and not df_filtered["body_mass_index"].dropna().empty:
                bmi = df_filtered["body_mass_index"].dropna()
                counts_bmi, edges = np.histogram(bmi, bins=40)
                centers = (edges[:-1] + edges[1:]) / 2
                fig, ax = plt.subplots(figsize=(8, 5))
                ax.fill_between(centers, counts_bmi, color="#B2E2F2", alpha=0.6)
                ax.plot(centers, counts_bmi, color="#82C0D1", linewidth=2)
                ax.set_xlabel("BMI Value")
                st.pyplot(fig)
                plt.close(fig)

        with col4:
            st.markdown("#### Comparison of Systolic Blood Pressure by Gender")
            if "gender" in df_filtered.columns and "blood_pressure_systolic" in df_filtered.columns:
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
                
                # CHỖ ĐÃ SỬA LỖI: Nhét hàm viết số liệu vào đây để nó chạy an toàn tuyệt đối
                for idx, val in enumerate(counts_diet.values):
                    ax.text(idx, val + (max(counts_diet.values)*0.02), f'{int(val):,}', va='bottom', ha='center', fontsize=10, fontweight='bold', color='#4a4a4a')
                st.pyplot(fig)
                plt.close(fig)

        st.markdown("---")

        # ---- PART 3 ----
        st.markdown("## Part 3: Lifestyle & Habits")
        col5, col6 = st.columns(2)
        
        with col5:
            st.markdown("#### Sleep Hours Per Night Distribution")
            if "sleep_hours_per_night" in df_filtered.columns and not df_filtered["sleep_hours_per_night"].dropna().empty:
                sleep_data = df_filtered["sleep_hours_per_night"].dropna()
                bins = np.arange(2, 11, 0.5)
                counts_sleep, edges = np.histogram(sleep_data, bins=bins)
                centers = (edges[:-1] + edges[1:]) / 2
                fig, ax = plt.subplots(figsize=(8, 5))
                ax.plot(centers, counts_sleep, color="steelblue", linewidth=2.5)
                ax.set_xlabel("Sleep Hours")
                st.pyplot(fig)
                plt.close(fig)

            st.markdown("#### Annual Travel Frequency Analysis")
            if "travel_frequency_per_year" in df_filtered.columns and not df_filtered["travel_frequency_per_year"].value_counts().empty:
                df_travel = df_filtered["travel_frequency_per_year"].value_counts().sort_index()
                fig, ax = plt.subplots(figsize=(8, 5))
                ax.plot(df_travel.index, df_travel.values, marker='o', color="#FBB4AE", linewidth=2)
                ax.fill_between(df_travel.index, df_travel.values, alpha=0.1, color="#FBB4AE")
                ax.set_xlabel("Trips per Year")
                st.pyplot(fig)
                plt.close(fig)

        with col6:
            st.markdown("#### Distribution of Books Read Per Year")
            if "books_read_per_year" in df_filtered.columns:
                fig, ax = plt.subplots(figsize=(8, 5))
                ax.hist(df_filtered["books_read_per_year"].dropna(), bins=20, color="#D2B7EA", edgecolor="white")
                ax.set_xlabel("Books Read")
                st.pyplot(fig)
                plt.close(fig)

            st.markdown("#### Distribution of Volunteer Hours")
            if "volunteer_hours_per_month" in df_filtered.columns and not df_filtered["volunteer_hours_per_month"].dropna().empty:
                v_hours = df_filtered["volunteer_hours_per_month"].dropna()
                fig, ax = plt.subplots(figsize=(8, 5))
                sns.histplot(v_hours, bins=25, kde=True, color="firebrick", ax=ax)
                ax.set_xlabel("Hours per Month")
                st.pyplot(fig)
                plt.close(fig)
else:
    st.warning("Vui lòng kiểm tra lại kết nối file dữ liệu.")

# 6. GỘP TOÀN BỘ ĐỐNG CSS TRANG TRÍ PASTEL VÀO CUỐI FILE (MƯỢT MÀ, KHÔNG LỖI)
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
            background-color: #e8f5e9 !important;
            border-right: 2px solid #c8e6c9 !important;
        }
        [data-testid="stSidebar"] .stMarkdown h1, [data-testid="stSidebar"] .stMarkdown h2 {
            font-family: 'Quicksand', sans-serif !important;
            color: #2E5A61 !important;
        }
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
        div[data-baseweb="slider"] > div { background-color: #ffe5ec !important; }
        div[role="slider"] {
            background-color: #ff718a !important;
            border: 2px solid #ffffff !important;
        }
        h1 {
            font-family: 'Quicksand', sans-serif !important;
            font-weight: 700 !important;
            color: #1e464d !important;
            font-size: 2.5rem !important;
            border-bottom: 3px solid #ffccd5;
            padding-bottom: 10px;
        }
        h2, h3 {
            font-family: 'Quicksand', sans-serif !important;
            color: #2c5259 !important;
            font-weight: 700 !important;
            border-left: 6px solid #ffb3c1 !important;
            padding-left: 12px !important;
            margin-top: 30px !important;
        }
        [data-testid="stSidebar"] div[data-testid="stMetric"] {
            background-color: #e0f7fa !important;
            padding: 18px !important;
            border-radius: 16px !important;
            border: 2px dashed #00e5ff !important;
            box-shadow: 0 4px 15px rgba(0, 229, 255, 0.2) !important;
        }
        [data-testid="stSidebar"] div[data-testid="stMetric"] label {
            color: #00838f !important;
            font-weight: bold !important;
        }
        [data-testid="stSidebar"] div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            color: #00b8d4 !important;
            font-weight: 800 !important;
        }
        div[data-testid="stExpander"] {
            background-color: #ffffff !important;
            border: 1px solid #ffe5ec !important;
            border-radius: 16px !important;
            box-shadow: 0 6px 15px rgba(255, 179, 193, 0.1) !important;
        }
    </style>
""", unsafe_allow_html=True)
