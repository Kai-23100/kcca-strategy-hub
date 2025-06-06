import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
import streamlit_authenticator as stauth
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date, timedelta

# ---- CONFIGURATION ----
GOOGLE_SHEET_NAME = "KCCA_Strategy_Hub"
CREDENTIALS_FILE = "service_account.json"

# ---- AUTHENTICATION ----
# Replace these with hashed passwords in prod!
names = ['Admin User', 'Strategy Officer']
usernames = ['admin', 'officer']
passwords = ['adminpass', 'officerpass']
hashed_pw = stauth.Hasher(passwords).generate()
authenticator = stauth.Authenticate(names, usernames, hashed_pw, "kcca_hub", "abcdef", cookie_expiry_days=1)
name, auth_status, username = authenticator.login('Login', 'main')

if not auth_status:
    st.warning("Please log in to access the KCCA Strategy Hub.")
    st.stop()
role = "admin" if username == "admin" else "user"
st.sidebar.success(f"Welcome {name}! ({role})")

# ---- GOOGLE SHEETS CONNECTION ----
@st.cache_resource(show_spinner=False)
def get_gspread_client():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
    return gspread.authorize(creds)

gc = get_gspread_client()
sh = gc.open(GOOGLE_SHEET_NAME)

def read_sheet(sheet_name):
    ws = sh.worksheet(sheet_name)
    return pd.DataFrame(ws.get_all_records())

def write_sheet(sheet_name, df):
    ws = sh.worksheet(sheet_name)
    ws.clear()
    ws.update([df.columns.values.tolist()] + df.values.tolist())

# ---- INITIAL DATA LOAD ----
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

departments = departments_df['Department'].tolist()
ndp_programmes = ndp_programmes_df['NDP Programme'].tolist()

# ---- SIDEBAR NAVIGATION ----
st.set_page_config(layout="wide", page_title="KCCA Strategy Hub")
st.title("📊 KCCA Strategy Hub")
st.caption("Role-based strategy management, powered by Streamlit & Google Sheets backend")

menu = st.sidebar.radio("Go to", [
    "Strategic Plan Tracker",
    "Weekly Evaluation",
    "Performance Dashboard",
    "NDP Alignment",
    "Project Management",
    "Risk Reporting",
    "Budget Monitoring",
    "Document Repository"
])

# ---- STRATEGIC PLAN TRACKER ----
if menu == "Strategic Plan Tracker":
    st.header("📈 Strategic Plan Tracker")
    st.write("Monitor KPIs for all KCCA departments, aligned to NDP III programmes.")
    color_map = {'Green': '#34c759', 'Amber': '#ffd60a', 'Red': '#ff3b30'}
    fig = px.bar(
        kpi_data, x='KPI', y='Current', color='Status', color_discrete_map=color_map,
        hover_data=['Department', 'Target', 'NDP Programme'], barmode='group', title='KPI Progress'
    )
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(kpi_data)
    if role == "admin":
        st.subheader("Add or Update KPI")
        with st.form("update_kpi"):
            dept = st.selectbox("Department", departments)
            kpi = st.text_input("KPI Name")
            ndp_prog = st.selectbox("NDP Programme", ndp_programmes)
            target = st.number_input("Target", min_value=0)
            current = st.number_input("Current Value", min_value=0)
            status = st.selectbox("Status", ["Green", "Amber", "Red"])
            submit = st.form_submit_button("Submit")
            if submit:
                # Update or add new row
                idx = kpi_data[(kpi_data['Department']==dept) & (kpi_data['KPI']==kpi)].index
                if len(idx):
                    kpi_data.loc[idx, ['Target','Current','Status','NDP Programme']] = [target,current,status,ndp_prog]
                else:
                    kpi_data = pd.concat([kpi_data, pd.DataFrame([{
                        'Department': dept, 'KPI': kpi, 'Target': target, 'Current': current, 'Status': status, 'NDP Programme': ndp_prog
                    }])], ignore_index=True)
                write_sheet("kpis", kpi_data)
                st.success("KPI updated.")

# ---- WEEKLY EVALUATION ----
elif menu == "Weekly Evaluation":
    st.header("📅 Weekly Departmental Evaluation")
    dept = st.selectbox("Department", departments)
    filtered = weekly_eval[weekly_eval['Department'] == dept]
    if not filtered.empty:
        st.line_chart(filtered.set_index('Week')['Score'])
    else:
        st.info("No data for this department yet.")
    if role == "admin":
        st.subheader("Add Weekly Evaluation")
        with st.form("add_weekly_eval"):
            score = st.number_input("Weekly Score", min_value=0, max_value=100)
            week = st.date_input("Week", value=date.today())
            submit = st.form_submit_button("Add Evaluation")
            if submit:
                new_row = pd.DataFrame([{'Department': dept, 'Week': str(week), 'Score': score}])
                weekly_eval = pd.concat([weekly_eval, new_row], ignore_index=True)
                write_sheet("weekly_eval", weekly_eval)
                st.success("Weekly evaluation added.")

# ---- PERFORMANCE DASHBOARD ----
elif menu == "Performance Dashboard":
    st.header("📊 Performance Dashboard")
    perf_agg = kpi_data.groupby('Department')['Current'].mean().reset_index()
    st.bar_chart(perf_agg.set_index('Department'))
    ndp_agg = kpi_data.groupby('NDP Programme').size()
    st.subheader("NDP Programme Coverage")
    st.bar_chart(ndp_agg)

# ---- NDP ALIGNMENT ----
elif menu == "NDP Alignment":
    st.header("🎯 KCCA Alignment to NDP III Programmes")
    st.dataframe(ndp_programmes_df)
    ndp_fulfillment = kpi_data.groupby('NDP Programme').apply(
        lambda df: (df['Status']=='Green').sum() / len(df) * 100 if len(df) > 0 else 0
    ).reset_index(name='Fulfillment %')
    fig = px.bar(ndp_fulfillment, x='NDP Programme', y='Fulfillment %', title="NDP Programme Fulfillment")
    st.plotly_chart(fig, use_container_width=True)
    if role == "admin":
        st.subheader("Tag KPIs/Projects to NDP Programmes")
        # Already in KPI add/update form above

# ---- PROJECT MANAGEMENT ----
elif menu == "Project Management":
    st.header("📋 Project Management")
    st.dataframe(projects_df)
    if role == "admin":
        st.subheader("Add New Project")
        with st.form("add_project"):
            proj = st.text_input("Project Title")
            dept = st.selectbox("Department", departments)
            ndp_prog = st.selectbox("NDP Programme", ndp_programmes)
            status = st.selectbox("Status", ["Not Started", "In Progress", "Completed", "Stalled"])
            due = st.date_input("Due Date", value=date.today())
            submit = st.form_submit_button("Add Project")
            if submit:
                new_row = pd.DataFrame([{
                    'Project': proj, 'Department': dept, 'NDP Programme': ndp_prog, 'Status': status, 'Due Date': str(due)
                }])
                projects_df = pd.concat([projects_df, new_row], ignore_index=True)
                write_sheet("projects", projects_df)
                st.success("Project added.")

# ---- RISK REPORTING ----
elif menu == "Risk Reporting":
    st.header("🚨 Risk & Bottleneck Reporting")
    st.dataframe(risks_df)
    st.subheader("Report a new risk/bottleneck")
    with st.form("risk_form"):
        dept = st.selectbox("Reporting Department", departments)
        issue = st.text_area("Describe the issue or risk")
        urgency = st.selectbox("Urgency", ["Low", "Medium", "High", "Critical"])
        submit = st.form_submit_button("Submit Report")
        if submit:
            new_row = pd.DataFrame([{
                'Department': dept, 'Issue': issue, 'Urgency': urgency, 'Date': str(date.today())
            }])
            risks_df = pd.concat([risks_df, new_row], ignore_index=True)
            write_sheet("risks", risks_df)
            st.success("Risk reported.")

# ---- BUDGET MONITORING ----
elif menu == "Budget Monitoring":
    st.header("💰 Budget Monitoring")
    st.write("Budget monitoring coming soon. (Extend with new Google Sheet tab and form.)")

# ---- DOCUMENT REPOSITORY ----
elif menu == "Document Repository":
    st.header("📁 Strategy Document Repository")
    st.write("Upload and view strategy documents and reports.")
    uploaded_file = st.file_uploader("Upload document (PDF, DOCX, XLSX)", type=["pdf", "docx", "xlsx"])
    if uploaded_file:
        st.success(f"File uploaded: {uploaded_file.name}")
        # In production, save to cloud storage and store metadata in Google Sheets

st.markdown("---")
st.caption("KCCA Strategy Hub | Powered by Streamlit & Google Sheets | Demo version")
