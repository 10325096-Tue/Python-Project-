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
    st.markdown("---")

    st.sidebar.header("GLOBAL FILTERS")
    st.sidebar.markdown("Select conditions to update the dashboard:")
    
    gender_list = ["All"] + list(df["gender"].dropna().unique())
    filter_gender = st.sidebar.selectbox("1. User Gender:", gender_list)
    
    children_list = ["All"] + list(df["has_children"].dropna().unique())
    filter_children = st.sidebar.selectbox("2. Parental Status:", children_list)
    
    diet_list = ["All"] + list(df["diet_quality"].dropna().unique()) if "diet_quality" in df.columns else ["All"]
    filter_diet = st.sidebar.selectbox("3. Diet Quality:", diet_list)
    
    min_steps = int(df["daily_steps_count"].min()) if "daily_steps_count" in df.columns else 0
    max_steps = int(df["daily_steps_count"].max()) if "daily_steps_count" in df.columns else 20000
    filter_steps = st.sidebar.slider("4. Daily Steps Range:", min_steps, max_steps, (min_steps, max_steps))

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