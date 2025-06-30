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
    
    st.title("🌍 IP Location Checker")
    st.markdown("Upload your CSV to find users with mismatched claimed vs actual locations")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a CSV file", 
        type="csv",
        help="Upload your CSV file with country codes in column F and country names in column G"
    )
    
    if uploaded_file is not None:
        try:
            # Read the CSV
            df = pd.read_csv(uploaded_file)
            
            st.success(f"✅ File uploaded successfully! Found {len(df)} total records")
            
            # Show data preview
            with st.expander("📋 Data Preview (First 5 rows)", expanded=False):
                st.dataframe(df.head())
            
            # Show column info
            st.write("**Column Structure:**")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"• Column F (Country Codes): `{df.columns[5] if len(df.columns) > 5 else 'N/A'}`")
            with col2:
                st.write(f"• Column G (Country Names): `{df.columns[6] if len(df.columns) > 6 else 'N/A'}`")
            
            # Process button
            if st.button("🔍 Check for Location Discrepancies", type="primary"):
                with st.spinner("Processing data..."):
                    suspect_df, processed_df = process_data(df)
                
                # Display results
                st.markdown("---")
                
                if len(suspect_df) > 0:
                    st.error(f"⚠️ Found {len(suspect_df)} suspect users with location mismatches!")
                    
                    # Show suspect entries
                    st.markdown("### 🚨 Suspect Users")
                    st.dataframe(suspect_df, use_container_width=True)
                    
                    # Prepare download
                    output = BytesIO()
                    suspect_df.to_csv(output, index=False)
                    output.seek(0)
                    
                    # Download button
                    st.download_button(
                        label="📥 Download Suspect Users CSV",
                        data=output.getvalue(),
                        file_name="suspect_users.csv",
                        mime="text/csv",
                        type="primary"
                    )
                    
                    # Show some examples of mismatches
                    st.markdown("### 📊 Example Mismatches")
                    for idx, row in suspect_df.head(3).iterrows():
                        country_code = row.iloc[5] if len(row) > 5 else 'N/A'  # Column F
                        country_name = row.iloc[6] if len(row) > 6 else 'N/A'  # Column G
                        mapped_name = get_country_name_from_code(country_code)
                        
                        st.write(f"• **{country_code}** (maps to: {mapped_name}) vs **{country_name}** ❌")
                
                else:
                    st.success("🎉 No location discrepancies found! All users have matching locations.")
                    st.balloons()
        
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            st.info("Please make sure your CSV has the correct format with country codes in column F and country names in column G")
    
    else:
        st.info("👆 Please upload a CSV file to get started")
        
        # Show example data format
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
        st.dataframe(example_df)
        st.caption("⚠️ The third row shows a mismatch: SI (Slovenia) vs United Arab Emirates")

if __name__ == "__main__":
    main()
