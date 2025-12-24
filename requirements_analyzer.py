"""
Requirements Analyzer - Core Analysis Engine
Handles Excel parsing, change detection, and impact analysis for integrity requirements
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import re


class RequirementsAnalyzer:
    """Main class for analyzing integrity requirements from Excel files"""
    
    def __init__(self):
        self.df = None
        self.df_old = None
        self.changes = []
        self.statistics = {}
        self.impact_analysis = {}
        
    def load_excel(self, filepath: str, sheet_name: str = None) -> bool:
        """
        Load Excel file and parse requirements
        
        Args:
            filepath: Path to Excel file
            sheet_name: Optional sheet name (uses first sheet if None)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if sheet_name:
                self.df = pd.read_excel(filepath, sheet_name=sheet_name)
            else:
                # Read first sheet
                xl_file = pd.ExcelFile(filepath)
                # Try to find a sheet with data (skip empty sheets)
                for sheet in xl_file.sheet_names:
                    df_temp = pd.read_excel(filepath, sheet_name=sheet)
                    if not df_temp.empty:
                        self.df = df_temp
                        break
            
            if self.df is not None and not self.df.empty:
                # Clean column names
                self.df.columns = self.df.columns.str.strip()
                return True
            return False
            
        except Exception as e:
            print(f"Error loading Excel file: {e}")
            return False
    
    def load_comparison_file(self, filepath: str, sheet_name: str = None) -> bool:
        """
        Load a second Excel file for comparison
        
        Args:
            filepath: Path to second Excel file
            sheet_name: Optional sheet name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if sheet_name:
                self.df_old = pd.read_excel(filepath, sheet_name=sheet_name)
            else:
                xl_file = pd.ExcelFile(filepath)
                for sheet in xl_file.sheet_names:
                    df_temp = pd.read_excel(filepath, sheet_name=sheet)
                    if not df_temp.empty:
                        self.df_old = df_temp
                        break
            
            if self.df_old is not None and not self.df_old.empty:
                self.df_old.columns = self.df_old.columns.str.strip()
                return True
            return False
            
        except Exception as e:
            print(f"Error loading comparison file: {e}")
            return False
    
    def extract_requirements(self, filters: Dict = None) -> pd.DataFrame:
        """
        Extract requirements based on filters
        
        Args:
            filters: Dictionary of column:value pairs to filter by
            
        Returns:
            Filtered DataFrame
        """
        if self.df is None:
            return pd.DataFrame()
        
        result = self.df.copy()
        
        if filters:
            for column, value in filters.items():
                if column in result.columns:
                    if isinstance(value, list):
                        result = result[result[column].isin(value)]
                    else:
                        result = result[result[column] == value]
        
        return result
    
    def detect_changes(self) -> List[Dict]:
        """
        Compare current file with old file to detect changes
        
        Returns:
            List of dictionaries containing change information
        """
        if self.df is None or self.df_old is None:
            return []
        
        changes = []
        
        # Ensure both dataframes have an ID column
        id_column = None
        for col in ['ID', 'Requirement ID', 'id', 'Id']:
            if col in self.df.columns and col in self.df_old.columns:
                id_column = col
                break
        
        if not id_column:
            print("Warning: No common ID column found for comparison")
            return []
        
        # Create dictionaries indexed by ID for faster lookup
        old_dict = self.df_old.set_index(id_column).to_dict('index')
        new_dict = self.df.set_index(id_column).to_dict('index')
        
        # Find added, removed, and modified requirements
        old_ids = set(old_dict.keys())
        new_ids = set(new_dict.keys())
        
        # New requirements
        added_ids = new_ids - old_ids
        for req_id in added_ids:
            changes.append({
                'id': req_id,
                'type': 'ADDED',
                'section': new_dict[req_id].get('Section', 'N/A'),
                'category': new_dict[req_id].get('Category', 'N/A'),
                'text': new_dict[req_id].get('Text', 'N/A'),
                'old_value': None,
                'new_value': new_dict[req_id].get('Text', 'N/A'),
                'impact_level': self._calculate_impact(req_id, 'ADDED', new_dict[req_id])
            })
        
        # Removed requirements
        removed_ids = old_ids - new_ids
        for req_id in removed_ids:
            changes.append({
                'id': req_id,
                'type': 'REMOVED',
                'section': old_dict[req_id].get('Section', 'N/A'),
                'category': old_dict[req_id].get('Category', 'N/A'),
                'text': old_dict[req_id].get('Text', 'N/A'),
                'old_value': old_dict[req_id].get('Text', 'N/A'),
                'new_value': None,
                'impact_level': self._calculate_impact(req_id, 'REMOVED', old_dict[req_id])
            })
        
        # Modified requirements
        common_ids = old_ids & new_ids
        for req_id in common_ids:
            old_req = old_dict[req_id]
            new_req = new_dict[req_id]
            
            # Check for changes in key fields
            changed_fields = []
            
            for field in ['Text', 'State', 'Category', 'Requirement Acceptance Criteria', 
                         'Analysis Comments', 'Sys Testing Comment']:
                if field in old_req and field in new_req:
                    old_val = str(old_req[field]) if pd.notna(old_req[field]) else ''
                    new_val = str(new_req[field]) if pd.notna(new_req[field]) else ''
                    
                    if old_val != new_val:
                        changed_fields.append(field)
            
            if changed_fields:
                changes.append({
                    'id': req_id,
                    'type': 'MODIFIED',
                    'section': new_req.get('Section', 'N/A'),
                    'category': new_req.get('Category', 'N/A'),
                    'text': new_req.get('Text', 'N/A'),
                    'changed_fields': changed_fields,
                    'old_value': {field: old_req.get(field, '') for field in changed_fields},
                    'new_value': {field: new_req.get(field, '') for field in changed_fields},
                    'impact_level': self._calculate_impact(req_id, 'MODIFIED', new_req, old_req)
                })
        
        self.changes = changes
        return changes
    
    def _calculate_impact(self, req_id, change_type: str, 
                         new_req: Dict = None, old_req: Dict = None) -> str:
        """
        Calculate impact level of a change
        
        Args:
            req_id: Requirement ID
            change_type: Type of change (ADDED, REMOVED, MODIFIED)
            new_req: New requirement data
            old_req: Old requirement data
            
        Returns:
            Impact level: 'HIGH', 'MEDIUM', 'LOW'
        """
        impact_score = 0
        
        # High impact for removed requirements
        if change_type == 'REMOVED':
            impact_score += 3
        
        # Check for test-related requirements
        if new_req:
            analysis_comments = str(new_req.get('Analysis Comments', ''))
            sys_testing = str(new_req.get('Sys Testing Comment', ''))
            
            if 'Test Case Related' in analysis_comments or 'Test Case Related' in sys_testing:
                impact_score += 2
            
            if 'Test case to be updated' in sys_testing:
                impact_score += 2
            
            # Check for relationships
            decomposes_to = str(new_req.get('Decomposes To', ''))
            validated_by = str(new_req.get('Validated By', ''))
            
            # Count comma-separated IDs
            if decomposes_to and decomposes_to != 'nan' and decomposes_to != 'NaN':
                num_dependencies = len([x.strip() for x in decomposes_to.split(',') if x.strip()])
                impact_score += min(num_dependencies, 3)
            
            if validated_by and validated_by != 'nan' and validated_by != 'NaN':
                impact_score += 1
            
            # Check category
            category = new_req.get('Category', '')
            if 'Functional' in str(category):
                impact_score += 1
        
        # Check for state changes
        if change_type == 'MODIFIED' and old_req and new_req:
            old_state = str(old_req.get('State', ''))
            new_state = str(new_req.get('State', ''))
            
            if old_state != new_state:
                impact_score += 2
        
        # Classify impact
        if impact_score >= 5:
            return 'HIGH'
        elif impact_score >= 2:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def generate_statistics(self) -> Dict:
        """
        Generate summary statistics from the requirements
        
        Returns:
            Dictionary containing various statistics
        """
        if self.df is None:
            return {}
        
        stats = {
            'total_requirements': len(self.df),
            'by_category': {},
            'by_state': {},
            'by_section': {},
            'with_analysis_comments': 0,
            'with_test_cases': 0,
            'with_dependencies': 0,
        }
        
        # Count by category
        if 'Category' in self.df.columns:
            stats['by_category'] = self.df['Category'].value_counts().to_dict()
        
        # Count by state
        if 'State' in self.df.columns:
            stats['by_state'] = self.df['State'].value_counts().to_dict()
        
        # Count by section
        if 'Section' in self.df.columns:
            # Group by major section (first part before decimal)
            sections = self.df['Section'].astype(str).apply(
                lambda x: x.split('.')[0] if '.' in x else x
            )
            stats['by_section'] = sections.value_counts().head(10).to_dict()
        
        # Count requirements with analysis comments
        if 'Analysis Comments' in self.df.columns:
            stats['with_analysis_comments'] = self.df['Analysis Comments'].notna().sum()
        
        # Count requirements with test cases
        if 'Sys Testing Comment' in self.df.columns:
            test_related = self.df['Sys Testing Comment'].astype(str).str.contains(
                'Test', case=False, na=False
            )
            stats['with_test_cases'] = test_related.sum()
        
        # Count requirements with dependencies
        if 'Decomposes To' in self.df.columns:
            stats['with_dependencies'] = self.df['Decomposes To'].notna().sum()
        
        self.statistics = stats
        return stats
    
    def analyze_impact(self) -> Dict:
        """
        Perform comprehensive impact analysis on changes
        
        Returns:
            Dictionary containing impact analysis results
        """
        if not self.changes:
            return {}
        
        impact = {
            'high_impact_count': 0,
            'medium_impact_count': 0,
            'low_impact_count': 0,
            'high_impact_items': [],
            'categories_affected': set(),
            'sections_affected': set(),
        }
        
        for change in self.changes:
            level = change['impact_level']
            
            if level == 'HIGH':
                impact['high_impact_count'] += 1
                impact['high_impact_items'].append(change)
            elif level == 'MEDIUM':
                impact['medium_impact_count'] += 1
            else:
                impact['low_impact_count'] += 1
            
            impact['categories_affected'].add(change['category'])
            impact['sections_affected'].add(change['section'])
        
        # Convert sets to lists for JSON serialization
        impact['categories_affected'] = list(impact['categories_affected'])
        impact['sections_affected'] = list(impact['sections_affected'])
        
        self.impact_analysis = impact
        return impact
    
    def export_to_csv(self, filepath: str, data_type: str = 'all'):
        """
        Export data to CSV file
        
        Args:
            filepath: Output file path
            data_type: Type of data to export ('all', 'changes', 'statistics')
        """
        try:
            if data_type == 'all' and self.df is not None:
                self.df.to_csv(filepath, index=False)
            elif data_type == 'changes' and self.changes:
                changes_df = pd.DataFrame(self.changes)
                changes_df.to_csv(filepath, index=False)
            elif data_type == 'statistics' and self.statistics:
                # Flatten statistics for CSV
                stats_df = pd.DataFrame([self.statistics])
                stats_df.to_csv(filepath, index=False)
            
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
    
    def get_requirement_details(self, req_id) -> Dict:
        """
        Get detailed information about a specific requirement
        
        Args:
            req_id: Requirement ID
            
        Returns:
            Dictionary with requirement details
        """
        if self.df is None:
            return {}
        
        # Find ID column
        id_column = None
        for col in ['ID', 'Requirement ID', 'id', 'Id']:
            if col in self.df.columns:
                id_column = col
                break
        
        if not id_column:
            return {}
        
        row = self.df[self.df[id_column] == req_id]
        if row.empty:
            return {}
        
        return row.iloc[0].to_dict()
