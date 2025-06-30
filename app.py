import streamlit as st
import pandas as pd
import pycountry
from io import BytesIO

def get_country_name_from_code(country_code):
    """Convert country code to country name using pycountry"""
    if pd.isna(country_code) or country_code == '':
        return None
    
    try:
        # Handle different code formats
        country_code = str(country_code).strip().upper()
        
        # Try alpha-2 code first (GB, FR, etc.)
        try:
            country = pycountry.countries.get(alpha_2=country_code)
            if country:
                return country.name
        except:
            pass
        
        # Try alpha-3 code (GBR, FRA, etc.)
        try:
            country = pycountry.countries.get(alpha_3=country_code)
            if country:
                return country.name
        except:
            pass
        
        # If no match found, return None
        return None
        
    except:
        return None

def process_data(df):
    """Process the dataframe to find country mismatches"""
    
    # Create a copy to avoid modifying original
    df_processed = df.copy()
    
    # Map country codes to names (column F has codes, column G has names)
    df_processed['mapped_country_name'] = df_processed.iloc[:, 5].apply(get_country_name_from_code)  # Column F (index 5)
    
    # Get the actual country names from column G (index 6)
    actual_countries = df_processed.iloc[:, 6].astype(str).str.strip()  # Column G
    mapped_countries = df_processed['mapped_country_name'].astype(str).str.strip()
    
    # Find mismatches (where mapped country name doesn't match actual country name)
    mismatches = (mapped_countries != actual_countries) & (mapped_countries != 'None') & (actual_countries != 'nan')
    
    # Filter for suspect entries
    suspect_df = df_processed[mismatches].copy()
    
    # Drop the helper column from the final result
    if 'mapped_country_name' in suspect_df.columns:
        suspect_df = suspect_df.drop('mapped_country_name', axis=1)
    
    return suspect_df, df_processed

def main():
    st.set_page_config(page_title="IP Location Checker", layout="wide")
    
    # Custom CSS for professional styling
    st.markdown("""
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        /* Global Styles */
        .main .block-container {
            padding-top: 2rem;
            max-width: 1000px;
        }
        
        /* Header Styling */
        .main-header {
            font-family: 'Inter', sans-serif;
            font-size: 2.5rem;
            font-weight: 700;
            color: #1e293b;
            text-align: center;
            margin-bottom: 0.5rem;
        }
        
        .sub-header {
            font-family: 'Inter', sans-serif;
            font-size: 1.1rem;
            color: #64748b;
            text-align: center;
            margin-bottom: 3rem;
        }
        
        /* Upload Area Styling */
        .upload-container {
            background: #f8fafc;
            border: 2px dashed #3b82f6;
            border-radius: 12px;
            padding: 3rem 2rem;
            text-align: center;
            margin: 2rem 0;
            transition: all 0.3s ease;
        }
        
        .upload-container:hover {
            border-color: #2563eb;
            background: #f1f5f9;
        }
        
        /* Button Styling */
        .stButton > button {
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.75rem 2rem;
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.3);
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            transform: translateY(-1px);
            box-shadow: 0 6px 12px -1px rgba(59, 130, 246, 0.4);
        }
        
        /* Success/Error Message Styling */
        .stSuccess {
            background: #f0f9ff;
            border: 1px solid #0ea5e9;
            border-radius: 8px;
            padding: 1rem;
        }
        
        .stError {
            background: #fef2f2;
            border: 1px solid #ef4444;
            border-radius: 8px;
            padding: 1rem;
        }
        
        /* Card Styling */
        .info-card {
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        }
        
        /* Data Preview Styling */
        .stDataFrame {
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            overflow: hidden;
        }
        
        /* Download Button Special Styling */
        .download-btn {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.75rem 2rem;
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            margin: 1rem 0;
        }
        
        /* Progress indicators */
        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, #3b82f6, #2563eb);
        }
        
        /* Example table styling */
        .example-table {
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            overflow: hidden;
            margin: 1rem 0;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)
    
    # Main header with custom styling
    st.markdown('<h1 class="main-header">🌍 IP Location Checker</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Upload your CSV to find users with mismatched claimed vs actual locations</p>', unsafe_allow_html=True)
    
    # File upload with custom styling
    st.markdown('<div class="upload-container">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Choose a CSV file", 
        type="csv",
        help="Upload your CSV file with country codes in column F and country names in column G",
        label_visibility="collapsed"
    )
    if not uploaded_file:
        st.markdown("""
        <div style="text-align: center; color: #64748b; margin-top: 1rem;">
            <p style="font-size: 1.1rem; font-weight: 500;">Select a file to upload</p>
            <p style="font-size: 0.9rem;">Supported format: CSV (100MB Max)</p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    if uploaded_file is not None:
        try:
            # Read the CSV
            df = pd.read_csv(uploaded_file)
            
            st.markdown(f'<div class="info-card">', unsafe_allow_html=True)
            st.success(f"✅ File uploaded successfully! Found {len(df)} total records")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Show data preview
            with st.expander("📋 Data Preview (First 5 rows)", expanded=False):
                st.dataframe(df.head(), use_container_width=True)
            
            # Show column info in styled card
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.markdown("**📊 Column Structure:**")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"• **Column F (Country Codes):** `{df.columns[5] if len(df.columns) > 5 else 'N/A'}`")
            with col2:
                st.markdown(f"• **Column G (Country Names):** `{df.columns[6] if len(df.columns) > 6 else 'N/A'}`")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Process button
            if st.button("🔍 Check for Location Discrepancies", type="primary"):
                with st.spinner("Processing data..."):
                    suspect_df, processed_df = process_data(df)
                
                # Display results
                st.markdown("---")
                
                if len(suspect_df) > 0:
                    st.markdown(f"""
                    <div class="info-card" style="border-left: 4px solid #ef4444;">
                        <h3 style="color: #ef4444; margin-top: 0;">⚠️ Found {len(suspect_df)} suspect users with location mismatches!</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show suspect entries
                    st.markdown("### 🚨 Suspect Users")
                    st.dataframe(suspect_df, use_container_width=True)
                    
                    # Prepare download
                    output = BytesIO()
                    suspect_df.to_csv(output, index=False)
                    output.seek(0)
                    
                    # Download button with custom styling
                    st.download_button(
                        label="📥 Download Suspect Users CSV",
                        data=output.getvalue(),
                        file_name="suspect_users.csv",
                        mime="text/csv",
                        type="primary",
                        use_container_width=True
                    )
                    
                    # Show some examples of mismatches in a styled card
                    st.markdown('<div class="info-card">', unsafe_allow_html=True)
                    st.markdown("### 📊 Example Mismatches")
                    for idx, row in suspect_df.head(3).iterrows():
                        country_code = row.iloc[5] if len(row) > 5 else 'N/A'  # Column F
                        country_name = row.iloc[6] if len(row) > 6 else 'N/A'  # Column G
                        mapped_name = get_country_name_from_code(country_code)
                        
                        st.markdown(f"• **{country_code}** (maps to: {mapped_name}) vs **{country_name}** ❌")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                else:
                    st.markdown("""
                    <div class="info-card" style="border-left: 4px solid #10b981;">
                        <h3 style="color: #10b981; margin-top: 0;">🎉 No location discrepancies found!</h3>
                        <p>All users have matching locations.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.balloons()
        
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            st.info("Please make sure your CSV has the correct format with country codes in column F and country names in column G")
    
    else:
        st.markdown("""
        <div class="info-card" style="text-align: center; padding: 2rem;">
            <p style="font-size: 1.1rem; color: #64748b; margin-bottom: 2rem;">👆 Please upload a CSV file to get started</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show example data format in styled card
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("### 📝 Expected Data Format")
        example_data = {
            'Column A': ['Data 1', 'Data 2', 'Data 3'],
            'Column B': ['Data 1', 'Data 2', 'Data 3'], 
            'Column C': ['Data 1', 'Data 2', 'Data 3'],
            'Column D': ['Data 1', 'Data 2', 'Data 3'],
            'Column E': ['Data 1', 'Data 2', 'Data 3'],
            'Country Code (F)': ['FR', 'GB', 'SI'],
            'Country Name (G)': ['France', 'United Kingdom', 'United Arab Emirates']
        }
        example_df = pd.DataFrame(example_data)
        st.dataframe(example_df, use_container_width=True)
        st.markdown("⚠️ *The third row shows a mismatch: SI (Slovenia) vs United Arab Emirates*")
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
