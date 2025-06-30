# CSV File Processor App

A Streamlit application that processes DirectSkip contact data and Land Portal property data to generate specialized output files for RooR and ReadyMode marketing campaigns.

## 📋 Overview

This app merges two CSV files containing contact information and property data, then creates two specialized output files based on phone number types:
- **RooR.csv**: Contacts with mobile phone numbers
- **RM.csv**: Contacts with residential phone numbers + complete property data

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- Required packages: `streamlit`, `pandas`, `numpy`

### Installation
1. Save the app code as `app.py`
2. Install dependencies:
   ```bash
   pip install streamlit pandas numpy
   ```
3. Run the app:
   ```bash
   streamlit run app.py
   ```

## 📁 Input Files

### DirectSkip File
**Purpose**: Contains contact information with phone numbers and types

**Required Columns**:
- `Input Custom Field 1` - Property ID for matching with Land Portal
- `Matched First Name` - Contact's first name
- `Matched Last Name` - Contact's last name
- `Phone1`, `Phone2`, ..., `Phone7` - Phone numbers
- `Phone1 Type`, `Phone2 Type`, ..., `Phone7 Type` - Phone types ("Mobile" or "Residential")

**Sample Structure**:
```
Input Custom Field 1 | Matched First Name | Matched Last Name | Phone1     | Phone1 Type | Phone2     | Phone2 Type
121906837           | John               | Smith             | 6155551234 | Mobile      | 6155555678 | Residential
```

### Land Portal File
**Purpose**: Contains property data with coordinates and hyperlinks

**Required Columns**:
- `propertyID` - Matches with DirectSkip's `Input Custom Field 1`
- `Latitude`, `Longitude` - GPS coordinates for Google Maps URLs
- `Hyperlink` - Used as email field in RooR output
- `Parcel Full Address`, `Parcel City`, `Parcel State`, `Parcel Zip` - Property address
- `APN` - Assessor's Parcel Number
- `Parcel County` - Property county
- `Calc Acreage` - Property acreage
- **Plus 200+ additional property data columns**

## 📤 Output Files

### RooR.csv
**Purpose**: Mobile marketing campaigns

**Includes**: Only contacts with mobile phone numbers

**Column Structure** (exact order):
1. `FirstName` - From DirectSkip matched name
2. `LastName` - From DirectSkip matched name
3. `Email` - Land Portal hyperlink field
4. `PropertyAddress` - Land Portal parcel address
5. `PropertyCity` - Land Portal parcel city
6. `PropertyState` - Land Portal parcel state
7. `PropertyZip` - Land Portal parcel zip
8. `Phone1` - First mobile number
9. `Phone2` - Second mobile number
10. `Phone3` - Third mobile number
11. `APN` - Assessor's Parcel Number
12. `PropertyCounty` - Land Portal parcel county
13. `Acreage` - Land Portal calculated acreage

### RM.csv (ReadyMode)
**Purpose**: Residential phone marketing campaigns

**Includes**: Only contacts with residential phone numbers

**Column Structure**:
1. `Phone1` - First residential number
2. `Phone2` - Second residential number
3. `Phone3` - Third residential number
4. `Phone4` - Fourth residential number
5. `Google Maps URL` - Constructed from coordinates
6. **All Land Portal columns** - Complete property dataset (226 columns)

**Google Maps URL Format**:
```
http://maps.google.com/maps?z=16&t=m&q={Latitude},{Longitude}
```

## 🔧 Processing Logic

### File Merging
- Merges DirectSkip and Land Portal files on:
  - `Input Custom Field 1` (DirectSkip) = `propertyID` (Land Portal)
- Uses **inner join** - only includes records that exist in both files

### Phone Type Classification
- **Mobile**: Phone type exactly matches "Mobile" (case-insensitive)
- **Residential**: Phone type exactly matches "Residential" (case-insensitive)
- **Excluded**: "OtherPhone", "Pager", and other types are ignored

### Record Selection
- **RooR**: Records with at least 1 mobile phone number
- **ReadyMode**: Records with at least 1 residential phone number
- Records can appear in both files if they have both mobile and residential numbers

## 📊 Statistics Display

The app provides detailed processing statistics:

### Input File Statistics
- DirectSkip Records: Total uploaded contacts
- Land Portal Records: Total uploaded properties
- Successfully Merged: Records found in both files

### Phone Number Analysis
- Total Mobile Phones: All mobile numbers in DirectSkip data
- Total Residential Phones: All residential numbers in DirectSkip data

### Output File Results
- RooR Records: Contacts with mobile numbers
- ReadyMode Records: Contacts with residential numbers

## ⚠️ Important Notes

### Data Requirements
- **Case-sensitive headers**: Column names must match exactly
- **Missing data handling**: App handles NaN/empty values gracefully
- **Phone type matching**: Only exact "Mobile"/"Residential" matches are processed

### File Compatibility
- **CSV format only**: Both input files must be CSV
- **Dynamic columns**: Land Portal file can have changing column order and new fields
- **Large files supported**: Handles thousands of records efficiently

### Common Issues
- **Missing required columns**: App will display helpful error messages
- **Unmatched records**: Properties without contact data are excluded
- **Empty phone types**: Handled automatically without errors

## 🔍 Troubleshooting

### Upload Errors
- Ensure files are in CSV format
- Check that required columns exist and are spelled correctly
- Verify files aren't corrupted or empty

### Processing Errors
- Confirm DirectSkip file has `Input Custom Field 1` column
- Verify Land Portal file has `propertyID` column
- Check that matching values exist between the files

### Output Issues
- No RooR records: Check if any contacts have "Mobile" phone types
- No ReadyMode records: Check if any contacts have "Residential" phone types
- Missing data: Verify source files contain expected information

## 📈 Performance

- **Processing Speed**: Handles 3,000+ records in seconds
- **Memory Usage**: Efficient pandas operations for large datasets
- **File Size**: Output files sized based on phone type distribution

## 🛡️ Data Privacy

- **No data storage**: Files are processed in memory only
- **Session-based**: Data is cleared when browser session ends
- **Local processing**: All operations happen on your machine

## 📞 Support

For technical issues or feature requests, ensure you have:
1. Clear description of the problem
2. Sample input file headers (if applicable)
3. Error messages (if any)
4. Expected vs. actual output