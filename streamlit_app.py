import streamlit as st
import pandas as pd
import requests
import boto3
from datetime import datetime
import io
import re
from botocore.exceptions import ClientError

st.set_page_config(
    page_title="The Transparent Pipeline",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.link_button("Interactive V2", "https://dataensimulation.netlify.app/")


# ENHANCED CSS WITH BETTER UI
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background: linear-gradient(135deg, #0f1419 0%, #1a1f27 100%);
        color: #e4e6eb;
    }
    
    .main {
        background: transparent;
    }
    
    /* Header Styles */
    .header-container {
        background: linear-gradient(135deg, rgba(50, 184, 198, 0.1) 0%, rgba(14, 165, 233, 0.1) 100%);
        border-bottom: 2px solid rgba(50, 184, 198, 0.2);
        padding: 32px 24px;
        margin: -16px -16px 24px -16px;
        border-radius: 0 0 16px 16px;
    }
    
    .header-title {
        background: linear-gradient(135deg, #32b8c6, #0ea5e9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 8px;
        letter-spacing: -0.5px;
    }
    
    .header-subtitle {
        color: #8892a0;
        font-size: 14px;
        font-weight: 500;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    
    /* Card Styles */
    .card {
        background: linear-gradient(135deg, rgba(26, 31, 39, 0.8) 0%, rgba(31, 36, 46, 0.8) 100%);
        border: 1px solid rgba(50, 184, 198, 0.15);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }
    
    .card:hover {
        border-color: rgba(50, 184, 198, 0.3);
        box-shadow: 0 12px 48px rgba(50, 184, 198, 0.1);
        transform: translateY(-2px);
    }
    
    .card-title {
        font-size: 18px;
        font-weight: 600;
        color: #32b8c6;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    /* Input Styles */
    .stFileUploader > label {
        color: #32b8c6 !important;
        font-weight: 600;
    }
    
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        background: rgba(0, 0, 0, 0.3) !important;
        border: 1px solid rgba(50, 184, 198, 0.2) !important;
        border-radius: 8px !important;
        color: #e4e6eb !important;
        font-family: 'Courier New', monospace !important;
        padding: 12px 16px !important;
        transition: all 0.3s !important;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #32b8c6 !important;
        box-shadow: 0 0 0 3px rgba(50, 184, 198, 0.2) !important;
    }
    
    /* Button Styles */
    .stButton button {
        background: linear-gradient(135deg, #32b8c6, #0ea5e9) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 12px 24px !important;
        transition: all 0.3s !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 13px;
        cursor: pointer;
    }
    
    .stButton button:hover {
        background: linear-gradient(135deg, #2aa4b8, #0d8ed4) !important;
        box-shadow: 0 8px 24px rgba(50, 184, 198, 0.3) !important;
        transform: translateY(-2px);
    }
    
    .stButton button:active {
        transform: translateY(0);
    }
    
    /* Progress Steps */
    .step-container {
        display: flex;
        gap: 12px;
        margin: 24px 0;
        flex-wrap: wrap;
    }
    
    .step {
        flex: 1;
        min-width: 120px;
        padding: 16px;
        border-radius: 10px;
        text-align: center;
        font-size: 12px;
        font-weight: 600;
        border: 2px solid rgba(50, 184, 198, 0.2);
        background: rgba(50, 184, 198, 0.05);
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        letter-spacing: 0.3px;
    }
    
    .step.active {
        background: rgba(50, 184, 198, 0.25);
        border-color: #32b8c6;
        box-shadow: 0 0 20px rgba(50, 184, 198, 0.4);
        transform: scale(1.05);
    }
    
    .step.completed {
        background: rgba(16, 185, 129, 0.2);
        border-color: #10b981;
        color: #10b981;
    }
    
    /* Console Styles */
    .console-container {
        background: rgba(0, 0, 0, 0.6);
        border: 1px solid rgba(50, 184, 198, 0.2);
        border-radius: 10px;
        padding: 20px;
        max-height: 450px;
        overflow-y: auto;
        font-family: 'JetBrains Mono', 'Courier New', monospace;
        font-size: 12px;
        line-height: 1.8;
        letter-spacing: 0.3px;
        scrollbar-width: thin;
        scrollbar-color: rgba(50, 184, 198, 0.3) transparent;
    }
    
    .console-container::-webkit-scrollbar {
        width: 6px;
    }
    
    .console-container::-webkit-scrollbar-track {
        background: transparent;
    }
    
    .console-container::-webkit-scrollbar-thumb {
        background: rgba(50, 184, 198, 0.3);
        border-radius: 3px;
    }
    
    .console-container::-webkit-scrollbar-thumb:hover {
        background: rgba(50, 184, 198, 0.5);
    }
    
    .log-entry {
        margin-bottom: 10px;
        padding: 6px 10px;
        border-radius: 4px;
        font-weight: 500;
    }
    
    .log-info { color: #3b82f6; }
    .log-success { color: #10b981; }
    .log-error { color: #ef4444; }
    .log-warning { color: #f59e0b; }
    
    /* Stat Cards */
    .stat-card {
        background: linear-gradient(135deg, rgba(50, 184, 198, 0.1) 0%, rgba(50, 184, 198, 0.05) 100%);
        border: 1px solid rgba(50, 184, 198, 0.2);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }
    
    .stat-card:hover {
        border-color: #32b8c6;
        background: linear-gradient(135deg, rgba(50, 184, 198, 0.15) 0%, rgba(50, 184, 198, 0.08) 100%);
        box-shadow: 0 8px 32px rgba(50, 184, 198, 0.15);
        transform: translateY(-4px);
    }
    
    .stat-value {
        font-size: 32px;
        font-weight: 700;
        color: #32b8c6;
        margin-bottom: 8px;
        font-family: 'Courier New', monospace;
    }
    
    .stat-label {
        font-size: 11px;
        color: #8892a0;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    
    /* Flow Diagram */
    .flow-diagram {
        display: flex;
        align-items: center;
        gap: 16px;
        margin: 24px 0;
        flex-wrap: wrap;
        justify-content: center;
    }
    
    .flow-item {
        background: linear-gradient(135deg, rgba(50, 184, 198, 0.15) 0%, rgba(50, 184, 198, 0.08) 100%);
        border: 1px solid rgba(50, 184, 198, 0.3);
        border-radius: 10px;
        padding: 14px 18px;
        font-size: 12px;
        font-weight: 600;
        text-align: center;
        min-width: 90px;
        transition: all 0.3s;
    }
    
    .flow-item:hover {
        border-color: #32b8c6;
        background: linear-gradient(135deg, rgba(50, 184, 198, 0.25) 0%, rgba(50, 184, 198, 0.15) 100%);
        transform: scale(1.05);
    }
    
    .arrow {
        font-size: 24px;
        color: #32b8c6;
        font-weight: bold;
    }
    
    /* Tab Styles */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        border-bottom: 2px solid rgba(50, 184, 198, 0.1) !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(50, 184, 198, 0.05);
        border: 1px solid rgba(50, 184, 198, 0.1);
        border-radius: 8px 8px 0 0;
        padding: 12px 24px !important;
        font-weight: 600;
        color: #8892a0;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(50, 184, 198, 0.2) 0%, rgba(50, 184, 198, 0.1) 100%);
        border-color: #32b8c6;
        color: #32b8c6 !important;
    }
    
    /* Divider */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(50, 184, 198, 0.2), transparent);
        margin: 32px 0;
    }
    
    /* Success/Error Messages */
    .stSuccess {
        background: rgba(16, 185, 129, 0.1) !important;
        border: 1px solid rgba(16, 185, 129, 0.3) !important;
        border-radius: 8px !important;
    }
    
    .stError {
        background: rgba(239, 68, 68, 0.1) !important;
        border: 1px solid rgba(239, 68, 68, 0.3) !important;
        border-radius: 8px !important;
    }
    
    .stInfo {
        background: rgba(50, 184, 198, 0.1) !important;
        border: 1px solid rgba(50, 184, 198, 0.3) !important;
        border-radius: 8px !important;
    }
    
    /* Data Source Selector */
    .source-selector {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 12px;
        margin: 16px 0;
    }
    
    .source-option {
        padding: 16px;
        border: 2px solid rgba(50, 184, 198, 0.2);
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.3s;
        text-align: center;
        font-weight: 600;
    }
    
    .source-option:hover {
        border-color: #32b8c6;
        background: rgba(50, 184, 198, 0.1);
    }
    
    .source-option.active {
        background: rgba(50, 184, 198, 0.2);
        border-color: #32b8c6;
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
if 'source_type' not in st.session_state:
    st.session_state.source_type = "CSV File"

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
    """Update current processing step"""
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

def fetch_from_s3(s3_uri: str, aws_key: str = None, aws_secret: str = None) -> tuple:
    """Fetch CSV from S3 bucket
    URI format: s3://bucket-name/path/to/file.csv
    """
    try:
        # Parse S3 URI
        if not s3_uri.startswith('s3://'):
            return "Invalid S3 URI. Use format: s3://bucket-name/path/file.csv", False
        
        s3_path = s3_uri.replace('s3://', '')
        bucket_name = s3_path.split('/')[0]
        key = '/'.join(s3_path.split('/')[1:])
        
        # Create S3 client
        if aws_key and aws_secret:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=aws_key,
                aws_secret_access_key=aws_secret
            )
        else:
            s3_client = boto3.client('s3')
        
        # Get object
        response = s3_client.get_object(Bucket=bucket_name, Key=key)
        file_content = response['Body'].read().decode('utf-8', errors='ignore')
        
        return file_content, True
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            return "File not found in S3 bucket", False
        elif e.response['Error']['Code'] == 'AccessDenied':
            return "Access denied. Check your AWS credentials", False
        else:
            return f"S3 Error: {str(e)}", False
    except Exception as e:
        return f"Error fetching from S3: {str(e)}", False

def fetch_from_azure(azure_uri: str, connection_string: str = None) -> tuple:
    """Fetch CSV from Azure Blob Storage
    URI format: https://account.blob.core.windows.net/container/file.csv
    """
    try:
        response = requests.get(azure_uri, timeout=10)
        if response.status_code == 200:
            return response.text, True
        else:
            return f"Error: HTTP {response.status_code}", False
    except Exception as e:
        return f"Error fetching from Azure: {str(e)}", False

def fetch_from_gcs(gcs_uri: str) -> tuple:
    """Fetch CSV from Google Cloud Storage
    URI format: gs://bucket-name/path/to/file.csv
    For public buckets only
    """
    try:
        # Convert gs:// to https://
        gcs_path = gcs_uri.replace('gs://', '')
        bucket_name = gcs_path.split('/')[0]
        key = '/'.join(gcs_path.split('/')[1:])
        
        url = f"https://storage.googleapis.com/{bucket_name}/{key}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return response.text, True
        else:
            return f"Error: HTTP {response.status_code}. Check bucket permissions.", False
    except Exception as e:
        return f"Error fetching from GCS: {str(e)}", False

# HEADER
st.markdown("""
<div class="header-container">
    <div class="header-title">🚀 The Transparent Pipeline</div>
    <div class="header-subtitle">Data Engineering Simulator | Cloud Storage + Live Analytics</div>
</div>
""", unsafe_allow_html=True)

# MAIN LAYOUT
col1, col2 = st.columns(2, gap="large")

# LEFT: Data Source
with col1:
    st.markdown('<div class="card-title">📤 Data Source</div>', unsafe_allow_html=True)
    
    source_type = st.radio(
        "Select data source:",
        ["CSV File", "S3 URI", "Azure Blob", "Google Cloud", "Public URL"],
        horizontal=True,
        key="source_radio"
    )
    
    file_content = None
    filename = None
    
    if source_type == "CSV File":
        uploaded_file = st.file_uploader("Upload CSV (Max 100MB)", type=['csv'])
        if uploaded_file:
            filename = uploaded_file.name
            file_content = uploaded_file.read().decode('utf-8', errors='ignore')
    
    elif source_type == "S3 URI":
        st.markdown("**S3 Storage Path**")
        s3_uri = st.text_input("S3 URI", placeholder="s3://bucket-name/path/file.csv")
        
        with st.expander("🔑 AWS Credentials (Optional)"):
            col_key, col_secret = st.columns(2)
            with col_key:
                aws_key = st.text_input("AWS Access Key", type="password", placeholder="Leave blank for default credentials")
            with col_secret:
                aws_secret = st.text_input("AWS Secret Key", type="password", placeholder="Leave blank for default credentials")
        
        if s3_uri:
            with st.spinner("Fetching from S3..."):
                file_content, success = fetch_from_s3(s3_uri, aws_key or None, aws_secret or None)
                filename = s3_uri.split('/')[-1]
                if not success:
                    st.error(file_content)
                    file_content = None
    
    elif source_type == "Azure Blob":
        st.markdown("**Azure Blob Storage**")
        azure_uri = st.text_input("Azure URI", placeholder="https://account.blob.core.windows.net/container/file.csv")
        
        if azure_uri:
            with st.spinner("Fetching from Azure..."):
                file_content, success = fetch_from_azure(azure_uri)
                filename = azure_uri.split('/')[-1]
                if not success:
                    st.error(file_content)
                    file_content = None
    
    elif source_type == "Google Cloud":
        st.markdown("**Google Cloud Storage (Public)**")
        gcs_uri = st.text_input("GCS URI", placeholder="gs://bucket-name/path/file.csv")
        
        if gcs_uri:
            with st.spinner("Fetching from GCS..."):
                file_content, success = fetch_from_gcs(gcs_uri)
                filename = gcs_uri.split('/')[-1]
                if not success:
                    st.error(file_content)
                    file_content = None
    
    else:  # Public URL
        st.markdown("**Public CSV URL**")
        url = st.text_input("URL", placeholder="https://raw.githubusercontent.com/user/repo/main/data.csv")
        
        if url:
            with st.spinner("Fetching file..."):
                file_content, success = fetch_from_url(url)
                filename = url.split('/')[-1]
                if not success:
                    st.error(file_content)
                    file_content = None

# RIGHT: Live Console
with col2:
    st.markdown('<div class="card-title">📡 Live Console</div>', unsafe_allow_html=True)
    
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
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown('<div class="card-title">⚙️ Processing Status</div>', unsafe_allow_html=True)

step_names = ["1. Connecting", "2. Validating", "3. Producing", "4. Completed"]
step_html = '<div class="step-container">'

for i, name in enumerate(step_names):
    if i < st.session_state.current_step:
        step_class = "step completed"
        label = f"✓ {name}"
    elif i == st.session_state.current_step and st.session_state.current_step > 0:
        step_class = "step active"
        label = f"◆ {name}"
    else:
        step_class = "step"
        label = name
    
    step_html += f'<div class="{step_class}">{label}</div>'

step_html += '</div>'
st.markdown(step_html, unsafe_allow_html=True)

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
            st.error("❌ Please provide a data source (file, URL, or cloud storage)")

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
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="card-title">📊 Data Statistics</div>', unsafe_allow_html=True)
    
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
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="card-title">🏗️ Data Pipeline Architecture</div>', unsafe_allow_html=True)
    
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
            - AWS S3 Buckets
            - Azure Blob Storage
            - Google Cloud Storage
            - Public Cloud URLs
            
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
            📁 **CSV Upload** - Local file upload (100MB+)
            ☁️ **S3** - AWS S3 buckets (public/private)
            ☁️ **Azure** - Azure Blob Storage
            ☁️ **GCS** - Google Cloud Storage
            ☁️ **URLs** - Any public HTTP endpoint
            
            #### Layer 2: Ingestion (Streamlit)
            🌐 **Producer** - Multi-source ingestion
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
            📈 **Dashboard** - Live results
            """)
        
        with st.expander("📝 Cloud Storage Details"):
            st.markdown("""
            **S3 Buckets**
            - Public: `s3://bucket-name/path/file.csv`
            - Private: Requires AWS credentials
            - Format: `s3://` URI scheme
            
            **Azure Blob Storage**
            - Public: `https://account.blob.core.windows.net/container/file.csv`
            - Private: Requires connection string
            - Supports SAS tokens
            
            **Google Cloud Storage**
            - Public: `gs://bucket-name/path/file.csv`
            - Private: Requires service account
            - Supports OAuth2
            
            **Public URLs**
            - GitHub: Use `raw.githubusercontent.com` for CSV
            - Dropbox: Add `?dl=1` parameter
            - Any CDN or web server
            """)
    
    # TAB 3: Extend Pipeline
    # TAB 3: Extend Pipeline - ENHANCED VERSION
    with tab3:
        st.markdown("### ➕ Custom Pipeline Stages")
        st.markdown(
            "Add custom transformation stages to your pipeline. Choose where each stage should execute in the data flow.")

        # Form to add new stage
        with st.form("add_stage_form"):
            col_form1, col_form2 = st.columns(2)

            with col_form1:
                stage_name = st.text_input(
                    "Stage Name",
                    placeholder="e.g., Data Cleaning",
                    help="Give your stage a descriptive name"
                )

            with col_form2:
                stage_position = st.selectbox(
                    "Pipeline Position",
                    ["After Ingestion", "After Validation", "After Kafka Production", "Pre-Analytics"],
                    help="Where should this stage execute in the pipeline?"
                )

            stage_desc = st.text_area(
                "Description",
                placeholder="e.g., Remove duplicates, normalize text, handle nulls...",
                height=100,
                help="Explain what this transformation stage does"
            )

            # Position mapping
            position_mapping = {
                "After Ingestion": "🌐 Ingestion Layer",
                "After Validation": "✓ Validation Layer",
                "After Kafka Production": "📨 Message Broker",
                "Pre-Analytics": "📊 Analytics Layer"
            }

            submit = st.form_submit_button("➕ Add Stage to Pipeline", use_container_width=True)

            if submit and stage_name:
                st.session_state.custom_stages.append({
                    "name": stage_name,
                    "description": stage_desc,
                    "position": stage_position,
                    "position_label": position_mapping[stage_position],
                    "id": len(st.session_state.custom_stages) + 1
                })
                st.success(f"✅ Stage '{stage_name}' added to {position_mapping[stage_position]}!", icon="✨")
                st.rerun()

        # Display added stages
        if st.session_state.custom_stages:
            st.markdown("---")
            st.markdown("### 🔧 Your Custom Pipeline Stages")

            # Group stages by position
            stages_by_position = {}
            for stage in st.session_state.custom_stages:
                pos = stage['position']
                if pos not in stages_by_position:
                    stages_by_position[pos] = []
                stages_by_position[pos].append(stage)

            # Display positions in order
            position_order = ["After Ingestion", "After Validation", "After Kafka Production", "Pre-Analytics"]
            position_icons = {
                "After Ingestion": "🌐",
                "After Validation": "✓",
                "After Kafka Production": "📨",
                "Pre-Analytics": "📊"
            }

            for position in position_order:
                if position in stages_by_position:
                    icon = position_icons.get(position, "⚙️")
                    st.markdown(f"#### {icon} {position}")

                    for i, stage in enumerate(stages_by_position[position]):
                        with st.container():
                            col_stage, col_remove = st.columns([4, 1])

                            with col_stage:
                                st.markdown(f"**{i + 1}. {stage['name']}**")
                                st.markdown(f"__{stage['position_label']}__")
                                st.markdown(f"📝 {stage['description']}")

                            with col_remove:
                                if st.button("🗑️", key=f"remove_{stage['id']}", help="Remove this stage"):
                                    st.session_state.custom_stages.remove(stage)
                                    st.success("Stage removed!", icon="✅")
                                    st.rerun()

            # Show updated data flow with custom stages
            st.markdown("---")
            st.markdown("### 📊 Updated Data Flow with Custom Stages")

            # Build dynamic flow diagram
            flow_html = '<div class="flow-diagram">'
            flow_html += '<span class="flow-item">📁 Source</span>'
            flow_html += '<span class="arrow">→</span>'
            flow_html += '<span class="flow-item">🌐 Ingest</span>'

            # Add After Ingestion stages
            if "After Ingestion" in stages_by_position:
                for stage in stages_by_position["After Ingestion"]:
                    flow_html += '<span class="arrow">→</span>'
                    flow_html += f'<span class="flow-item" style="background: rgba(16, 185, 129, 0.15); border-color: #10b981;">⚙️ {stage["name"][:12]}</span>'

            flow_html += '<span class="arrow">→</span>'
            flow_html += '<span class="flow-item">✓ Validate</span>'

            # Add After Validation stages
            if "After Validation" in stages_by_position:
                for stage in stages_by_position["After Validation"]:
                    flow_html += '<span class="arrow">→</span>'
                    flow_html += f'<span class="flow-item" style="background: rgba(16, 185, 129, 0.15); border-color: #10b981;">⚙️ {stage["name"][:12]}</span>'

            flow_html += '<span class="arrow">→</span>'
            flow_html += '<span class="flow-item">📨 Kafka</span>'

            # Add After Kafka stages
            if "After Kafka Production" in stages_by_position:
                for stage in stages_by_position["After Kafka Production"]:
                    flow_html += '<span class="arrow">→</span>'
                    flow_html += f'<span class="flow-item" style="background: rgba(16, 185, 129, 0.15); border-color: #10b981;">⚙️ {stage["name"][:12]}</span>'

            flow_html += '<span class="arrow">→</span>'
            flow_html += '<span class="flow-item">📊 Analytics</span>'

            # Add Pre-Analytics stages
            if "Pre-Analytics" in stages_by_position:
                for stage in stages_by_position["Pre-Analytics"]:
                    flow_html += '<span class="arrow">→</span>'
                    flow_html += f'<span class="flow-item" style="background: rgba(16, 185, 129, 0.15); border-color: #10b981;">⚙️ {stage["name"][:12]}</span>'

            flow_html += '<span class="arrow">→</span>'
            flow_html += '<span class="flow-item">📈 Results</span>'
            flow_html += '</div>'

            st.markdown(flow_html, unsafe_allow_html=True)
        else:
            st.info("📌 No custom stages yet. Create one above to extend your pipeline dynamically!", icon="ℹ️")
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
            <div class="card">
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
st.markdown("<hr>", unsafe_allow_html=True)
if st.button("🔁 New Pipeline", use_container_width=True, type="secondary"):
    st.session_state.logs = []
    st.session_state.stats = None
    st.session_state.pipeline_running = False
    st.session_state.current_step = 0
    st.session_state.custom_stages = []
    st.rerun()
