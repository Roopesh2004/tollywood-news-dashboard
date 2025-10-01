import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for CrewAI environment"""
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Optional: Other LLM providers
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    # CrewAI Settings
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4")
    MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "10"))
    VERBOSE = os.getenv("VERBOSE", "true").lower() == "true"
    
    @classmethod
    def validate(cls):
        """Validate that required configuration is present"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required. Please set it in your .env file.")
        
        return True
