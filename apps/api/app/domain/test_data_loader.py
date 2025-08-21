"""Test data loader service for loading SWOT and Porter's data from YAML files."""

import os
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from .swot_models import SWOTAnalysis, SWOTElement, SWOTCategory
from .porters_models import PortersAnalysis, PortersElement, PortersForce, ForceIntensity
from .agent_models import AgentResult


class TestDataLoader:
    """Service for loading test data from YAML files."""
    
    def __init__(self, data_dir: str = "data/test_scenarios"):
        """Initialize the test data loader.
        
        Args:
            data_dir: Directory containing test scenario YAML files
        """
        self.data_dir = Path(data_dir)
        if not self.data_dir.is_absolute():
            # Make relative to current file location
            current_file = Path(__file__)
            self.data_dir = current_file.parent.parent / data_dir
        
        # Load taxonomy for understanding the structure
        self.taxonomy = self._load_taxonomy()
    
    def load_swot_analysis(self, scenario: str, tenant_id: str, user_id: str, scope: str = "industry") -> SWOTAnalysis:
        """Load SWOT analysis from YAML file.
        
        Args:
            scenario: Scenario name (e.g., 'fintech', 'healthcare', 'startup_fintech')
            tenant_id: Tenant ID for the analysis
            user_id: User ID who created the analysis
            scope: Scope of the analysis ('megatrends', 'regional', 'industry', 'company')
            
        Returns:
            SWOTAnalysis object populated from YAML data
        """
        # Determine file path based on scope
        if scope == "megatrends":
            yaml_file = self.data_dir / "megatrends" / f"megatrends_{scenario}.yaml"
        elif scope == "regional":
            yaml_file = self.data_dir / "regional" / f"regional_{scenario}.yaml"
        elif scope == "industry":
            yaml_file = self.data_dir / "industry" / f"{scenario}_global_swot.yaml"
        elif scope == "company":
            yaml_file = self.data_dir / "company" / f"{scenario}_swot.yaml"
        else:
            # Fallback to old pattern
            yaml_file = self.data_dir / f"{scenario}_swot.yaml"
        
        if not yaml_file.exists():
            raise FileNotFoundError(f"SWOT scenario file not found: {yaml_file}")
        
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)
        
        # Convert YAML data to SWOTAnalysis object
        return self._create_swot_analysis_from_data(data, tenant_id, user_id)
    
    def load_porters_analysis(self, scenario: str, tenant_id: str, user_id: str, scope: str = "industry") -> PortersAnalysis:
        """Load Porter's analysis from YAML file.
        
        Args:
            scenario: Scenario name (e.g., 'fintech', 'healthcare', 'startup_fintech')
            tenant_id: Tenant ID for the analysis
            user_id: User ID who created the analysis
            scope: Scope of the analysis ('megatrends', 'regional', 'industry', 'company')
            
        Returns:
            PortersAnalysis object populated from YAML data
        """
        # Determine file path based on scope
        if scope == "megatrends":
            yaml_file = self.data_dir / "megatrends" / f"megatrends_{scenario}.yaml"
        elif scope == "regional":
            yaml_file = self.data_dir / "regional" / f"regional_{scenario}.yaml"
        elif scope == "industry":
            yaml_file = self.data_dir / "industry" / f"{scenario}_global_porters.yaml"
        elif scope == "company":
            yaml_file = self.data_dir / "company" / f"{scenario}_porters.yaml"
        else:
            # Fallback to old pattern
            yaml_file = self.data_dir / f"{scenario}_porters.yaml"
        
        if not yaml_file.exists():
            raise FileNotFoundError(f"Porter's scenario file not found: {yaml_file}")
        
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)
        
        # Convert YAML data to PortersAnalysis object
        return self._create_porters_analysis_from_data(data, tenant_id, user_id)
    
    def load_agent_results(self, scenario: str = "test") -> List[AgentResult]:
        """Load test agent results from YAML file.
        
        Args:
            scenario: Scenario name (defaults to 'test')
            
        Returns:
            List of AgentResult objects
        """
        yaml_file = self.data_dir / "shared" / f"{scenario}_agent_results.yaml"
        
        if not yaml_file.exists():
            raise FileNotFoundError(f"Agent results file not found: {yaml_file}")
        
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)
        
        return self._create_agent_results_from_data(data)
    
    def load_strategic_sources(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load strategic sources configuration from YAML file.
        
        Returns:
            Dictionary of strategic sources by frequency
        """
        yaml_file = self.data_dir / "shared" / "strategic_sources.yaml"
        
        if not yaml_file.exists():
            raise FileNotFoundError(f"Strategic sources file not found: {yaml_file}")
        
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)
        
        return data
    
    def get_available_scenarios(self) -> Dict[str, List[str]]:
        """Get list of available test scenarios organized by scope.
        
        Returns:
            Dictionary of scenarios organized by scope
        """
        scenarios = {
            "megatrends": [],
            "regional": [],
            "industry": [],
            "company": [],
            "shared": []
        }
        
        # Scan each directory for available scenarios
        for scope in scenarios.keys():
            scope_dir = self.data_dir / scope
            if scope_dir.exists():
                if scope == "megatrends":
                    for yaml_file in scope_dir.glob("megatrends_*.yaml"):
                        scenario = yaml_file.stem.replace("megatrends_", "")
                        scenarios[scope].append(scenario)
                elif scope == "regional":
                    for yaml_file in scope_dir.glob("regional_*.yaml"):
                        scenario = yaml_file.stem.replace("regional_", "")
                        scenarios[scope].append(scenario)
                elif scope == "industry":
                    for yaml_file in scope_dir.glob("*_global_swot.yaml"):
                        scenario = yaml_file.stem.replace("_global_swot", "")
                        scenarios[scope].append(scenario)
                elif scope == "company":
                    for yaml_file in scope_dir.glob("*_swot.yaml"):
                        scenario = yaml_file.stem.replace("_swot", "")
                        scenarios[scope].append(scenario)
                elif scope == "shared":
                    for yaml_file in scope_dir.glob("*.yaml"):
                        scenarios[scope].append(yaml_file.stem)
        
        return scenarios
    
    def get_taxonomy(self) -> Dict[str, Any]:
        """Get the strategic intelligence taxonomy.
        
        Returns:
            Taxonomy structure
        """
        return self.taxonomy
    
    def _load_taxonomy(self) -> Dict[str, Any]:
        """Load the taxonomy from YAML file.
        
        Returns:
            Taxonomy data
        """
        yaml_file = self.data_dir / "shared" / "taxonomy.yaml"
        
        if not yaml_file.exists():
            return {}
        
        with open(yaml_file, 'r') as f:
            return yaml.safe_load(f)
    
    def load_megatrend(self, trend_name: str) -> Dict[str, Any]:
        """Load a specific megatrend.
        
        Args:
            trend_name: Name of the megatrend (e.g., 'climate_change')
            
        Returns:
            Megatrend data
        """
        yaml_file = self.data_dir / "megatrends" / f"megatrends_{trend_name}.yaml"
        
        if not yaml_file.exists():
            raise FileNotFoundError(f"Megatrend file not found: {yaml_file}")
        
        with open(yaml_file, 'r') as f:
            return yaml.safe_load(f)
    
    def load_regional_factor(self, region_name: str, factor_type: str) -> Dict[str, Any]:
        """Load a specific regional factor.
        
        Args:
            region_name: Name of the region (e.g., 'asia')
            factor_type: Type of factor (e.g., 'demographics')
            
        Returns:
            Regional factor data
        """
        yaml_file = self.data_dir / "regional" / f"regional_{region_name}_{factor_type}.yaml"
        
        if not yaml_file.exists():
            raise FileNotFoundError(f"Regional factor file not found: {yaml_file}")
        
        with open(yaml_file, 'r') as f:
            return yaml.safe_load(f)
    
    def _create_swot_analysis_from_data(self, data: Dict[str, Any], tenant_id: str, user_id: str) -> SWOTAnalysis:
        """Create SWOTAnalysis object from YAML data."""
        
        def create_swot_elements(elements_data: List[Dict], category: SWOTCategory) -> List[SWOTElement]:
            """Create SWOT elements from data."""
            elements = []
            for elem_data in elements_data:
                element = SWOTElement(
                    tenant_id=tenant_id,
                    category=category,
                    title=elem_data["title"],
                    description=elem_data["description"],
                    priority=elem_data["priority"],
                    keywords=elem_data["keywords"],
                    impact_areas=elem_data["impact_areas"],
                    created_by=user_id
                )
                elements.append(element)
            return elements
        
        return SWOTAnalysis(
            tenant_id=tenant_id,
            name=data["name"],
            description=data["description"],
            created_by=user_id,
            strategic_period=data.get("strategic_period", ""),
            industry_focus=data.get("industry_focus", []),
            market_position=data.get("market_position", ""),
            strengths=create_swot_elements(data.get("strengths", []), SWOTCategory.STRENGTH),
            weaknesses=create_swot_elements(data.get("weaknesses", []), SWOTCategory.WEAKNESS),
            opportunities=create_swot_elements(data.get("opportunities", []), SWOTCategory.OPPORTUNITY),
            threats=create_swot_elements(data.get("threats", []), SWOTCategory.THREAT)
        )
    
    def _create_porters_analysis_from_data(self, data: Dict[str, Any], tenant_id: str, user_id: str) -> PortersAnalysis:
        """Create PortersAnalysis object from YAML data."""
        
        def create_porters_elements(elements_data: List[Dict], force: PortersForce) -> List[PortersElement]:
            """Create Porter's elements from data."""
            elements = []
            for elem_data in elements_data:
                element = PortersElement(
                    tenant_id=tenant_id,
                    force=force,
                    title=elem_data["title"],
                    description=elem_data["description"],
                    intensity=ForceIntensity(elem_data["intensity"]),
                    impact_score=elem_data["impact_score"],
                    keywords=elem_data["keywords"],
                    factors=elem_data["factors"],
                    created_by=user_id
                )
                elements.append(element)
            return elements
        
        return PortersAnalysis(
            tenant_id=tenant_id,
            name=data["name"],
            description=data["description"],
            created_by=user_id,
            industry=data.get("industry", ""),
            market_position=data.get("market_position", ""),
            geographic_scope=data.get("geographic_scope", []),
            competitive_rivalry=create_porters_elements(
                data.get("competitive_rivalry", []), PortersForce.COMPETITIVE_RIVALRY
            ),
            new_entrants=create_porters_elements(
                data.get("new_entrants", []), PortersForce.NEW_ENTRANTS
            ),
            substitute_products=create_porters_elements(
                data.get("substitute_products", []), PortersForce.SUBSTITUTE_PRODUCTS
            ),
            supplier_power=create_porters_elements(
                data.get("supplier_power", []), PortersForce.SUPPLIER_POWER
            ),
            buyer_power=create_porters_elements(
                data.get("buyer_power", []), PortersForce.BUYER_POWER
            )
        )
    
    def _create_agent_results_from_data(self, data: Dict[str, Any]) -> List[AgentResult]:
        """Create AgentResult objects from YAML data."""
        agent_results = []
        
        for i, result_data in enumerate(data.get("agent_results", [])):
            # Parse datetime string and make it naive (UTC)
            published_at_str = result_data["published_at"].replace("Z", "+00:00")
            published_at = datetime.fromisoformat(published_at_str).replace(tzinfo=None)
            
            agent_result = AgentResult(
                id=f"test-result-{i}",
                agent_id="test-agent",
                execution_id="test-execution",
                tenant_id="demo",  # Default tenant for test data
                title=result_data["title"],
                content=result_data["content"],
                source_url=result_data["source_url"],
                source_name=result_data["source_name"],
                published_at=published_at,
                keywords_matched=result_data["keywords_matched"],
                sentiment=result_data["sentiment"],
                created_at=published_at
            )
            agent_results.append(agent_result)
        
        return agent_results
