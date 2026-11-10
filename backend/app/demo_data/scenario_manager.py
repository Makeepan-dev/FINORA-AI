from typing import List, Optional
from .scenarios.catalogue import get_predefined_scenarios, TestScenario

class ScenarioManager:
    def __init__(self):
        self._scenarios = {s.scenario_id: s for s in get_predefined_scenarios()}
        self._active_scenario: Optional[TestScenario] = self._scenarios.get("scen_01_normal_spending")

    def list_all(self) -> List[TestScenario]:
        return list(self._scenarios.values())

    def get_by_id(self, scenario_id: str) -> Optional[TestScenario]:
        return self._scenarios.get(scenario_id)

    def activate(self, scenario_id: str) -> Optional[TestScenario]:
        if scenario_id in self._scenarios:
            self._active_scenario = self._scenarios[scenario_id]
            return self._active_scenario
        return None

    @property
    def active_scenario(self) -> Optional[TestScenario]:
        return self._active_scenario

global_scenario_manager = ScenarioManager()
