"""
ZYRO DYNAMICS HR HELP DESK — STREAMLIT CHATBOT
Deploy this to https://share.streamlit.io

Setup:
  1. Push this file + requirements.txt to a GitHub repo
  2. Go to share.streamlit.io → New App → select the repo
  3. Add GROQ_API_KEY to Streamlit Secrets
  4. Deploy → copy the public URL for submission.csv
"""

import os, re, time, warnings
warnings.filterwarnings("ignore")

import streamlit as st

# ── Page config ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Zyro Dynamics HR Help Desk",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .main { background: #0e1117; }
  .chat-user {
    background: #1a2744;
    border-left: 4px solid #5c6bc0;
    padding: 14px 18px;
    border-radius: 10px;
    margin: 8px 0;
    line-height: 1.65;
  }
  .chat-bot {
    background: #1b2838;
    border-left: 4px solid #26a69a;
    padding: 14px 18px;
    border-radius: 10px;
    margin: 8px 0;
    line-height: 1.65;
  }
  .stButton > button {
    background: #5c6bc0;
    color: #fff;
    border: none;
    border-radius: 7px;
    font-weight: 600;
  }
  .stButton > button:hover { background: #3949ab; }
  div[data-testid="metric-container"] {
    background: #1a1f36;
    border-radius: 8px;
    padding: 10px;
  }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# HR POLICY KNOWLEDGE BASE (built-in, no external files needed)
# ─────────────────────────────────────────────────────────────────
HR_POLICIES = {
    "Leave_Policy": """
ZYRO DYNAMICS — LEAVE POLICY

1. EARNED LEAVE (EL)
All permanent employees receive 18 days of Earned Leave per calendar year.
Accrues at 1.5 days per month. Minimum 6 months of service before availing EL.
Maximum accumulation: 45 days. Unused EL beyond 45 days lapses at year-end.
Apply at least 2 working days in advance via the HRIS portal.

2. SICK LEAVE (SL)
12 days per year. Medical certificate required for more than 3 consecutive days.
SL cannot be carried forward or encashed.

3. CASUAL LEAVE (CL)
8 days per year. Maximum 3 consecutive days per instance.
Cannot be combined with EL. Expires at year-end.

4. MATERNITY LEAVE
26 weeks paid (Maternity Benefit Act, 1961). Available for up to 2 children.
Adoptive mothers: 12 weeks.

5. PATERNITY LEAVE
5 paid days within 3 months of childbirth or adoption.

6. BEREAVEMENT LEAVE
3 days for immediate family (spouse, children, parents, siblings).
1 day for extended family.

7. LOSS OF PAY (LOP)
Leave beyond entitlement or unauthorized absence treated as LOP.
LOP reduces month's gross salary proportionally.

8. LEAVE APPLICATION
Submit via HRIS portal. Emergency leave: notify manager within 2 hours.
Unapproved leave treated as LOP.
""",
    "Compensation_Benefits": """
ZYRO DYNAMICS — COMPENSATION & BENEFITS POLICY

1. SALARY DISBURSEMENT
Credited on last working day of each month.
Salary slips available on HRIS portal by 2nd working day of next month.

2. SALARY STRUCTURE
Basic Salary: 40–50% of CTC
HRA: 50% of Basic (metro) / 40% of Basic (non-metro)
DA: 10% of Basic | LTA: One month's Basic per year
Medical Allowance: Rs. 1,250/month (tax-exempt)

3. EPF / PROVIDENT FUND
Employee: 12% of (Basic + DA). Employer: 12% of (Basic + DA) — over & above CTC.
EPF account created within 30 days of joining.

4. ESI
Applicable for gross salary ≤ Rs. 21,000/month.
Employee: 0.75%. Employer: 3.25%.

5. TDS
Deducted monthly per income-tax slabs.
Investment declarations by 31 Dec. Final proof by 15 Feb. Form 16 by 15 June.

6. OVERTIME (OT)
1.5× hourly rate for hours beyond 9 hrs/day or 48 hrs/week.
Pre-approved only. Claims within 7 days.

7. HEALTH BENEFITS (GMC)
Coverage: Employee + Spouse + 2 dependent children.
Sum Insured: Rs. 5,00,000 per family per year.
Cashless hospitalisation at 5,000+ network hospitals. Pre-existing covered Day 1.
Non-network claims reimbursed within 30 working days.
Dental: Rs. 5,000/year. Vision: Rs. 3,000/year.

8. TERM LIFE INSURANCE
3× Annual CTC (minimum Rs. 50 lakhs).
Nomination to be updated in HRIS within 30 days of joining.

9. NPS
Optional. Employee minimum Rs. 500/month.
Employer contributes 10% of Basic + DA for NPS-enrolled employees.

10. WELLNESS
Annual health check-up: Rs. 5,000 (employees aged 35+).
Gym/fitness reimbursement: Rs. 1,000/month (quarterly receipts).
Mental health: up to 5 free counselling sessions/year via EAP.

11. SALARY REVISION
Annual increments effective April 1st, linked to performance rating.
Employees on PIP are not eligible for increments.
""",
    "WFH_Policy": """
ZYRO DYNAMICS — WORK FROM HOME (WFH) POLICY

1. ELIGIBILITY
Post-probation (6 months) employees may avail WFH.
Employees on PIP are NOT eligible. Contractors/interns require HR Head approval.

2. WFH FREQUENCY
Standard hybrid: up to 2 WFH days per week.
Additional days: documented approval from department head.
Extended WFH (>3 months): HR + VP approval required.

3. INFRASTRUCTURE ALLOWANCE
One-time WFH setup allowance: Rs. 5,000 (taxable as perquisite).
Claim within 60 days of WFH approval.

4. CORE HOURS & AVAILABILITY
Online during core hours: 10:00 AM – 4:00 PM IST.
Response time: within 30 minutes during core hours.
Video on for all team calls and 1-on-1s.

5. ATTENDANCE
Mark attendance in HRIS before 9:30 AM every WFH day.
3 failures in a month = LOP.

6. PRODUCTIVITY
Weekly status reports mandatory for extended WFH employees.
Manager may revoke WFH for consistent productivity issues.
""",
    "Performance_Review": """
ZYRO DYNAMICS — PERFORMANCE REVIEW POLICY

1. REVIEW CYCLE
Mid-Year Review: July (covering Jan–Jun).
Annual Review: January (covering Jul–Dec).
Probation Review: End of 6-month probation.

2. RATING SCALE
5 — Exceptional: consistently and significantly exceeds expectations
4 — Exceeds Expectations: frequently exceeds targets
3 — Meets Expectations: consistently delivers on all targets
2 — Needs Improvement: partially meets expectations
1 — Unsatisfactory: fails to meet minimum expectations

3. PERFORMANCE IMPROVEMENT PLAN (PIP)
Triggered by rating 1 or 2 for TWO consecutive review cycles.
Duration: 60–90 days with clear, measurable targets.
Managed by reporting manager + HR Business Partner.
Failure to meet PIP targets may result in separation.
Employees on PIP: ineligible for WFH, increment, or promotion.

4. INCREMENTS
Effective April 1st. Linked to rating + company financial performance.

5. PROMOTIONS
Minimum 2 years in current role. Submitted during annual review cycle.
""",
    "Travel_Expense": """
ZYRO DYNAMICS — TRAVEL & EXPENSE POLICY

1. PRE-APPROVAL
Domestic: 3 working days in advance. International: 10 working days + CEO approval.

2. TRAVEL GRADES
Grade A (VP+): Business class; 5-star hotels.
Grade B (Manager–Sr. Mgr): Economy; 4-star hotels.
Grade C (All others): Economy; 3-star hotels.

3. DAILY ALLOWANCE
Metro: Grade A Rs. 2,500 | Grade B Rs. 1,800 | Grade C Rs. 1,200
Non-metro: Grade A Rs. 1,800 | Grade B Rs. 1,200 | Grade C Rs. 800

4. REIMBURSEMENT
Submit HRIS expense claim within 15 days of return.
Receipts required for all expenses above Rs. 500.
Claims after 30 days: NOT processed.
Reimbursement credited within 15 working days of approval.

5. TRANSPORT
Cab-to-airport: reimbursable with receipt.
Personal vehicle: Rs. 12/km (4-wheeler), Rs. 6/km (2-wheeler).
Metro/local train: reimbursable as actuals.
""",
    "Conduct_POSH": """
ZYRO DYNAMICS — CODE OF CONDUCT & POSH POLICY

1. PROFESSIONAL BEHAVIOUR
Respectful, professional conduct at all times.
Harassment, discrimination, bullying strictly prohibited.
Employees equal regardless of gender, religion, caste, or nationality.

2. POSH (Prevention of Sexual Harassment)
Zero-tolerance policy toward sexual harassment (POSH Act, 2013).
Internal Complaints Committee (ICC) constituted per law.
Complaints must be filed within 3 months of the incident.
Anonymous reporting available via HR helpline.
Violations subject to strict disciplinary action.

3. CONFLICT OF INTEREST
Disclose financial/personal interests conflicting with company interests.
Approval required for external consulting, directorships, or competing investments.

4. CONFIDENTIALITY & NDA
No disclosure of proprietary info, client data, or trade secrets.
NDA in force for 2 years post-employment.

5. SOCIAL MEDIA
No posting of confidential company/client info.
Personal opinions must not damage the company's reputation.

6. DISCIPLINARY ACTIONS
Warning → Suspension → Termination (based on severity and recurrence).
Major misconduct (fraud, theft, violence) → immediate termination.
""",
    "Onboarding_Separation": """
ZYRO DYNAMICS — ONBOARDING & SEPARATION POLICY

1. JOINING DOCUMENTS (within 3 working days of DOJ)
Aadhar + PAN (mandatory), educational certificates, relieving + experience letter,
last 3 months' salary slips, bank account details, 4 passport photos.
Nominee details for PF, ESI, and insurance.

2. PROBATION PERIOD
Duration: 6 months from Date of Joining (DOJ).
Confirmation letter issued after satisfactory probation review.
Notice period during probation: 15 days (either side).
Probation may be extended by up to 3 months if unsatisfactory.

3. NOTICE PERIOD (Post-Confirmation)
Individual Contributor (IC): 60 days.
Manager and above: 90 days.
Buyout: allowed by paying equivalent gross salary.
Garden leave: at company's discretion.

4. FULL & FINAL SETTLEMENT (F&F)
Processed within 45 days of last working day.
F&F includes: unpaid salary, earned leave encashment, gratuity (if eligible).
Gratuity payable after 5 years of continuous service (Payment of Gratuity Act).
PF settlement via EPFO: typically 15–30 days separately.

5. NO DUES CERTIFICATE (NDC)
Collect from IT, Finance, Admin, and reporting manager before last working day.
IT assets (laptop, access card, phone) must be returned.
Exit interview with HR is mandatory.
Outstanding loans/advances deducted from F&F.
""",
    "IT_Security": """
ZYRO DYNAMICS — IT & DATA SECURITY POLICY

1. DEVICE USAGE
All company devices must be password-protected with MFA enabled.
Unauthorised software installation is prohibited.
Lost/stolen devices must be reported to IT within 24 hours.
No personal use of company devices for illegal or inappropriate activities.

2. DATA PROTECTION
Confidential data must not be shared via personal email or unsanctioned cloud.
All data transfers must use company-approved encrypted channels.
Customer data handled per the company's data classification policy.

3. INTERNET & EMAIL POLICY
Company email must not be used for personal subscriptions.
Phishing emails must be reported to IT security immediately.

4. REMOTE ACCESS
VPN mandatory for all remote access to company systems.
Multi-factor authentication (MFA) required for all critical systems.

5. VIOLATIONS
IT policy violations may result in disciplinary action up to termination.
""",
    "Employee_Handbook": """
ZYRO DYNAMICS — EMPLOYEE HANDBOOK

1. WORKING HOURS
Standard: 9:00 AM – 6:00 PM, Monday to Friday.
Total: 9 hours/day including 1 hour lunch break.
Flexible hours: by prior agreement with reporting manager.

2. ATTENDANCE & PUNCTUALITY
Mark attendance in HRIS by 9:30 AM.
3 late arrivals in a month without notice = half-day deduction.

3. DRESS CODE
Business casual for office days.
Formal attire may be required for client-facing meetings.

4. INTERNAL COMMUNICATION
Primary channels: Microsoft Teams and company email.
Sensitive HR matters: via HRIS or directly to HR.

5. GRIEVANCE REDRESSAL
Raise concerns with reporting manager first.
Escalate to HRBP if unresolved within 5 working days.
Anonymous grievance: HR helpline or HRIS suggestion box.

6. LEARNING & DEVELOPMENT
Annual L&D budget of Rs. 15,000 per employee for approved courses.
Internal learning platform available 24/7 on the HRIS portal.
""",
    "Company_Profile": """
ZYRO DYNAMICS — COMPANY PROFILE

ABOUT
Zyro Dynamics Pvt. Ltd. — technology-driven SaaS company founded in 2015.
Specialises in enterprise workflow automation and AI-powered productivity tools.

HEADQUARTERS: Bangalore, Karnataka, India
EMPLOYEES: 500+ (Engineering, Sales, Operations, HR, Finance, Legal)
OFFICES: Bangalore (HQ), Mumbai, Hyderabad, Delhi NCR

CORE VALUES
1. Innovation First  2. Customer Obsession  3. Integrity
4. Collaboration  5. Growth Mindset

BENEFITS PHILOSOPHY
Compensation benchmarked to 75th percentile of industry.
Comprehensive health coverage, flexible work, continuous learning.
""",
}

# ── OOS keywords ────────────────────────────────────────────────────
OOS_KEYWORDS = [
    "weather", "sports", "cricket", "football", "ipl", "stock market",
    "bitcoin", "cryptocurrency", "cooking", "recipe", "movie", "music",
    "politics", "election", "programming", "python code", "javascript",
    "geography", "capital of", "science", "physics", "chemistry",
    "who invented", "celebrity", "actor", "write a function", "write code",
]
_OOS_RE = [re.compile(rf"\b{re.escape(k)}\b", re.I) for k in OOS_KEYWORDS]

OOS_REFUSAL = (
    "I'm sorry, but that question is outside the scope of the Zyro Dynamics "
    "HR Help Desk. I can only answer questions about Zyro Dynamics HR policies — "
    "such as leave, payroll, benefits, performance, conduct, and onboarding. "
    "For other queries, please consult the appropriate resource or department."
)


@st.cache_resource(show_spinner="🔄 Loading HR knowledge base...")
def load_pipeline():
    try:
        from langchain_groq import ChatGroq
        from langchain_community.embeddings import HuggingFaceEmbeddings
        from langchain_community.vectorstores import FAISS
        from langchain_core.documents import Document
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.runnables import RunnablePassthrough, RunnableLambda
    except ImportError as e:
        return None, f"Missing dependency: {e}"

    groq_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
    if not groq_key:
        return None, "GROQ_API_KEY not set in Streamlit Secrets."

    os.environ["GROQ_API_KEY"] = groq_key

    # Build documents from built-in policies
    docs = [
        Document(page_content=v.strip(), metadata={"source": k})
        for k, v in HR_POLICIES.items()
    ]

    splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=120)
    chunks = splitter.split_documents(docs)
    chunks = [c for c in chunks if len(c.page_content.strip()) >= 80]

    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-large-en-v1.5",
        encode_kwargs={"normalize_embeddings": True},
    )
    vectorstore = FAISS.from_documents(chunks, embeddings)
    retriever   = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 5, "fetch_k": 20},
    )

    SYSTEM_PROMPT = """You are the Zyro Dynamics HR Help Desk AI assistant.
Answer ONLY from the retrieved HR policy context below.
If the answer is not in the context, say: "I could not find this in the HR policy documents. Please contact HR."
Always cite the policy document name. Be concise and professional."""

    HR_PROMPT = """HR Policy Context:
{context}

---
Employee Question: {question}

Provide a grounded answer referencing only the context above."""

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", HR_PROMPT),
    ])

    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.05, max_tokens=1024)

    def fmt(docs):
        return "\n\n---\n\n".join(
            f"[{i+1}] {d.metadata.get('source','HR Policy')}\n{d.page_content}"
            for i, d in enumerate(docs)
        )

    chain = (
        {"context": retriever | RunnableLambda(fmt), "question": RunnablePassthrough()}
        | prompt | llm | StrOutputParser()
    )
    return chain, None


def answer(question: str, chain) -> str:
    for pat in _OOS_RE:
        if pat.search(question):
            return OOS_REFUSAL
    try:
        return chain.invoke(question).strip()
    except Exception as e:
        return f"I could not find this information in the HR policy documents. Please contact HR directly. (Error: {e})"


# ─────────────────────────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────────────────────────
chain, err = load_pipeline()

st.markdown("""
<div style="background:linear-gradient(135deg,#1a1f36,#0e1117);
  border-bottom:2px solid #5c6bc0;padding:18px 24px;border-radius:8px;margin-bottom:20px">
  <h1 style="margin:0;color:#fff">🏢 Zyro Dynamics HR Help Desk</h1>
  <p style="margin:4px 0 0;color:#90caf9">
    AI-powered HR policy assistant · Leave · Payroll · Benefits · Compliance
  </p>
</div>
""", unsafe_allow_html=True)

if err:
    st.error(err)
    st.stop()

# Session state
for key in ["history", "n_queries", "latencies"]:
    if key not in st.session_state:
        st.session_state[key] = [] if key != "n_queries" else 0

# Sidebar
with st.sidebar:
    st.markdown("### 📊 Session Stats")
    c1, c2 = st.columns(2)
    c1.metric("Queries", st.session_state.n_queries)
    avg_lat = (
        sum(st.session_state.latencies) / len(st.session_state.latencies)
        if st.session_state.latencies else 0
    )
    c2.metric("Avg Response", f"{avg_lat:.1f}s")

    st.markdown("---")
    st.markdown("### 💡 Quick Questions")
    quick_qs = [
        "How many earned leave days per year?",
        "What is the WFH policy?",
        "How is EPF calculated?",
        "What is the notice period?",
        "Maternity leave entitlement?",
        "How to claim travel reimbursement?",
        "What is the POSH policy?",
        "How does PIP work?",
        "What are health insurance benefits?",
        "How is F&F settlement calculated?",
    ]
    for q in quick_qs:
        if st.button(q, use_container_width=True, key=f"qb_{q}"):
            st.session_state._pending = q
            st.rerun()

    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.history = []
        st.session_state.n_queries = 0
        st.session_state.latencies = []
        st.rerun()

    st.markdown("---")
    st.markdown("""
    <div style="font-size:12px;color:#666;line-height:1.5">
    ℹ️ <b>About</b><br>
    Answers are sourced exclusively from Zyro Dynamics official HR policy documents.
    For urgent matters, contact HR directly.
    </div>
    """, unsafe_allow_html=True)

# Chat history
for msg in st.session_state.history:
    if msg["role"] == "user":
        st.markdown(
            f'<div class="chat-user"><strong>👤 You</strong><br><br>{msg["text"]}</div>',
            unsafe_allow_html=True,
        )
    else:
        ans_html = msg["text"].replace("\n", "<br>")
        st.markdown(
            f'<div class="chat-bot"><strong>🤖 HR Assistant</strong><br><br>{ans_html}</div>',
            unsafe_allow_html=True,
        )

# Input
st.markdown("<br>", unsafe_allow_html=True)
col1, col2 = st.columns([6, 1])
with col1:
    user_input = st.text_input(
        "", placeholder="Ask an HR policy question...",
        label_visibility="collapsed", key="inp",
    )
with col2:
    send_btn = st.button("Send →", use_container_width=True)

# Process
pending = st.session_state.pop("_pending", None)
query   = pending or (user_input.strip() if send_btn and user_input.strip() else None)

if query:
    st.session_state.history.append({"role": "user", "text": query})
    with st.spinner("🔍 Searching HR policies..."):
        t0  = time.time()
        ans = answer(query, chain)
        elapsed = round(time.time() - t0, 2)

    st.session_state.n_queries += 1
    st.session_state.latencies.append(elapsed)
    st.session_state.history.append({"role": "assistant", "text": ans})
    st.rerun()

# Feedback on last answer
if st.session_state.history and st.session_state.history[-1]["role"] == "assistant":
    fc1, fc2, fc3, _ = st.columns([1, 1, 1, 5])
    if fc1.button("👍 Helpful"):
        st.success("Thanks for the feedback!")
    if fc2.button("👎 Not helpful"):
        st.warning("Noted — we'll improve.")
    if fc3.button("⚠️ Incorrect"):
        st.error("Flagged for HR review.")

st.markdown(
    '<hr><p style="text-align:center;color:#424a60;font-size:.78em">'
    "Zyro Dynamics HR Help Desk · Powered by GROQ + LangChain · Internal use only</p>",
    unsafe_allow_html=True,
)
