import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Page Configuration
st.set_page_config(page_title="Instagram Data Analytics", layout="wide")
st.title("Instagram User Behavior Analysis")

# 1. Load Data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data.csv", encoding='latin1', sep=';') 
        df.columns = [str(col).lower().strip() for col in df.columns]
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

df = load_data()

# 2. Sidebar Navigation
st.sidebar.header("Navigation")

plot_options = [
    "Gender Distribution",
    "Annual Travel Frequency",
    "Daily Step Count",
    "Blood Pressure Systolic",
    "Sleep Hours per Night",
    "Body Mass Index (BMI)",
    "Books Read Per Year",
    "Volunteer Hours",
    "Number of People with Children",
    "Diet Quality"
]
choice = st.sidebar.selectbox("Select a visualization:", plot_options)

# 3. Main Content Area
if df is not None:
    if choice == "Gender Distribution":
        st.header("User Distribution by Gender")
        
        # Lấy dữ liệu
        gender_counts = df["gender"].value_counts()
        
        
        fig, ax = plt.subplots(figsize=(10, 7))
        
        ax.pie(
            gender_counts.values,
            colors=plt.get_cmap("Pastel1").colors,
            startangle=90,
            wedgeprops=dict(width=0.4, edgecolor="white")
        )
        
        ax.legend(
            [f"{g} ({n:,})" for g, n in zip(gender_counts.index, gender_counts.values)],
            title="Gender Details",
            loc="center left",
            bbox_to_anchor=(1, 0.5)
        )
        
        ax.set_title("Instagram Users Distribution by Gender")
        
        # Đưa lên web
        st.pyplot(fig)
        st.info("Description: This chart shows the distribution of users based on gender.")
    elif choice == "Annual Travel Frequency":
        st.header("Annual Travel Frequency Analysis")
        df_count = df["travel_frequency_per_year"].value_counts().sort_index()
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(df_count.index, df_count.values, marker='o', linewidth=3, color="#FBB4AE")
        ax.fill_between(df_count.index, df_count.values, alpha=0.2, color="#FBB4AE")
        ax.set_title("Travel Habits of Instagram Users")
        ax.set_xlabel("Number of Trips per Year")
        ax.set_ylabel("Total Users")
        st.pyplot(fig)
    elif choice == "Daily Step Count":
        st.header("Daily Step Count Distribution")
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.hist(df["daily_steps_count"].dropna(), 
                bins=30, 
                color="#B2E2F2", 
                edgecolor="white", 
                alpha=0.9)

        ax.set_title("Distribution of Daily Steps Count")
        ax.set_xlabel("Daily Steps")
        ax.set_ylabel("Number of Users")

        st.pyplot(fig)
    elif choice == "Blood Pressure Systolic":
        st.header("Comparison of Systolic Blood Pressure by Gender")
        
        # 1. Tính toán dữ liệu
        avg_bp = df.groupby("gender")["blood_pressure_systolic"].mean()
        
        # 2. Khởi tạo khung hình
        fig, ax = plt.subplots(figsize=(9, 5))
        
        # 3. Vẽ đường kẻ ngang (y, xmin, xmax)
        ax.hlines(y=avg_bp.index, xmin=0, xmax=avg_bp.values, 
                  color="lightgray", linewidth=4)

        # 4. Vẽ điểm tròn tại đầu đường kẻ
        ax.plot(avg_bp.values, avg_bp.index, "o", markersize=15)

        # 5. Vẽ đường giới hạn 120 mmHg
        ax.axvline(x=120, linestyle='--', color="gray")

        # 6. Thiết lập tiêu đề và nhãn trục
        ax.set_title("Comparison of Systolic Blood Pressure by Gender")
        ax.set_xlabel("Average Systolic Blood Pressure (mmHg)")
        ax.set_ylabel("Gender")

        # 7. Hiển thị lên Web
        st.pyplot(fig)
    elif choice == "Sleep Hours per Night":
        st.header("Sleep Hours per Night Distribution")
        
        sleep_data = df["sleep_hours_per_night"].dropna()
        
        bins = np.arange(2, 11, 0.5)
        counts, edges = np.histogram(sleep_data, bins=bins)
        centers = (edges[:-1] + edges[1:]) / 2

        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.plot(centers, counts, color="steelblue", linewidth=2.5)
        
        ax.set_xlim(2, 11)
        ax.set_xticks([2, 4, 6, 8, 10])
        
        ax.set_title("Sleep Hours Per Night")
        ax.set_xlabel("Sleep Hours Per Night")
        ax.set_ylabel("Count of Users")
        
        ax.grid(True, linestyle='-', alpha=0.2)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        st.pyplot(fig)
    elif choice == "Body Mass Index (BMI)":
        st.header("Body Mass Index (BMI) Distribution")
        
        bmi = df["body_mass_index"].dropna()
        
        counts, edges = np.histogram(bmi, bins=60)
        centers = (edges[:-1] + edges[1:]) / 2
        
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.fill_between(centers, counts, color="#B2E2F2", alpha=0.6)
        
        
        ax.plot(centers, counts, color="#82C0D1", linewidth=2)
        
       
        ax.set_title("Distribution of Body Mass Index")
        ax.set_xlabel("BMI Value")
        ax.set_ylabel("Count")
        
        st.pyplot(fig)
    elif choice == "Books Read Per Year":
        st.header("Books Read Per Year Distribution")
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.hist(
            df["books_read_per_year"].dropna(),
            bins=30,
            color="#D2B7EA",
            edgecolor="white"
        )
        
        ax.set_title("Distribution of Books Read Per Year", fontsize=16, fontweight='bold')
        ax.set_xlabel("Books Read Per Year")
        ax.set_ylabel("Number of Users")
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='y', alpha=0.2)
        
        st.pyplot(fig)
    elif choice == "Volunteer Hours":
        st.header("Distribution of Volunteer Hours")
        
        x = df["volunteer_hours_per_month"].dropna()
        fig, ax = plt.subplots(figsize=(8, 5))
        
        sns.histplot(
            x,
            bins=30,
            kde=True,
            color="firebrick",
            ax=ax
        )
        
        ax.set_title("Distribution of Volunteer Hours", fontsize=14, fontweight="bold")
        ax.set_xlabel("Hours per Month")
        ax.set_ylabel("Count")
        
        st.pyplot(fig)
    elif choice == "Number of People with Children":
        st.header("Proportion of Users with Children")
        
        counts = df["has_children"].value_counts()
        colors = ["#87C5FF", "#F8EBA3"]
        fig, ax = plt.subplots(figsize=(7, 6))
        
        wedges, texts, autotexts = ax.pie(
            counts.values,
            autopct='%1.0f%%',
            colors=colors,
            textprops={
                "fontsize": 12,
                "fontweight": "bold"
            }
        )
        
        ax.legend(
            wedges,
            counts.index.astype(str),
            title="Has children",
            loc="center left",
            bbox_to_anchor=(1, 0.5),
            fontsize=11,
            title_fontsize=12
        )
        
        ax.set_title("Proportion of User with children", fontsize=16, fontweight="bold")
        
        st.pyplot(fig)
    elif choice == "Diet Quality":
        st.header("Distribution of Diet Quality among Instagram Users")
        
        order = ["Average", "Good", "Excellent", "Poor", "Very poor"]
        counts = df["diet_quality"].value_counts().reindex(order)
        colors = ["#669DD7", "#FFC285", "#FA9192", "#87EAE1", "#9DD895"]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.vlines(counts.index, 0, counts.values, colors=colors, linewidth=4)
        ax.scatter(counts.index, counts.values, s=700, color=colors, alpha=0.9)
        
        offset = max(counts.values) * 0.1
        for i, v in enumerate(counts.values):
            ax.text(i, v + offset, f"{int(v):,}", ha="center", fontsize=11, fontweight="bold")
            
        ax.set_ylim(0, max(counts.values) * 1.5)
        ax.set_title("Distribution of Diet Quality", fontsize=22, fontweight="bold", pad=20)
        ax.set_xlabel("Diet Quality", fontsize=18)
        ax.set_ylabel("Number of Users", fontsize=18)
        
        ax.tick_params(axis='x', labelsize=14)
        ax.tick_params(axis='y', labelsize=14)
        ax.grid(axis="y", alpha=0.25)
        
        plt.tight_layout()
        st.pyplot(fig)

    else:
        st.info(f"The visualization for **{choice}** is currently being updated.")
else:
    st.warning("Please check if 'data.csv' exists in your project folder.")