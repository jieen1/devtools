import streamlit as st
import pandas as pd
import tabula
import io
import PyPDF2
import tempfile
import os
import re
import time
import logging
import pdfplumber
from typing import Dict, Any, List
from ..base import BaseTool, ToolResult

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('pdf_excel_tools')

class PDFToExcelConverter(BaseTool):
    """Convert PDF files to Excel format"""

    def execute(self, params: Dict[str, Any] = None) -> ToolResult:
        if not params or 'pdf_file' not in params:
            return ToolResult(success=False, message="Missing PDF file", data=None)

        pdf_file = params['pdf_file']
        extraction_method = params.get('extraction_method', 'tabula')
        pages = params.get('pages', 'all')
        password = params.get('password', '')
        merge_tables = params.get('merge_tables', False)
        
        logger.debug(f"Starting PDF conversion with parameters: extraction_method={extraction_method}, "
                    f"pages={pages}, merge_tables={merge_tables}")
        
        temp_excel_path = None
        excel_data = None
        
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_excel:
                temp_excel_path = temp_excel.name
                logger.debug(f"Created temporary Excel file: {temp_excel_path}")
                
            if extraction_method == 'tabula':
                # Use tabula for table extraction
                try:
                    logger.debug(f"Using tabula to extract tables from {pdf_file}")
                    if pages == 'all':
                        tables = tabula.read_pdf(
                            pdf_file, 
                            pages='all', 
                            multiple_tables=True,
                            password=password if password else None
                        )
                    else:
                        tables = tabula.read_pdf(
                            pdf_file, 
                            pages=pages, 
                            multiple_tables=True,
                            password=password if password else None
                        )
                    logger.debug(f"Extracted {len(tables)} tables from PDF")
                except Exception as e:
                    error_msg = str(e)
                    logger.error(f"Error in tabula extraction: {error_msg}")
                    if "password is incorrect" in error_msg:
                        return ToolResult(
                            success=False, 
                            message="This PDF is password protected. Please provide the correct password.", 
                            data=None
                        )
                    raise e
                
                if not tables:
                    logger.warning("No tables found in the PDF")
                    return ToolResult(
                        success=False, 
                        message="No tables found in the PDF", 
                        data=None
                    )
                
                # Process the tables
                if merge_tables and len(tables) > 0:
                    logger.debug("Attempting to merge tables")
                    
                    # Check for duplicate columns and make them unique
                    for i in range(len(tables)):
                        # Check if there are any duplicate column names
                        if tables[i].columns.duplicated().any():
                            logger.debug(f"Table {i+1} has duplicate columns, making them unique")
                            # Make columns unique by appending a suffix
                            tables[i].columns = self._make_unique_columns(tables[i].columns)
                    
                    try:
                        # Merge all tables into a single dataframe
                        logger.debug("Merging tables into a single DataFrame")
                        merged_df = pd.concat(tables, ignore_index=True)
                        logger.debug(f"Merged DataFrame has shape: {merged_df.shape}")
                        
                        # Write to Excel
                        logger.debug(f"Writing merged DataFrame to Excel: {temp_excel_path}")
                        with pd.ExcelWriter(temp_excel_path) as writer:
                            merged_df.to_excel(writer, sheet_name='Merged_Tables', index=False)
                            
                    except ValueError as e:
                        # If merging still fails, write each table to a separate sheet
                        error_msg = str(e)
                        logger.warning(f"Error merging tables: {error_msg}. Writing tables to separate sheets.")
                        with pd.ExcelWriter(temp_excel_path) as writer:
                            for i, table in enumerate(tables):
                                if not table.empty:
                                    # Ensure no duplicate column names
                                    if table.columns.duplicated().any():
                                        logger.debug(f"Table {i+1} has duplicate columns, making them unique")
                                        table.columns = self._make_unique_columns(table.columns)
                                    sheet_name = f'Table_{i+1}'
                                    if len(sheet_name) > 31:  # Excel sheet name length limit
                                        sheet_name = sheet_name[:31]
                                    logger.debug(f"Writing table {i+1} to sheet: {sheet_name}")
                                    table.to_excel(writer, sheet_name=sheet_name, index=False)
                            
                        return ToolResult(
                            success=True, 
                            data=self._read_excel_to_memory(temp_excel_path),
                            message=f"Tables could not be merged due to inconsistent structures. Each table has been saved as a separate sheet. Error: {error_msg}"
                        )
                else:
                    # Write each table to a separate sheet
                    logger.debug("Writing each table to a separate sheet")
                    with pd.ExcelWriter(temp_excel_path) as writer:
                        for i, table in enumerate(tables):
                            if not table.empty:
                                # Ensure no duplicate column names
                                if table.columns.duplicated().any():
                                    logger.debug(f"Table {i+1} has duplicate columns, making them unique")
                                    table.columns = self._make_unique_columns(table.columns)
                                sheet_name = f'Table_{i+1}'
                                if len(sheet_name) > 31:  # Excel sheet name length limit
                                    sheet_name = sheet_name[:31]
                                logger.debug(f"Writing table {i+1} to sheet: {sheet_name}")
                                table.to_excel(writer, sheet_name=sheet_name, index=False)
            
            elif extraction_method == 'pdfplumber':
                # Use pdfplumber for table extraction
                logger.debug(f"Using pdfplumber to extract tables from {pdf_file}")
                
                try:
                    tables = []
                    page_numbers = []
                    
                    with pdfplumber.open(pdf_file, password=password if password else None) as pdf:
                        if pages == 'all':
                            page_range = range(len(pdf.pages))
                        else:
                            # Convert pages string to list of page numbers
                            page_list = [int(p) for p in pages.split(',')]
                            page_range = [p-1 for p in page_list if 0 < p <= len(pdf.pages)]
                        
                        for page_num in page_range:
                            if page_num < len(pdf.pages):
                                page = pdf.pages[page_num]
                                extracted_tables = page.extract_tables()
                                
                                for table in extracted_tables:
                                    if table and len(table) > 0:
                                        # Use first row as header
                                        headers = table[0]
                                        data = table[1:]
                                        
                                        # Create DataFrame
                                        df = pd.DataFrame(data, columns=headers)
                                        
                                        # Clean up the DataFrame - remove empty rows and columns
                                        df = df.dropna(how='all').reset_index(drop=True)
                                        df = df.dropna(axis=1, how='all')
                                        
                                        # Add to tables list if not empty
                                        if not df.empty:
                                            tables.append(df)
                                            page_numbers.append(page_num + 1)
                    
                    logger.debug(f"Extracted {len(tables)} tables from PDF using pdfplumber")
                    
                    if not tables:
                        logger.warning("No tables found in the PDF with pdfplumber")
                        return ToolResult(
                            success=False, 
                            message="No tables found in the PDF using pdfplumber", 
                            data=None
                        )
                    
                    # Process the tables - similar to tabula section
                    if merge_tables and len(tables) > 0:
                        logger.debug("Attempting to merge tables")
                        
                        # Check for duplicate columns and make them unique
                        for i in range(len(tables)):
                            # Check if there are any duplicate column names
                            if tables[i].columns.duplicated().any():
                                logger.debug(f"Table {i+1} has duplicate columns, making them unique")
                                # Make columns unique by appending a suffix
                                tables[i].columns = self._make_unique_columns(tables[i].columns)
                        
                        try:
                            # Merge all tables into a single dataframe
                            logger.debug("Merging tables into a single DataFrame")
                            merged_df = pd.concat(tables, ignore_index=True)
                            logger.debug(f"Merged DataFrame has shape: {merged_df.shape}")
                            
                            # Write to Excel
                            logger.debug(f"Writing merged DataFrame to Excel: {temp_excel_path}")
                            with pd.ExcelWriter(temp_excel_path) as writer:
                                merged_df.to_excel(writer, sheet_name='Merged_Tables', index=False)
                                
                        except ValueError as e:
                            # If merging still fails, write each table to a separate sheet
                            error_msg = str(e)
                            logger.warning(f"Error merging tables: {error_msg}. Writing tables to separate sheets.")
                            with pd.ExcelWriter(temp_excel_path) as writer:
                                for i, table in enumerate(tables):
                                    if not table.empty:
                                        # Ensure no duplicate column names
                                        if table.columns.duplicated().any():
                                            logger.debug(f"Table {i+1} has duplicate columns, making them unique")
                                            table.columns = self._make_unique_columns(table.columns)
                                        sheet_name = f'Table_Page{page_numbers[i]}'
                                        if len(sheet_name) > 31:  # Excel sheet name length limit
                                            sheet_name = sheet_name[:31]
                                        logger.debug(f"Writing table {i+1} from page {page_numbers[i]} to sheet: {sheet_name}")
                                        table.to_excel(writer, sheet_name=sheet_name, index=False)
                                
                            return ToolResult(
                                success=True, 
                                data=self._read_excel_to_memory(temp_excel_path),
                                message=f"Tables could not be merged due to inconsistent structures. Each table has been saved as a separate sheet. Error: {error_msg}"
                            )
                    else:
                        # Write each table to a separate sheet
                        logger.debug("Writing each table to a separate sheet")
                        with pd.ExcelWriter(temp_excel_path) as writer:
                            for i, table in enumerate(tables):
                                if not table.empty:
                                    # Ensure no duplicate column names
                                    if table.columns.duplicated().any():
                                        logger.debug(f"Table {i+1} has duplicate columns, making them unique")
                                        table.columns = self._make_unique_columns(table.columns)
                                    sheet_name = f'Table_Page{page_numbers[i]}'
                                    if len(sheet_name) > 31:  # Excel sheet name length limit
                                        sheet_name = sheet_name[:31]
                                    logger.debug(f"Writing table {i+1} from page {page_numbers[i]} to sheet: {sheet_name}")
                                    table.to_excel(writer, sheet_name=sheet_name, index=False)
                    
                except Exception as e:
                    error_msg = str(e)
                    logger.error(f"Error in pdfplumber extraction: {error_msg}")
                    if "password" in error_msg.lower():
                        return ToolResult(
                            success=False, 
                            message="This PDF is password protected. Please provide the correct password.", 
                            data=None
                        )
                    raise e
            
            elif extraction_method == 'text':
                # Use PyPDF2 for text extraction
                try:
                    logger.debug(f"Using PyPDF2 to extract text from {pdf_file}")
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    
                    # Check if PDF is encrypted and try to decrypt
                    if pdf_reader.is_encrypted:
                        if not password:
                            return ToolResult(
                                success=False, 
                                message="This PDF is password protected. Please provide a password.", 
                                data=None
                            )
                        try:
                            pdf_reader.decrypt(password)
                        except Exception:
                            return ToolResult(
                                success=False, 
                                message="Incorrect password for the PDF file.", 
                                data=None
                            )
                    
                    all_text = []
                    page_labels = []
                    
                    if pages == 'all':
                        page_range = range(len(pdf_reader.pages))
                    else:
                        # Convert pages string to list of page numbers
                        page_list = [int(p) for p in pages.split(',')]
                        page_range = [p-1 for p in page_list if 0 < p <= len(pdf_reader.pages)]
                    
                    for page_num in page_range:
                        page = pdf_reader.pages[page_num]
                        all_text.append(page.extract_text())
                        page_labels.append(f'Page {page_num+1}')
                    
                    # Create DataFrame from text
                    df = pd.DataFrame({'Page': page_labels, 'Text': all_text})
                    
                    # Create a single sheet for text extraction, as merging is not relevant for text
                    logger.debug(f"Writing text to Excel: {temp_excel_path}")
                    with pd.ExcelWriter(temp_excel_path) as writer:
                        df.to_excel(writer, sheet_name='Text_Content', index=False)
                
                except Exception as e:
                    error_msg = str(e)
                    logger.error(f"Error extracting text from PDF: {error_msg}")
                    return ToolResult(
                        success=False, 
                        message=f"Error extracting text from PDF: {error_msg}", 
                        data=None
                    )
            
            else:
                return ToolResult(
                    success=False, 
                    message=f"Unsupported extraction method: {extraction_method}", 
                    data=None
                )
            
            # Read the Excel file into memory
            logger.debug(f"Reading Excel file into memory: {temp_excel_path}")
            excel_data = self._read_excel_to_memory(temp_excel_path)
            
            return ToolResult(
                success=True, 
                data=excel_data, 
                message="PDF successfully converted to Excel"
            )
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error converting PDF to Excel: {error_msg}")
            return ToolResult(
                success=False, 
                message=f"Error converting PDF to Excel: {error_msg}", 
                data=None
            )
        finally:
            # Clean up temp file in a safe way
            if temp_excel_path and os.path.exists(temp_excel_path):
                try:
                    os.unlink(temp_excel_path)
                except (PermissionError, OSError):
                    # If file is still in use, we'll just leave it for the OS to clean up later
                    pass
    
    def _read_excel_to_memory(self, excel_path):
        """
        Read an Excel file into memory as BytesIO object, with proper error handling
        """
        max_retries = 3
        retry_delay = 0.5
        
        for attempt in range(max_retries):
            try:
                with open(excel_path, 'rb') as f:
                    return io.BytesIO(f.read())
            except PermissionError:
                if attempt < max_retries - 1:
                    # Wait a bit before trying again
                    time.sleep(retry_delay)
                else:
                    raise
    
    def _make_unique_columns(self, columns):
        """
        Create unique column names by appending a suffix (_1, _2, etc.) to duplicates
        """
        seen = {}
        new_columns = []
        
        for col in columns:
            col_str = str(col)
            if col_str in seen:
                seen[col_str] += 1
                new_columns.append(f"{col_str}_{seen[col_str]}")
            else:
                seen[col_str] = 0
                new_columns.append(col_str)
                
        return new_columns

    def render_ui(self) -> None:
        st.write("## PDF to Excel Converter")
        st.write("Convert tables and text from PDF files to Excel format")
        
        uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
        
        col1, col2 = st.columns(2)
        
        with col1:
            extraction_method = st.selectbox(
                "Extraction Method", 
                ["tabula", "pdfplumber", "text"], 
                index=0,
                help="Tabula: Extract structured tables (requires Java). PDFPlumber: Alternative table extraction. Text: Extract all text content."
            )
        
        with col2:
            pages = st.text_input(
                "Pages", 
                value="all", 
                help="Specify pages to convert (e.g., '1,3,5-7' or 'all')"
            )
        
        # Add password field and merge tables option
        col3, col4 = st.columns(2)
        
        with col3:
            password = st.text_input(
                "PDF Password", 
                type="password",
                help="Enter password if the PDF is protected"
            )
        
        with col4:
            merge_tables = st.checkbox(
                "Merge All Tables",
                value=False,
                help="Merge all tables from all pages into a single sheet"
            )
        
        if uploaded_file is not None:
            # Save the uploaded file to a temporary location
            pdf_path = None
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
                    temp_pdf.write(uploaded_file.getvalue())
                    pdf_path = temp_pdf.name
                
                if st.button("Convert to Excel"):
                    with st.spinner("Converting PDF to Excel..."):
                        result = self.execute({
                            "pdf_file": pdf_path, 
                            "extraction_method": extraction_method,
                            "pages": pages,
                            "password": password,
                            "merge_tables": merge_tables
                        })
                    
                    if result.success:
                        st.success(result.message)
                        
                        # Create a download button for the Excel file
                        excel_data = result.data
                        if excel_data:
                            excel_data.seek(0)  # Reset the BytesIO pointer
                            
                            file_name = uploaded_file.name.replace(".pdf", ".xlsx")
                            st.download_button(
                                label="Download Excel File",
                                data=excel_data,
                                file_name=file_name,
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                    else:
                        st.error(result.message)
            finally:
                # Clean up temporary file
                if pdf_path and os.path.exists(pdf_path):
                    try:
                        os.unlink(pdf_path)
                    except (PermissionError, OSError):
                        # If file is still in use, we'll just leave it
                        pass
