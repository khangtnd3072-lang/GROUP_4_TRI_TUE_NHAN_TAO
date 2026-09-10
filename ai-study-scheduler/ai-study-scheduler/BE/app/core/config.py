from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "AI Study Scheduler API"
    API_PREFIX: str = "/api"

    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "smart_study_scheduler"

    FRONTEND_ORIGINS: str = "http://localhost:5500,http://127.0.0.1:5500"

    SLOT_MINUTES: int = 30
    MAX_STUDY_HOURS_PER_DAY: float = 3.0
    MAX_SESSION_HOURS: float = 2.0

    GA_POPULATION_SIZE: int = 80
    GA_GENERATIONS: int = 180
    GA_MUTATION_RATE: float = 0.06
    GA_CROSSOVER_RATE: float = 0.85
    GA_ELITE_SIZE: int = 6
    GA_RANDOM_SEED: int = 42

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.FRONTEND_ORIGINS.split(",") if origin.strip()]

    def scheduler_config(self) -> dict:
        return {
            "SLOT_MINUTES": self.SLOT_MINUTES,
            "MAX_STUDY_HOURS_PER_DAY": self.MAX_STUDY_HOURS_PER_DAY,
            "MAX_SESSION_HOURS": self.MAX_SESSION_HOURS,
            "GA_POPULATION_SIZE": self.GA_POPULATION_SIZE,
            "GA_GENERATIONS": self.GA_GENERATIONS,
            "GA_MUTATION_RATE": self.GA_MUTATION_RATE,
            "GA_CROSSOVER_RATE": self.GA_CROSSOVER_RATE,
            "GA_ELITE_SIZE": self.GA_ELITE_SIZE,
            "GA_RANDOM_SEED": self.GA_RANDOM_SEED,
        }


settings = Settings()
