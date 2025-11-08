#!/usr/bin/env python3
"""
Standalone TOR Analysis System - Fixed Version
"""

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="TOR Analysis System",
    description="Advanced TOR Network Analysis System",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data
MOCK_STATS = {
    "total_nodes": 1247,
    "active_correlations": 89,
    "high_confidence_matches": 23,
    "countries_monitored": 67,
    "total_bandwidth": "2.4 GB/s",
    "uptime_percentage": 99.2,
    "last_updated": datetime.utcnow()
}

# Routes
@app.get("/", response_class=HTMLResponse)
async def root():
    """Redirect to dashboard"""
    return RedirectResponse(url="/dashboard")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Dashboard page"""
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TOR Analysis Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #eff6ff 0%, #ffffff 50%, #eff6ff 100%);
            min-height: 100vh;
        }}
        
        .header {{
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            color: white;
            padding: 1rem 0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }}
        
        .header-content {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .logo {{
            font-size: 1.5rem;
            font-weight: 700;
        }}
        
        .nav {{
            display: flex;
            gap: 2rem;
        }}
        
        .nav a {{
            color: rgba(255, 255, 255, 0.9);
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
            transition: all 0.2s;
        }}
        
        .nav a:hover {{
            background: rgba(255, 255, 255, 0.1);
            color: white;
        }}
        
        .main-content {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem 1rem;
        }}
        
        .page-header {{
            margin-bottom: 2rem;
            padding: 2rem;
            background: white;
            border-radius: 1rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }}
        
        .page-title {{
            font-size: 2.5rem;
            font-weight: 700;
            color: #1f2937;
            margin-bottom: 0.5rem;
        }}
        
        .page-subtitle {{
            color: #6b7280;
            font-size: 1.125rem;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            color: white;
            padding: 2rem;
            border-radius: 1rem;
            box-shadow: 0 10px 25px -3px rgba(59, 130, 246, 0.3);
            transition: transform 0.2s;
            cursor: pointer;
        }}
        
        .stat-card:hover {{
            transform: translateY(-4px);
        }}
        
        .stat-card:nth-child(2) {{
            background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
            box-shadow: 0 10px 25px -3px rgba(6, 182, 212, 0.3);
        }}
        
        .stat-card:nth-child(3) {{
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            box-shadow: 0 10px 25px -3px rgba(16, 185, 129, 0.3);
        }}
        
        .stat-card:nth-child(4) {{
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            box-shadow: 0 10px 25px -3px rgba(245, 158, 11, 0.3);
        }}
        
        .stat-value {{
            font-size: 3rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
        }}
        
        .stat-label {{
            font-size: 0.875rem;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
        }}
        
        .charts-grid {{
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 2rem;
            margin-bottom: 2rem;
        }}
        
        .card {{
            background: white;
            border-radius: 1rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        
        .card-header {{
            padding: 1.5rem;
            border-bottom: 1px solid #e5e7eb;
            background: #f9fafb;
        }}
        
        .card-title {{
            font-size: 1.25rem;
            font-weight: 600;
            color: #1f2937;
        }}
        
        .card-body {{
            padding: 1.5rem;
        }}
        
        .chart-container {{
            height: 300px;
            position: relative;
        }}
        
        .btn {{
            display: inline-flex;
            align-items: center;
            padding: 0.75rem 1.5rem;
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            color: white;
            border: none;
            border-radius: 0.5rem;
            font-weight: 600;
            text-decoration: none;
            cursor: pointer;
            transition: all 0.2s;
            margin: 0.25rem;
        }}
        
        .btn:hover {{
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            transform: translateY(-2px);
        }}
        
        .btn-secondary {{
            background: white;
            color: #3b82f6;
            border: 1px solid #3b82f6;
        }}
        
        .btn-secondary:hover {{
            background: #eff6ff;
        }}
        
        .status-item {{
            margin-bottom: 1rem;
            padding: 0.75rem;
            background: #f9fafb;
            border-radius: 0.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .status-label {{
            font-weight: 500;
            color: #374151;
        }}
        
        .status-value {{
            font-weight: 600;
            color: #1f2937;
        }}
        
        .status-success {{
            color: #10b981;
        }}
        
        @media (max-width: 768px) {{
            .charts-grid {{
                grid-template-columns: 1fr;
            }}
            
            .nav {{
                display: none;
            }}
            
            .stats-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <header class="header">
        <div class="header-content">
            <div class="logo">🔒 TOR Analysis System</div>
            <nav class="nav">
                <a href="/dashboard">Dashboard</a>
                <a href="/network">Network</a>
                <a href="/correlations">Correlations</a>
                <a href="/analysis">Analysis</a>
                <a href="/reports">Reports</a>
            </nav>
            <div>
                <a href="/auth/logout" class="btn btn-secondary">Logout</a>
            </div>
        </div>
    </header>

    <main class="main-content">
        <div class="page-header">
            <h1 class="page-title">TOR Network Analysis Dashboard</h1>
            <p class="page-subtitle">Real-time monitoring and correlation analysis of TOR network traffic</p>
            <div style="margin-top: 1rem;">
                <button class="btn" onclick="refreshData()">🔄 Refresh Data</button>
                <button class="btn btn-secondary" onclick="exportData()">📊 Export</button>
                <button class="btn" onclick="runAnalysis()">🔍 Run Analysis</button>
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{MOCK_STATS["total_nodes"]}</div>
                <div class="stat-label">Total TOR Nodes</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{MOCK_STATS["active_correlations"]}</div>
                <div class="stat-label">Active Correlations</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{MOCK_STATS["high_confidence_matches"]}</div>
                <div class="stat-label">High Confidence Matches</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{MOCK_STATS["countries_monitored"]}</div>
                <div class="stat-label">Countries Monitored</div>
            </div>
        </div>

        <div class="charts-grid">
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">📊 Network Topology Distribution</h3>
                </div>
                <div class="card-body">
                    <div class="chart-container">
                        <canvas id="topologyChart"></canvas>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">⚡ System Status</h3>
                </div>
                <div class="card-body">
                    <div class="status-item">
                        <span class="status-label">Network Uptime:</span>
                        <span class="status-value status-success">{MOCK_STATS["uptime_percentage"]}%</span>
                    </div>
                    <div class="status-item">
                        <span class="status-label">Total Bandwidth:</span>
                        <span class="status-value">{MOCK_STATS["total_bandwidth"]}</span>
                    </div>
                    <div class="status-item">
                        <span class="status-label">Analysis Status:</span>
                        <span class="status-value status-success">🟢 Running</span>
                    </div>
                    <div class="status-item">
                        <span class="status-label">Last Update:</span>
                        <span class="status-value">Just now</span>
                    </div>
                    <div style="margin-top: 1rem;">
                        <button class="btn" onclick="runCorrelationAnalysis()" style="width: 100%;">
                            🚀 Run Correlation Analysis
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <h3 class="card-title">📈 Recent Activity</h3>
            </div>
            <div class="card-body">
                <div class="status-item">
                    <span class="status-label">🔍 Correlation Analysis</span>
                    <span class="status-value status-success">Completed - 23 matches found</span>
                </div>
                <div class="status-item">
                    <span class="status-label">🌐 Network Scan</span>
                    <span class="status-value status-success">Active - 1,247 nodes monitored</span>
                </div>
                <div class="status-item">
                    <span class="status-label">📊 Data Export</span>
                    <span class="status-value">Ready - Click export to download</span>
                </div>
            </div>
        </div>
    </main>

    <script>
        // Initialize chart
        const ctx = document.getElementById('topologyChart').getContext('2d');
        new Chart(ctx, {{
            type: 'doughnut',
            data: {{
                labels: ['Guard Nodes', 'Middle Nodes', 'Exit Nodes', 'Bridge Nodes'],
                datasets: [{{
                    data: [450, 520, 200, 77],
                    backgroundColor: ['#3b82f6', '#06b6d4', '#10b981', '#f59e0b'],
                    borderWidth: 3,
                    borderColor: '#ffffff'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'bottom',
                        labels: {{
                            padding: 20,
                            usePointStyle: true
                        }}
                    }}
                }},
                animation: {{
                    animateRotate: true,
                    duration: 1500
                }}
            }}
        }});

        function refreshData() {{
            // Animate the stat cards
            document.querySelectorAll('.stat-card').forEach((card, index) => {{
                setTimeout(() => {{
                    card.style.transform = 'scale(1.05)';
                    setTimeout(() => {{
                        card.style.transform = 'scale(1)';
                    }}, 200);
                }}, index * 100);
            }});
            
            setTimeout(() => {{
                alert('✅ Data refreshed successfully! All systems updated.');
            }}, 800);
        }}

        function exportData() {{
            alert('📊 Data exported successfully! Download started.');
        }}

        function runAnalysis() {{
            alert('🔍 Analysis started! Processing TOR network correlations...');
        }}

        function runCorrelationAnalysis() {{
            alert('🚀 Correlation analysis initiated! Analyzing traffic patterns...');
        }}

        // Add some interactive animations
        document.querySelectorAll('.stat-card').forEach(card => {{
            card.addEventListener('click', function() {{
                this.style.transform = 'scale(0.95)';
                setTimeout(() => {{
                    this.style.transform = 'scale(1)';
                }}, 150);
            }});
        }});
    </script>
</body>
</html>
"""
    return HTMLResponse(content=html)

@app.get("/auth/login", response_class=HTMLResponse)
async def login_page(error: str = None):
    """Login page"""
    error_html = ""
    if error:
        error_html = f'<div style="background: #fef2f2; border: 1px solid #fecaca; color: #dc2626; padding: 0.75rem 1rem; border-radius: 0.5rem; margin-bottom: 1rem; font-size: 0.875rem;">{error}</div>'
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - TOR Analysis System</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #eff6ff 0%, #ffffff 50%, #eff6ff 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .login-container {{
            max-width: 400px;
            width: 100%;
            margin: 0 1rem;
        }}
        
        .login-header {{
            text-align: center;
            margin-bottom: 2rem;
        }}
        
        .logo-icon {{
            width: 4rem;
            height: 4rem;
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            border-radius: 50%;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 1rem;
            animation: pulse 2s infinite;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.8; }}
        }}
        
        .login-title {{
            font-size: 2rem;
            font-weight: 700;
            color: #1f2937;
            margin-bottom: 0.5rem;
        }}
        
        .login-subtitle {{
            color: #6b7280;
            font-size: 1rem;
        }}
        
        .login-card {{
            background: white;
            border-radius: 1rem;
            box-shadow: 0 10px 25px -3px rgba(0, 0, 0, 0.1);
            border: 1px solid #e5e7eb;
            padding: 2rem;
        }}
        
        .form-title {{
            font-size: 1.25rem;
            font-weight: 600;
            text-align: center;
            margin-bottom: 1.5rem;
            color: #1f2937;
        }}
        
        .form-group {{
            margin-bottom: 1.5rem;
        }}
        
        .form-label {{
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
            color: #374151;
            font-size: 0.875rem;
        }}
        
        .form-input {{
            width: 100%;
            padding: 0.75rem 1rem;
            border: 1px solid #d1d5db;
            border-radius: 0.5rem;
            font-size: 1rem;
            transition: all 0.2s ease;
        }}
        
        .form-input:focus {{
            outline: none;
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }}
        
        .login-button {{
            width: 100%;
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            color: white;
            padding: 0.875rem 1.5rem;
            border: none;
            border-radius: 0.5rem;
            font-weight: 600;
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.025em;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        
        .login-button:hover {{
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            transform: translateY(-2px);
            box-shadow: 0 10px 25px -3px rgba(59, 130, 246, 0.3);
        }}
        
        .demo-credentials {{
            margin-top: 1.5rem;
            padding: 1rem;
            background: #eff6ff;
            border: 1px solid #bfdbfe;
            border-radius: 0.5rem;
        }}
        
        .demo-title {{
            font-size: 0.875rem;
            font-weight: 600;
            color: #1e40af;
            margin-bottom: 0.5rem;
        }}
        
        .demo-info {{
            font-size: 0.75rem;
            color: #1e40af;
            line-height: 1.4;
        }}
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-header">
            <div class="logo-icon">
                🔒
            </div>
            <h1 class="login-title">TOR Analysis System</h1>
            <p class="login-subtitle">Secure access to network analysis tools</p>
        </div>

        <div class="login-card">
            <h2 class="form-title">Sign In</h2>
            
            {error_html}

            <form method="POST">
                <div class="form-group">
                    <label for="username" class="form-label">Username</label>
                    <input 
                        type="text" 
                        id="username" 
                        name="username" 
                        class="form-input" 
                        required 
                        placeholder="Enter your username"
                        value="admin"
                    >
                </div>

                <div class="form-group">
                    <label for="password" class="form-label">Password</label>
                    <input 
                        type="password" 
                        id="password" 
                        name="password" 
                        class="form-input" 
                        required 
                        placeholder="Enter your password"
                        value="admin123"
                    >
                </div>

                <button type="submit" class="login-button">
                    🚀 Sign In
                </button>
            </form>

            <div class="demo-credentials">
                <div class="demo-title">🎯 Demo Credentials</div>
                <div class="demo-info">
                    <strong>Username:</strong> admin<br>
                    <strong>Password:</strong> admin123
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""
    return HTMLResponse(content=html)

@app.post("/auth/login")
async def login(username: str = Form(...), password: str = Form(...)):
    """Handle login"""
    if username == "admin" and password == "admin123":
        return RedirectResponse(url="/dashboard", status_code=302)
    else:
        return RedirectResponse(url="/auth/login?error=Invalid credentials. Use admin/admin123", status_code=302)

@app.get("/auth/logout")
async def logout():
    """Handle logout"""
    return RedirectResponse(url="/auth/login", status_code=302)

# Simple redirects for other pages
@app.get("/network")
async def network():
    return RedirectResponse(url="/dashboard")

@app.get("/correlations")
async def correlations():
    return RedirectResponse(url="/dashboard")

@app.get("/analysis")
async def analysis():
    return RedirectResponse(url="/dashboard")

@app.get("/reports")
async def reports():
    return RedirectResponse(url="/dashboard")

# API endpoints
@app.get("/api/v1/dashboard/stats")
async def get_stats():
    return JSONResponse(content={"success": True, "data": MOCK_STATS})

@app.get("/health")
async def health():
    return JSONResponse(content={"status": "healthy", "timestamp": datetime.utcnow().isoformat()})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)