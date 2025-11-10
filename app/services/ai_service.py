import logging
from typing import Dict, List, Optional, Any
import json
import asyncio
from datetime import datetime

try:
    import google.generativeai as genai
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.schema import HumanMessage, SystemMessage
except ImportError:
    genai = None
    ChatGoogleGenerativeAI = None
    HumanMessage = None
    SystemMessage = None

from app.config import settings
from app.models import Correlation, TORNode

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.llm = None
        self.initialized = False
        self._initialize_ai()
        
    def _initialize_ai(self):
        """Initialize AI services"""
        try:
            # Disable AI service for now to prevent errors
            if False and settings.gemini_api_key and genai:
                genai.configure(api_key=settings.gemini_api_key)
                
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-pro",  # Use the stable model name
                    google_api_key=settings.gemini_api_key,
                    temperature=0.1,
                    max_tokens=1000
                )
                
                self.initialized = True
                logger.info("AI service initialized successfully")
            else:
                logger.debug("AI service disabled - using fallback responses")
                
        except Exception as e:
            logger.debug(f"AI service not available: {e}")
            
    async def analyze_correlation(self, correlation: Correlation, context: Dict) -> Optional[Dict]:
        """Analyze correlation using AI"""
        if not self.initialized:
            return None
            
        try:
            # Prepare analysis prompt
            prompt = self._create_correlation_prompt(correlation, context)
            
            # Get AI analysis
            messages = [
                SystemMessage(content="You are an expert cybersecurity analyst specializing in TOR network analysis and traffic correlation. Provide detailed, technical analysis."),
                HumanMessage(content=prompt)
            ]
            
            response = await self._call_ai_async(messages)
            
            if response:
                return self._parse_ai_response(response)
                
        except Exception as e:
            logger.error(f"Error in AI correlation analysis: {e}")
            
        return None
        
    def _create_correlation_prompt(self, correlation: Correlation, context: Dict) -> str:
        """Create analysis prompt for AI"""
        prompt = f"""
        Analyze this TOR network traffic correlation:
        
        CORRELATION DATA:
        - Entry Node: {correlation.entry_node}
        - Exit Node: {correlation.exit_node}
        - Origin IP: {correlation.origin_ip}
        - Destination IP: {correlation.destination_ip}
        - Confidence Score: {correlation.confidence_score}
        - Method: {correlation.correlation_method}
        - Timing Analysis: {json.dumps(correlation.timing_analysis, indent=2)}
        - Traffic Pattern: {json.dumps(correlation.traffic_pattern, indent=2)}
        
        CONTEXT DATA:
        - Entry Node Info: {json.dumps(context.get('entry_node', {}), indent=2)}
        - Exit Node Info: {json.dumps(context.get('exit_node', {}), indent=2)}
        - Geolocation: {json.dumps(context.get('geolocation', {}), indent=2)}
        
        Please provide analysis in the following JSON format:
        {{
            "confidence_assessment": {{
                "original_score": {correlation.confidence_score},
                "adjusted_score": <float between 0 and 1>,
                "confidence_multiplier": <float>,
                "reasoning": "<detailed reasoning>"
            }},
            "risk_assessment": {{
                "risk_level": "<low|medium|high|critical>",
                "risk_factors": ["<factor1>", "<factor2>"],
                "threat_indicators": ["<indicator1>", "<indicator2>"]
            }},
            "evidence_quality": {{
                "timing_evidence": "<weak|moderate|strong>",
                "pattern_evidence": "<weak|moderate|strong>",
                "geolocation_evidence": "<weak|moderate|strong>",
                "overall_quality": "<weak|moderate|strong>"
            }},
            "recommendations": [
                "<recommendation1>",
                "<recommendation2>"
            ],
            "additional_evidence": [
                {{
                    "type": "<evidence_type>",
                    "description": "<description>",
                    "weight": <float between 0 and 1>
                }}
            ]
        }}
        """
        
        return prompt
        
    async def _call_ai_async(self, messages: List) -> Optional[str]:
        """Make async call to AI service"""
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: self.llm.invoke(messages).content
            )
            return response
            
        except Exception as e:
            logger.error(f"Error calling AI service: {e}")
            return None
            
    def _parse_ai_response(self, response: str) -> Dict:
        """Parse AI response"""
        try:
            # Try to extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx]
                parsed = json.loads(json_str)
                
                # Extract key information
                confidence_mult = parsed.get('confidence_assessment', {}).get('confidence_multiplier', 1.0)
                evidence = parsed.get('additional_evidence', [])
                
                return {
                    'confidence_multiplier': confidence_mult,
                    'evidence': evidence,
                    'risk_assessment': parsed.get('risk_assessment', {}),
                    'recommendations': parsed.get('recommendations', []),
                    'full_analysis': parsed
                }
                
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            
        return {'confidence_multiplier': 1.0, 'evidence': []}
        
    async def analyze_network_patterns(self, nodes: List[TORNode], timeframe: str = "24h") -> Dict:
        """Analyze network patterns using AI"""
        if not self.initialized:
            return {}
            
        try:
            # Prepare network analysis prompt
            prompt = self._create_network_analysis_prompt(nodes, timeframe)
            
            messages = [
                SystemMessage(content="You are an expert in TOR network analysis and cybersecurity threat detection."),
                HumanMessage(content=prompt)
            ]
            
            response = await self._call_ai_async(messages)
            
            if response:
                return self._parse_network_analysis(response)
                
        except Exception as e:
            logger.error(f"Error in AI network analysis: {e}")
            
        return {}
        
    def _create_network_analysis_prompt(self, nodes: List[TORNode], timeframe: str) -> str:
        """Create network analysis prompt"""
        # Summarize node data
        total_nodes = len(nodes)
        countries = list(set(node.country for node in nodes))
        node_types = {}
        
        for node in nodes:
            node_types[node.type] = node_types.get(node.type, 0) + 1
            
        prompt = f"""
        Analyze this TOR network topology for the last {timeframe}:
        
        NETWORK SUMMARY:
        - Total Nodes: {total_nodes}
        - Countries: {len(countries)} ({', '.join(countries[:10])}...)
        - Node Distribution: {json.dumps(node_types, indent=2)}
        
        TOP NODES BY BANDWIDTH:
        """
        
        # Add top nodes by bandwidth
        sorted_nodes = sorted(nodes, key=lambda x: x.bandwidth, reverse=True)[:10]
        for i, node in enumerate(sorted_nodes):
            prompt += f"\n{i+1}. {node.nickname} ({node.country}) - {node.bandwidth} KB/s"
            
        prompt += """
        
        Please analyze and provide insights in JSON format:
        {
            "network_health": {
                "overall_status": "<healthy|concerning|critical>",
                "diversity_score": <float 0-1>,
                "centralization_risk": "<low|medium|high>",
                "geographic_distribution": "<poor|fair|good|excellent>"
            },
            "anomalies": [
                {
                    "type": "<anomaly_type>",
                    "description": "<description>",
                    "severity": "<low|medium|high>",
                    "affected_nodes": ["<fingerprint1>", "<fingerprint2>"]
                }
            ],
            "recommendations": [
                "<recommendation1>",
                "<recommendation2>"
            ],
            "threat_indicators": [
                {
                    "indicator": "<indicator>",
                    "confidence": <float 0-1>,
                    "description": "<description>"
                }
            ]
        }
        """
        
        return prompt
        
    def _parse_network_analysis(self, response: str) -> Dict:
        """Parse network analysis response"""
        try:
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
                
        except Exception as e:
            logger.error(f"Error parsing network analysis: {e}")
            
        return {}
        
    async def generate_threat_report(self, correlations: List[Correlation], analysis_period: Dict) -> str:
        """Generate threat intelligence report"""
        if not self.initialized:
            return "AI service not available for report generation."
            
        try:
            # Prepare report prompt
            prompt = self._create_report_prompt(correlations, analysis_period)
            
            messages = [
                SystemMessage(content="You are a cybersecurity analyst writing a professional threat intelligence report for law enforcement."),
                HumanMessage(content=prompt)
            ]
            
            response = await self._call_ai_async(messages)
            return response or "Unable to generate report."
            
        except Exception as e:
            logger.error(f"Error generating threat report: {e}")
            return f"Error generating report: {str(e)}"
            
    def _create_report_prompt(self, correlations: List[Correlation], analysis_period: Dict) -> str:
        """Create threat report prompt"""
        high_confidence = [c for c in correlations if c.confidence_score >= 0.8]
        medium_confidence = [c for c in correlations if 0.5 <= c.confidence_score < 0.8]
        
        prompt = f"""
        Generate a professional threat intelligence report based on TOR network analysis:
        
        ANALYSIS PERIOD: {analysis_period.get('start')} to {analysis_period.get('end')}
        
        CORRELATION SUMMARY:
        - Total Correlations: {len(correlations)}
        - High Confidence (≥80%): {len(high_confidence)}
        - Medium Confidence (50-79%): {len(medium_confidence)}
        
        HIGH CONFIDENCE CORRELATIONS:
        """
        
        for i, corr in enumerate(high_confidence[:5]):
            prompt += f"""
        {i+1}. Origin: {corr.origin_ip} → Destination: {corr.destination_ip}
           Confidence: {corr.confidence_score:.2%}
           Method: {corr.correlation_method}
           Entry Node: {corr.entry_node[:16]}...
           Exit Node: {corr.exit_node[:16]}...
        """
        
        prompt += """
        
        Please generate a comprehensive report including:
        1. Executive Summary
        2. Key Findings
        3. Threat Assessment
        4. Technical Analysis
        5. Recommendations
        6. Appendices (if needed)
        
        Format as a professional law enforcement report.
        """
        
        return prompt
        
    async def analyze_suspicious_activity(self, activity_data: Dict) -> Dict:
        """Analyze suspicious activity patterns"""
        if not self.initialized:
            return {}
            
        try:
            prompt = f"""
            Analyze this suspicious TOR network activity:
            
            {json.dumps(activity_data, indent=2)}
            
            Provide analysis in JSON format with threat level, indicators, and recommendations.
            """
            
            messages = [
                SystemMessage(content="You are a cybersecurity threat analyst specializing in TOR network monitoring."),
                HumanMessage(content=prompt)
            ]
            
            response = await self._call_ai_async(messages)
            
            if response:
                return self._parse_ai_response(response)
                
        except Exception as e:
            logger.error(f"Error analyzing suspicious activity: {e}")
            
        return {}