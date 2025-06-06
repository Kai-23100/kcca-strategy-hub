import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from bs4 import BeautifulSoup
from datetime import date, datetime

# ----------------- App Configuration -----------------
st.set_page_config(
    page_title="KCCA Strategy Hub",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- Utility: Scrape Departments -----------------
@st.cache_data(ttl=86400)
def fetch_kcca_departments():
    url = "https://www.kcca.go.ug/departments"
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        # Try to find all department names in the KCCA departments page
        depts = []
        for div in soup.find_all("div", {"class": "panel-group"}):
            for panel in div.find_all("div", {"class": "panel"}):
                title = panel.find("h4", {"class": "panel-title"})
                if title:
                    dept_name = title.get_text(strip=True)
                    depts.append(dept_name)
        # Fallback for alternate HTML structure
        if not depts:
            depts = [h4.get_text(strip=True) for h4 in soup.find_all("h4")]
        # Remove duplicates and blanks
        depts = sorted(set([d for d in depts if d.strip()]))
        return depts
    except Exception:
        # Fallback: hardcoded
        return [
            "Directorate of Engineering and Technical Services",
            "Directorate of Public Health and Environment",
            "Directorate of Education and Social Services",
            "Directorate of Treasury Services",
            "Directorate of Revenue Collection",
            "Directorate of Human Resource and Administration",
            "Directorate of Internal Audit",
            "Directorate of Legal Affairs",
            "Directorate of Gender, Community Services and Production",
            "Directorate of Strategy, Research and Performance"
        ]

DEPARTMENTS = fetch_kcca_departments()

# ----------------- Static: NDP III Programmes -----------------
NDP_PROGRAMMES = [
    "Integrated Transport Infrastructure and Services",
    "Sustainable Urban Development",
    "Human Capital Development",
    "Community Mobilization and Mindset Change",
    "Natural Resources, Environment, Climate Change, Land and Water Management",
    "Private Sector Development",
    "Digital Transformation",
    "Innovation, Technology Development",
    "Governance and Security",
    "Public Sector Transformation",
    "Sustainable Energy Development",
    "Tourism Development",
    "Regional Development"
]

# ----------------- Session State for Data -----------------
def init_df(key, columns):
    if key not in st.session_state:
        st.session_state[key] = pd.DataFrame(columns=columns)

init_df("kpi_data", ["Department", "KPI", "Target", "Current", "Status", "NDP Programme"])
init_df("weekly_eval", ["Department", "Directorate", "Week", "Score"])
init_df("projects_df", ["Project", "Department", "NDP Programme", "Status", "Due Date"])
init_df("risks_df", ["Department", "Issue", "Urgency", "Date"])
init_df("budget_df", ["Department", "Budget", "Expenditure", "Variance"])
init_df("documents", ["Name", "Type", "Uploaded By", "Date", "Notes"])

# ----------------- Simple Authentication (Session Only) -----------------
with st.sidebar:
    st.markdown("## User Login")
    username = st.text_input("Username", value="", max_chars=30, key="user")
    role = st.selectbox("Role", ["Strategy Officer", "Admin", "Viewer"], key="role")
    st.markdown("---")
    menu = st.radio(
        "📑 **Navigate**",
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
    st.markdown("---")
    st.caption(f"Logged in as: **{username or 'Anonymous'}** ({role})")

# ----------------- Strategic Plan Tracker -----------------
def strategic_plan_tracker():
    st.header("📈 Strategic Plan Tracker")
    kpi_data = st.session_state["kpi_data"]
    st.write(
        "Monitor, add, and update KPIs for all KCCA departments, aligned to NDP III programmes."
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
        st.dataframe(kpi_data, use_container_width=True)
    else:
        st.info("No KPI data available yet.")

    if role in ["Admin", "Strategy Officer"]:
        st.subheader("Add or Update KPI")
        with st.form("update_kpi", clear_on_submit=True):
            dept = st.selectbox("Department", DEPARTMENTS)
            kpi = st.text_input("KPI Name")
            ndp_prog = st.selectbox("NDP Programme", NDP_PROGRAMMES)
            target = st.number_input("Target Value", min_value=0)
            current = st.number_input("Current Value", min_value=0)
            status = st.selectbox("Status", ["Green", "Amber", "Red"])
            submit = st.form_submit_button("Submit KPI")
            if submit and kpi:
                df = st.session_state["kpi_data"]
                idx = df[(df["Department"] == dept) & (df["KPI"] == kpi)].index
                if len(idx):
                    df.loc[idx, ["Target", "Current", "Status", "NDP Programme"]] = [
                        target, current, status, ndp_prog
                    ]
                else:
                    new_row = pd.DataFrame([{
                        "Department": dept,
                        "KPI": kpi,
                        "Target": target,
                        "Current": current,
                        "Status": status,
                        "NDP Programme": ndp_prog
                    }])
                    df = pd.concat([df, new_row], ignore_index=True)
                st.session_state["kpi_data"] = df
                st.success("KPI added or updated!")

# ----------------- Weekly Evaluation -----------------
def weekly_evaluation():
    st.header("📅 Weekly Evaluation of Directorates & Departments")
    weekly_eval = st.session_state["weekly_eval"]
    st.write("Track and report weekly performance for directorates and departments.")
    dept = st.selectbox("Department", DEPARTMENTS)
    directorate = st.text_input("Directorate", value="", key="dir_eval")
    filtered = weekly_eval[
        (weekly_eval["Department"] == dept) & (weekly_eval["Directorate"] == directorate)
    ] if not weekly_eval.empty else pd.DataFrame()

    if not filtered.empty:
        st.line_chart(filtered.set_index("Week")["Score"])
        st.dataframe(filtered, use_container_width=True)
    else:
        st.info("No data for this department/directorate yet.")

    if role in ["Admin", "Strategy Officer"]:
        st.subheader("Add Weekly Evaluation")
        with st.form("add_weekly_eval", clear_on_submit=True):
            score = st.number_input("Weekly Score", min_value=0, max_value=100)
            week = st.date_input("Week", value=date.today())
            submit = st.form_submit_button("Add Evaluation")
            if submit:
                new_row = pd.DataFrame([{
                    "Department": dept,
                    "Directorate": directorate,
                    "Week": str(week),
                    "Score": score
                }])
                weekly_eval = pd.concat([weekly_eval, new_row], ignore_index=True)
                st.session_state["weekly_eval"] = weekly_eval
                st.success("Weekly evaluation added.")

# ----------------- Performance Dashboard -----------------
def performance_dashboard():
    st.header("📊 Performance Dashboard")
    kpi_data = st.session_state["kpi_data"]

    if not kpi_data.empty:
        st.subheader("Average Departmental Performance")
        perf_agg = kpi_data.groupby("Department")["Current"].mean().reset_index()
        st.bar_chart(perf_agg.set_index("Department"))

        st.subheader("NDP Programme KPI Coverage")
        ndp_agg = kpi_data.groupby("NDP Programme").size().sort_values(ascending=False)
        st.bar_chart(ndp_agg)
    else:
        st.info("No KPI data to show performance.")

# ----------------- NDP Alignment -----------------
def ndp_alignment():
    st.header("🎯 KCCA Alignment to NDP III Programmes")
    kpi_data = st.session_state["kpi_data"]
    st.write("Overview of alignment to the 13 NDP III Programmes.")
    st.dataframe(pd.DataFrame({"NDP Programme": NDP_PROGRAMMES}), use_container_width=True)
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
        st.dataframe(ndp_fulfillment, use_container_width=True)
    else:
        st.info("No KPI data for NDP alignment.")

# ----------------- Project Management -----------------
def project_management():
    st.header("📋 Project Management")
    projects_df = st.session_state["projects_df"]
    st.write("Manage projects, assign to departments, and track status.")
    if not projects_df.empty:
        st.dataframe(projects_df, use_container_width=True)
    else:
        st.info("No projects found.")

    if role in ["Admin", "Strategy Officer"]:
        st.subheader("Add New Project")
        with st.form("add_project", clear_on_submit=True):
            proj = st.text_input("Project Title")
            dept = st.selectbox("Department", DEPARTMENTS, key="proj_dept")
            ndp_prog = st.selectbox("NDP Programme", NDP_PROGRAMMES, key="proj_ndp")
            status = st.selectbox("Status", ["Not Started", "In Progress", "Completed", "Stalled"])
            due = st.date_input("Due Date", value=date.today(), key="proj_due")
            submit = st.form_submit_button("Add Project")
            if submit and proj:
                new_row = pd.DataFrame([{
                    "Project": proj,
                    "Department": dept,
                    "NDP Programme": ndp_prog,
                    "Status": status,
                    "Due Date": str(due)
                }])
                projects_df = pd.concat([projects_df, new_row], ignore_index=True)
                st.session_state["projects_df"] = projects_df
                st.success("Project added.")

# ----------------- Risk Reporting -----------------
def risk_reporting():
    st.header("🚨 Risk & Bottleneck Reporting")
    risks_df = st.session_state["risks_df"]
    st.write("Report and view risks and operational bottlenecks.")
    if not risks_df.empty:
        st.dataframe(risks_df, use_container_width=True)
    else:
        st.info("No risks reported yet.")
    if role in ["Admin", "Strategy Officer"]:
        st.subheader("Report a New Risk or Bottleneck")
        with st.form("risk_form", clear_on_submit=True):
            dept = st.selectbox("Reporting Department", DEPARTMENTS, key="risk_dept")
            issue = st.text_area("Describe the issue or risk")
            urgency = st.selectbox("Urgency", ["Low", "Medium", "High", "Critical"])
            submit = st.form_submit_button("Submit Report")
            if submit and issue:
                new_row = pd.DataFrame([{
                    "Department": dept,
                    "Issue": issue,
                    "Urgency": urgency,
                    "Date": datetime.now().isoformat(timespec="seconds")
                }])
                risks_df = pd.concat([risks_df, new_row], ignore_index=True)
                st.session_state["risks_df"] = risks_df
                st.success("Risk reported.")

# ----------------- Budget Monitoring -----------------
def budget_monitoring():
    st.header("💰 Budget Monitoring")
    budget_df = st.session_state["budget_df"]
    st.write("Monitor and report budgeting and expenditure.")

    if not budget_df.empty:
        st.dataframe(budget_df, use_container_width=True)
        st.bar_chart(budget_df.set_index("Department")["Expenditure"])
    else:
        st.info("No budget data yet.")

    if role in ["Admin", "Strategy Officer"]:
        st.subheader("Add Budget Data")
        with st.form("add_budget", clear_on_submit=True):
            dept = st.selectbox("Department", DEPARTMENTS, key="budget_dept")
            budget = st.number_input("Approved Budget (UGX)", min_value=0)
            expenditure = st.number_input("Expenditure (UGX)", min_value=0)
            variance = budget - expenditure
            submit = st.form_submit_button("Add Budget Data")
            if submit:
                new_row = pd.DataFrame([{
                    "Department": dept,
                    "Budget": budget,
                    "Expenditure": expenditure,
                    "Variance": variance
                }])
                budget_df = pd.concat([budget_df, new_row], ignore_index=True)
                st.session_state["budget_df"] = budget_df
                st.success("Budget data added.")

# ----------------- Document Repository -----------------
def document_repository():
    st.header("📁 Strategy Document Repository")
    docs = st.session_state["documents"]
    st.write("Upload and view strategy documents and reports (demo only, not persistent).")
    if not docs.empty:
        st.dataframe(docs, use_container_width=True)

    uploaded_file = st.file_uploader("Upload document (PDF, DOCX, XLSX)", type=["pdf", "docx", "xlsx"])
    notes = st.text_area("Notes (describe document purpose, content, etc.)")
    if uploaded_file and role in ["Admin", "Strategy Officer"]:
        # "Storing" the file info only; real storage would save to S3, GDrive, etc.
        doc_type = uploaded_file.type
        new_row = pd.DataFrame([{
            "Name": uploaded_file.name,
            "Type": doc_type,
            "Uploaded By": username or "Anonymous",
            "Date": datetime.now().isoformat(timespec="seconds"),
            "Notes": notes
        }])
        docs = pd.concat([docs, new_row], ignore_index=True)
        st.session_state["documents"] = docs
        st.success(f"File '{uploaded_file.name}' uploaded! (Demo only, not stored)")

# ----------------- MAIN APP FLOW -----------------
if menu == "Strategic Plan Tracker":
    strategic_plan_tracker()
elif menu == "Weekly Evaluation":
    weekly_evaluation()
elif menu == "Performance Dashboard":
    performance_dashboard()
elif menu == "NDP Alignment":
    ndp_alignment()
elif menu == "Project Management":
    project_management()
elif menu == "Risk Reporting":
    risk_reporting()
elif menu == "Budget Monitoring":
    budget_monitoring()
elif menu == "Document Repository":
    document_repository()

# ----------------- App Footer -----------------
st.markdown("---")
st.caption(
    "KCCA Strategy Hub | Streamlit Demo (In-memory, not persistent). "
    "Developed for professional Monitoring, Evaluation & Reporting across KCCA directorates. "
    f"Session started on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)
