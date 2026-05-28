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
        
        # Chia làm 2 cột cho đẹp mắt
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
    
    gender_list = ["All"] + list(df["gender"].dropna().unique())
    filter_gender = st.sidebar.selectbox("👤 1. User Gender:", gender_list)

    children_list = ["All"] + list(df["has_children"].dropna().unique())
    filter_children = st.sidebar.selectbox("🏡 2. Parental Status:", children_list)
    
    diet_list = ["All"] + list(df["diet_quality"].dropna().unique())
    filter_diet = st.sidebar.selectbox("🥗 3. Diet Quality:", diet_list)
    
    min_steps = int(df["daily_steps_count"].min()) if "daily_steps_count" in df.columns else 0
    max_steps = int(df["daily_steps_count"].max()) if "daily_steps_count" in df.columns else 20000
    filter_steps = st.sidebar.slider("👟 4. Daily Steps Range:", min_steps, max_steps, (min_steps, max_steps))
    df_filtered = df.copy()
    
    if filter_gender != "All":
        df_filtered = df_filtered[df_filtered["gender"] == filter_gender]
    if filter_children != "All":
        df_filtered = df_filtered[df_filtered["has_children"] == filter_children]
    if filter_diet != "All" and "diet_quality" in df.columns:
        df_filtered = df_filtered[df_filtered["diet_quality"] == filter_diet]
    if "daily_steps_count" in df.columns:
        df_filtered = df_filtered[
            (df_filtered["daily_steps_count"] >= filter_steps[0]) & 
            (df_filtered["daily_steps_count"] <= filter_steps[1])
        ]

    st.sidebar.metric("Sample Count:", f"{len(df_filtered):,}")
    
    if df_filtered.empty:
        st.warning("No users match the selected filters. Please adjust your criteria.")
    else:
        st.markdown("## Part 1: Demographics & Family")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### User Distribution by Gender")
            gender_counts = df_filtered["gender"].value_counts()
            if not gender_counts.empty:
                fig, ax = plt.subplots(figsize=(8, 5))
                ax.pie(
                    gender_counts.values,
                    colors=plt.get_cmap("Pastel1").colors,
                    startangle=90,
                    wedgeprops=dict(width=0.4, edgecolor="white"),
                    autopct='%1.1f%%'
                )
                ax.legend([f"{g} ({n:,})" for g, n in zip(gender_counts.index, gender_counts.values)], loc="center left", bbox_to_anchor=(1, 0.5))
                st.pyplot(fig)
                plt.close(fig)
            else:
                st.info("Gender chart is stationary because a single gender filter is active.")

        with col2:
            st.markdown("#### Proportion of Users with Children")
            counts_child = df_filtered["has_children"].value_counts()
            if not counts_child.empty:
                fig, ax = plt.subplots(figsize=(8, 5))
                ax.pie(counts_child.values, autopct='%1.0f%%', colors=["#87C5FF", "#F8EBA3"], startangle=90)
                ax.legend(counts_child.index.astype(str), title="Has Children?", loc="center left", bbox_to_anchor=(1, 0.5))
                st.pyplot(fig)
                plt.close(fig)
            else:
                st.info("Children chart is stationary because a single status filter is active.")

        st.markdown("---")

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
                st.pyplot(fig)
                plt.close(fig)

        st.markdown("---")

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
    # --- ĐOẠN CODE ĐỔI MÀU GIAO DIỆN PASTEL RỰC RỠ HƠN ---
st.markdown("""
    <style>
        /* 1. Đổi màu nền chính của trang (Màu kem sữa pastel cực mịn) */
        .main {
            background-color: #fcf8f5;
            color: #4A4A4A;
        }
        
        /* 2. Đổi màu thanh Sidebar bên trái (Màu xanh Mint pastel tươi mát) */
        [data-testid="stSidebar"] {
            background-color: #e8f5e9;
            border-right: 2px solid #c8e6c9;
        }
        
        /* 3. Làm nổi bật các chữ tiêu đề bằng màu xanh Teal đậm */
        h1 {
            color: #2E5A61 !important;
            font-size: 2.5rem !important;
            border-bottom: 3px solid #ffccd5; /* Đường gạch chân màu hồng pastel */
            padding-bottom: 10px;
        }
        
        h2, h3 {
            color: #3A6B74 !important;
            background: linear-gradient(90s, #fff0f3, transparent); /* Nền highlight nhẹ dưới chữ */
            padding: 5px 10px;
            border-left: 5px solid #ffb3c1; /* Vạch màu hồng bên cạnh tiêu đề */
        }
        
/* 4. Đổi màu ô chọn và tạo hiệu ứng tỏa sáng lấp lánh khi rê chuột */
    [data-testid="stSidebar"] .stSelectbox {
        background-color: #ffffff !important;
        border: 2px solid #b3e5fc !important;
        border-radius: 12px !important;
        transition: all 0.3s ease-in-out !important; /* Tạo độ mượt khi di chuột */
        padding: 5px !important;
    }

    /* KHI DI CHUỘT VÀO: Ô chọn phát sáng ánh hồng pastel lung linh lấp lánh */
    [data-testid="stSidebar"] .stSelectbox:hover {
        border-color: #ffb3c1 !important;
        background-color: #fff9fa !important;
        box-shadow: 0 0 15px rgba(255, 179, 193, 0.8), 0 0 5px rgba(179, 229, 252, 0.5) !important; /* Ánh hào quang lấp lánh */
        transform: scale(1.02) !important; /* Ô hơi phóng to nhẹ cực kỳ thích mắt */
    }

    /* Hiệu ứng lấp lánh cho thanh trượt Slider */
    div[role="slider"] {
        background-color: #ff718a !important;
        border: 2px solid #ffffff !important;
        transition: all 0.3s ease !important;
    }
    div[role="slider"]:hover {
        box-shadow: 0 0 15px #ff718a !important;
        transform: scale(1.2) !important;
    }
}
        
 /* 5. Làm nổi bật con số tổng "Sample Count" thành hộp màu XANH NEON / MINT lung linh */
    [data-testid="stSidebar"] div[data-testid="stMetric"] {
        background-color: #e0f7fa !important; /* Màu nền xanh mint pastel dịu mát */
        padding: 18px !important;
        border-radius: 16px !important; /* Bo góc dễ thương */
        text-align: center !important;
        box-shadow: 0 4px 15px rgba(0, 229, 255, 0.2) !important; /* Bóng đổ neon nhẹ */
        border: 2px dashed #00e5ff !important; /* Viền nét đứt màu xanh neon phát sáng */
        transition: all 0.3s ease-in-out !important;
    }

    /* Hiệu ứng khi rê chuột vào: Hộp phát sáng neon mạnh hơn và nhún nhảy */
    [data-testid="stSidebar"] div[data-testid="stMetric"]:hover {
        transform: translateY(-3px) scale(1.03) !important;
        background-color: #b2ebf2 !important; /* Nền xanh đậm hơn một xíu khi hover */
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.6), 0 0 8px rgba(179, 229, 252, 0.4) !important; /* Tỏa hào quang xanh neon */
    }

    /* Định dạng lại chữ tiêu đề bên trong */
    [data-testid="stSidebar"] div[data-testid="stMetric"] label {
        color: #00838f !important; /* Màu chữ tiêu đề xanh Teal đậm cho dễ đọc */
        font-weight: bold !important;
        font-size: 1.1rem !important;
    }

    /* Định dạng lại con số chính màu xanh neon đậm cực kỳ nổi bật */
    [data-testid="stSidebar"] div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #00b8d4 !important; /* Con số màu xanh neon cực kỳ rực rỡ */
        font-weight: 800 !important;
        font-size: 2.2rem !important;
    }
        
        /* 6. Trang trí lại cái hộp "About Instagram User Analysis" */
        .stDetails {
            border: 2px solid #ffd6ff !important; /* Viền tím pastel */
            border-radius: 12px !important;
            background-color: #fff0f3 !important; /* Nền hồng siêu nhẹ */
        }
    </style>
""", unsafe_allow_html=True)
# --- ĐOẠN CODE LỘT XÁC GIAO DIỆN: FONT ĐẸP + MÀU PASTEL XỊN ---
st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;600;700&family=Quicksand:wght@500;700&display=swap" rel="stylesheet">

    <style>
        /* 1. Đổi toàn bộ font chữ trên trang và màu nền chính (Màu kem hồng pastel cực nghệ) */
        html, body, [data-testid="stAppViewContainer"], .main {
            font-family: 'Be Vietnam Pro', sans-serif !important;
            background-color: #fff9f6 !important;
        }
        
        /* 2. Trang trí thanh Sidebar bên trái (Màu xanh Mint pastel) */
        [data-testid="stSidebar"] {
            background-color: #f0f7f4 !important;
            border-right: 2px solid #e1efe6 !important;
        }
        
        /* Đổi font riêng cho các chữ lớn ở Sidebar */
        [data-testid="stSidebar"] .stMarkdown h1, [data-testid="stSidebar"] .stMarkdown h2 {
            font-family: 'Quicksand', sans-serif !important;
            color: #2E5A61 !important;
        }

        /* 3. Làm các ô lọc bo tròn rực rỡ, nổi bật trên sidebar */
        div[data-testid="stSelectbox"] {
            background-color: #ffffff !important;
            padding: 8px 12px !important;
            border-radius: 16px !important;
            border: 1px solid #e1efe6 !important;
            box-shadow: 0 4px 10px rgba(46, 90, 97, 0.05) !important;
            margin-bottom: 10px !important;
        }

        /* 4. Thiết kế lại Tiêu đề chính (Font Quicksand to, dày, màu xanh Teal đậm) */
        h1 {
            font-family: 'Quicksand', sans-serif !important;
            font-weight: 700 !important;
            color: #1e464d !important;
            font-size: 2.8rem !important;
            letter-spacing: -0.5px;
        }
        
        /* Thanh gạch ngang trang trí dưới tiêu đề chính */
        .stMarkdown hr {
            border: none !important;
            height: 4px !important;
            background: linear-gradient(90deg, #ffb3c1, #ffe5ec, transparent) !important;
            border-radius: 10px !important;
            margin-top: -10px !important;
            margin-bottom: 25px !important;
        }

        /* 5. Trang trí các tiêu đề nhỏ (Part 1: Demographics,...) */
        h2, h3 {
            font-family: 'Quicksand', sans-serif !important;
            color: #2c5259 !important;
            font-weight: 700 !important;
            border-left: 6px solid #ffb3c1 !important; /* Vạch hồng pastel bên trái tiêu đề */
            padding-left: 12px !important;
            margin-top: 30px !important;
        }

        /* 6. Biến cái hộp "About Instagram User Analysis" thành một cái Card siêu xinh */
        div[data-testid="stExpander"] {
            background-color: #ffffff !important;
            border: 1px solid #ffe5ec !important;
            border-radius: 16px !important;
            box-shadow: 0 6px 15px rgba(255, 179, 193, 0.1) !important;
            overflow: hidden !important;
            padding: 5px !important;
        }
        
        /* Màu chữ tiêu đề bên trong hộp Expander */
        div[data-testid="stExpander"] details summary p {
            font-family: 'Quicksand', sans-serif !important;
            font-weight: 700 !important;
            color: #2c5259 !important;
            font-size: 1.1rem !important;
        }

        /* 7. Bo góc nhẹ cho toàn bộ các hình ảnh/biểu đồ xuất hiện trên trang */
        [data-testid="stImage"], [data-testid="stElementToolbar"] + div {
            border-radius: 16px !important;
            overflow: hidden !important;
        }
    </style>
""", unsafe_allow_html=True)

# Thêm một đường kẻ trang trí ngay dưới tiêu đề chính (để kích hoạt hiệu ứng gradient ở trên)
st.markdown("---")
# --- CODE THÊM SỐ LIỆU LÊN ĐẦU BIỂU ĐỒ DIET QUALITY ---
# Giả sử 'counts' là biến lưu số lượng của từng nhóm (Average, Good, Excellent...)
# Bạn hãy kiểm tra xem trong code của nhóm đang đặt tên biến này là gì để thay thế nhé (ví dụ: diet_counts, counts,...)

for i, val in enumerate(counts):
    ax.text(i, val + 10000, f'{val:,}',      # val + 10000 để chữ nằm dịch lên trên dấu chấm một chút
            va='bottom',                     # Căn chữ nằm bên trên điểm tọa độ
            ha='center',                     # Căn chữ nằm chính giữa cột
            fontsize=10,                     # Cỡ chữ vừa vặn, dễ nhìn
            fontweight='bold',               # In đậm cho rõ ràng
            color='#4a4a4a')                 # Màu chữ xám đậm hài hòa
# -----------------------------------------------------
  
# --- ĐOẠN CODE TRANG TRÍ NÚT BẤM VÀ CÁC Ô LỌC (AN TOÀN 100%) ---
st.markdown("""
    <style>
        /* 1. TRANG TRÍ CÁC Ô CHỌN LỰA (SELECTBOX) */
        /* Tạo viền màu xanh dương pastel và bo tròn góc cho các ô chọn */
        div[data-baseweb="select"] {
            border: 2px solid #b3e5fc !important;
            border-radius: 12px !important;
            background-color: #ffffff !important;
            transition: all 0.2s ease-in-out;
        }
        
        /* Hiệu ứng khi bạn rê chuột vào ô chọn: Đổi sang viền hồng pastel nhẹ */
        div[data-baseweb="select"]:hover {
            border-color: #ffb3c1 !important;
            box-shadow: 0 4px 10px rgba(255, 179, 193, 0.2) !important;
        }

        /* 2. TRANG TRÍ THANH TRƯỢT (SLIDER) */
        /* Đổi màu thanh nền của Slider sang màu hồng pastel nhạt */
        div[data-baseweb="slider"] > div {
            background-color: #ffe5ec !important;
        }
        
        /* Biến cục tròn kéo trên thanh Slider thành màu hồng đậm rực rỡ, nổi bật */
        div[role="slider"] {
            background-color: #ff718a !important;
            border: 2px solid #ffffff !important;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2) !important;
        }

        /* 3. TRANG TRÍ HỘP THÔNG TIN "About Instagram User Analysis" */
        /* Bo tròn góc và thêm viền hồng pastel siêu mảnh cho hộp expander */
        div[data-testid="stExpander"] {
            border: 1px solid #ffe5ec !important;
            border-radius: 12px !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.02) !important;
            background-color: #ffffff !important;
        }
    </style>
""", unsafe_allow_html=True)

