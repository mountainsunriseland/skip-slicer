import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

def main():
    st.title("📊 SkipSlicer CSV File Processor")
    st.markdown("Upload DirectSkip and Land Portal CSV files to generate RooR and ReadyMode output files.")
    
    # File upload widgets
    st.header("📥 File Uploads")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("DirectSkip File")
        directskip_file = st.file_uploader(
            "Upload DirectSkip CSV file",
            type=['csv'],
            key="directskip",
            help="Contains contact information with phone numbers and types"
        )
    
    with col2:
        st.subheader("Land Portal File")
        landportal_file = st.file_uploader(
            "Upload Land Portal CSV file", 
            type=['csv'],
            key="landportal",
            help="Contains parcel data with propertyID, coordinates, and hyperlinks"
        )
    
    if directskip_file is not None and landportal_file is not None:
        try:
            # Read CSV files
            df_directskip = pd.read_csv(directskip_file)
            df_landportal = pd.read_csv(landportal_file)
            
            st.success("✅ Files uploaded successfully!")
            
            # Display file info
            with st.expander("📋 File Information"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**DirectSkip File:** {df_directskip.shape[0]} rows, {df_directskip.shape[1]} columns")
                    st.write("**Columns:**", list(df_directskip.columns))
                with col2:
                    st.write(f"**Land Portal File:** {df_landportal.shape[0]} rows, {df_landportal.shape[1]} columns")
                    st.write("**Columns:**", list(df_landportal.columns))
            
            # Validate required columns
            validation_errors = validate_columns(df_directskip, df_landportal)
            if validation_errors:
                st.error("❌ Missing required columns:")
                for error in validation_errors:
                    st.error(f"• {error}")
                return
            
            # Process the files
            with st.spinner("Processing files..."):
                roor_df, readymode_df, stats = process_files(df_directskip, df_landportal)
            
            # Display processing statistics
            st.header("📊 Processing Results")
            
            # Create metrics in a more organized layout
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📥 Input File Statistics")
                st.metric("DirectSkip Records", stats['directskip_records'])
                st.metric("Land Portal Records", stats['landportal_records'])
                st.metric("Successfully Merged", stats['total_merged'])
                
            with col2:
                st.subheader("📞 Phone Number Analysis")
                st.metric("Total Mobile Phones", stats['total_mobile_phones'])
                st.metric("Total Residential Phones", stats['total_residential_phones'])
                
            # Output file metrics
            st.subheader("📄 Output File Results")
            col3, col4 = st.columns(2)
            with col3:
                st.metric("RooR Records (Mobile)", stats['roor_count'])
            with col4:
                st.metric("ReadyMode Records (Residential)", stats['readymode_count'])
            
            # Download buttons
            st.header("💾 Download Processed Files")
            col1, col2 = st.columns(2)
            
            with col1:
                if not roor_df.empty:
                    roor_csv = convert_df_to_csv(roor_df)
                    st.download_button(
                        label="📥 Download RooR.csv",
                        data=roor_csv,
                        file_name="RooR.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                else:
                    st.warning("No records with Mobile phone types found for RooR file")
            
            with col2:
                if not readymode_df.empty:
                    readymode_csv = convert_df_to_csv(readymode_df)
                    st.download_button(
                        label="📥 Download RM.csv",
                        data=readymode_csv,
                        file_name="RM.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                else:
                    st.warning("No records with Residential phone types found for ReadyMode file")
            
            # Preview data
            with st.expander("👀 Preview Generated Files"):
                st.subheader("RooR File Preview")
                if not roor_df.empty:
                    st.dataframe(roor_df.head(10))
                else:
                    st.info("No RooR records to display")
                
                st.subheader("ReadyMode File Preview")
                if not readymode_df.empty:
                    st.dataframe(readymode_df.head(10))
                else:
                    st.info("No ReadyMode records to display")
                    
        except Exception as e:
            st.error(f"❌ Error processing files: {str(e)}")
            st.exception(e)

def validate_columns(df_directskip, df_landportal):
    """Validate that required columns exist in both dataframes"""
    errors = []
    
    # Required columns for DirectSkip
    directskip_required = ['Input Custom Field 1', 'Matched First Name', 'Matched Last Name']
    for col in directskip_required:
        if col not in df_directskip.columns:
            errors.append(f"DirectSkip file missing column: '{col}'")
    
    # Required columns for Land Portal
    landportal_required = ['propertyID', 'Latitude', 'Longitude', 'Hyperlink', 'Parcel Full Address', 
                          'Parcel City', 'Parcel State', 'Parcel Zip', 'APN', 'Parcel County', 'Calc Acreage']
    for col in landportal_required:
        if col not in df_landportal.columns:
            errors.append(f"Land Portal file missing column: '{col}'")
    
    # Check for phone columns in DirectSkip (Phone1, Phone2, etc.)
    phone_cols = [col for col in df_directskip.columns if col.startswith('Phone') and col[5:].isdigit()]
    if not phone_cols:
        errors.append("DirectSkip file missing phone number columns (Phone1, Phone2, etc.)")
    
    return errors

def get_phone_data(df):
    """Extract phone numbers and their types from the DirectSkip dataframe"""
    phone_data = []
    
    for _, row in df.iterrows():
        phones = {'mobile': [], 'residential': []}
        
        # Check main person phones (Phone1, Phone2, ..., Phone7)
        for i in range(1, 8):
            phone_col = f"Phone{i}"
            phone_type_col = f"Phone{i} Type"
            
            phone_num = row.get(phone_col)
            phone_type = row.get(phone_type_col, '')
            
            # Handle NaN/None values properly
            if pd.notna(phone_type):
                phone_type = str(phone_type).strip()
            else:
                phone_type = ''
            
            if pd.notna(phone_num) and phone_num != '':
                if phone_type.lower() == 'mobile':
                    phones['mobile'].append(str(int(phone_num)))
                elif phone_type.lower() == 'residential':
                    phones['residential'].append(str(int(phone_num)))
        
        phone_data.append(phones)
    
    return phone_data

def process_files(df_directskip, df_landportal):
    """Process the uploaded files and generate RooR and ReadyMode output files"""
    
    # Get initial counts
    directskip_count = len(df_directskip)
    landportal_count = len(df_landportal)
    
    # Store original Land Portal columns for RM file
    landportal_columns = df_landportal.columns.tolist()
    
    # Count total mobile and residential phones in DirectSkip
    total_mobile_phones = 0
    total_residential_phones = 0
    
    for _, row in df_directskip.iterrows():
        for i in range(1, 8):
            phone_num = row.get(f"Phone{i}")
            phone_type = row.get(f"Phone{i} Type", '')
            
            # Handle NaN/None values properly
            if pd.notna(phone_type):
                phone_type = str(phone_type).strip()
            else:
                phone_type = ''
            
            if pd.notna(phone_num) and phone_num != '':
                if phone_type.lower() == 'mobile':
                    total_mobile_phones += 1
                elif phone_type.lower() == 'residential':
                    total_residential_phones += 1
    
    # Merge the dataframes on the matching columns
    merged_df = pd.merge(
        df_directskip, 
        df_landportal, 
        left_on='Input Custom Field 1', 
        right_on='propertyID', 
        how='inner'
    )
    
    # Get phone data for each row
    phone_data = get_phone_data(merged_df)
    
    # Initialize output dataframes
    roor_records = []
    readymode_records = []
    
    for idx, (_, row) in enumerate(merged_df.iterrows()):
        phones = phone_data[idx]
        
        # RooR file - records with mobile phones
        if phones['mobile']:
            roor_record = create_roor_record(row, phones['mobile'])
            roor_records.append(roor_record)
        
        # ReadyMode file - records with residential phones
        if phones['residential']:
            readymode_record = create_readymode_record(row, phones['residential'], landportal_columns)
            readymode_records.append(readymode_record)
    
    # Create output dataframes
    roor_df = pd.DataFrame(roor_records) if roor_records else pd.DataFrame()
    readymode_df = pd.DataFrame(readymode_records) if readymode_records else pd.DataFrame()
    
    # Enhanced statistics
    stats = {
        'directskip_records': directskip_count,
        'landportal_records': landportal_count,
        'total_merged': len(merged_df),
        'total_mobile_phones': total_mobile_phones,
        'total_residential_phones': total_residential_phones,
        'roor_count': len(roor_records),
        'readymode_count': len(readymode_records)
    }
    
    return roor_df, readymode_df, stats

def create_roor_record(row, mobile_phones):
    """Create a RooR record with required columns in specified order"""
    record = {
        'FirstName': row.get('Matched First Name', ''),
        'LastName': row.get('Matched Last Name', ''),
        'Email': row.get('Hyperlink', ''),  # Using Hyperlink as Email field
        'PropertyAddress': row.get('Parcel Full Address', ''),
        'PropertyCity': row.get('Parcel City', ''),
        'PropertyState': row.get('Parcel State', ''),
        'PropertyZip': row.get('Parcel Zip', ''),
        'Phone1': str(int(float(mobile_phones[0]))) if len(mobile_phones) > 0 and mobile_phones[0] != '' else '',
        'Phone2': str(int(float(mobile_phones[1]))) if len(mobile_phones) > 1 and mobile_phones[1] != '' else '',
        'Phone3': str(int(float(mobile_phones[2]))) if len(mobile_phones) > 2 and mobile_phones[2] != '' else '',
        'APN': row.get('APN', ''),
        'PropertyCounty': row.get('Parcel County', ''),
        'Acreage': row.get('Calc Acreage', '')
    }
    return record

def create_readymode_record(row, residential_phones, landportal_columns):
    """Create a ReadyMode record with residential phones, Google Maps URL, and all Land Portal columns"""
    # Start with an ordered dictionary to maintain column order
    record = {}
    
    # Columns 1-4: Add residential phone numbers (up to 4)
    for i in range(4):
        phone_key = f'Phone{i+1}'
        if i < len(residential_phones):
            record[phone_key] = str(int(float(residential_phones[i]))) if residential_phones[i] != '' else ''
        else:
            record[phone_key] = ''
    
    # Column 5: Add Google Maps URL
    lat = row.get('Latitude', '')
    lon = row.get('Longitude', '')
    if pd.notna(lat) and pd.notna(lon) and lat != '' and lon != '':
        record['Google Maps URL'] = f"http://maps.google.com/maps?z=16&t=m&q={lat},{lon}"
    else:
        record['Google Maps URL'] = ''
    
    # Columns 6+: Add ALL Land Portal columns in their original order
    for col in landportal_columns:
        record[col] = row.get(col, '')
    
    return record

def convert_df_to_csv(df):
    """Convert dataframe to CSV string for download"""
    output = BytesIO()
    df.to_csv(output, index=False)
    return output.getvalue()

if __name__ == "__main__":
    st.set_page_config(
        page_title="CSV File Processor",
        page_icon="📊",
        layout="wide"
    )
    main()
