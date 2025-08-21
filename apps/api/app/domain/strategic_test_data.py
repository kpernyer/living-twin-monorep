"""Comprehensive test data for SWOT and Porter's Five Forces strategic signal detection."""

from datetime import datetime
from typing import Dict, List, Any

from .swot_models import SWOTAnalysis, SWOTElement, SWOTCategory
from .porters_models import PortersAnalysis, PortersElement, PortersForce, ForceIntensity


class StrategicTestData:
    """Test data generator for strategic signal detection."""
    
    @staticmethod
    def create_fintech_swot_analysis(tenant_id: str, user_id: str) -> SWOTAnalysis:
        """Create a realistic fintech SWOT analysis for testing."""
        
        return SWOTAnalysis(
            tenant_id=tenant_id,
            name="Q1 2024 Fintech Strategic Review",
            description="Strategic analysis for emerging fintech startup in digital payments",
            created_by=user_id,
            strategic_period="Q1 2024",
            industry_focus=["fintech", "digital payments", "mobile banking"],
            market_position="emerging challenger in mobile payments",
            
            # Strengths (Priority 1-4)
            strengths=[
                SWOTElement(
                    tenant_id=tenant_id,
                    category=SWOTCategory.STRENGTH,
                    title="AI-Powered Security",
                    description="Advanced machine learning fraud detection system with 99.9% accuracy",
                    priority=1,
                    keywords=["AI security", "fraud detection", "machine learning", "payment protection", "cybersecurity"],
                    impact_areas=["technology", "security"],
                    created_by=user_id
                ),
                SWOTElement(
                    tenant_id=tenant_id,
                    category=SWOTCategory.STRENGTH,
                    title="User Experience Design",
                    description="Intuitive mobile app with 4.8-star rating and 95% user retention",
                    priority=2,
                    keywords=["UX", "user interface", "mobile app", "customer experience", "user retention"],
                    impact_areas=["market", "operations"],
                    created_by=user_id
                ),
                SWOTElement(
                    tenant_id=tenant_id,
                    category=SWOTCategory.STRENGTH,
                    title="Agile Development",
                    description="Rapid iteration capability with 2-week sprint cycles",
                    priority=3,
                    keywords=["agile", "rapid development", "quick iteration", "flexible", "sprint cycles"],
                    impact_areas=["operations", "technology"],
                    created_by=user_id
                ),
                SWOTElement(
                    tenant_id=tenant_id,
                    category=SWOTCategory.STRENGTH,
                    title="Regulatory Compliance",
                    description="Full compliance with PCI DSS, GDPR, and local financial regulations",
                    priority=4,
                    keywords=["compliance", "PCI DSS", "GDPR", "regulatory", "financial regulations"],
                    impact_areas=["compliance", "operations"],
                    created_by=user_id
                )
            ],
            
            # Weaknesses (Priority 1-4)
            weaknesses=[
                SWOTElement(
                    tenant_id=tenant_id,
                    category=SWOTCategory.WEAKNESS,
                    title="Limited Market Share",
                    description="Only 2% market share in target markets, trailing major competitors",
                    priority=1,
                    keywords=["market share", "competition", "small player", "penetration", "market position"],
                    impact_areas=["market", "finance"],
                    created_by=user_id
                ),
                SWOTElement(
                    tenant_id=tenant_id,
                    category=SWOTCategory.WEAKNESS,
                    title="Brand Recognition",
                    description="Low brand awareness compared to established players like Apple Pay",
                    priority=2,
                    keywords=["brand awareness", "marketing", "visibility", "recognition", "brand building"],
                    impact_areas=["market", "operations"],
                    created_by=user_id
                ),
                SWOTElement(
                    tenant_id=tenant_id,
                    category=SWOTCategory.WEAKNESS,
                    title="Funding Constraints",
                    description="Limited capital for aggressive expansion and marketing campaigns",
                    priority=3,
                    keywords=["funding", "capital", "investment", "budget", "financial resources"],
                    impact_areas=["finance", "operations"],
                    created_by=user_id
                ),
                SWOTElement(
                    tenant_id=tenant_id,
                    category=SWOTCategory.WEAKNESS,
                    title="Geographic Concentration",
                    description="Over-reliance on North American markets, limited international presence",
                    priority=4,
                    keywords=["geographic", "international", "global expansion", "market concentration", "regional focus"],
                    impact_areas=["market", "operations"],
                    created_by=user_id
                )
            ],
            
            # Opportunities (Priority 1-4)
            opportunities=[
                SWOTElement(
                    tenant_id=tenant_id,
                    category=SWOTCategory.OPPORTUNITY,
                    title="Emerging Markets",
                    description="High growth potential in Southeast Asia and Latin America",
                    priority=1,
                    keywords=["emerging markets", "global expansion", "international", "growth", "Southeast Asia", "Latin America"],
                    impact_areas=["market", "finance"],
                    created_by=user_id
                ),
                SWOTElement(
                    tenant_id=tenant_id,
                    category=SWOTCategory.OPPORTUNITY,
                    title="Partnership Opportunities",
                    description="Potential partnerships with major banks and retailers",
                    priority=2,
                    keywords=["partnership", "collaboration", "alliance", "integration", "banks", "retailers"],
                    impact_areas=["market", "operations"],
                    created_by=user_id
                ),
                SWOTElement(
                    tenant_id=tenant_id,
                    category=SWOTCategory.OPPORTUNITY,
                    title="AI Innovation",
                    description="Opportunity to lead in AI-powered financial services",
                    priority=3,
                    keywords=["AI innovation", "new technology", "breakthrough", "innovation", "financial services"],
                    impact_areas=["technology", "market"],
                    created_by=user_id
                ),
                SWOTElement(
                    tenant_id=tenant_id,
                    category=SWOTCategory.OPPORTUNITY,
                    title="Regulatory Changes",
                    description="New open banking regulations creating opportunities for fintech",
                    priority=4,
                    keywords=["open banking", "regulation", "policy change", "fintech opportunity", "regulatory changes"],
                    impact_areas=["compliance", "market"],
                    created_by=user_id
                )
            ],
            
            # Threats (Priority 1-4)
            threats=[
                SWOTElement(
                    tenant_id=tenant_id,
                    category=SWOTCategory.THREAT,
                    title="Big Tech Competition",
                    description="Apple Pay, Google Pay, and Amazon expanding aggressively",
                    priority=1,
                    keywords=["Apple Pay", "Google Pay", "big tech", "competition", "Amazon", "aggressive expansion"],
                    impact_areas=["market", "competition"],
                    created_by=user_id
                ),
                SWOTElement(
                    tenant_id=tenant_id,
                    category=SWOTCategory.THREAT,
                    title="Regulatory Changes",
                    description="Increasing financial regulations and compliance requirements",
                    priority=2,
                    keywords=["regulation", "policy change", "compliance", "legal", "financial regulations"],
                    impact_areas=["compliance", "operations"],
                    created_by=user_id
                ),
                SWOTElement(
                    tenant_id=tenant_id,
                    category=SWOTCategory.THREAT,
                    title="Cybersecurity Threats",
                    description="Growing sophistication of cyber attacks on financial systems",
                    priority=3,
                    keywords=["cybersecurity", "hacking", "data breach", "security threat", "cyber attacks"],
                    impact_areas=["technology", "security"],
                    created_by=user_id
                ),
                SWOTElement(
                    tenant_id=tenant_id,
                    category=SWOTCategory.THREAT,
                    title="Economic Downturn",
                    description="Potential recession affecting consumer spending on fintech",
                    priority=4,
                    keywords=["economic downturn", "recession", "consumer spending", "economic risk", "market volatility"],
                    impact_areas=["market", "finance"],
                    created_by=user_id
                )
            ]
        )
    
    @staticmethod
    def create_fintech_porters_analysis(tenant_id: str, user_id: str) -> PortersAnalysis:
        """Create a realistic fintech Porter's Five Forces analysis for testing."""
        
        return PortersAnalysis(
            tenant_id=tenant_id,
            name="Q1 2024 Fintech Competitive Landscape",
            description="Porter's Five Forces analysis for digital payments industry",
            created_by=user_id,
            industry="fintech",
            market_position="emerging challenger",
            geographic_scope=["North America", "Europe", "Southeast Asia"],
            
            # Competitive Rivalry
            competitive_rivalry=[
                PortersElement(
                    tenant_id=tenant_id,
                    force=PortersForce.COMPETITIVE_RIVALRY,
                    title="Big Tech Dominance",
                    description="Apple Pay and Google Pay control 85% of mobile payments market",
                    intensity=ForceIntensity.VERY_HIGH,
                    impact_score=0.9,
                    keywords=["Apple Pay", "Google Pay", "market dominance", "mobile payments", "big tech"],
                    factors=["brand recognition", "user base", "ecosystem integration"],
                    created_by=user_id
                ),
                PortersElement(
                    tenant_id=tenant_id,
                    force=PortersForce.COMPETITIVE_RIVALRY,
                    title="Traditional Banks",
                    description="Major banks launching their own digital payment solutions",
                    intensity=ForceIntensity.HIGH,
                    impact_score=0.7,
                    keywords=["traditional banks", "digital payments", "banking apps", "financial institutions"],
                    factors=["customer trust", "regulatory advantage", "existing relationships"],
                    created_by=user_id
                ),
                PortersElement(
                    tenant_id=tenant_id,
                    force=PortersForce.COMPETITIVE_RIVALRY,
                    title="Startup Competition",
                    description="Numerous fintech startups competing for market share",
                    intensity=ForceIntensity.MEDIUM,
                    impact_score=0.5,
                    keywords=["fintech startups", "market competition", "startup rivalry", "new players"],
                    factors=["innovation", "agility", "funding"],
                    created_by=user_id
                )
            ],
            
            # New Entrants
            new_entrants=[
                PortersElement(
                    tenant_id=tenant_id,
                    force=PortersForce.NEW_ENTRANTS,
                    title="Tech Giants",
                    description="Amazon, Meta, and other tech companies entering payments",
                    intensity=ForceIntensity.HIGH,
                    impact_score=0.8,
                    keywords=["Amazon", "Meta", "tech giants", "new entrants", "market entry"],
                    factors=["capital resources", "user base", "technology expertise"],
                    created_by=user_id
                ),
                PortersElement(
                    tenant_id=tenant_id,
                    force=PortersForce.NEW_ENTRANTS,
                    title="International Players",
                    description="Alipay, WeChat Pay expanding globally",
                    intensity=ForceIntensity.MEDIUM,
                    impact_score=0.6,
                    keywords=["Alipay", "WeChat Pay", "international expansion", "global players"],
                    factors=["market experience", "capital", "technology"],
                    created_by=user_id
                )
            ],
            
            # Substitute Products
            substitute_products=[
                PortersElement(
                    tenant_id=tenant_id,
                    force=PortersForce.SUBSTITUTE_PRODUCTS,
                    title="Cryptocurrency Payments",
                    description="Bitcoin, Ethereum, and stablecoins as payment alternatives",
                    intensity=ForceIntensity.MEDIUM,
                    impact_score=0.6,
                    keywords=["cryptocurrency", "Bitcoin", "Ethereum", "stablecoins", "crypto payments"],
                    factors=["decentralization", "lower fees", "global access"],
                    created_by=user_id
                ),
                PortersElement(
                    tenant_id=tenant_id,
                    force=PortersForce.SUBSTITUTE_PRODUCTS,
                    title="Traditional Payment Methods",
                    description="Cash, credit cards, and bank transfers still dominant",
                    intensity=ForceIntensity.LOW,
                    impact_score=0.3,
                    keywords=["cash", "credit cards", "bank transfers", "traditional payments"],
                    factors=["familiarity", "acceptance", "simplicity"],
                    created_by=user_id
                )
            ],
            
            # Supplier Power
            supplier_power=[
                PortersElement(
                    tenant_id=tenant_id,
                    force=PortersForce.SUPPLIER_POWER,
                    title="Payment Processors",
                    description="Stripe, Square, and other processors control payment infrastructure",
                    intensity=ForceIntensity.HIGH,
                    impact_score=0.7,
                    keywords=["Stripe", "Square", "payment processors", "infrastructure", "processing fees"],
                    factors=["market concentration", "switching costs", "technology dependency"],
                    created_by=user_id
                ),
                PortersElement(
                    tenant_id=tenant_id,
                    force=PortersForce.SUPPLIER_POWER,
                    title="Cloud Providers",
                    description="AWS, Google Cloud, Azure control cloud infrastructure",
                    intensity=ForceIntensity.MEDIUM,
                    impact_score=0.5,
                    keywords=["AWS", "Google Cloud", "Azure", "cloud providers", "infrastructure"],
                    factors=["market concentration", "switching costs", "reliability"],
                    created_by=user_id
                )
            ],
            
            # Buyer Power
            buyer_power=[
                PortersElement(
                    tenant_id=tenant_id,
                    force=PortersForce.BUYER_POWER,
                    title="Large Merchants",
                    description="Walmart, Amazon, and other large retailers have bargaining power",
                    intensity=ForceIntensity.HIGH,
                    impact_score=0.8,
                    keywords=["Walmart", "Amazon", "large merchants", "bargaining power", "retailers"],
                    factors=["volume", "alternatives", "brand power"],
                    created_by=user_id
                ),
                PortersElement(
                    tenant_id=tenant_id,
                    force=PortersForce.BUYER_POWER,
                    title="Consumer Choice",
                    description="Consumers have multiple payment options and low switching costs",
                    intensity=ForceIntensity.MEDIUM,
                    impact_score=0.6,
                    keywords=["consumer choice", "switching costs", "payment options", "user preferences"],
                    factors=["alternatives", "low switching costs", "price sensitivity"],
                    created_by=user_id
                )
            ]
        )
    
    @staticmethod
    def get_strategic_test_sources() -> Dict[str, List[Dict[str, Any]]]:
        """Get strategic test sources with different update frequencies."""
        
        return {
            "high_frequency": [
                {
                    "name": "TechCrunch",
                    "url": "https://techcrunch.com",
                    "category": "tech_news",
                    "update_frequency": "real_time",
                    "keywords": ["startup", "funding", "AI", "technology", "fintech"],
                    "description": "Real-time tech news and startup coverage"
                },
                {
                    "name": "Reuters Technology",
                    "url": "https://www.reuters.com/technology",
                    "category": "tech_news",
                    "update_frequency": "real_time",
                    "keywords": ["technology", "AI", "regulation", "cybersecurity", "fintech"],
                    "description": "Real-time technology news and analysis"
                },
                {
                    "name": "Financial Times Tech",
                    "url": "https://www.ft.com/technology",
                    "category": "tech_news",
                    "update_frequency": "daily",
                    "keywords": ["technology", "fintech", "regulation", "market analysis", "AI"],
                    "description": "Daily technology and fintech coverage"
                }
            ],
            "medium_frequency": [
                {
                    "name": "MIT Technology Review",
                    "url": "https://www.technologyreview.com",
                    "category": "research",
                    "update_frequency": "weekly",
                    "keywords": ["AI", "machine learning", "innovation", "research", "technology trends"],
                    "description": "Weekly technology research and trends"
                },
                {
                    "name": "Harvard Business Review",
                    "url": "https://hbr.org",
                    "category": "business_strategy",
                    "update_frequency": "weekly",
                    "keywords": ["strategy", "leadership", "innovation", "business", "management"],
                    "description": "Weekly business strategy and leadership insights"
                },
                {
                    "name": "McKinsey Insights",
                    "url": "https://www.mckinsey.com/insights",
                    "category": "business_strategy",
                    "update_frequency": "weekly",
                    "keywords": ["strategy", "digital transformation", "innovation", "business", "management"],
                    "description": "Weekly strategic insights and analysis"
                }
            ],
            "low_frequency": [
                {
                    "name": "CIA World Factbook",
                    "url": "https://www.cia.gov/the-world-factbook",
                    "category": "geopolitical",
                    "update_frequency": "yearly",
                    "keywords": ["demographics", "economy", "geography", "government", "infrastructure"],
                    "description": "Annual geopolitical and demographic data"
                },
                {
                    "name": "World Bank Data",
                    "url": "https://data.worldbank.org",
                    "category": "economic",
                    "update_frequency": "quarterly",
                    "keywords": ["economy", "GDP", "development", "demographics", "trade"],
                    "description": "Quarterly economic and development data"
                },
                {
                    "name": "UNESCO Statistics",
                    "url": "https://en.unesco.org/fieldoffice/brussels/statistics",
                    "category": "demographic",
                    "update_frequency": "yearly",
                    "keywords": ["education", "demographics", "culture", "development", "statistics"],
                    "description": "Annual demographic and cultural statistics"
                }
            ],
            "megatrends": [
                {
                    "name": "Pew Research Center",
                    "url": "https://www.pewresearch.org",
                    "category": "demographic_trends",
                    "update_frequency": "monthly",
                    "keywords": ["demographics", "social trends", "technology adoption", "generational changes", "lifestyle"],
                    "description": "Monthly demographic and social trend analysis"
                },
                {
                    "name": "Brookings Institution",
                    "url": "https://www.brookings.edu",
                    "category": "policy_trends",
                    "update_frequency": "weekly",
                    "keywords": ["policy", "economics", "technology", "demographics", "global trends"],
                    "description": "Weekly policy and economic trend analysis"
                },
                {
                    "name": "World Economic Forum",
                    "url": "https://www.weforum.org",
                    "category": "global_trends",
                    "update_frequency": "monthly",
                    "keywords": ["global trends", "technology", "economics", "demographics", "future of work"],
                    "description": "Monthly global trend analysis and future insights"
                }
            ]
        }
    
    @staticmethod
    def get_test_agent_results() -> List[Dict[str, Any]]:
        """Get realistic test agent results for signal detection."""
        
        return [
            {
                "title": "Apple Pay Expands to 15 New Countries",
                "content": "Apple announced today that Apple Pay will be available in 15 new countries including South Korea, Brazil, and South Africa. This expansion significantly increases Apple's global reach in mobile payments and puts pressure on local competitors.",
                "keywords_matched": ["Apple Pay", "expansion", "mobile payments", "global reach"],
                "sentiment": "neutral",
                "source_name": "TechCrunch",
                "source_url": "https://techcrunch.com/apple-pay-expansion",
                "published_at": datetime.utcnow()
            },
            {
                "title": "New AI Security Regulations Proposed for Financial Services",
                "content": "Federal regulators proposed new AI security requirements for financial institutions. The regulations would require enhanced cybersecurity measures and AI governance frameworks, potentially increasing compliance costs for fintech companies.",
                "keywords_matched": ["AI security", "regulation", "compliance", "financial services", "cybersecurity"],
                "sentiment": "negative",
                "source_name": "Reuters",
                "source_url": "https://reuters.com/ai-security-regulation",
                "published_at": datetime.utcnow()
            },
            {
                "title": "Digital Payment Adoption Soars in Emerging Markets",
                "content": "Mobile payment adoption in emerging markets grew 45% year-over-year, with Southeast Asia and Latin America leading the growth. This presents significant opportunities for fintech companies looking to expand internationally.",
                "keywords_matched": ["emerging markets", "digital payments", "growth", "Southeast Asia", "Latin America"],
                "sentiment": "positive",
                "source_name": "Financial Times",
                "source_url": "https://ft.com/emerging-markets-payments",
                "published_at": datetime.utcnow()
            },
            {
                "title": "Stripe Raises Processing Fees for Small Businesses",
                "content": "Payment processor Stripe announced a 0.5% increase in processing fees for small businesses, citing rising infrastructure costs. This could impact fintech companies that rely on Stripe's payment infrastructure.",
                "keywords_matched": ["Stripe", "processing fees", "payment processors", "infrastructure costs"],
                "sentiment": "negative",
                "source_name": "TechCrunch",
                "source_url": "https://techcrunch.com/stripe-fee-increase",
                "published_at": datetime.utcnow()
            },
            {
                "title": "South Korea's Digital Payment Market Grows 60%",
                "content": "South Korea's digital payment market experienced 60% growth in 2023, driven by government initiatives and changing consumer preferences. The market is now valued at $45 billion, creating opportunities for international fintech players.",
                "keywords_matched": ["South Korea", "digital payments", "growth", "market opportunity", "government initiatives"],
                "sentiment": "positive",
                "source_name": "Financial Times",
                "source_url": "https://ft.com/south-korea-payments",
                "published_at": datetime.utcnow()
            },
            {
                "title": "Amazon Launches New Payment Service",
                "content": "Amazon announced Amazon Pay Plus, a new payment service that integrates with existing bank accounts. This move intensifies competition in the digital payments space and could impact market share for existing players.",
                "keywords_matched": ["Amazon", "payment service", "competition", "market share", "digital payments"],
                "sentiment": "negative",
                "source_name": "Reuters",
                "source_url": "https://reuters.com/amazon-pay-plus",
                "published_at": datetime.utcnow()
            },
            {
                "title": "Open Banking Regulations Take Effect in Europe",
                "content": "New open banking regulations came into effect across Europe, requiring banks to share customer data with authorized third-party providers. This creates opportunities for fintech companies to develop new services.",
                "keywords_matched": ["open banking", "regulation", "Europe", "fintech opportunity", "banking data"],
                "sentiment": "positive",
                "source_name": "Financial Times",
                "source_url": "https://ft.com/open-banking-europe",
                "published_at": datetime.utcnow()
            },
            {
                "title": "Major Data Breach Affects Payment Processors",
                "content": "A sophisticated cyber attack targeted multiple payment processors, compromising customer data from over 100 million accounts. This highlights the growing cybersecurity threats facing the financial services industry.",
                "keywords_matched": ["cybersecurity", "data breach", "payment processors", "cyber attacks", "financial services"],
                "sentiment": "negative",
                "source_name": "Reuters",
                "source_url": "https://reuters.com/payment-processor-breach",
                "published_at": datetime.utcnow()
            }
        ]
