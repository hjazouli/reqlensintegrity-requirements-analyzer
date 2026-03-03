## Integrity Requirements Analyzer - Web Application 

A modern, beautiful web application for analyzing system integrity requirements from Excel files, detecting changes between versions, and performing impact analysis.

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## Features

- 🎨 **Modern UI** - Beautiful glassmorphism design with smooth animations
- 📊 **Interactive Charts** - Dynamic visualizations using Plotly
- 🔄 **Change Detection** - Compare two versions to identify all changes
- ⚠️ **Impact Analysis** - Automatic assessment of change impact levels
- 📂 **Drag & Drop** - Easy file upload with drag-and-drop support
- 💾 **Export** - Download analysis results as CSV
- 📱 **Responsive** - Works on desktop, tablet, and mobile
- ⚡ **Fast** - Handles 3,000+ requirements instantly

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python app.py
```

### 3. Open Your Browser
Navigate to: **http://localhost:5000**

That's it! 🎉

## How to Use

### Step 1: Load Files
1. **Current Requirements File** (Required)
   - Click the upload box or drag & drop your Excel file
   - Supports `.xlsx` and `.xls` formats

2. **Comparison File** (Optional)
   - Upload an older version to detect changes
   - Same format as current file

### Step 2: Analyze
Click the **"Analyze Requirements"** button to:
- Generate comprehensive statistics
- Detect changes (if comparison file provided)
- Calculate impact levels
- Create visualizations

### Step 3: Review Results

#### 📊 Overview Tab
- Total requirements count
- Requirements broken down by category, state, and section
- Interactive pie charts and bar graphs
- Key metrics dashboard

#### 🔄 Changes Tab
- Complete list of all detected changes
- Changes are categorized as: **ADDED**, **REMOVED**, **MODIFIED**
- Color-coded by impact level:
  - 🔴 **HIGH** - Requires immediate attention
  - 🟡 **MEDIUM** - Should be reviewed
  - 🟢 **LOW** - Informational

#### ⚠️ Impact Analysis Tab
- Visual breakdown of impact distribution
- Affected categories and sections
- High-impact items highlighted

### Step 4: Export
Click **"Export CSV"** to download your analysis results.

## 🎨 UI Features

### Modern Design Elements
- **Glassmorphism** - Frosted glass effect with blur
- **Gradient Backgrounds** - Smooth color transitions
- **Smooth Animations** - Subtle hover effects and transitions
- **Toast Notifications** - Real-time feedback messages
- **Loading Indicators** - Visual feedback during processing
- **Responsive Layout** - Adapts to any screen size

### Color Scheme
- **Primary**: Blue (#2E86AB)
- **Success**: Green (#06A77D)
- **Warning**: Orange (#F77F00)
- **Danger**: Red (#E63946)
- **Background**: Purple gradient

## 📊 Impact Analysis Logic

Impact levels are calculated based on:

| Criteria | Impact Score |
|----------|--------------|
| Requirement removed | +3 |
| State changed | +2 |
| Test case related | +2 |
| Has dependencies | +1 to +3 |
| Functional requirement | +1 |

**Classification**:
- **HIGH**: Score ≥ 5
- **MEDIUM**: Score 2-4
- **LOW**: Score < 2

## 🗂️ Expected File Format

Your Excel file should contain these columns:

| Column | Description |
|--------|-------------|
| Section | Requirement section identifier |
| ID | Unique requirement ID |
| Category | Type (e.g., "Functional Requirement") |
| Text | Requirement description |
| State | Current state (e.g., "Approved") |
| Analysis Comments | Analysis notes |
| Sys Testing Comment | Testing information |
| Decomposes To | Related requirement IDs |
| Validated By | Validation references |

## 🚀 Deployment Options

### Option 1: Local Development Server (Current)
```bash
python app.py
```
Access at: http://localhost:5000

### Option 2: Production Server
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Option 3: Standalone Desktop App
Package as a desktop app using PyWebView:
```bash
pip install pywebview
# Create a wrapper script that launches the Flask app in a native window
```

### Option 4: Docker Container
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

## 📁 Project Structure

```
Requirements/
├── app.py                          # Flask application
├── requirements_analyzer.py        # Core analysis engine
├── requirements.txt                # Python dependencies
├── templates/
│   └── index.html                  # Main HTML template
├── static/
│   ├── css/
│   │   └── styles.css              # Modern CSS styling
│   └── js/
│       └── app.js                  # JavaScript functionality
├── uploads/                        # Uploaded files (auto-created)
├── README.md                       # This file
└── 20231129_L3_System_Reqs_FS.xlsx # Sample data
```

## 🔧 Troubleshooting

### Port Already in Use
```bash
# Change port in app.py (last line)
app.run(debug=True, host='0.0.0.0', port=8080)  # Use different port
```

### File Upload Issues
- Maximum file size: 50 MB
- Ensure file is not open in another application
- Check file format (must be Excel .xlsx or .xls)

### Charts Not Loading
- Ensure internet connection (Plotly loads from CDN)
- Check browser console for errors
- Try clearing browser cache

### Performance
- Files with 10,000+ requirements may take 10-30 seconds
- Consider analyzing smaller batches if needed

## 🎓 Tips & Best Practices

1. **File Comparison**: Always load files in chronological order (old → new)
2. **Large Files**: For files > 5,000 requirements, allow extra processing time
3. **Export Early**: Export results after analysis for record-keeping
4. **Browser**: Best experienced in Chrome, Firefox, or Edge
5. **Screen Size**: Optimal viewing on screens 1280px+ wide

## 🆕 What's New in v2.0

- ✨ Complete UI redesign with modern web interface
- 🎨 Glassmorphism and gradient design
- 📊 Interactive Plotly charts instead of static
- 🖱️ Drag-and-drop file upload
- 🌐 Web-based (accessible from any device)
- 📱 Fully responsive mobile design
- ⚡ Real-time toast notifications
- 🎯 Improved user experience

## 💻 Technical Stack

- **Backend**: Python 3.8+ with Flask
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Charts**: Plotly.js
- **Data Processing**: Pandas, NumPy
- **Excel**: openpyxl
- **Icons**: Font Awesome
- **Fonts**: Google Fonts (Inter)

## 📝 License

MIT License - Feel free to use and modify!

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the sample file for expected format
3. Ensure all dependencies are installed

## 🎉 Enjoy!

Start analyzing your requirements with style! 🚀

---

**Made with ❤️ using Python and modern web technologies**
