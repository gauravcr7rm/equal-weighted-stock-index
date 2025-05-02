import pandas as pd
import os
from datetime import date
from pathlib import Path
from app.services.data_storage import (
    get_index_performance,
    get_index_composition,
    get_composition_changes,
    get_trading_dates
)

# Ensure exports directory exists
exports_dir = Path("./exports")
exports_dir.mkdir(parents=True, exist_ok=True)

def export_index_data(start_date: date, end_date: date) -> str:
    """
    Export index data to Excel file.
    
    Args:
        start_date (date): Start date for export
        end_date (date): End date for export
        
    Returns:
        str: Path to the exported Excel file
    """
    # Convert dates to strings
    start_str = start_date.isoformat()
    end_str = end_date.isoformat()
    
    # Create Excel writer
    file_name = f"index_data_{start_str}_to_{end_str}.xlsx"
    file_path = os.path.join(exports_dir, file_name)
    
    writer = pd.ExcelWriter(file_path, engine='openpyxl')
    
    # Export index performance
    performance_data = get_index_performance(start_str, end_str)
    if performance_data:
        df_performance = pd.DataFrame(performance_data)
        df_performance.to_excel(writer, sheet_name='Index Performance', index=False)
        
        # Format the performance sheet
        workbook = writer.book
        worksheet = writer.sheets['Index Performance']
        
        # Format percentage columns
        for col in ['daily_return', 'cumulative_return']:
            col_idx = df_performance.columns.get_loc(col) + 1  # +1 because Excel is 1-indexed
            for row in range(2, len(df_performance) + 2):  # +2 for header and 1-indexing
                cell = worksheet.cell(row=row, column=col_idx)
                cell.number_format = '0.00%'
    
    # Export index compositions for each date
    trading_dates = get_trading_dates(start_str, end_str)
    
    if trading_dates:
        # Get the first and last date compositions for the sheet
        first_date = trading_dates[0]
        last_date = trading_dates[-1]
        
        first_composition = get_index_composition(first_date)
        last_composition = get_index_composition(last_date)
        
        if first_composition:
            df_first = pd.DataFrame(first_composition)
            df_first.to_excel(writer, sheet_name=f'Composition {first_date}', index=False)
        
        if last_composition and last_date != first_date:
            df_last = pd.DataFrame(last_composition)
            df_last.to_excel(writer, sheet_name=f'Composition {last_date}', index=False)
    
    # Export composition changes
    changes_data = get_composition_changes(start_str, end_str)
    if changes_data:
        # Prepare data for Excel
        changes_rows = []
        for change in changes_data:
            date_str = change['date']
            for ticker in change['added']:
                changes_rows.append({
                    'date': date_str,
                    'ticker': ticker,
                    'change_type': 'Added'
                })
            for ticker in change['removed']:
                changes_rows.append({
                    'date': date_str,
                    'ticker': ticker,
                    'change_type': 'Removed'
                })
        
        if changes_rows:
            df_changes = pd.DataFrame(changes_rows)
            df_changes.to_excel(writer, sheet_name='Composition Changes', index=False)
    
    # Save the Excel file
    writer.close()
    
    return file_path
