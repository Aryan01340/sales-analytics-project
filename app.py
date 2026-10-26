
import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# 1. Configure the page
st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Sales Analytics & Revenue Forecasting")
st.write("Analyze sales, profit, products, and business performance.")

# 2. Upload the dataset
uploaded_file = st.file_uploader(
    "Upload your sales CSV file",
    type=["csv"]
)

if uploaded_file is None:
    st.info("Upload your Superstore CSV file to begin.")
    st.stop()

# 3. Read the CSV file
try:
    df = pd.read_csv(
        BytesIO(uploaded_file.getvalue()),
        encoding="utf-8"
    )
except UnicodeDecodeError:
    uploaded_file.seek(0)
    df = pd.read_csv(
        BytesIO(uploaded_file.getvalue()),
        encoding="latin1"
    )
except Exception as error:
    st.error(f"Could not read the CSV file: {error}")
    st.stop()

# 4. Clean column names
df.columns = df.columns.str.strip()

# Support common column-name variations
column_aliases = {
    "Order Date": ["Order Date", "Order_Date"],
    "Order ID": ["Order ID", "Order_ID"],
    "Sales": ["Sales"],
    "Profit": ["Profit"],
    "Region": ["Region"],
    "Category": ["Category"],
    "Product Name": ["Product Name", "Product_Name"]
}

for standard_name, alternatives in column_aliases.items():
    for column in alternatives:
        if column in df.columns:
            df = df.rename(columns={column: standard_name})
            break

# 5. Check essential columns
required = ["Order Date", "Sales", "Profit", "Region", "Category"]
missing = [col for col in required if col not in df.columns]

if missing:
    st.error(f"Missing required columns: {missing}")
    st.write("Available columns:", df.columns.tolist())
    st.stop()

# 6. Convert columns to the correct data types
df["Order Date"] = pd.to_datetime(
    df["Order Date"], errors="coerce"
)
df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce")
df["Profit"] = pd.to_numeric(df["Profit"], errors="coerce")

# Remove rows that cannot be used for core analysis
df = df.dropna(
    subset=["Order Date", "Sales", "Profit"]
)

if df.empty:
    st.error("No valid sales records were found.")
    st.stop()

# 7. Sidebar filters
st.sidebar.header("Dashboard Filters")

regions = sorted(df["Region"].dropna().unique().tolist())
categories = sorted(df["Category"].dropna().unique().tolist())

selected_regions = st.sidebar.multiselect(
    "Select Region",
    options=regions,
    default=regions
)

selected_categories = st.sidebar.multiselect(
    "Select Category",
    options=categories,
    default=categories
)

filtered_df = df[
    df["Region"].isin(selected_regions)
    & df["Category"].isin(selected_categories)
].copy()

if filtered_df.empty:
    st.warning("No records match your selected filters.")
    st.stop()

# 8. Calculate key performance indicators
total_sales = filtered_df["Sales"].sum()
total_profit = filtered_df["Profit"].sum()

if "Order ID" in filtered_df.columns:
    total_orders = filtered_df["Order ID"].nunique()
else:
    total_orders = len(filtered_df)

profit_margin = (
    total_profit / total_sales * 100
    if total_sales != 0 else 0
)

# 9. Display KPI cards
c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Sales", f"${total_sales:,.2f}")
c2.metric("Total Profit", f"${total_profit:,.2f}")
c3.metric("Total Orders", f"{total_orders:,}")
c4.metric("Profit Margin", f"{profit_margin:.2f}%")

st.divider()

# 10. Monthly sales trend
st.subheader("Monthly Sales Trend")

monthly = (
    filtered_df
    .assign(Month=filtered_df["Order Date"].dt.to_period("M").astype(str))
    .groupby("Month", as_index=False)["Sales"]
    .sum()
)

if not monthly.empty:
    fig_monthly = px.line(
        monthly,
        x="Month",
        y="Sales",
        markers=True,
        title="Sales Over Time"
    )
    st.plotly_chart(fig_monthly, use_container_width=True)

# 11. Sales by category and region
left, right = st.columns(2)

with left:
    st.subheader("Sales by Category")
    category_sales = (
        filtered_df.groupby("Category", as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=False)
    )
    fig_category = px.bar(
        category_sales,
        x="Category",
        y="Sales",
        title="Category Performance"
    )
    st.plotly_chart(fig_category, use_container_width=True)

with right:
    st.subheader("Sales by Region")
    region_sales = (
        filtered_df.groupby("Region", as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=False)
    )
    fig_region = px.bar(
        region_sales,
        x="Region",
        y="Sales",
        title="Regional Performance"
    )
    st.plotly_chart(fig_region, use_container_width=True)

# 12. Top products
if "Product Name" in filtered_df.columns:
    st.subheader("Top 10 Products by Sales")

    top_products = (
        filtered_df.groupby("Product Name", as_index=False)["Sales"]
        .sum()
        .nlargest(10, "Sales")
        .sort_values("Sales")
    )

    fig_products = px.bar(
        top_products,
        x="Sales",
        y="Product Name",
        orientation="h",
        title="Best-Selling Products"
    )
    st.plotly_chart(fig_products, use_container_width=True)

# 13. Display the filtered data
with st.expander("View Filtered Sales Data"):
    st.dataframe(filtered_df, use_container_width=True)

# 14. Download filtered data
csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Filtered Data",
    data=csv_data,
    file_name="filtered_sales_data.csv",
    mime="text/csv"
)

st.caption("Sales Analytics Dashboard | Python + Pandas + Plotly + Streamlit")
