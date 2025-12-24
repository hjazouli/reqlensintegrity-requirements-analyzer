"""
Flask Web Application for Requirements Analyzer
Modern web interface with beautiful UI
"""

from flask import Flask, render_template, request, jsonify, send_file, session
from werkzeug.utils import secure_filename
import os
import json
from requirements_analyzer import RequirementsAnalyzer
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Global analyzer instance (in production, use session-based storage)
analyzers = {}


@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        file_type = request.form.get('type', 'current')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith(('.xlsx', '.xls')):
            return jsonify({'error': 'Invalid file format. Please upload Excel files only.'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_type}_{filename}")
        file.save(filepath)
        
        # Create or get analyzer
        session_id = request.form.get('session_id', 'default')
        if session_id not in analyzers:
            analyzers[session_id] = RequirementsAnalyzer()
        
        analyzer = analyzers[session_id]
        
        # Load file
        if file_type == 'current':
            success = analyzer.load_excel(filepath)
        else:
            success = analyzer.load_comparison_file(filepath)
        
        if not success:
            return jsonify({'error': 'Failed to parse Excel file'}), 400
        
        # Get basic stats
        if file_type == 'current':
            stats = analyzer.generate_statistics()
            return jsonify({
                'success': True,
                'filename': filename,
                'total_requirements': stats.get('total_requirements', 0),
                'message': f'Loaded {stats.get("total_requirements", 0)} requirements'
            })
        else:
            return jsonify({
                'success': True,
                'filename': filename,
                'message': 'Comparison file loaded successfully'
            })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/analyze', methods=['POST'])
def analyze():
    """Perform analysis"""
    try:
        data = request.get_json()
        session_id = data.get('session_id', 'default')
        
        if session_id not in analyzers:
            return jsonify({'error': 'No file loaded'}), 400
        
        analyzer = analyzers[session_id]
        
        # Generate statistics
        stats = analyzer.generate_statistics()
        
        # Detect changes if comparison file exists
        changes = []
        impact = {}
        
        if analyzer.df_old is not None:
            changes = analyzer.detect_changes()
            impact = analyzer.analyze_impact()
        
        return jsonify({
            'success': True,
            'statistics': stats,
            'changes': changes,
            'impact': impact
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/visualizations/overview', methods=['POST'])
def overview_chart():
    """Generate overview visualizations"""
    try:
        data = request.get_json()
        session_id = data.get('session_id', 'default')
        
        if session_id not in analyzers:
            return jsonify({'error': 'No data available'}), 400
        
        analyzer = analyzers[session_id]
        stats = analyzer.statistics or analyzer.generate_statistics()
        
        charts = {}
        
        # Category pie chart
        if stats.get('by_category'):
            categories = list(stats['by_category'].keys())[:8]
            values = [stats['by_category'][cat] for cat in categories]
            
            fig_category = go.Figure(data=[go.Pie(
                labels=categories,
                values=values,
                hole=0.4,
                marker=dict(colors=px.colors.qualitative.Set3)
            )])
            fig_category.update_layout(
                title='Requirements by Category',
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12)
            )
            charts['category'] = fig_category.to_json()
        
        # State bar chart
        if stats.get('by_state'):
            states = list(stats['by_state'].keys())
            values = list(stats['by_state'].values())
            
            fig_state = go.Figure(data=[go.Bar(
                x=values,
                y=states,
                orientation='h',
                marker=dict(color='#2E86AB')
            )])
            fig_state.update_layout(
                title='Requirements by State',
                height=300,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(title='Count'),
                font=dict(size=12)
            )
            charts['state'] = fig_state.to_json()
        
        # Section bar chart
        if stats.get('by_section'):
            sections = list(stats['by_section'].keys())[:10]
            values = [stats['by_section'][sec] for sec in sections]
            
            fig_section = go.Figure(data=[go.Bar(
                x=sections,
                y=values,
                marker=dict(color='#06A77D')
            )])
            fig_section.update_layout(
                title='Top Sections',
                height=350,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                yaxis=dict(title='Count'),
                font=dict(size=12)
            )
            charts['section'] = fig_section.to_json()
        
        return jsonify({
            'success': True,
            'charts': charts,
            'metrics': {
                'total': stats.get('total_requirements', 0),
                'with_comments': stats.get('with_analysis_comments', 0),
                'with_tests': stats.get('with_test_cases', 0),
                'with_dependencies': stats.get('with_dependencies', 0)
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/visualizations/impact', methods=['POST'])
def impact_chart():
    """Generate impact analysis visualizations"""
    try:
        data = request.get_json()
        session_id = data.get('session_id', 'default')
        
        if session_id not in analyzers:
            return jsonify({'error': 'No data available'}), 400
        
        analyzer = analyzers[session_id]
        impact = analyzer.impact_analysis
        
        if not impact:
            return jsonify({'error': 'No impact analysis available. Load comparison file first.'}), 400
        
        # Impact distribution pie chart
        labels = ['High Impact', 'Medium Impact', 'Low Impact']
        values = [
            impact.get('high_impact_count', 0),
            impact.get('medium_impact_count', 0),
            impact.get('low_impact_count', 0)
        ]
        
        fig_impact = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            marker=dict(colors=['#E63946', '#F77F00', '#06A77D']),
            hole=0.4
        )])
        fig_impact.update_layout(
            title='Changes by Impact Level',
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12)
        )
        
        return jsonify({
            'success': True,
            'chart': fig_impact.to_json(),
            'metrics': {
                'high': impact.get('high_impact_count', 0),
                'medium': impact.get('medium_impact_count', 0),
                'low': impact.get('low_impact_count', 0),
                'categories_affected': impact.get('categories_affected', []),
                'sections_affected': impact.get('sections_affected', [])
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/export', methods=['POST'])
def export_data():
    """Export data to CSV"""
    try:
        data = request.get_json()
        session_id = data.get('session_id', 'default')
        export_type = data.get('type', 'all')
        
        if session_id not in analyzers:
            return jsonify({'error': 'No data available'}), 400
        
        analyzer = analyzers[session_id]
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'requirements_{export_type}_{timestamp}.csv'
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Export
        success = analyzer.export_to_csv(filepath, export_type)
        
        if success:
            return send_file(filepath, as_attachment=True, download_name=filename)
        else:
            return jsonify({'error': 'Export failed'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("="*60)
    print("Requirements Analyzer Web Application")
    print("="*60)
    print("\nStarting server...")
    print("\nOpen your browser and navigate to:")
    print("\n    http://localhost:5000")
    print("\nPress Ctrl+C to stop the server")
    print("="*60)
    app.run(debug=True, host='0.0.0.0', port=5000)
