# TOR Analysis System - "Unveil: Peel the Onion"
## Tamil Nadu Police Hackathon 2025

---

## 🎯 Problem Statement

**Objective:** Develop an analytical system to trace TOR network users by correlating activity patterns and TOR node data to identify the probable origin IPs behind TOR-based traffic (email, browsing, etc.)

**Challenge:** Build a system that can "de-anonymize" TOR users for legitimate law enforcement investigations by analyzing network topology, timing patterns, and traffic correlations.

---

## 🏗️ Solution Approach

### Core Strategy: Multi-Layer Correlation Engine

Our approach focuses on building a comprehensive TOR traffic analysis system that combines:

1. **Real-time TOR network topology mapping**
2. **Statistical correlation analysis** using timing and traffic patterns
3. **AI-enhanced pattern recognition** for improved accuracy
4. **Interactive visualization dashboard** for forensic analysis
5. **Comprehensive reporting system** for legal documentation

### Key Innovation Points

- **Multi-Source Data Correlation**: Combine TOR directory data, network traffic analysis, and timing correlation
- **AI-Enhanced Analysis**: Use Google Gemini API for advanced pattern recognition and correlation
- **Probabilistic Matching**: Provide confidence scores rather than absolute identification
- **Real-time Processing**: Live monitoring and analysis capabilities
- **Forensic-Grade Documentation**: Legal-ready reports with audit trails

---

## 🛠️ Complete Tech Stack

### **Backend Core**
```
Framework & API:
├── FastAPI                 # High-performance async web framework
├── Python 3.11+           # Core programming language
├── Pydantic               # Data validation and serialization
├── Uvicorn                # ASGI server
└── Celery + Redis         # Distributed task queue for heavy processing
```

### **Frontend (Simplified Approach)**
```
Template Engine & UI:
├── Jinja2                 # Server-side templating
├── HTML5                  # Semantic markup
├── CSS3 + Tailwind CSS    # Styling framework
├── Vanilla JavaScript     # Client-side interactivity
├── D3.js                  # Network topology visualization
├── Chart.js               # Real-time charts and graphs
└── Socket.io              # Real-time WebSocket communication
```

### **Database & Storage**
```
Data Layer:
├── MongoDB Atlas          # Primary database (Free: 512MB)
├── Redis                  # Caching and session storage
└── GridFS                 # File storage for PCAP files
```

### **Network Analysis & TOR Integration**
```
TOR & Network Tools:
├── Stem                   # TOR controller library
├── Scapy                  # Packet analysis and manipulation
├── NetworkX               # Graph analysis and network topology
├── Requests + aiohttp     # Async HTTP client for API calls
└── dnspython              # DNS resolution and analysis
```

### **Data Processing & AI**
```
Analytics & ML:
├── Pandas + NumPy         # Data manipulation and analysis
├── Scikit-learn           # Machine learning algorithms
├── LangChain              # AI orchestration framework
├── Google Gemini API      # AI pattern recognition (Free: 15 req/min)
├── Matplotlib + Plotly    # Data visualization
└── Hugging Face           # Additional NLP capabilities
```

### **Security & Containerization**
```
Infrastructure:
├── Docker                 # Containerization
├── Docker Compose         # Multi-container orchestration
├── Nginx                  # Reverse proxy and load balancer
└── Let's Encrypt          # Free SSL certificates
```

---

## 🔒 8-Layer Security Firewall (All Free)

### **Layer 1: Network Perimeter Security**
```bash
Tool: UFW (Uncomplicated Firewall)
- Default deny all incoming traffic
- Allow only essential ports (22, 80, 443)
- Rate limiting on SSH connections
```

### **Layer 2: Web Application Firewall**
```bash
Tool: Nginx + ModSecurity
- SQL injection protection
- XSS attack prevention
- Rate limiting per IP
- Malicious request filtering
```

### **Layer 3: Container Security**
```bash
Tools: Docker Security + Trivy Scanner
- Non-root container execution
- Minimal base images (Alpine Linux)
- Regular vulnerability scanning
- Resource limits and isolation
```

### **Layer 4: API Gateway Security**
```python
Tool: FastAPI Security Middleware
- JWT token authentication
- API key validation
- Request rate limiting
- CORS policy enforcement
```

### **Layer 5: Database Security**
```bash
Tool: MongoDB Atlas Security
- Connection encryption (TLS/SSL)
- IP address whitelisting
- Database-level authentication
- Role-based access control
```

### **Layer 6: Input Validation & Sanitization**
```python
Tool: Pydantic + Custom Validators
- Strict data type validation
- SQL injection prevention
- XSS protection
- File upload security
```

### **Layer 7: Intrusion Detection & Monitoring**
```bash
Tools: Fail2Ban + ELK Stack
- Real-time log monitoring
- Automated threat response
- Suspicious activity detection
- Performance monitoring
```

### **Layer 8: Encryption & Secrets Management**
```bash
Tools: HashiCorp Vault + Environment Encryption
- API key encryption
- Database credential rotation
- Secure configuration management
- End-to-end encryption
```

---

## 🌐 Free APIs & External Services

### **TOR Network Data Sources**
```
├── TOR Metrics API        # Official TOR network statistics
├── TOR Directory APIs     # Relay and consensus information
├── OnionScan API          # Hidden service analysis
└── Stem Controller        # Direct TOR process interaction
```

### **Geolocation & Network Intelligence**
```
├── IPGeolocation.io       # 1000 requests/day free
├── IP-API.com             # 1000 requests/hour free
├── MaxMind GeoLite2       # Free IP geolocation database
└── Shodan API             # Limited free tier for network scanning
```

### **Additional AI Services**
```
├── Google Gemini API      # 15 requests/minute free
├── Hugging Face API       # Free transformer models
├── Cohere API             # Free tier available
└── OpenAI API             # Limited free credits
```

---

## 🏛️ System Architecture

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

---

## 📊 Expected Deliverables

### **1. Automated TOR Topology Mapping**
- Real-time collection of TOR relay information
- Dynamic network graph visualization
- Node correlation and path analysis

### **2. Interactive Visualization Dashboard**
- Network topology with live updates
- Traffic flow visualization
- Confidence scoring heat maps
- Timeline reconstruction interface

### **3. AI-Enhanced Correlation Engine**
- Pattern recognition using Gemini API
- Statistical analysis of timing correlations
- Machine learning models for accuracy improvement
- Behavioral analysis algorithms

### **4. Forensic Reporting System**
- Exportable PDF reports
- Legal-grade documentation
- Audit trail maintenance
- Evidence chain documentation

### **5. Real-time Monitoring Interface**
- Live traffic analysis
- Alert system for suspicious activities
- Performance metrics dashboard
- System health monitoring

---

## 🎯 Key Success Metrics

- **Correlation Accuracy**: >80% in controlled environments
- **Response Time**: <2 seconds for real-time analysis
- **Scalability**: Handle 1000+ concurrent TOR connections
- **Security**: Zero security vulnerabilities in penetration testing
- **Usability**: Intuitive interface for law enforcement personnel

---

## 📅 Development Timeline

### **Phase 1: Foundation (Week 1-2)**
- Set up development environment
- Implement basic FastAPI structure
- Configure MongoDB Atlas connection
- Create basic Jinja2 templates

### **Phase 2: Core Features (Week 3-4)**
- TOR data collection modules
- Basic correlation algorithms
- Database schema design
- Security implementation

### **Phase 3: Advanced Features (Week 5-6)**
- AI integration with Gemini API
- Advanced visualization with D3.js
- Real-time processing pipeline
- Comprehensive testing

### **Phase 4: Polish & Documentation (Week 7)**
- Performance optimization
- Security hardening
- Documentation completion
- Presentation preparation

---

## 💡 Competitive Advantages

1. **Simplified Architecture**: No heavy frontend frameworks, faster development
2. **AI-Enhanced Analysis**: Advanced pattern recognition capabilities
3. **Real-time Processing**: Live monitoring and analysis
4. **Comprehensive Security**: 8-layer security implementation
5. **Cost-Effective**: Entirely built on free/open-source technologies
6. **Forensic-Ready**: Legal-grade documentation and reporting

---

## 🚀 Deployment Strategy

### **Development Environment**
- Local Docker containers
- MongoDB Atlas free tier
- Local Redis instance

### **Production Deployment**
- Google Cloud Run (free tier)
- Railway or Render (free hosting)
- Cloudflare CDN (free tier)
- Let's Encrypt SSL certificates

---

*This documentation serves as the complete blueprint for developing a winning TOR analysis system for the Tamil Nadu Police Hackathon 2025.*