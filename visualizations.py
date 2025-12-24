"""
Visualizations Module
Creates charts and graphs for requirements analysis
"""

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')
from typing import Dict, List
import numpy as np


class RequirementsVisualizer:
    """Handles creation of charts and visualizations"""
    
    def __init__(self):
        # Set style for better-looking charts
        plt.style.use('seaborn-v0_8-darkgrid')
        self.colors = {
            'primary': '#2E86AB',
            'secondary': '#A23B72',
            'success': '#06A77D',
            'warning': '#F18F01',
            'danger': '#C73E1D',
            'high': '#E63946',
            'medium': '#F77F00',
            'low': '#06A77D'
        }
    
    def create_overview_dashboard(self, statistics: Dict, parent_frame) -> FigureCanvasTkAgg:
        """
        Create overview dashboard with multiple charts
        
        Args:
            statistics: Statistics dictionary from analyzer
            parent_frame: Tkinter frame to embed chart in
            
        Returns:
            Canvas with embedded chart
        """
        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle('Requirements Overview Dashboard', fontsize=16, fontweight='bold')
        
        # Chart 1: Requirements by Category (Pie Chart)
        if statistics.get('by_category'):
            categories = list(statistics['by_category'].keys())
            counts = list(statistics['by_category'].values())
            
            # Limit to top 5 categories for clarity
            if len(categories) > 5:
                top_5_indices = np.argsort(counts)[-5:]
                categories = [categories[i] for i in top_5_indices]
                counts = [counts[i] for i in top_5_indices]
            
            colors = plt.cm.Set3(np.linspace(0, 1, len(categories)))
            ax1.pie(counts, labels=categories, autopct='%1.1f%%', colors=colors, startangle=90)
            ax1.set_title('Requirements by Category')
        else:
            ax1.text(0.5, 0.5, 'No category data', ha='center', va='center')
            ax1.set_title('Requirements by Category')
        
        # Chart 2: Requirements by State (Bar Chart)
        if statistics.get('by_state'):
            states = list(statistics['by_state'].keys())
            counts = list(statistics['by_state'].values())
            
            colors_bar = [self.colors['success'] if 'Approved' in s else self.colors['warning'] 
                         for s in states]
            
            ax2.barh(states, counts, color=colors_bar)
            ax2.set_xlabel('Count')
            ax2.set_title('Requirements by State')
            ax2.grid(axis='x', alpha=0.3)
        else:
            ax2.text(0.5, 0.5, 'No state data', ha='center', va='center')
            ax2.set_title('Requirements by State')
        
        # Chart 3: Key Metrics (Text Summary)
        ax3.axis('off')
        metrics_text = f"""
        Total Requirements: {statistics.get('total_requirements', 0):,}
        
        With Analysis Comments: {statistics.get('with_analysis_comments', 0):,}
        
        With Test Cases: {statistics.get('with_test_cases', 0):,}
        
        With Dependencies: {statistics.get('with_dependencies', 0):,}
        """
        ax3.text(0.1, 0.5, metrics_text, fontsize=12, verticalalignment='center',
                fontfamily='monospace', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
        ax3.set_title('Key Metrics')
        
        # Chart 4: Top Sections (Bar Chart)
        if statistics.get('by_section'):
            sections = list(statistics['by_section'].keys())
            counts = list(statistics['by_section'].values())
            
            # Show top 8 sections
            if len(sections) > 8:
                sections = sections[:8]
                counts = counts[:8]
            
            ax4.bar(sections, counts, color=self.colors['primary'], alpha=0.7)
            ax4.set_xlabel('Section')
            ax4.set_ylabel('Count')
            ax4.set_title('Top Sections')
            ax4.tick_params(axis='x', rotation=45)
            ax4.grid(axis='y', alpha=0.3)
        else:
            ax4.text(0.5, 0.5, 'No section data', ha='center', va='center')
            ax4.set_title('Top Sections')
        
        plt.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        canvas.draw()
        
        return canvas
    
    def create_impact_chart(self, impact_analysis: Dict, parent_frame) -> FigureCanvasTkAgg:
        """
        Create impact analysis visualization
        
        Args:
            impact_analysis: Impact analysis dictionary
            parent_frame: Tkinter frame to embed chart in
            
        Returns:
            Canvas with embedded chart
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        fig.suptitle('Impact Analysis', fontsize=16, fontweight='bold')
        
        # Chart 1: Impact Level Distribution (Pie Chart)
        labels = ['High Impact', 'Medium Impact', 'Low Impact']
        sizes = [
            impact_analysis.get('high_impact_count', 0),
            impact_analysis.get('medium_impact_count', 0),
            impact_analysis.get('low_impact_count', 0)
        ]
        colors_impact = [self.colors['high'], self.colors['medium'], self.colors['low']]
        
        if sum(sizes) > 0:
            explode = (0.1, 0, 0)  # Explode high impact slice
            ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
                   colors=colors_impact, shadow=True, startangle=90)
            ax1.set_title('Changes by Impact Level')
        else:
            ax1.text(0.5, 0.5, 'No impact data', ha='center', va='center')
            ax1.set_title('Changes by Impact Level')
        
        # Chart 2: Affected Categories/Sections
        affected_items = []
        affected_counts = []
        
        if impact_analysis.get('categories_affected'):
            affected_items.extend(impact_analysis['categories_affected'][:5])
            # For simplicity, show count as 1 per category (can be enhanced)
            affected_counts.extend([1] * len(affected_items))
        
        if affected_items:
            ax2.barh(affected_items, affected_counts, color=self.colors['secondary'], alpha=0.7)
            ax2.set_xlabel('Categories Affected')
            ax2.set_title('Affected Categories')
            ax2.grid(axis='x', alpha=0.3)
        else:
            ax2.text(0.5, 0.5, 'No affected categories', ha='center', va='center')
            ax2.set_title('Affected Categories')
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        canvas.draw()
        
        return canvas
    
    def create_change_distribution_chart(self, changes: List[Dict], parent_frame) -> FigureCanvasTkAgg:
        """
        Create chart showing distribution of changes
        
        Args:
            changes: List of changes
            parent_frame: Tkinter frame to embed chart in
            
        Returns:
            Canvas with embedded chart
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        fig.suptitle('Change Distribution', fontsize=16, fontweight='bold')
        
        # Chart 1: Change Types
        change_types = {}
        for change in changes:
            change_type = change.get('type', 'UNKNOWN')
            change_types[change_type] = change_types.get(change_type, 0) + 1
        
        if change_types:
            types = list(change_types.keys())
            counts = list(change_types.values())
            
            colors_types = []
            for t in types:
                if t == 'ADDED':
                    colors_types.append(self.colors['success'])
                elif t == 'REMOVED':
                    colors_types.append(self.colors['danger'])
                else:
                    colors_types.append(self.colors['warning'])
            
            ax1.bar(types, counts, color=colors_types, alpha=0.7)
            ax1.set_ylabel('Count')
            ax1.set_title('Changes by Type')
            ax1.grid(axis='y', alpha=0.3)
        else:
            ax1.text(0.5, 0.5, 'No changes detected', ha='center', va='center')
            ax1.set_title('Changes by Type')
        
        # Chart 2: Changes by Category
        category_changes = {}
        for change in changes:
            category = change.get('category', 'Unknown')
            category_changes[category] = category_changes.get(category, 0) + 1
        
        if category_changes:
            # Show top 10 categories
            sorted_categories = sorted(category_changes.items(), key=lambda x: x[1], reverse=True)[:10]
            categories = [c[0] for c in sorted_categories]
            counts = [c[1] for c in sorted_categories]
            
            ax2.barh(categories, counts, color=self.colors['primary'], alpha=0.7)
            ax2.set_xlabel('Number of Changes')
            ax2.set_title('Top 10 Categories with Changes')
            ax2.grid(axis='x', alpha=0.3)
        else:
            ax2.text(0.5, 0.5, 'No category data', ha='center', va='center')
            ax2.set_title('Changes by Category')
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        canvas.draw()
        
        return canvas
