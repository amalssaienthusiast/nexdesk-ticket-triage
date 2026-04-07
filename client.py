"""
NexDesk Client
EnvClient subclass for the NexDesk IT Ticket Triage environment.
Provides typed interface for interacting with the NexDesk server.
"""

from typing import Optional

import requests

try:
    # When installed as package
    from .models import (
        NexDeskAction,
        NexDeskObservation,
        NexDeskState,
        NexDeskInfo,
        StepResult,
        ResetResult,
    )
except ImportError:
    # When run directly
    from models import (
        NexDeskAction,
        NexDeskObservation,
        NexDeskState,
        NexDeskInfo,
        StepResult,
        ResetResult,
    )


class NexDeskClient:
    """
    Client for interacting with the NexDesk OpenEnv environment.

    Usage:
        client = NexDeskClient("https://your-hf-space.hf.space")
        result = client.reset(task="ticket_classify")
        step_result = client.step(NexDeskAction(
            session_id=result.session_id,
            priority="high",
            category="network"
        ))
    """

    def __init__(self, base_url: str, timeout: int = 30):
        """
        Initialize the NexDesk client.

        Args:
            base_url: Base URL of the NexDesk server (e.g., "http://localhost:7860")
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session_id: Optional[str] = None

    def health(self) -> dict:
        """Check server health status."""
        response = requests.get(f"{self.base_url}/health", timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def reset(self, task: str = "ticket_classify") -> ResetResult:
        """
        Reset the environment and start a new episode.

        Args:
            task: Task to run. One of:
                - "ticket_classify" (easy, 1 step)
                - "ticket_route" (medium, 2 steps)
                - "ticket_resolve" (hard, 3 steps)
                - "crisis_surge" (hard, 10 steps) - batch ticket handling

        Returns:
            ResetResult with observation and session_id
        """
        response = requests.post(
            f"{self.base_url}/reset", json={"task": task}, timeout=self.timeout
        )
        response.raise_for_status()
        data = response.json()

        self._session_id = data["session_id"]

        return ResetResult(
            observation=NexDeskObservation(**data["observation"]),
            session_id=data["session_id"],
        )

    def step(self, action: NexDeskAction) -> StepResult:
        """
        Take a step in the environment.

        Args:
            action: Action to take (must include session_id)

        Returns:
            StepResult with observation, reward, done flag, and info
        """
        payload = action.model_dump(exclude_none=True)

        response = requests.post(f"{self.base_url}/step", json=payload, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()

        return StepResult(
            observation=NexDeskObservation(**data["observation"]),
            reward=data["reward"],
            done=data["done"],
            info=NexDeskInfo(**data.get("info", {"step": 0, "total_reward": 0.0, "task": ""})),
        )

    def state(self, session_id: Optional[str] = None) -> NexDeskState:
        """
        Get current state of an episode.

        Args:
            session_id: Session to query. Uses last session if not provided.

        Returns:
            NexDeskState with current episode state
        """
        sid = session_id or self._session_id
        if not sid:
            raise ValueError("No session_id available. Call reset() first.")

        response = requests.get(
            f"{self.base_url}/state", params={"session_id": sid}, timeout=self.timeout
        )
        response.raise_for_status()
        data = response.json()

        return NexDeskState(**data)

    def list_tasks(self) -> dict:
        """Get list of available tasks."""
        response = requests.get(f"{self.base_url}/tasks", timeout=self.timeout)
        response.raise_for_status()
        return response.json()


# Convenience function for one-off usage
def create_client(base_url: str = "http://localhost:7860") -> NexDeskClient:
    """Create a NexDesk client with default settings."""
    return NexDeskClient(base_url)


if __name__ == "__main__":
    # Example usage
    client = NexDeskClient("http://localhost:7860")

    # Check health
    print("Health:", client.health())

    # List tasks
    print("Tasks:", client.list_tasks())

    # Run a simple classification
    result = client.reset(task="ticket_classify")
    print(f"\nTicket: {result.observation.subject}")
    print(f"Description: {result.observation.description[:100]}...")

    # Take action
    step_result = client.step(
        NexDeskAction(
            session_id=result.session_id,
            priority="high",
            category="network",
            confidence=0.85,
        )
    )

    print(f"\nReward: {step_result.reward}")
    print(f"Done: {step_result.done}")
    print(f"Message: {step_result.observation.message}")
