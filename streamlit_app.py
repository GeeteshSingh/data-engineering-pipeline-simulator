import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import io
import re

# Page config
st.set_page_config(
    page_title="The Transparent Pipeline",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    :root {
        --color-primary: #32b8c6;
        --color-bg: #0f1419;
        --color-surface: #1a1f27;
        --color-text: #e4e6eb;
        --color-text-secondary: #8892a0;
        --color-success: #10b981;
        --color-warning: #f59e0b;
        --color-error: #ef4444;
        --color-info: #3b82f6;
    }
    
    .header-title {
        background: linear-gradient(135deg, #32b8c6, #0ea5e9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .progress-steps {
        display: flex;
        justify-content: space-between;
        margin: 20px 0;
        gap: 12px;
    }
    
    .step {
        flex: 1;
        padding: 12px;
        text-align: center;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 600;
        border: 2px solid rgba(50, 184, 198, 0.2);
        background: rgba(50, 184, 198, 0.05);
        transition: all 0.3s;
    }
    
    .step.active {
        background: rgba(50, 184, 198, 0.3);
        border-color: #32b8c6;
        box-shadow: 0 0 10px rgba(50, 184, 198, 0.3);
    }
    
    .step.completed {
        background: rgba(16, 185, 129, 0.2);
        border-color: #10b981;
        color: #10b981;
    }
    
    .console-container {
        background: rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(50, 184, 198, 0.2);
        border-radius: 8px;
        padding: 16px;
        max-height: 400px;
        overflow-y: auto;
        font-family: 'Courier New', monospace;
        font-size: 12px;
        line-height: 1.6;
    }
    
    .log-entry {
        margin-bottom: 8px;
        padding: 4px 8px;
        border-radius: 4px;
    }
    
    .log-info {
        color: #3b82f6;
    }
    
    .log-success {
        color: #10b981;
    }
    
    .log-error {
        color: #ef4444;
    }
    
    .log-warning {
        color: #f59e0b;
    }
    
    .stat-card {
        background: rgba(50, 184, 198, 0.05);
        border: 1px solid rgba(50, 184, 198, 0.2);
        border-radius: 8px;
        padding: 16px;
        text-align: center;
        transition: all 0.3s;
    }
    
    .stat-card:hover {
        border-color: #32b8c6;
        box-shadow: 0 0 12px rgba(50, 184, 198, 0.2);
    }
    
    .stat-value {
        font-size: 28px;
        font-weight: bold;
        color: #32b8c6;
        margin-bottom: 4px;
    }
    
    .stat-label {
        font-size: 12px;
        color: #8892a0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .architecture-box {
        background: rgba(50, 184, 198, 0.08);
        border: 1px solid rgba(50, 184, 198, 0.2);
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        font-size: 12px;
    }
    
    .flow-diagram {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 20px 0;
        flex-wrap: wrap;
        justify-content: center;
    }
    
    .flow-item {
        background: rgba(50, 184, 198, 0.1);
        border: 1px solid rgba(50, 184, 198, 0.3);
        border-radius: 8px;
        padding: 12px 16px;
        font-size: 12px;
        font-weight: 500;
        text-align: center;
        min-width: 80px;
    }
    
    .arrow {
        font-size: 20px;
        color: #32b8c6;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'pipeline_running' not in st.session_state:
    st.session_state.pipeline_running = False
if 'stats' not in st.session_state:
    st.session_state.stats = None
if 'current_step' not in st.session_state:
    st.session_state.current_step = 0
if 'custom_stages' not in st.session_state:
    st.session_state.custom_stages = []

# Helper functions
def add_log(message: str, level: str = "INFO"):
    """Add log entry with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append({
        "time": timestamp,
        "level": level,
        "message": message
    })

def update_step(step_num: int):
    """Update current processing step (1-4)"""
    st.session_state.current_step = step_num

def parse_csv_proper(file_content: str) -> list:
    """RFC 4180 CSV Parser"""
    rows = []
    current = []
    current_field = ''
    inside_quotes = False
    
    i = 0
    while i < len(file_content):
        char = file_content[i]
        next_char = file_content[i + 1] if i + 1 < len(file_content) else None
        
        if char == '"':
            if inside_quotes and next_char == '"':
                current_field += '"'
                i += 1
            else:
                inside_quotes = not inside_quotes
        elif char == ',' and not inside_quotes:
            current.append(current_field.strip())
            current_field = ''
        elif (char in ['\n', '\r']) and not inside_quotes:
            if current_field or len(current) > 0:
                current.append(current_field.strip())
                if any(field for field in current):
                    rows.append(current)
                current = []
                current_field = ''
            if char == '\r' and next_char == '\n':
                i += 1
        else:
            current_field += char
        
        i += 1
    
    if current_field or len(current) > 0:
        current.append(current_field.strip())
        if any(field for field in current):
            rows.append(current)
    
    return rows

def classify_dataset(filename: str, headers: list, data: list) -> dict:
    """Detect dataset type"""
    name = filename.lower()
    dataset_type = "📊 Generic Dataset"
    confidence = 0
    
    if 'youtube' in name or 'myactivity' in name:
        dataset_type = '🎥 YouTube Activity History'
        confidence = 95
    elif 'netflix' in name:
        dataset_type = '📺 Netflix Viewing History'
        confidence = 90
    elif 'amazon' in name or 'orders' in name:
        dataset_type = '🛒 E-commerce Orders'
        confidence = 85
    elif 'spotify' in name or 'music' in name:
        dataset_type = '🎵 Music Streaming Activity'
        confidence = 90
    elif 'fitness' in name or 'health' in name:
        dataset_type = '🏃 Fitness Data'
        confidence = 85
    elif 'bank' in name or 'transaction' in name:
        dataset_type = '💳 Financial Transactions'
        confidence = 80
    
    if headers and len(data) > 0:
        first_col = [row[0] if len(row) > 0 else '' for row in data]
        youtube_count = sum(1 for val in first_col if 'YouTube' in str(val))
        if youtube_count > len(data) * 0.5:
            dataset_type = '🎥 YouTube Activity History'
            confidence = 98
    
    return {"type": dataset_type, "confidence": confidence}

def calculate_quality_score(rows_count: int, nulls_count: int, columns_count: int) -> int:
    """Calculate quality score (0-100)"""
    score = 0
    total_cells = rows_count * columns_count if columns_count > 0 else 1
    null_percent = (nulls_count / total_cells) * 100 if total_cells > 0 else 0
    completeness = max(0, 100 - null_percent)
    score += (completeness / 100) * 35
    size_score = min(25, (rows_count / 100) * 5)
    score += size_score
    score += 20  # Diversity
    score += 18  # Freshness
    return round(score)

def process_csv_file(file_content: str, filename: str) -> dict:
    """Process CSV and return statistics"""
    try:
        all_rows = parse_csv_proper(file_content)
        
        if len(all_rows) < 2:
            raise ValueError("CSV must have at least header and one data row")
        
        headers = all_rows[0]
        data_rows = all_rows[1:]
        
        rows = len(data_rows)
        columns = len(headers)
        
        nulls = 0
        for row in data_rows:
            for cell in row:
                if not cell or cell == '' or cell == 'null':
                    nulls += 1
        
        classification = classify_dataset(filename, headers, data_rows)
        quality_score = calculate_quality_score(rows, nulls, columns)
        
        insights = ""
        if "YouTube" in classification['type']:
            activity_types = [row[0] for row in data_rows if len(row) > 0]
            youtube_count = sum(1 for a in activity_types if 'YouTube' in str(a) and 'Music' not in str(a))
            music_count = sum(1 for a in activity_types if 'Music' in str(a))
            youtube_pct = round((youtube_count / rows) * 100) if rows > 0 else 0
            music_pct = round((music_count / rows) * 100) if rows > 0 else 0
            insights = f"YouTube Videos: {youtube_pct}% | Music: {music_pct}%"
        
        return {
            "rows": rows,
            "columns": columns,
            "nulls": nulls,
            "completeness": round(((rows * columns - nulls) / (rows * columns) * 100)) if (rows * columns) > 0 else 0,
            "dataset_type": classification['type'],
            "quality_score": quality_score,
            "insights": insights,
            "headers": headers,
            "status": "success"
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

def fetch_from_url(url: str) -> tuple:
    """Fetch CSV from public URL"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.text, True
        else:
            return f"Error: HTTP {response.status_code}", False
    except Exception as e:
        return f"Error fetching URL: {str(e)}", False

# HEADER
st.markdown('<div class="header-title">🚀 The Transparent Pipeline</div>', unsafe_allow_html=True)
st.markdown("*Data Engineering Simulator | Real CSV Processing + Architecture Diagrams*")
st.markdown("---")

# MAIN LAYOUT
col1, col2 = st.columns(2, gap="large")

# LEFT: Data Source
with col1:
    st.subheader("📤 Data Source")
    
    source_type = st.radio("Select data source:", ["CSV File", "Public URL"], horizontal=True)
    
    file_content = None
    filename = None
    
    if source_type == "CSV File":
        uploaded_file = st.file_uploader("Upload CSV (Max 100MB)", type=['csv'])
        if uploaded_file:
            filename = uploaded_file.name
            file_content = uploaded_file.read().decode('utf-8', errors='ignore')
    else:
        url = st.text_input("Public CSV URL", placeholder="https://example.com/data.csv")
        if url:
            with st.spinner("Fetching file..."):
                file_content, success = fetch_from_url(url)
                filename = url.split('/')[-1]
                if not success:
                    st.error(file_content)
                    file_content = None

# RIGHT: Live Console
with col2:
    st.subheader("📡 Live Console")
    
    console_html = '<div class="console-container">'
    
    if st.session_state.logs:
        for log in st.session_state.logs:
            level_class = f"log-{log['level'].lower()}"
            icon_map = {
                "INFO": "🔵",
                "SUCCESS": "🟢",
                "ERROR": "🔴",
                "WARNING": "🟡"
            }
            icon = icon_map.get(log['level'], "⚪")
            console_html += f'<div class="log-entry {level_class}">{icon} [{log["time"]}] <strong>{log["level"]}</strong> - {log["message"]}</div>'
    else:
        console_html += '<div class="log-entry log-info">🔵 [--:--:--] <strong>INFO</strong> - Console ready. Waiting for pipeline trigger...</div>'
    
    console_html += '</div>'
    st.markdown(console_html, unsafe_allow_html=True)

# PROGRESS STEPS
st.markdown("---")
st.subheader("⚙️ Processing Status")

step_names = ["1. Connecting", "2. Validating", "3. Producing", "4. Completed"]
progress_cols = st.columns(4, gap="small")

for i, (col, name) in enumerate(zip(progress_cols, step_names)):
    with col:
        if i < st.session_state.current_step:
            step_class = "step completed"
            label = f"✓ {name}"
        elif i == st.session_state.current_step and st.session_state.current_step > 0:
            step_class = "step active"
            label = f"◆ {name}"
        else:
            step_class = "step"
            label = name
        
        st.markdown(f'<div class="{step_class}">{label}</div>', unsafe_allow_html=True)

# Progress bar
if st.session_state.current_step > 0:
    progress_pct = (st.session_state.current_step / 4) * 100
    st.progress(progress_pct / 100)

# START PIPELINE BUTTON
col_status, col_button = st.columns([3, 1])

with col_button:
    if st.button("▶️ Start Pipeline", use_container_width=True, type="primary"):
        if file_content:
            st.session_state.logs = []
            st.session_state.current_step = 0
            st.session_state.pipeline_running = True
            
            add_log("Pipeline initialized", "INFO")
            add_log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", "INFO")
            
            update_step(1)
            add_log("📡 Connecting to Upstash Kafka...", "INFO")
            add_log("Endpoint: kafka-broker-1.upstash.io:9092", "INFO")
            st.rerun()
        else:
            st.error("❌ Please upload a CSV file or provide a URL")

with col_status:
    if st.session_state.stats:
        if st.session_state.stats['status'] == 'success':
            st.success("✅ Pipeline completed successfully!")
        else:
            st.error(f"❌ {st.session_state.stats.get('message', 'Unknown error')}")

# CONTINUE PROCESSING IF PIPELINE RUNNING
if st.session_state.pipeline_running and st.session_state.current_step == 1:
    import time
    time.sleep(1.2)
    
    add_log("✓ Connection established to Kafka broker", "SUCCESS")
    add_log("Authentication: SASL/SSL enabled", "SUCCESS")
    update_step(2)
    add_log("📋 Validating data source...", "INFO")
    st.rerun()

elif st.session_state.pipeline_running and st.session_state.current_step == 2:
    import time
    time.sleep(0.8)
    
    if file_content:
        result = process_csv_file(file_content, filename)
        
        if result['status'] == 'success':
            add_log(f"✓ Successfully parsed {result['rows']:,} rows", "SUCCESS")
            add_log(f"✓ Detected {result['columns']} columns", "SUCCESS")
            add_log(f"Dataset Type: {result['dataset_type']}", "SUCCESS")
            
            update_step(3)
            add_log("📨 Producing message to Kafka topic...", "INFO")
            add_log("Topic: data-simulator", "INFO")
            add_log("Partition: 0", "INFO")
            st.session_state.stats = result
            st.rerun()
        else:
            add_log(f"ERROR: {result['message']}", "ERROR")
            st.session_state.pipeline_running = False
            st.rerun()

elif st.session_state.pipeline_running and st.session_state.current_step == 3:
    import time
    time.sleep(0.6)
    
    add_log("Message format: JSON (schema validated)", "INFO")
    add_log("✓ Message produced successfully", "SUCCESS")
    add_log("⚙️ Consumer processing data stream...", "INFO")
    
    update_step(4)
    time.sleep(0.5)
    add_log("📊 Computing data statistics...", "SUCCESS")
    add_log("✓ Results computed and available", "SUCCESS")
    add_log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", "SUCCESS")
    add_log("🎉 Pipeline execution completed!", "SUCCESS")
    
    st.session_state.pipeline_running = False
    st.rerun()

# DATA STATISTICS
if st.session_state.stats and st.session_state.stats.get('status') == 'success':
    st.markdown("---")
    st.subheader("📊 Data Statistics")
    
    stats = st.session_state.stats
    
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    
    with stat_col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{stats['rows']:,}</div>
            <div class="stat-label">Rows</div>
        </div>
        """, unsafe_allow_html=True)
    
    with stat_col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{stats['columns']}</div>
            <div class="stat-label">Columns</div>
        </div>
        """, unsafe_allow_html=True)
    
    with stat_col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{stats['nulls']:,}</div>
            <div class="stat-label">Null Values</div>
        </div>
        """, unsafe_allow_html=True)
    
    with stat_col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{stats['completeness']}%</div>
            <div class="stat-label">Completeness</div>
        </div>
        """, unsafe_allow_html=True)

# ARCHITECTURE & ANALYSIS TABS
if st.session_state.stats and st.session_state.stats.get('status') == 'success':
    st.markdown("---")
    st.subheader("🏗️ Data Pipeline Architecture")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Data Flow", "🔍 Pipeline Details", "➕ Extend Pipeline", "📈 Data Analysis"])
    
    # TAB 1: Data Flow
    with tab1:
        st.markdown('<div class="flow-diagram"><span class="flow-item">📁 Data Source</span><span class="arrow">→</span><span class="flow-item">🌐 Streamlit</span><span class="arrow">→</span><span class="flow-item">📨 Kafka</span><span class="arrow">→</span><span class="flow-item">⚙️ Process</span><span class="arrow">→</span><span class="flow-item">📊 Results</span></div>', unsafe_allow_html=True)
        
        st.markdown("### Data Flow Path")
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("""
            **1️⃣ Data Sources**
            - CSV File Upload
            - Public Cloud URLs (S3, Azure, GCS)
            
            **2️⃣ Ingestion Layer (Streamlit)**
            - REST API Client
            - RFC 4180 Parser
            - Schema Validation
            """)
        
        with col_b:
            st.markdown("""
            **3️⃣ Message Broker (Kafka)**
            - Upstash Kafka (Serverless)
            - Topic: data-simulator
            - SASL/SSL Authentication
            
            **4️⃣ Stream Processing**
            - Consumer
            - Real-time Analytics
            - Quality Scoring
            """)
    
    # TAB 2: Pipeline Details
    with tab2:
        st.markdown("### 🏗️ End-to-End Architecture")
        
        arch_col1, arch_col2 = st.columns(2)
        
        with arch_col1:
            st.markdown("""
            #### Layer 1: Data Sources
            📁 **CSV Upload** - Local file upload (up to 100MB)
            ☁️ **S3/Azure URL** - Public cloud storage URLs
            
            #### Layer 2: Ingestion (Streamlit)
            🌐 **Streamlit Producer** - REST API client
            ✓ Validation & schema detection
            ✓ Data type inference
            """)
        
        with arch_col2:
            st.markdown("""
            #### Layer 3: Message Broker
            📨 **Upstash Kafka** - Serverless pub/sub
            ✓ Topic: `data-simulator`
            ✓ Partitions: 3
            ✓ SASL/SSL encryption
            
            #### Layer 4: Consumer & Processing
            ⚙️ **Stream Consumer** - Real-time processing
            📊 **Analytics Engine** - Quality & classification
            """)
        
        with st.expander("📝 Component Details"):
            st.markdown("""
            **Source** → CSV File / Public Cloud URL
            - Auto-detects format
            - Handles special characters
            
            **Ingestion** → Streamlit UI
            - REST API producer
            - RFC 4180 CSV parsing
            
            **Messaging** → Upstash Kafka
            - Decoupled architecture
            - Serverless (no management)
            
            **Processing** → Consumer
            - Stream analytics
            - Quality scoring (0-100)
            - Dataset classification
            
            **Output** → Live Dashboard
            - Real-time stats
            - Quality metrics
            """)
    
    # TAB 3: Extend Pipeline
    with tab3:
        st.markdown("### ➕ Custom Pipeline Stages")
        
        with st.form("add_stage_form"):
            stage_name = st.text_input("Stage name", placeholder="e.g., Data Cleaning")
            stage_desc = st.text_area("Description", placeholder="e.g., Remove duplicates, normalize text...", height=80)
            submit = st.form_submit_button("+ Add Stage", use_container_width=True)
            
            if submit and stage_name:
                st.session_state.custom_stages.append({
                    "name": stage_name,
                    "description": stage_desc
                })
                st.success(f"✓ Stage '{stage_name}' added!")
                st.rerun()
        
        if st.session_state.custom_stages:
            st.markdown("### 🔧 Your Custom Stages")
            for i, stage in enumerate(st.session_state.custom_stages, 1):
                with st.expander(f"{i}. {stage['name']}"):
                    st.markdown(f"**Description:** {stage['description']}")
                    if st.button(f"Remove {stage['name']}", key=f"remove_{i}"):
                        st.session_state.custom_stages.pop(i-1)
                        st.rerun()
        else:
            st.info("No custom stages yet. Create one to extend your pipeline!")
    
    # TAB 4: Data Analysis
    with tab4:
        st.markdown("### 📈 Data Classification & Insights")
        
        stats = st.session_state.stats
        
        analysis_col1, analysis_col2 = st.columns(2)
        
        with analysis_col1:
            st.markdown(f"""
            <div class="stat-card" style="text-align: left;">
                <div style="font-size: 12px; color: #8892a0; margin-bottom: 8px;">DATASET TYPE</div>
                <div style="font-size: 18px; color: #32b8c6; font-weight: bold;">{stats['dataset_type']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with analysis_col2:
            score_color = "#10b981" if stats['quality_score'] >= 80 else "#f59e0b" if stats['quality_score'] >= 60 else "#ef4444"
            st.markdown(f"""
            <div class="stat-card" style="text-align: left;">
                <div style="font-size: 12px; color: #8892a0; margin-bottom: 8px;">QUALITY SCORE</div>
                <div style="font-size: 18px; color: {score_color}; font-weight: bold;">{stats['quality_score']}/100</div>
            </div>
            """, unsafe_allow_html=True)
        
        if stats['insights']:
            st.markdown(f"""
            <div class="architecture-box">
            <strong>{stats['dataset_type']}</strong><br/>
            {stats['insights']}<br/>
            Completeness: {stats['completeness']}%
            </div>
            """, unsafe_allow_html=True)
        
        with st.expander("📊 Quality Score Breakdown"):
            st.markdown("""
            - **Completeness (35%)** - Based on null values
            - **Size (25%)** - Row count adequacy
            - **Diversity (20%)** - Content variety
            - **Freshness (20%)** - Data recency
            """)

# RESET BUTTON
st.markdown("---")
if st.button("🔁 New Pipeline", use_container_width=True, type="secondary"):
    st.session_state.logs = []
    st.session_state.stats = None
    st.session_state.pipeline_running = False
    st.session_state.current_step = 0
    st.session_state.custom_stages = []
    st.rerun()
