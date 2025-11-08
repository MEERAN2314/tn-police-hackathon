# TOR Analysis System
## Tamil Nadu Police Hackathon 2025 - "Unveil: Peel the Onion"

A comprehensive TOR network analysis and correlation system designed for law enforcement investigations. This system provides real-time monitoring, traffic correlation analysis, and AI-enhanced pattern recognition to identify probable origin IPs behind TOR-based traffic.

## 🎯 Project Overview

**Challenge**: Develop an analytical system to trace TOR network users by correlating activity patterns and TOR node data to identify the probable origin IPs behind TOR-based traffic (email, browsing, etc.)

**Solution**: A multi-layer correlation engine that combines real-time TOR network topology mapping, statistical correlation analysis, AI-enhanced pattern recognition, and comprehensive forensic reporting.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Layer                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Jinja2    │  │   D3.js     │  │   Real-time         │ │
│  │  Templates  │  │ Visualization│  │   Dashboard         │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   API Gateway Layer                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   FastAPI   │  │  Security   │  │   Rate Limiting     │ │
│  │   Router    │  │ Middleware  │  │   & Authentication  │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                 Business Logic Layer                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │    TOR      │  │ Correlation │  │      AI Pattern     │ │
│  │ Data Collector│ │   Engine    │  │    Recognition      │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Data Processing Layer                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Celery    │  │    Redis    │  │    Background       │ │
│  │ Task Queue  │  │   Cache     │  │    Workers          │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Data Storage Layer                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  MongoDB    │  │   GridFS    │  │    Time Series      │ │
│  │   Atlas     │  │File Storage │  │      Data           │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Tech Stack

### Backend
- **FastAPI**: High-performance async web framework
- **Python 3.11+**: Core programming language
- **MongoDB Atlas**: Primary database (Free: 512MB)
- **Redis**: Caching and task queue
- **Celery**: Distributed task processing

### Frontend
- **Jinja2**: Server-side templating
- **HTML5/CSS3**: Modern web standards
- **Vanilla JavaScript**: Client-side interactivity
- **D3.js**: Network topology visualization
- **Chart.js**: Real-time charts and graphs

### TOR & Network Analysis
- **Stem**: TOR controller library
- **Scapy**: Packet analysis
- **NetworkX**: Graph analysis
- **Requests/aiohttp**: HTTP clients

### AI & Machine Learning
- **Google Gemini API**: AI pattern recognition
- **LangChain**: AI orchestration
- **Scikit-learn**: Machine learning algorithms
- **Pandas/NumPy**: Data analysis

### Security & Infrastructure
- **Docker**: Containerization
- **Nginx**: Reverse proxy and load balancer
- **8-Layer Security**: Comprehensive security implementation

## 🔒 Security Features

### 8-Layer Security Implementation

1. **Network Perimeter**: UFW firewall with strict rules
2. **Web Application Firewall**: Nginx + ModSecurity
3. **Container Security**: Docker security + vulnerability scanning
4. **API Gateway Security**: JWT authentication + rate limiting
5. **Database Security**: MongoDB Atlas encryption + access control
6. **Input Validation**: Pydantic models + sanitization
7. **Intrusion Detection**: Fail2Ban + monitoring
8. **Encryption & Secrets**: SSL/TLS + secure configuration

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+
- MongoDB Atlas account (free tier)
- Google Gemini API key (optional)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd tor-analysis-system
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start the application**
```bash
docker-compose up -d
```

4. **Access the application**
- Main Dashboard: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Default Login: admin / admin123

### Manual Setup (Development)

1. **Install dependencies**
```bash
pip install -r requirements.txt
```

2. **Start Redis**
```bash
redis-server
```

3. **Start Celery worker**
```bash
celery -A app.celery_app worker --loglevel=info
```

4. **Start the application**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📊 Features

### Core Functionality

#### 1. Real-time TOR Network Monitoring
- **Live Data Collection**: Continuous monitoring of TOR network topology
- **Node Classification**: Automatic identification of Guard, Middle, Exit, and Bridge nodes
- **Geographic Distribution**: Global mapping of TOR nodes by country
- **Bandwidth Analysis**: Real-time bandwidth and performance metrics

#### 2. Advanced Correlation Engine
- **Timing Analysis**: Statistical correlation based on circuit build times
- **Traffic Pattern Recognition**: ML-based pattern analysis using DBSCAN clustering
- **Multi-source Correlation**: Combines timing, volume, and behavioral data
- **Confidence Scoring**: Probabilistic matching with uncertainty quantification

#### 3. AI-Enhanced Analysis
- **Google Gemini Integration**: Advanced pattern recognition and threat assessment
- **Behavioral Analysis**: Identification of suspicious activity patterns
- **Automated Reporting**: AI-generated forensic reports with legal documentation
- **Adaptive Learning**: Continuous improvement of correlation accuracy

#### 4. Interactive Visualization
- **Network Topology**: Interactive D3.js-based network graphs
- **Real-time Dashboards**: Live monitoring with WebSocket updates
- **Geographic Mapping**: World map showing node distribution
- **Traffic Flow Analysis**: Visual representation of correlation paths

#### 5. Forensic Reporting
- **Legal-grade Documentation**: Comprehensive audit trails
- **Export Capabilities**: JSON, CSV, and PDF report generation
- **Evidence Chain**: Detailed correlation evidence with timestamps
- **Confidence Metrics**: Clear uncertainty quantification for legal use

### Dashboard Features

#### Statistics Overview
- Total TOR nodes monitored
- Active traffic correlations
- High-confidence matches
- Global country coverage
- Network uptime and performance

#### Real-time Monitoring
- Live network topology updates
- Traffic flow visualization
- Correlation confidence levels
- System health monitoring

#### Analysis Tools
- Automated correlation analysis
- AI-powered threat assessment
- Pattern recognition algorithms
- Suspicious activity detection

## 🔧 Configuration

### Environment Variables

```bash
# Database Configuration
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/tor_analysis
REDIS_URL=redis://localhost:6379

# API Keys
GEMINI_API_KEY=your_gemini_api_key_here
IPGEOLOCATION_API_KEY=your_ipgeolocation_api_key_here

# Security
SECRET_KEY=your_super_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Settings
DEBUG=True
LOG_LEVEL=INFO
MAX_WORKERS=4

# TOR Configuration
TOR_CONTROL_PORT=9051
TOR_SOCKS_PORT=9050
TOR_DATA_REFRESH_INTERVAL=300
```

### MongoDB Atlas Setup

1. Create a free MongoDB Atlas account
2. Create a new cluster
3. Add your IP to the whitelist
4. Create a database user
5. Get the connection string and add to `.env`

### API Keys Setup

#### Google Gemini API
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add to `.env` as `GEMINI_API_KEY`

#### IP Geolocation API
1. Sign up at [IPGeolocation.io](https://ipgeolocation.io/)
2. Get your free API key (1000 requests/day)
3. Add to `.env` as `IPGEOLOCATION_API_KEY`

## 📈 Performance & Scalability

### Expected Performance
- **Correlation Accuracy**: >80% in controlled environments
- **Response Time**: <2 seconds for real-time analysis
- **Scalability**: Handle 1000+ concurrent TOR connections
- **Throughput**: Process 10,000+ nodes with sub-second updates

### Resource Requirements
- **Memory**: 2GB RAM minimum, 4GB recommended
- **Storage**: 10GB for database and logs
- **CPU**: 2 cores minimum, 4 cores recommended
- **Network**: Stable internet connection for TOR data collection

## 🧪 Testing

### Unit Tests
```bash
pytest tests/unit/
```

### Integration Tests
```bash
pytest tests/integration/
```

### Load Testing
```bash
pytest tests/load/
```

### Security Testing
```bash
pytest tests/security/
```

## 📚 API Documentation

### Authentication
```bash
# Login
POST /auth/login
{
  "username": "admin",
  "password": "admin123"
}

# Get current user
GET /auth/me
Authorization: Bearer <token>
```

### TOR Nodes
```bash
# Get all nodes
GET /api/v1/nodes?limit=100&country=US&type=guard

# Search nodes
GET /api/v1/nodes/search?query=nickname

# Get network topology
GET /api/v1/network/topology
```

### Correlations
```bash
# Get correlations
GET /api/v1/correlations?min_confidence=0.8

# Start analysis
POST /api/v1/correlations/analyze

# Export data
GET /api/v1/export/correlations?format=json
```

### AI Analysis
```bash
# Get AI analysis
GET /api/v1/analysis/ai?type=network_patterns

# Generate report
POST /api/v1/reports/generate
```

## 🔍 Monitoring & Logging

### Application Logs
- **Location**: `/var/log/tor-analysis/`
- **Format**: JSON structured logging
- **Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL

### Metrics Collection
- **Response Times**: API endpoint performance
- **Error Rates**: Application error tracking
- **Resource Usage**: CPU, memory, disk utilization
- **Security Events**: Authentication failures, suspicious activity

### Health Checks
- **Endpoint**: `/health`
- **Database**: MongoDB connection status
- **Cache**: Redis connectivity
- **External APIs**: TOR network data sources

## 🛡️ Security Considerations

### Data Protection
- **Encryption**: All data encrypted in transit and at rest
- **Access Control**: Role-based permissions
- **Audit Trails**: Complete activity logging
- **Data Retention**: Configurable retention policies

### Network Security
- **Firewall Rules**: Strict ingress/egress controls
- **Rate Limiting**: API and authentication protection
- **DDoS Protection**: Nginx-based mitigation
- **SSL/TLS**: Strong encryption protocols

### Application Security
- **Input Validation**: Comprehensive sanitization
- **SQL Injection**: Parameterized queries
- **XSS Protection**: Content Security Policy
- **CSRF Protection**: Token-based validation

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Code Standards
- **Python**: Follow PEP 8 guidelines
- **JavaScript**: Use ESLint configuration
- **Documentation**: Update README and API docs
- **Testing**: Maintain >90% code coverage

### Commit Guidelines
```
feat: add new correlation algorithm
fix: resolve memory leak in node processing
docs: update API documentation
test: add unit tests for correlation service
```

## 📄 License

This project is developed for the Tamil Nadu Police Hackathon 2025. All rights reserved.

## 🏆 Hackathon Submission

### Team Information
- **Event**: Tamil Nadu Police Hackathon 2025
- **Challenge**: TOR - Unveil: Peel the Onion
- **Submission Date**: November 2025
- **Category**: Cybersecurity & Network Analysis

### Key Differentiators
1. **Real-time Processing**: Live correlation analysis with WebSocket updates
2. **AI Enhancement**: Advanced pattern recognition using Google Gemini API
3. **Comprehensive Security**: 8-layer security implementation
4. **Forensic Ready**: Legal-grade documentation and reporting
5. **Cost Effective**: Built entirely on free/open-source technologies
6. **Scalable Architecture**: Microservices with Docker containerization

### Expected Outcomes
- **Automated TOR topology mapping** with node correlation
- **Visualization dashboard** showing origin identification and confidence metrics
- **Exportable forensic report** with traced node data and activity flow
- **Real-time monitoring** capabilities for ongoing investigations
- **AI-enhanced analysis** for improved accuracy and threat detection

## 📞 Support

For technical support or questions about this project:

- **Documentation**: Check the `/docs` directory
- **Issues**: Create a GitHub issue
- **Security**: Report security issues privately
- **General**: Contact the development team

---

**Built with ❤️ for the Tamil Nadu Police Hackathon 2025**

*"Unveiling the layers of anonymity through advanced correlation analysis"*