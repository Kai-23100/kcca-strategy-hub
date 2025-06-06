import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Config ---
st.set_page_config(layout="wide", page_title="KCCA Strategy Hub")
st.title("📊 KCCA Strategy Hub")
st.markdown("Welcome to the **Kampala Capital City Authority (KCCA) Strategy Hub**. "
    "Use the navigation menu to explore strategic plan tracking, performance dashboards, GIS insights, risk reporting, and access to key documents.")

# --- Sidebar Navigation ---
st.sidebar.title("Navigation")
menu = st.sidebar.radio("Go to", [
    "Strategic Plan Tracker",
    "Policy Implementation Matrix",
    "Performance Dashboard",
    "GIS Insights",
    "Risk & Bottleneck Reporting",
    "Document Repository"
])

# --- Data Samples ---
kpi_data = pd.DataFrame({
    'Department': ['Health', 'Education', 'Works', 'Environment'],
    'KPI': ['Maternal Health Index', 'Literacy Rate', 'Road Quality Score', 'Air Quality Index'],
    'Target': [85, 90, 80, 70],
    'Current': [75, 88, 70, 60],
    'Status': ['Amber', 'Green', 'Amber', 'Red']
})

policy_matrix = pd.DataFrame({
    'Policy Action': ['Upgrade city hospitals', 'Increase school funding', 'Rehabilitate roads', 'Improve waste management'],
    'Responsible': ['Health Dept.', 'Education Dept.', 'Works Dept.', 'Environment Dept.'],
    'Due Date': ['2025-12-31', '2025-10-01', '2025-11-30', '2025-09-30'],
    'Progress': ['Ongoing', 'Planned', 'Delayed', 'Ongoing']
})

score_data = pd.DataFrame({
    'Department': ['Health', 'Education', 'Works', 'Environment'],
    'Score': [76, 88, 72, 65]
})

map_data = pd.DataFrame({
    'lat': [0.3136, 0.3156, 0.3100],
    'lon': [32.5811, 32.5822, 32.5850],
    'Project': ['Health Centre', 'New School', 'Road Upgrade']
})

# --- Strategic Plan Tracker ---
if menu == "Strategic Plan Tracker":
    st.header("📈 Strategic Plan Tracker")
    st.write(
        "Monitor the **Key Performance Indicators (KPIs)** across KCCA's departments. "
        "Hover over bars to see targets. Status colors: 🟩 Green = On Track, 🟨 Amber = Needs Attention, 🟥 Red = Off Track."
    )
    color_map = {'Green': '#34c759', 'Amber': '#ffd60a', 'Red': '#ff3b30'}
    fig = px.bar(
        kpi_data,
        x='KPI',
        y='Current',
        color='Status',
        color_discrete_map=color_map,
        hover_data=['Department', 'Target', 'Current'],
        barmode='group',
        title='KPI Progress Against Targets'
    )
    st.plotly_chart(fig, use_container_width=True)
    # Add progress bars and target comparisons
    st.markdown("### Detailed KPI Table")
    for i, row in kpi_data.iterrows():
        st.write(f"**{row['KPI']}** ({row['Department']}):")
        st.progress(min(int(row['Current'] / row['Target'] * 100), 100), text=f"{row['Current']} / {row['Target']} (Status: {row['Status']})")
    st.dataframe(kpi_data, use_container_width=True)

# --- Policy Implementation Matrix ---
elif menu == "Policy Implementation Matrix":
    st.header("📋 Policy Implementation Matrix")
    st.write(
        "Track the status of major policy actions, responsible departments, and due dates. "
        "Use this table to follow up on progress and identify bottlenecks."
    )
    st.dataframe(policy_matrix, use_container_width=True)
    st.markdown("#### Legend")
    st.markdown("- **Ongoing:** Work is in progress")
    st.markdown("- **Planned:** Work is scheduled but not started")
    st.markdown("- **Delayed:** Action is behind schedule")

# --- Performance Dashboard ---
elif menu == "Performance Dashboard":
    st.header("📊 Performance Dashboard")
    st.markdown(
        "Visualize **overall departmental performance**. "
        "Scores are derived from aggregate KPIs and other assessment tools."
    )
    fig = px.pie(score_data, values='Score', names='Department',
                 title='Departmental Performance Distribution')
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("#### Department Scores")
    for idx, row in score_data.iterrows():
        st.write(f"{row['Department']}: **{row['Score']}**")
    st.dataframe(score_data, use_container_width=True)

# --- GIS Insights ---
elif menu == "GIS Insights":
    st.header("🌍 GIS-linked Data Insights")
    st.write(
        "Interactive map of recent **city projects**. "
        "Zoom and pan to explore project locations."
    )
    st.map(map_data)
    st.dataframe(map_data, use_container_width=True)

# --- Risk & Bottleneck Reporting ---
elif menu == "Risk & Bottleneck Reporting":
    st.header("🚨 Risk & Bottleneck Reporting")
    st.write(
        "Use this form to **report operational risks or bottlenecks** affecting strategy implementation. "
        "Submissions go to the KCCA strategy monitoring team."
    )
    with st.form("risk_form"):
        dept = st.selectbox("Department reporting the issue", kpi_data['Department'].unique())
        issue = st.text_area("Describe the issue or risk in detail")
        urgency = st.selectbox("Urgency", ["Low", "Medium", "High", "Critical"])
        submitted = st.form_submit_button("Submit Report")
        if submitted:
            st.success(f"Issue reported for {dept} department. Thank you for your feedback!")
            st.info(f"Issue details: {issue}\n\nUrgency: {urgency}")

# --- Document Repository ---
elif menu == "Document Repository":
    st.header("📁 Strategy Document Repository")
    st.write(
        "Upload new files or download/view existing strategic documents, reports, and reference material."
    )
    uploaded_file = st.file_uploader("Upload a document (PDF, DOCX, XLSX)", type=["pdf", "docx", "xlsx"])
    if uploaded_file:
        st.success(f"Uploaded file: {uploaded_file.name}")
        st.download_button("Download File", uploaded_file.read(), file_name=uploaded_file.name)

    st.markdown("#### Sample Files")
    st.markdown("- [Strategic Plan 2025 (PDF)](#)")
    st.markdown("- [Annual Performance Report (DOCX)](#)")
    st.markdown("- [Environmental Impact Statement (XLSX)](#)")
    st.info("To add more files, please contact the Strategy Office.")

st.markdown("---")
st.caption("KCCA Strategy Hub | Powered by Streamlit")