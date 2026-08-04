import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from models import Strategy

# Load environment variables
load_dotenv()

class Settings(BaseModel):
    # Core API Keys
    gemini_api_key: str = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    
    # Paritok Token Optimization Settings
    paritok_api_key: str = Field(default_factory=lambda: os.getenv("PARITOK_API_KEY", ""))
    paritok_base_url: str = Field(default_factory=lambda: os.getenv("PARITOK_BASE_URL", "https://api.paritok.ai/v1"))
    paritok_model: str = Field(default_factory=lambda: os.getenv("PARITOK_MODEL", "paritok-4b-v1"))
    token_cost_per_1k_tokens: float = Field(default_factory=lambda: float(os.getenv("TOKEN_COST_PER_1K_TOKENS", "0.002")))

    # Core Agent Thresholds
    photo_confidence_threshold: float = Field(default=0.70)
    verification_threshold: float = Field(default=0.65)
    escalation_threshold: float = Field(default=0.85)

    # Simulated/Mock Configuration
    monitor_sleep_interval_sec: int = Field(default=10)
    max_portal_retries: int = Field(default=3)

    # Database Configuration
    db_provider: str = Field(default="json")

    # Standard Strategic Workflows
    default_routing: dict[str, Strategy] = Field(default_factory=lambda: {
        "garbage": Strategy(
            name="Waste Management Route",
            department="Waste Management Dept",
            sla_hours=24,
            escalation_path=["Area Supervisor", "Social Escalation"]
        ),
        "pothole": Strategy(
            name="Public Works Route",
            department="Public Works Dept (PWD)",
            sla_hours=72,
            escalation_path=["Chief PWD Engineer", "Social Escalation"]
        ),
        "fallen_tree": Strategy(
            name="Forestry Emergency Route",
            department="Forest & Parks Dept",
            sla_hours=12,
            escalation_path=["Horticulture Officer", "Social Escalation"]
        )
    })

# Central configuration instance
settings = Settings()

# Backward compatible global exports to prevent breaking existing imports
GEMINI_API_KEY = settings.gemini_api_key
PARITOK_API_KEY = settings.paritok_api_key
PARITOK_BASE_URL = settings.paritok_base_url
PARITOK_MODEL = settings.paritok_model
TOKEN_COST_PER_1K_TOKENS = settings.token_cost_per_1k_tokens
PHOTO_CONFIDENCE_THRESHOLD = settings.photo_confidence_threshold
VERIFICATION_THRESHOLD = settings.verification_threshold
ESCALATION_THRESHOLD = settings.escalation_threshold
MONITOR_SLEEP_INTERVAL_SEC = settings.monitor_sleep_interval_sec
MAX_PORTAL_RETRIES = settings.max_portal_retries
DEFAULT_ROUTING = settings.default_routing
