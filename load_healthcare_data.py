"""
Healthcare Data Loading Script
================================
This script provides utilities for loading and validating healthcare data
from various file formats (CSV, Excel, JSON, etc.)

Author: Rakesh824
Date: 2026-08-24
"""

import pandas as pd
import numpy as np
import warnings
from pathlib import Path
from typing import Union, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

warnings.filterwarnings('ignore')


class HealthcareDataLoader:
    """
    A comprehensive class for loading and preprocessing healthcare data.
    Supports multiple file formats and provides data validation capabilities.
    """
    
    def __init__(self, data_path: Union[str, Path], verbose: bool = True):
        """
        Initialize the HealthcareDataLoader.
        
        Args:
            data_path (Union[str, Path]): Path to the data file or directory
            verbose (bool): Enable verbose logging
        """
        self.data_path = Path(data_path)
        self.verbose = verbose
        self.data = None
        self.metadata = {}
        
        if self.verbose:
            logger.info(f"Initialized HealthcareDataLoader with path: {self.data_path}")
    
    def load_csv(self, filename: str, encoding: str = 'utf-8', 
                 **kwargs) -> pd.DataFrame:
        """
        Load data from CSV file.
        
        Args:
            filename (str): Name of the CSV file
            encoding (str): File encoding (default: 'utf-8')
            **kwargs: Additional arguments to pass to pd.read_csv()
            
        Returns:
            pd.DataFrame: Loaded healthcare data
        """
        try:
            file_path = self.data_path / filename if self.data_path.is_dir() else self.data_path
            self.data = pd.read_csv(file_path, encoding=encoding, **kwargs)
            
            if self.verbose:
                logger.info(f"Successfully loaded CSV: {filename}")
                logger.info(f"Shape: {self.data.shape}")
            
            self._update_metadata('csv', filename)
            return self.data
        
        except FileNotFoundError:
            logger.error(f"File not found: {filename}")
            raise
        except Exception as e:
            logger.error(f"Error loading CSV file: {str(e)}")
            raise
    
    def load_excel(self, filename: str, sheet_name: str = 0, 
                   **kwargs) -> pd.DataFrame:
        """
        Load data from Excel file.
        
        Args:
            filename (str): Name of the Excel file
            sheet_name (str or int): Sheet name or index (default: 0)
            **kwargs: Additional arguments to pass to pd.read_excel()
            
        Returns:
            pd.DataFrame: Loaded healthcare data
        """
        try:
            file_path = self.data_path / filename if self.data_path.is_dir() else self.data_path
            self.data = pd.read_excel(file_path, sheet_name=sheet_name, **kwargs)
            
            if self.verbose:
                logger.info(f"Successfully loaded Excel: {filename} (Sheet: {sheet_name})")
                logger.info(f"Shape: {self.data.shape}")
            
            self._update_metadata('excel', filename)
            return self.data
        
        except FileNotFoundError:
            logger.error(f"File not found: {filename}")
            raise
        except Exception as e:
            logger.error(f"Error loading Excel file: {str(e)}")
            raise
    
    def load_json(self, filename: str, **kwargs) -> pd.DataFrame:
        """
        Load data from JSON file.
        
        Args:
            filename (str): Name of the JSON file
            **kwargs: Additional arguments to pass to pd.read_json()
            
        Returns:
            pd.DataFrame: Loaded healthcare data
        """
        try:
            file_path = self.data_path / filename if self.data_path.is_dir() else self.data_path
            self.data = pd.read_json(file_path, **kwargs)
            
            if self.verbose:
                logger.info(f"Successfully loaded JSON: {filename}")
                logger.info(f"Shape: {self.data.shape}")
            
            self._update_metadata('json', filename)
            return self.data
        
        except FileNotFoundError:
            logger.error(f"File not found: {filename}")
            raise
        except Exception as e:
            logger.error(f"Error loading JSON file: {str(e)}")
            raise
    
    def load_parquet(self, filename: str, **kwargs) -> pd.DataFrame:
        """
        Load data from Parquet file.
        
        Args:
            filename (str): Name of the Parquet file
            **kwargs: Additional arguments to pass to pd.read_parquet()
            
        Returns:
            pd.DataFrame: Loaded healthcare data
        """
        try:
            file_path = self.data_path / filename if self.data_path.is_dir() else self.data_path
            self.data = pd.read_parquet(file_path, **kwargs)
            
            if self.verbose:
                logger.info(f"Successfully loaded Parquet: {filename}")
                logger.info(f"Shape: {self.data.shape}")
            
            self._update_metadata('parquet', filename)
            return self.data
        
        except FileNotFoundError:
            logger.error(f"File not found: {filename}")
            raise
        except Exception as e:
            logger.error(f"Error loading Parquet file: {str(e)}")
            raise
    
    def get_data_info(self) -> dict:
        """
        Get comprehensive information about loaded data.
        
        Returns:
            dict: Dictionary containing data information
        """
        if self.data is None:
            logger.warning("No data loaded yet")
            return {}
        
        info = {
            'shape': self.data.shape,
            'columns': list(self.data.columns),
            'dtypes': self.data.dtypes.to_dict(),
            'missing_values': self.data.isnull().sum().to_dict(),
            'duplicate_rows': self.data.duplicated().sum(),
            'memory_usage_mb': self.data.memory_usage(deep=True).sum() / 1024**2
        }
        
        return info
    
    def validate_data(self) -> dict:
        """
        Validate loaded healthcare data.
        
        Returns:
            dict: Validation report
        """
        if self.data is None:
            logger.warning("No data to validate")
            return {}
        
        validation_report = {
            'total_rows': len(self.data),
            'total_columns': len(self.data.columns),
            'missing_values': self.data.isnull().sum().sum(),
            'duplicate_rows': self.data.duplicated().sum(),
            'columns_with_missing': self.data.columns[self.data.isnull().any()].tolist(),
            'numeric_columns': self.data.select_dtypes(include=['number']).columns.tolist(),
            'categorical_columns': self.data.select_dtypes(include=['object']).columns.tolist()
        }
        
        if self.verbose:
            logger.info("Data Validation Report:")
            for key, value in validation_report.items():
                logger.info(f"  {key}: {value}")
        
        return validation_report
    
    def handle_missing_values(self, strategy: str = 'drop', 
                             fill_value: Optional[Union[int, str]] = None) -> pd.DataFrame:
        """
        Handle missing values in the data.
        
        Args:
            strategy (str): 'drop', 'mean', 'median', 'mode', or 'forward_fill'
            fill_value (Optional): Value to use for filling (for custom fill)
            
        Returns:
            pd.DataFrame: Data with handled missing values
        """
        if self.data is None:
            logger.error("No data loaded")
            return None
        
        try:
            data_copy = self.data.copy()
            
            if strategy == 'drop':
                data_copy = data_copy.dropna()
                if self.verbose:
                    logger.info(f"Dropped rows with missing values. New shape: {data_copy.shape}")
            
            elif strategy == 'mean':
                numeric_cols = data_copy.select_dtypes(include=['number']).columns
                data_copy[numeric_cols] = data_copy[numeric_cols].fillna(data_copy[numeric_cols].mean())
                if self.verbose:
                    logger.info("Filled numeric columns with mean values")
            
            elif strategy == 'median':
                numeric_cols = data_copy.select_dtypes(include=['number']).columns
                data_copy[numeric_cols] = data_copy[numeric_cols].fillna(data_copy[numeric_cols].median())
                if self.verbose:
                    logger.info("Filled numeric columns with median values")
            
            elif strategy == 'mode':
                for col in data_copy.columns:
                    data_copy[col].fillna(data_copy[col].mode()[0], inplace=True)
                if self.verbose:
                    logger.info("Filled columns with mode values")
            
            elif strategy == 'forward_fill':
                data_copy = data_copy.fillna(method='ffill')
                if self.verbose:
                    logger.info("Applied forward fill strategy")
            
            elif fill_value is not None:
                data_copy = data_copy.fillna(fill_value)
                if self.verbose:
                    logger.info(f"Filled missing values with: {fill_value}")
            
            self.data = data_copy
            return self.data
        
        except Exception as e:
            logger.error(f"Error handling missing values: {str(e)}")
            raise
    
    def remove_duplicates(self, subset: Optional[list] = None) -> pd.DataFrame:
        """
        Remove duplicate rows from the data.
        
        Args:
            subset (Optional[list]): Column names to consider for duplicates
            
        Returns:
            pd.DataFrame: Data with duplicates removed
        """
        if self.data is None:
            logger.error("No data loaded")
            return None
        
        try:
            initial_count = len(self.data)
            self.data = self.data.drop_duplicates(subset=subset)
            removed_count = initial_count - len(self.data)
            
            if self.verbose:
                logger.info(f"Removed {removed_count} duplicate rows")
            
            return self.data
        
        except Exception as e:
            logger.error(f"Error removing duplicates: {str(e)}")
            raise
    
    def get_summary_statistics(self) -> pd.DataFrame:
        """
        Get summary statistics of numeric columns.
        
        Returns:
            pd.DataFrame: Summary statistics
        """
        if self.data is None:
            logger.error("No data loaded")
            return None
        
        return self.data.describe()
    
    def save_data(self, filename: str, format: str = 'csv', **kwargs) -> None:
        """
        Save processed data to file.
        
        Args:
            filename (str): Output filename
            format (str): File format ('csv', 'excel', 'json', 'parquet')
            **kwargs: Additional arguments for the save function
        """
        if self.data is None:
            logger.error("No data to save")
            return
        
        try:
            output_path = self.data_path / filename if self.data_path.is_dir() else Path(filename)
            
            if format.lower() == 'csv':
                self.data.to_csv(output_path, index=False, **kwargs)
            elif format.lower() == 'excel':
                self.data.to_excel(output_path, index=False, **kwargs)
            elif format.lower() == 'json':
                self.data.to_json(output_path, **kwargs)
            elif format.lower() == 'parquet':
                self.data.to_parquet(output_path, index=False, **kwargs)
            else:
                logger.error(f"Unsupported format: {format}")
                return
            
            if self.verbose:
                logger.info(f"Data saved successfully to: {output_path}")
        
        except Exception as e:
            logger.error(f"Error saving data: {str(e)}")
            raise
    
    def _update_metadata(self, file_format: str, filename: str) -> None:
        """Update metadata after loading data."""
        self.metadata = {
            'format': file_format,
            'filename': filename,
            'rows': len(self.data),
            'columns': len(self.data.columns),
            'dtypes': self.data.dtypes.to_dict()
        }


# Example usage function
def example_usage():
    """
    Example of how to use the HealthcareDataLoader class.
    """
    print("\n" + "="*60)
    print("Healthcare Data Loading - Example Usage")
    print("="*60 + "\n")
    
    # Example 1: Load CSV file
    print("Example 1: Loading CSV file")
    print("-" * 60)
    loader = HealthcareDataLoader(data_path='./data')
    
    # Load sample data
    # data = loader.load_csv('healthcare_data.csv')
    
    # Get data info
    # info = loader.get_data_info()
    # print(f"Data Info: {info}\n")
    
    # Example 2: Data validation
    print("\nExample 2: Data Validation")
    print("-" * 60)
    # validation = loader.validate_data()
    
    # Example 3: Handle missing values
    print("\nExample 3: Handle Missing Values")
    print("-" * 60)
    # loader.handle_missing_values(strategy='mean')
    
    # Example 4: Remove duplicates
    print("\nExample 4: Remove Duplicates")
    print("-" * 60)
    # loader.remove_duplicates()
    
    # Example 5: Get summary statistics
    print("\nExample 5: Summary Statistics")
    print("-" * 60)
    # stats = loader.get_summary_statistics()
    # print(stats)
    
    # Example 6: Save processed data
    print("\nExample 6: Save Data")
    print("-" * 60)
    # loader.save_data('processed_healthcare_data.csv')
    
    print("\n" + "="*60)
    print("Setup complete! Use the HealthcareDataLoader class with your data.")
    print("="*60 + "\n")


if __name__ == "__main__":
    example_usage()
