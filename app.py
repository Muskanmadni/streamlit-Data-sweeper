import streamlit as st
import pandas as pd
import os

from io import BytesIO

st.set_page_config(page_title="Data Sweeper", page_icon=":bar_chart:", layout="wide")
st.title("Data Sweeper")
st.write("This is a simple web app that allows you to upload a dataset and view its contents. You can also view the summary statistics of the dataset and download the dataset.")

uploaded_files = st.file_uploader("Choose a file", type=['csv', 'xlsx'], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_name_no_ext, file_ext = os.path.splitext(file.name)
        file_ext = file_ext.lower()

        if file_ext == ".csv":
            try:
                df = pd.read_csv(file)
            except Exception as e:
                st.error(f"Error reading CSV file: {e}")
                continue
        elif file_ext == ".xlsx":
            try:
                df = pd.read_excel(file)
            except Exception as e:
                st.error(f"Error reading Excel file: {e}")
                continue
        else:
            st.error(f"File type not supported: {file_ext}")
            continue

        file_size_kb = file.size / 1024
        file_size_display = f"{file_size_kb:.2f} KB" if file_size_kb < 1024 else f"{file_size_kb / 1024:.2f} MB"

        st.write(f"File Name: {file.name}")
        st.write(f"File Size: {file_size_display}")

        st.write("Preview the Head of the Dataframe")
        st.dataframe(df.head())

        st.subheader("Data Cleaning Options")
        if st.checkbox(f"Clean Data for {file.name}"):
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Remove Duplicates from {file.name}"):
                    original_rows = len(df)
                    df.drop_duplicates(inplace=True)
                    duplicates_removed = original_rows - len(df)
                    st.write(f"Duplicates Removed: {duplicates_removed}")

            with col2:
                if st.button(f"Fill Missing Values for {file.name}"):
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    if not numeric_cols.empty:
                        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                        st.write("Missing values filled in numeric columns.")
                    else:
                        st.write("No numeric columns found.")

        st.subheader("Select Columns to Keep")
        columns = st.multiselect(f"Choose columns for {file.name}", df.columns, default=df.columns)
        df = df[columns]
        st.dataframe(df.head())

        st.subheader("Data Visualization")
        if st.checkbox(f"Show Visualization for {file.name}"):
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) >= 2:
                st.bar_chart(df[numeric_cols.iloc[:2]])
            else:
                st.write("Insufficient numeric columns for visualization.")

        st.subheader("Conversion Options")
        conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=file.name)
        if st.button(f"Convert {file.name} to {conversion_type}"):
            buffer = BytesIO()
            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                file_name = file_name_no_ext + ".csv"
                mime_type = "text/csv"
            elif conversion_type == "Excel":
                df.to_excel(buffer, index=False)
                file_name = file_name_no_ext + ".xlsx"
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            buffer.seek(0)
            st.download_button(label=f"Click here to download {file_name} as {conversion_type}", data=buffer, file_name=file_name, mime=mime_type)

st.success("")