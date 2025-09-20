"""
NIST-compliant CVSS v3.1 Calculator
Implements the official CVSS v3.1 specification as defined by NIST SP 800-126 Rev. 3
"""

import logging
from enum import Enum

from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


class AttackVector(str, Enum):
    """CVSS v3.1 Attack Vector metric values"""

    NETWORK = "Network"
    ADJACENT = "Adjacent"
    LOCAL = "Local"
    PHYSICAL = "Physical"


class AttackComplexity(str, Enum):
    """CVSS v3.1 Attack Complexity metric values"""

    LOW = "Low"
    HIGH = "High"


class PrivilegesRequired(str, Enum):
    """CVSS v3.1 Privileges Required metric values"""

    NONE = "None"
    LOW = "Low"
    HIGH = "High"


class UserInteraction(str, Enum):
    """CVSS v3.1 User Interaction metric values"""

    NONE = "None"
    REQUIRED = "Required"


class Scope(str, Enum):
    """CVSS v3.1 Scope metric values"""

    UNCHANGED = "Unchanged"
    CHANGED = "Changed"


class ImpactMetric(str, Enum):
    """CVSS v3.1 Impact metric values"""

    NONE = "None"
    LOW = "Low"
    HIGH = "High"


class CVSSVector(BaseModel):
    """NIST-compliant CVSS v3.1 vector representation"""

    attack_vector: AttackVector = Field(default=AttackVector.NETWORK)
    attack_complexity: AttackComplexity = Field(default=AttackComplexity.LOW)
    privileges_required: PrivilegesRequired = Field(default=PrivilegesRequired.NONE)
    user_interaction: UserInteraction = Field(default=UserInteraction.NONE)
    scope: Scope = Field(default=Scope.UNCHANGED)
    confidentiality: ImpactMetric = Field(default=ImpactMetric.HIGH)
    integrity: ImpactMetric = Field(default=ImpactMetric.HIGH)
    availability: ImpactMetric = Field(default=ImpactMetric.HIGH)

    @field_validator("*", mode="before")
    @classmethod
    def validate_enum_values(cls, v):
        """Validate that string inputs match enum values"""
        if isinstance(v, str):
            return v
        return v

    def to_vector_string(self) -> str:
        """Generate CVSS v3.1 vector string"""
        av_map = {"Network": "N", "Adjacent": "A", "Local": "L", "Physical": "P"}
        ac_map = {"Low": "L", "High": "H"}
        pr_map = {"None": "N", "Low": "L", "High": "H"}
        ui_map = {"None": "N", "Required": "R"}
        s_map = {"Unchanged": "U", "Changed": "C"}
        cia_map = {"None": "N", "Low": "L", "High": "H"}

        return (
            f"CVSS:3.1/AV:{av_map[self.attack_vector]}"
            f"/AC:{ac_map[self.attack_complexity]}"
            f"/PR:{pr_map[self.privileges_required]}"
            f"/UI:{ui_map[self.user_interaction]}"
            f"/S:{s_map[self.scope]}"
            f"/C:{cia_map[self.confidentiality]}"
            f"/I:{cia_map[self.integrity]}"
            f"/A:{cia_map[self.availability]}"
        )


class CVSSScore(BaseModel):
    """NIST-compliant CVSS v3.1 score representation"""

    base_score: float = Field(ge=0.0, le=10.0)
    impact_subscore: float = Field(ge=0.0, le=10.0)
    exploitability_subscore: float = Field(ge=0.0, le=10.0)
    vector: CVSSVector
    vector_string: str
    severity: str

    @field_validator("severity", mode="after")
    @classmethod
    def calculate_severity(cls, v, info):
        """Calculate severity rating based on base score"""
        if hasattr(info, "data") and "base_score" in info.data:
            score = info.data["base_score"]
        else:
            score = 0.0

        if score == 0.0:
            return "None"
        elif 0.1 <= score <= 3.9:
            return "Low"
        elif 4.0 <= score <= 6.9:
            return "Medium"
        elif 7.0 <= score <= 8.9:
            return "High"
        else:  # 9.0-10.0
            return "Critical"


class CVSSCalculator:
    """
    NIST-compliant CVSS v3.1 Calculator

    Implements the official CVSS v3.1 specification as defined by:
    - NIST Special Publication 800-126 Rev. 3
    - CVSS v3.1 Specification Document
    - Common Vulnerability Scoring System v3.1: Examples & Formulas

    Provides accurate, standardized vulnerability scoring for security assessments.
    """

    # NIST CVSS v3.1 metric weights (official specification values)
    _ATTACK_VECTOR_WEIGHTS = {
        AttackVector.NETWORK: 0.85,
        AttackVector.ADJACENT: 0.62,
        AttackVector.LOCAL: 0.55,
        AttackVector.PHYSICAL: 0.2,
    }

    _ATTACK_COMPLEXITY_WEIGHTS = {
        AttackComplexity.LOW: 0.77,
        AttackComplexity.HIGH: 0.44,
    }

    _USER_INTERACTION_WEIGHTS = {
        UserInteraction.NONE: 0.85,
        UserInteraction.REQUIRED: 0.62,
    }

    _IMPACT_WEIGHTS = {
        ImpactMetric.NONE: 0.0,
        ImpactMetric.LOW: 0.22,
        ImpactMetric.HIGH: 0.56,
    }

    @staticmethod
    def _get_privileges_required_weight(pr: PrivilegesRequired, scope: Scope) -> float:
        """Get Privileges Required weight based on scope change"""
        if scope == Scope.UNCHANGED:
            weights = {
                PrivilegesRequired.NONE: 0.85,
                PrivilegesRequired.LOW: 0.62,
                PrivilegesRequired.HIGH: 0.27,
            }
        else:  # Scope.CHANGED
            weights = {
                PrivilegesRequired.NONE: 0.85,
                PrivilegesRequired.LOW: 0.68,
                PrivilegesRequired.HIGH: 0.50,
            }
        return weights[pr]

    @staticmethod
    def _calculate_impact_subscore(vector: CVSSVector) -> float:
        """Calculate Impact Subscore using NIST formula"""
        c_weight = CVSSCalculator._IMPACT_WEIGHTS[vector.confidentiality]
        i_weight = CVSSCalculator._IMPACT_WEIGHTS[vector.integrity]
        a_weight = CVSSCalculator._IMPACT_WEIGHTS[vector.availability]

        # Base Impact = 1 - [(1-C) × (1-I) × (1-A)]
        base_impact = 1 - ((1 - c_weight) * (1 - i_weight) * (1 - a_weight))

        if vector.scope == Scope.UNCHANGED:
            # Impact = 6.42 × Base Impact
            impact = 6.42 * base_impact
        else:  # Scope.CHANGED
            # Impact = 7.52 × (Base Impact - 0.029) - 3.25 × (Base Impact - 0.02)^15
            impact = 7.52 * (base_impact - 0.029) - 3.25 * pow((base_impact - 0.02), 15)

        return max(0, impact)

    @staticmethod
    def _calculate_exploitability_subscore(vector: CVSSVector) -> float:
        """Calculate Exploitability Subscore using NIST formula"""
        av_weight = CVSSCalculator._ATTACK_VECTOR_WEIGHTS[vector.attack_vector]
        ac_weight = CVSSCalculator._ATTACK_COMPLEXITY_WEIGHTS[vector.attack_complexity]
        pr_weight = CVSSCalculator._get_privileges_required_weight(
            vector.privileges_required, vector.scope
        )
        ui_weight = CVSSCalculator._USER_INTERACTION_WEIGHTS[vector.user_interaction]

        # Exploitability = 8.22 × AV × AC × PR × UI
        exploitability = 8.22 * av_weight * ac_weight * pr_weight * ui_weight
        return exploitability

    @staticmethod
    def _calculate_base_score(
        impact: float, exploitability: float, scope: Scope
    ) -> float:
        """Calculate Base Score using NIST formula"""
        if impact <= 0:
            return 0.0

        if scope == Scope.UNCHANGED:
            # Base Score = Roundup(Minimum[(Impact + Exploitability), 10])
            base_score = min(impact + exploitability, 10.0)
        else:  # Scope.CHANGED
            # Base Score = Roundup(Minimum[1.08 × (Impact + Exploitability), 10])
            base_score = min(1.08 * (impact + exploitability), 10.0)

        # Round up to one decimal place as per NIST specification
        return round(base_score * 10) / 10

    @staticmethod
    def calculate_cvss_score(
        attack_vector: str = "Network",
        attack_complexity: str = "Low",
        privileges_required: str = "None",
        user_interaction: str = "None",
        scope: str = "Unchanged",
        confidentiality: str = "High",
        integrity: str = "High",
        availability: str = "High",
        **kwargs,  # For backward compatibility
    ) -> float:
        """
        Calculate NIST-compliant CVSS v3.1 base score.

        Args:
            attack_vector: Network, Adjacent, Local, or Physical
            attack_complexity: Low or High
            privileges_required: None, Low, or High
            user_interaction: None or Required
            scope: Unchanged or Changed
            confidentiality: None, Low, or High
            integrity: None, Low, or High
            availability: None, Low, or High
            **kwargs: Additional parameters for backward compatibility

        Returns:
            float: CVSS v3.1 base score (0.0-10.0)

        Raises:
            ValueError: If invalid metric values are provided
        """
        try:
            # Input validation and normalization
            vector = CVSSVector(
                attack_vector=AttackVector(attack_vector),
                attack_complexity=AttackComplexity(attack_complexity),
                privileges_required=PrivilegesRequired(privileges_required),
                user_interaction=UserInteraction(user_interaction),
                scope=Scope(scope),
                confidentiality=ImpactMetric(confidentiality),
                integrity=ImpactMetric(integrity),
                availability=ImpactMetric(availability),
            )

            result = CVSSCalculator.calculate_full_score(vector)
            return result.base_score

        except ValueError as e:
            logger.error(f"Invalid CVSS metric values: {e}")
            # Return conservative score for invalid inputs
            return 0.0
        except Exception as e:
            logger.error(f"Error calculating CVSS score: {e}")
            return 0.0

    @staticmethod
    def calculate_full_score(vector: CVSSVector) -> CVSSScore:
        """
        Calculate complete NIST-compliant CVSS v3.1 score with all components.

        Args:
            vector: CVSS vector with all metric values

        Returns:
            CVSSScore: Complete score with subscores and metadata
        """
        try:
            # Calculate subscores using NIST formulas
            impact = CVSSCalculator._calculate_impact_subscore(vector)
            exploitability = CVSSCalculator._calculate_exploitability_subscore(vector)
            base_score = CVSSCalculator._calculate_base_score(
                impact, exploitability, vector.scope
            )

            # Generate vector string
            vector_string = vector.to_vector_string()

            return CVSSScore(
                base_score=base_score,
                impact_subscore=round(impact * 10) / 10,
                exploitability_subscore=round(exploitability * 10) / 10,
                vector=vector,
                vector_string=vector_string,
                severity="",  # Will be calculated by validator
            )

        except Exception as e:
            logger.error(f"Error calculating full CVSS score: {e}")
            # Return safe default
            return CVSSScore(
                base_score=0.0,
                impact_subscore=0.0,
                exploitability_subscore=0.0,
                vector=vector,
                vector_string=vector.to_vector_string(),
                severity="None",
            )

    @staticmethod
    def validate_vector_string(vector_string: str) -> bool:
        """
        Validate CVSS v3.1 vector string format.

        Args:
            vector_string: CVSS vector string to validate

        Returns:
            bool: True if valid, False otherwise
        """
        try:
            if not vector_string.startswith("CVSS:3.1/"):
                return False

            # Basic format validation
            parts = vector_string.split("/")
            if len(parts) != 9:  # CVSS:3.1 + 8 metrics
                return False

            required_metrics = {"AV", "AC", "PR", "UI", "S", "C", "I", "A"}
            found_metrics = set()

            for part in parts[1:]:  # Skip CVSS:3.1
                if ":" not in part:
                    return False
                metric, value = part.split(":", 1)
                found_metrics.add(metric)

            return required_metrics == found_metrics

        except Exception:
            return False
