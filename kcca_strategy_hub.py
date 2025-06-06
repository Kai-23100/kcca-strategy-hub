import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime

# ---------------------- APP CONFIGURATION ----------------------
st.set_page_config(
    page_title="KCCA Strategy Hub",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------- DIRECTORATES & DEPARTMENTS ----------------------
KCCA_DIRECTORATES = [
    "Office of the Executive Director",
    "Administration & Human Resource",
    "Physical Planning",
    "Treasury Services",
    "Engineering & Technical Services",
    "Public Health Services & Environment",
    "Education & Social Services",
    "Legal Affairs",
    "Revenue Collection",
    "Internal Audit",
    "Gender, Community Services & Production",
    "Deputy Executive Director"
]

ED_DEPARTMENTS = [
    "Information & Communication Technology",
    "Public & Corporate Affairs",
    "Procurement & Disposal Unit",
    "Research & Strategy Management"
]

DIRECTORATE_DEPTS_MAP = {
    "Office of the Executive Director": ED_DEPARTMENTS,
    "Administration & Human Resource": ["Administration & Human Resource"],
    "Physical Planning": ["Physical Planning"],
    "Treasury Services": ["Treasury Services"],
    "Engineering & Technical Services": ["Engineering & Technical Services"],
    "Public Health Services & Environment": ["Public Health Services & Environment"],
    "Education & Social Services": ["Education & Social Services"],
    "Legal Affairs": ["Legal Affairs"],
    "Revenue Collection": ["Revenue Collection"],
    "Internal Audit": ["Internal Audit"],
    "Gender, Community Services & Production": ["Gender, Community Services & Production"],
    "Deputy Executive Director": ["Deputy Executive Director"]
}

# ---------------------- NDP III PROGRAMMES ----------------------
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

# ---------------------- SESSION STATE INITIALIZATION ----------------------
def init_df(key, columns, starter_data=None):
    if key not in st.session_state or not isinstance(st.session_state[key], pd.DataFrame):
        if starter_data is not None:
            st.session_state[key] = pd.DataFrame(starter_data)
        else:
            st.session_state[key] = pd.DataFrame(columns=columns)

def make_demo_kpi_data():
    demo = []
    status_cycle = ["Green", "Amber", "Red", "Green"]
    ndp_cycle = NDP_PROGRAMMES * 3
    idx = 0
    # Office of the Executive Director
    for dept in ED_DEPARTMENTS:
        demo.append({
            "Directorate": "Office of the Executive Director",
            "Department": dept,
            "KPI": f"{dept} KPI Example",
            "Target": 100,
            "Current": 90-idx*5,
            "Status": status_cycle[idx % len(status_cycle)],
            "NDP Programme": ndp_cycle[idx % len(ndp_cycle)]
        })
        idx += 1
    for dir_name in [d for d in KCCA_DIRECTORATES if d != "Office of the Executive Director"]:
        demo.append({
            "Directorate": dir_name,
            "Department": dir_name,
            "KPI": f"{dir_name} KPI Example",
            "Target": 100,
            "Current": 85-idx*4,
            "Status": status_cycle[idx % len(status_cycle)],
            "NDP Programme": ndp_cycle[idx % len(ndp_cycle)]
        })
        idx += 1
    return demo

init_df("kpi_data", ["Directorate", "Department", "KPI", "Target", "Current", "Status", "NDP Programme"], starter_data=make_demo_kpi_data())
init_df("weekly_eval", ["Directorate", "Department", "Week", "Score"])
init_df("projects_df", ["Directorate", "Department", "Project", "NDP Programme", "Status", "Due Date"])
init_df("risks_df", ["Directorate", "Department", "Issue", "Urgency", "Date"])
init_df("budget_df", ["Directorate", "Department", "Budget", "Expenditure", "Variance"])
init_df("documents", ["Name", "Type", "Uploaded By", "Date", "Notes"])

# ---------------------- SIDEBAR: AUTH & NAVIGATION ----------------------
with st.sidebar:
    st.title("KCCA Strategy Hub")
    username = st.text_input("Username", value="", max_chars=30, key="user")
    role = st.selectbox("Role", ["Strategy Officer", "Admin", "Viewer"], key="role")
    menu = st.radio(
        "Navigate",
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
    st.caption(f"Logged in as: **{username or 'Anonymous'}** ({role})")

# ---------------------- STRATEGIC PLAN TRACKER ----------------------
def strategic_plan_tracker():
    st.header("📈 Strategic Plan Tracker")
    kpi_data = st.session_state["kpi_data"]
    st.write("Monitor, add, and update KPIs for all KCCA directorates/departments, aligned to NDP III programmes. Officers can fine-tune demo data below.")
    if not kpi_data.empty:
        color_map = {"Green": "#34c759", "Amber": "#ffd60a", "Red": "#ff3b30"}
        fig = px.bar(
            kpi_data,
            x="KPI",
            y="Current",
            color="Status",
            color_discrete_map=color_map,
            hover_data=["Directorate", "Department", "Target", "NDP Programme"],
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
            directorate = st.selectbox("Directorate", KCCA_DIRECTORATES)
            if directorate == "Office of the Executive Director":
                departments = ED_DEPARTMENTS
                dept = st.selectbox("Department", departments)
            else:
                dept = directorate
                st.text_input("Department", value=dept, disabled=True, key="kpi_dept_display")
            kpi = st.text_input("KPI Name")
            ndp_prog = st.selectbox("NDP Programme", NDP_PROGRAMMES)
            target = st.number_input("Target Value", min_value=0)
            current = st.number_input("Current Value", min_value=0)
            status = st.selectbox("Status", ["Green", "Amber", "Red"])
            submit = st.form_submit_button("Submit KPI")
            if submit and kpi:
                df = st.session_state["kpi_data"]
                idx = df[
                    (df["Directorate"] == directorate) &
                    (df["Department"] == (dept if directorate == "Office of the Executive Director" else directorate)) &
                    (df["KPI"] == kpi)
                ].index
                if len(idx):
                    df.loc[idx, ["Target", "Current", "Status", "NDP Programme"]] = [
                        target, current, status, ndp_prog
                    ]
                else:
                    new_row = pd.DataFrame([{
                        "Directorate": directorate,
                        "Department": dept if directorate == "Office of the Executive Director" else directorate,
                        "KPI": kpi,
                        "Target": target,
                        "Current": current,
                        "Status": status,
                        "NDP Programme": ndp_prog
                    }])
                    df = pd.concat([df, new_row], ignore_index=True)
                st.session_state["kpi_data"] = df
                st.success("KPI added or updated!")

# ---------------------- WEEKLY EVALUATION ----------------------
def weekly_evaluation():
    st.header("📅 Weekly Evaluation: Directorate & Department Performance")
    """
    This module allows users to record, review, and visualize weekly performance scores
    for each directorate and department. The system supports continuous performance monitoring,
    trend analysis, and timely interventions for underperforming units.
    """
    weekly_eval = st.session_state["weekly_eval"]
    st.write(
        "Track and report weekly performance for directorates and departments. "
        "Select the relevant directorate and department to view their recent scores and trends."
    )
    directorate = st.selectbox("Directorate", KCCA_DIRECTORATES, key="weekly_dir")
    if directorate == "Office of the Executive Director":
        departments = ED_DEPARTMENTS
        dept = st.selectbox("Department", departments, key="weekly_dept")
    else:
        dept = directorate
        st.text_input("Department", value=dept, disabled=True, key="weekly_dept_display")
    filtered = weekly_eval[
        (weekly_eval["Directorate"] == directorate) & (weekly_eval["Department"] == (dept if directorate == "Office of the Executive Director" else directorate))
    ] if not weekly_eval.empty else pd.DataFrame()

    if not filtered.empty:
        st.subheader("Weekly Performance Trend")
        st.line_chart(filtered.set_index("Week")["Score"])
        st.dataframe(filtered, use_container_width=True)
    else:
        st.info("No data for this department/directorate yet.")

    if role in ["Admin", "Strategy Officer"]:
        st.subheader("Add Weekly Evaluation Score")
        with st.form("add_weekly_eval", clear_on_submit=True):
            score = st.number_input("Weekly Score (0-100)", min_value=0, max_value=100)
            week = st.date_input("Week", value=date.today())
            submit = st.form_submit_button("Add Evaluation")
            if submit:
                new_row = pd.DataFrame([{
                    "Directorate": directorate,
                    "Department": dept if directorate == "Office of the Executive Director" else directorate,
                    "Week": str(week),
                    "Score": score
                }])
                weekly_eval = pd.concat([weekly_eval, new_row], ignore_index=True)
                st.session_state["weekly_eval"] = weekly_eval
                st.success("Weekly evaluation added.")

# ---------------------- PERFORMANCE DASHBOARD ----------------------
def performance_dashboard():
    st.header("📊 Organisational Performance Dashboard")
    """
    This dashboard provides a consolidated view of performance across all directorates and departments.
    It visualizes average scores, highlights leading and lagging units, and shows NDP Programme coverage.
    """
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

# ---------------------- NDP ALIGNMENT ----------------------
def ndp_alignment():
    st.header("🎯 KCCA Alignment to NDP III Programmes")
    """
    This module summarizes how KCCA's strategic actions and KPIs align with Uganda's National Development Plan III.
    It identifies strengths and gaps in programme fulfillment across all directorates and departments.
    """
    kpi_data = st.session_state["kpi_data"]
    st.write(
        "Review how departmental KPIs and targets are distributed across the 13 NDP III Programmes. "
        "This helps ensure that KCCA's work is fully aligned with national priorities."
    )
    st.dataframe(pd.DataFrame({"NDP Programme": NDP_PROGRAMMES}), use_container_width=True)
    if not kpi_data.empty:
        ndp_fulfillment = (
            kpi_data.groupby("NDP Programme")
            .apply(lambda df: (df["Status"] == "Green").sum() / len(df) * 100 if len(df) > 0 else 0)
            .reset_index(name="Fulfillment %")
        )
        st.subheader("Programme Fulfillment Status")
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

# ---------------------- PROJECT MANAGEMENT ----------------------
def project_management():
    st.header("📋 Project Management & Tracking")
    """
    The project management module enables users to add, monitor, and update projects
    under different directorates and departments. This supports effective delivery and
    accountability for all project milestones and outcomes.
    """
    projects_df = st.session_state["projects_df"]
    st.write(
        "Manage projects, assign them to departments, and track their status and deadlines. "
        "View all ongoing and completed initiatives below."
    )
    if not projects_df.empty:
        st.dataframe(projects_df, use_container_width=True)
    else:
        st.info("No projects found.")
    if role in ["Admin", "Strategy Officer"]:
        st.subheader("Add New Project")
        with st.form("add_project", clear_on_submit=True):
            directorate = st.selectbox("Directorate", KCCA_DIRECTORATES, key="proj_dir")
            if directorate == "Office of the Executive Director":
                departments = ED_DEPARTMENTS
                dept = st.selectbox("Department", departments, key="proj_dept")
            else:
                dept = directorate
                st.text_input("Department", value=dept, disabled=True, key="proj_dept_display")
            proj = st.text_input("Project Title")
            ndp_prog = st.selectbox("NDP Programme", NDP_PROGRAMMES, key="proj_ndp")
            status = st.selectbox("Status", ["Not Started", "In Progress", "Completed", "Stalled"])
            due = st.date_input("Due Date", value=date.today(), key="proj_due")
            submit = st.form_submit_button("Add Project")
            if submit and proj:
                new_row = pd.DataFrame([{
                    "Directorate": directorate,
                    "Department": dept if directorate == "Office of the Executive Director" else directorate,
                    "Project": proj,
                    "NDP Programme": ndp_prog,
                    "Status": status,
                    "Due Date": str(due)
                }])
                projects_df = pd.concat([projects_df, new_row], ignore_index=True)
                st.session_state["projects_df"] = projects_df
                st.success("Project added.")

# ---------------------- RISK & BOTTLENECK REPORTING ----------------------
def risk_reporting():
    st.header("🚨 Risk & Bottleneck Identification and Reporting")
    """
    This module facilitates risk management by capturing operational risks, bottlenecks,
    and challenges encountered by directorates and departments. It supports early detection,
    escalation, and resolution of key issues.
    """
    risks_df = st.session_state["risks_df"]
    st.write(
        "Report and view risks or operational bottlenecks that affect performance. "
        "Review all reported issues, their urgency, and date of reporting."
    )
    if not risks_df.empty:
        st.dataframe(risks_df, use_container_width=True)
    else:
        st.info("No risks reported yet.")
    if role in ["Admin", "Strategy Officer"]:
        st.subheader("Report a New Risk or Bottleneck")
        with st.form("risk_form", clear_on_submit=True):
            directorate = st.selectbox("Directorate", KCCA_DIRECTORATES, key="risk_dir")
            if directorate == "Office of the Executive Director":
                departments = ED_DEPARTMENTS
                dept = st.selectbox("Department", departments, key="risk_dept")
            else:
                dept = directorate
                st.text_input("Department", value=dept, disabled=True, key="risk_dept_display")
            issue = st.text_area("Describe the issue or risk")
            urgency = st.selectbox("Urgency", ["Low", "Medium", "High", "Critical"])
            submit = st.form_submit_button("Submit Report")
            if submit and issue:
                new_row = pd.DataFrame([{
                    "Directorate": directorate,
                    "Department": dept if directorate == "Office of the Executive Director" else directorate,
                    "Issue": issue,
                    "Urgency": urgency,
                    "Date": datetime.now().isoformat(timespec="seconds")
                }])
                risks_df = pd.concat([risks_df, new_row], ignore_index=True)
                st.session_state["risks_df"] = risks_df
                st.success("Risk reported.")

# ---------------------- BUDGET MONITORING ----------------------
def budget_monitoring():
    st.header("💰 Financial Budget Monitoring & Analysis")
    """
    This section enables real-time tracking and comparison of approved budgets and actual expenditures
    for each directorate and department. It helps ensure budget discipline and financial accountability.
    """
    budget_df = st.session_state["budget_df"]
    st.write(
        "Monitor, report, and analyze budgeting and expenditure performance for all directorates and departments. "
        "Visualize spending trends and identify areas of over- or under-expenditure."
    )
    if not budget_df.empty:
        st.dataframe(budget_df, use_container_width=True)
        st.bar_chart(budget_df.set_index("Department")["Expenditure"])
    else:
        st.info("No budget data yet.")
    if role in ["Admin", "Strategy Officer"]:
        st.subheader("Add Budget Data")
        with st.form("add_budget", clear_on_submit=True):
            directorate = st.selectbox("Directorate", KCCA_DIRECTORATES, key="budget_dir")
            if directorate == "Office of the Executive Director":
                departments = ED_DEPARTMENTS
                dept = st.selectbox("Department", departments, key="budget_dept")
            else:
                dept = directorate
                st.text_input("Department", value=dept, disabled=True, key="budget_dept_display")
            budget = st.number_input("Approved Budget (UGX)", min_value=0)
            expenditure = st.number_input("Expenditure (UGX)", min_value=0)
            variance = budget - expenditure
            submit = st.form_submit_button("Add Budget Data")
            if submit:
                new_row = pd.DataFrame([{
                    "Directorate": directorate,
                    "Department": dept if directorate == "Office of the Executive Director" else directorate,
                    "Budget": budget,
                    "Expenditure": expenditure,
                    "Variance": variance
                }])
                budget_df = pd.concat([budget_df, new_row], ignore_index=True)
                st.session_state["budget_df"] = budget_df
                st.success("Budget data added.")

# ---------------------- DOCUMENT REPOSITORY ----------------------
def document_repository():
    st.header("📁 Strategy Document & Knowledge Repository")
    """
    This module provides a secure and centralized repository for uploading, storing, and reviewing
    key strategy documents, reports, and knowledge products across KCCA.
    """
    docs = st.session_state["documents"]
    st.write(
        "Upload and view strategy documents, reports, and reference materials. "
        "This helps facilitate knowledge sharing and institutional memory."
    )
    if not docs.empty:
        st.dataframe(docs, use_container_width=True)
    uploaded_file = st.file_uploader("Upload document (PDF, DOCX, XLSX)", type=["pdf", "docx", "xlsx"])
    notes = st.text_area("Notes (describe document purpose, content, etc.)")
    if uploaded_file and role in ["Admin", "Strategy Officer"]:
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

# ---------------------- MAIN APP FLOW ----------------------
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

# ---------------------- FOOTER ----------------------
st.markdown("---")
st.caption(
    "KCCA Strategy Hub | Streamlit Professional Demo (In-memory, not persistent). "
    "Developed for comprehensive Monitoring, Evaluation, Reporting, and Strategic Management across KCCA directorates. "
    f"Session started on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)
