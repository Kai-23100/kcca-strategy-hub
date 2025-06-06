import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
import streamlit_authenticator as stauth
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

# -------------- CONFIGURATION --------------
GOOGLE_SHEET_NAME = "KCCA_Strategy_Hub"
CREDENTIALS_FILE = "service_account.json"

# -------------- AUTHENTICATION --------------
names = ["Admin User", "Strategy Officer"]
usernames = ["admin", "officer"]
# Use bcrypt hashes generated externally for security
hashed_pw = [
    "$2b$12$OfG5IH7Nw5w5VjM9QyU6hO2ddR2pWq8bYfQO0vA4v3xESfF7EKn7u",  # hash for adminpass
    "$2b$12$LkAqKp9S1y6O3w8Q8G3xZe3X4r0nE0E9H9bE9bF4uNfM6hT0nF9jO"   # hash for officerpass
]
authenticator = stauth.Authenticate(
    names, usernames, hashed_pw, "kcca_strategy_hub", "abcdef", cookie_expiry_days=1
)
name, auth_status, username = authenticator.login("Login", "main")

if not auth_status:
    st.warning("Please log in to access the KCCA Strategy Hub.")
    st.stop()
role = "admin" if username == "admin" else "user"
st.sidebar.success(f"Welcome {name}! ({role})")

# -------------- GOOGLE SHEETS CONNECTION --------------
@st.cache_resource(show_spinner=False)
def get_gspread_client():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
    return gspread.authorize(creds)

gc = get_gspread_client()
sh = gc.open(GOOGLE_SHEET_NAME)

def read_sheet(sheet_name):
    ws = sh.worksheet(sheet_name)
    df = pd.DataFrame(ws.get_all_records())
    if df.empty:
        return pd.DataFrame()
    return df

def write_sheet(sheet_name, df):
    ws = sh.worksheet(sheet_name)
    ws.clear()
    ws.update([df.columns.values.tolist()] + df.values.tolist())

# -------------- DATA LOAD --------------
try:
    departments_df = read_sheet("departments")
    kpi_data = read_sheet("kpis")
    weekly_eval = read_sheet("weekly_eval")
    ndp_programmes_df = read_sheet("ndp_programmes")
    projects_df = read_sheet("projects")
    risks_df = read_sheet("risks")
except Exception as e:
    st.error(f"Error loading data from Google Sheets: {e}")
    st.stop()

departments = departments_df["Department"].dropna().tolist() if not departments_df.empty else []
ndp_programmes = ndp_programmes_df["NDP Programme"].dropna().tolist() if not ndp_programmes_df.empty else []

# -------------- SIDEBAR NAVIGATION --------------
st.set_page_config(layout="wide", page_title="KCCA Strategy Hub")
st.title("📊 KCCA Strategy Hub")
st.caption("Role-based strategy, M&E, and project management for KCCA")

menu = st.sidebar.radio(
    "Go to",
    [
        "Strategic Plan Tracker",
        "Weekly Evaluation",
        "Performance Dashboard",
        "NDP Alignment",
        "Project Management",
        "Risk Reporting",
        "Budget Monitoring",
        "Document Repository"
    ]
)

# -------------- STRATEGIC PLAN TRACKER --------------
if menu == "Strategic Plan Tracker":
    st.header("📈 Strategic Plan Tracker")
    st.write(
        "Monitor KPIs for all KCCA departments, aligned to NDP III programmes. "
        "Admins can update or add KPIs. All users can view departmental performance and targets."
    )
    if not kpi_data.empty:
        color_map = {"Green": "#34c759", "Amber": "#ffd60a", "Red": "#ff3b30"}
        fig = px.bar(
            kpi_data,
            x="KPI",
            y="Current",
            color="Status",
            color_discrete_map=color_map,
            hover_data=["Department", "Target", "NDP Programme"],
            barmode="group",
            title="KPI Progress"
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(kpi_data)
    else:
        st.info("No KPI data available yet.")
    if role == "admin":
        st.subheader("Add or Update KPI")
        with st.form("update_kpi"):
            dept = st.selectbox("Department", departments)
            kpi = st.text_input("KPI Name")
            ndp_prog = st.selectbox("NDP Programme", ndp_programmes)
            target = st.number_input("Target", min_value=0, step=1)
            current = st.number_input("Current Value", min_value=0, step=1)
            status = st.selectbox("Status", ["Green", "Amber", "Red"])
            submit = st.form_submit_button("Submit")
            if submit:
                idx = kpi_data[
                    (kpi_data["Department"] == dept) & (kpi_data["KPI"] == kpi)
                ].index if not kpi_data.empty else []
                if len(idx):
                    kpi_data.loc[idx, ["Target", "Current", "Status", "NDP Programme"]] = [
                        target, current, status, ndp_prog
                    ]
                else:
                    kpi_data = pd.concat([kpi_data, pd.DataFrame([{
                        "Department": dept, "KPI": kpi, "Target": target,
                        "Current": current, "Status": status, "NDP Programme": ndp_prog
                    }])], ignore_index=True)
                write_sheet("kpis", kpi_data)
                st.success("KPI updated.")

# -------------- WEEKLY EVALUATION --------------
elif menu == "Weekly Evaluation":
    st.header("📅 Weekly Departmental Evaluation")
    dept = st.selectbox("Department", departments)
    filtered = weekly_eval[weekly_eval["Department"] == dept] if not weekly_eval.empty else pd.DataFrame()
    if not filtered.empty:
        st.line_chart(filtered.set_index("Week")["Score"])
        st.dataframe(filtered)
    else:
        st.info("No data for this department yet.")
    if role == "admin":
        st.subheader("Add Weekly Evaluation")
        with st.form("add_weekly_eval"):
            score = st.number_input("Weekly Score", min_value=0, max_value=100)
            week = st.date_input("Week", value=date.today())
            submit = st.form_submit_button("Add Evaluation")
            if submit:
                new_row = pd.DataFrame([{
                    "Department": dept, "Week": str(week), "Score": score
                }])
                weekly_eval = pd.concat([weekly_eval, new_row], ignore_index=True)
                write_sheet("weekly_eval", weekly_eval)
                st.success("Weekly evaluation added.")

# -------------- PERFORMANCE DASHBOARD --------------
elif menu == "Performance Dashboard":
    st.header("📊 Performance Dashboard")
    if not kpi_data.empty:
        perf_agg = kpi_data.groupby("Department")["Current"].mean().reset_index()
        st.bar_chart(perf_agg.set_index("Department"))
        ndp_agg = kpi_data.groupby("NDP Programme").size().sort_values(ascending=False)
        st.subheader("NDP Programme Coverage")
        st.bar_chart(ndp_agg)
    else:
        st.info("No KPI data to show performance.")

# -------------- NDP ALIGNMENT --------------
elif menu == "NDP Alignment":
    st.header("🎯 KCCA Alignment to NDP III Programmes")
    st.write("Track departmental and project alignment to the 13 NDP III programmes.")
    st.dataframe(ndp_programmes_df)
    if not kpi_data.empty:
        ndp_fulfillment = (
            kpi_data.groupby("NDP Programme")
            .apply(lambda df: (df["Status"] == "Green").sum() / len(df) * 100 if len(df) > 0 else 0)
            .reset_index(name="Fulfillment %")
        )
        fig = px.bar(
            ndp_fulfillment,
            x="NDP Programme",
            y="Fulfillment %",
            title="NDP Programme Fulfillment (%)"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No KPI data for NDP alignment.")

# -------------- PROJECT MANAGEMENT --------------
elif menu == "Project Management":
    st.header("📋 Project Management")
    if not projects_df.empty:
        st.dataframe(projects_df)
    else:
        st.info("No projects found.")
    if role == "admin":
        st.subheader("Add New Project")
        with st.form("add_project"):
            proj = st.text_input("Project Title")
            dept = st.selectbox("Department", departments, key="proj_dept")
            ndp_prog = st.selectbox("NDP Programme", ndp_programmes, key="proj_ndp")
            status = st.selectbox("Status", ["Not Started", "In Progress", "Completed", "Stalled"])
            due = st.date_input("Due Date", value=date.today(), key="proj_due")
            submit = st.form_submit_button("Add Project")
            if submit:
                new_row = pd.DataFrame([{
                    "Project": proj, "Department": dept, "NDP Programme": ndp_prog,
                    "Status": status, "Due Date": str(due)
                }])
                projects_df = pd.concat([projects_df, new_row], ignore_index=True)
                write_sheet("projects", projects_df)
                st.success("Project added.")

# -------------- RISK REPORTING --------------
elif menu == "Risk Reporting":
    st.header("🚨 Risk & Bottleneck Reporting")
    if not risks_df.empty:
        st.dataframe(risks_df)
    st.subheader("Report a new risk/bottleneck")
    with st.form("risk_form"):
        dept = st.selectbox("Reporting Department", departments, key="risk_dept")
        issue = st.text_area("Describe the issue or risk")
        urgency = st.selectbox("Urgency", ["Low", "Medium", "High", "Critical"])
        submit = st.form_submit_button("Submit Report")
        if submit:
            new_row = pd.DataFrame([{
                "Department": dept, "Issue": issue, "Urgency": urgency, "Date": str(date.today())
            }])
            risks_df = pd.concat([risks_df, new_row], ignore_index=True)
            write_sheet("risks", risks_df)
            st.success("Risk reported.")

# -------------- BUDGET MONITORING --------------
elif menu == "Budget Monitoring":
    st.header("💰 Budget Monitoring")
    st.info("Budget monitoring and analysis module coming soon.")

# -------------- DOCUMENT REPOSITORY --------------
elif menu == "Document Repository":
    st.header("📁 Strategy Document Repository")
    st.write("Upload and view strategy documents and reports. (Storage for files not yet implemented in this demo.)")
    uploaded_file = st.file_uploader("Upload document (PDF, DOCX, XLSX)", type=["pdf", "docx", "xlsx"])
    if uploaded_file:
        st.success(f"File uploaded: {uploaded_file.name} (Demo only, not stored!)")
        # For production, save to cloud storage and update a Sheet for metadata

st.markdown("---")
st.caption("KCCA Strategy Hub | Powered by Streamlit & Google Sheets | Demo version")
# hashed_pw = ['$2b$12$...', '$2b$12$...']

st.markdown("---")
st.caption("KCCA Strategy Hub | Powered by Streamlit & Google Sheets | Demo version")
