from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
import os

from cua.tools import (
    MultimediaAssistantTool,
    ImageCreatorTool,
    NotionTool,
    CodeCompilerTool,
    OctaveOnlineTool,
    search_tool,
    LabReportGeneratorTool,
    WolframAlphaTool,
    DataVizTool,
    CitationFinderTool,
    SmartPDFParserTool,
    GrammarCheckerTool,
    LatexRendererTool,
    PlagiarismCheckerTool,
)


@CrewBase
class Cua:
    """Academix University Automation System crew."""

    agents: List[BaseAgent]
    tasks: List[Task]

    agents_config = os.path.join(os.path.dirname(__file__), "config/agents.yaml")
    tasks_config  = os.path.join(os.path.dirname(__file__), "config/tasks.yaml")

    # ── Agents ────────────────────────────────────────────────────────────────

    @agent
    def YouTubeMediaAssistant(self) -> Agent:
        return Agent(
            config=self.agents_config["YouTubeMediaAssistant"],  # type: ignore[index]
            tools=[MultimediaAssistantTool()],
            verbose=True,
        )

    @agent
    def Elite_Academic_Document_Architect(self) -> Agent:
        return Agent(
            config=self.agents_config["Elite_Academic_Document_Architect"],  # type: ignore[index]
            tools=[
                ImageCreatorTool(), NotionTool(), WolframAlphaTool(),
                CitationFinderTool(), GrammarCheckerTool(),
                LatexRendererTool(), PlagiarismCheckerTool(), search_tool,
            ],
            verbose=True,
        )

    @agent
    def PlannerAgent(self) -> Agent:
        return Agent(
            config=self.agents_config["PlannerAgent"],  # type: ignore[index]
            tools=[search_tool],
            verbose=True,
        )

    @agent
    def CoderAgent(self) -> Agent:
        return Agent(
            config=self.agents_config["CoderAgent"],  # type: ignore[index]
            tools=[CodeCompilerTool(), DataVizTool(), search_tool],
            verbose=True,
        )

    @agent
    def NumericalMethodsAgent(self) -> Agent:
        return Agent(
            config=self.agents_config["NumericalMethodsAgent"],  # type: ignore[index]
            tools=[OctaveOnlineTool(), NotionTool(), WolframAlphaTool(), search_tool],
            verbose=True,
        )

    @agent
    def LabReportGeneratorAgent(self) -> Agent:
        return Agent(
            config=self.agents_config["LabReportGeneratorAgent"],  # type: ignore[index]
            tools=[
                LabReportGeneratorTool(),
                SmartPDFParserTool(),
                OctaveOnlineTool(),
                ImageCreatorTool(),
                NotionTool(),
                WolframAlphaTool(),
                DataVizTool(),
                CitationFinderTool(),
                LatexRendererTool(),
                search_tool,
            ],
            verbose=True,
        )

    # ── Tasks ─────────────────────────────────────────────────────────────────

    @task
    def planner_agent_task(self) -> Task:
        return Task(config=self.tasks_config["planner_agent_task"])  # type: ignore[index]

    @task
    def routing_decision_task(self) -> Task:
        return Task(
            config=self.tasks_config["routing_decision_task"],  # type: ignore[index]
            context=[self.planner_agent_task()],
        )

    @task
    def video_download_task(self) -> Task:
        return Task(
            config=self.tasks_config["video_download_task"],  # type: ignore[index]
            context=[self.routing_decision_task()],
        )

    @task
    def code_execution_task(self) -> Task:
        return Task(
            config=self.tasks_config["code_execution_task"],  # type: ignore[index]
            context=[self.routing_decision_task()],
        )

    @task
    def numerical_methods_task(self) -> Task:
        return Task(
            config=self.tasks_config["numerical_methods_task"],  # type: ignore[index]
            context=[self.routing_decision_task()],
        )

    @task
    def lab_report_generation_task(self) -> Task:
        return Task(
            config=self.tasks_config["lab_report_generation_task"],  # type: ignore[index]
            context=[self.routing_decision_task()],
        )

    @task
    def notes_creation_task(self, output_file: str = "study_notes.md") -> Task:
        return Task(
            config=self.tasks_config["notes_creation_task"],  # type: ignore[index]
            context=[
                self.routing_decision_task(),
                self.video_download_task(),
                self.code_execution_task(),
                self.numerical_methods_task(),
                self.lab_report_generation_task(),
            ],
            output_file=output_file,
        )

    # ── Crew ──────────────────────────────────────────────────────────────────

    @crew
    def crew(self, inputs: dict | None = None, callbacks: list | None = None) -> Crew:
        youtube_output_mode = (inputs or {}).get("youtube_output_mode", "summary")
        output_file = "transcript.md" if youtube_output_mode == "transcript" else "study_notes.md"

        return Crew(
            agents=self.agents,
            tasks=[
                self.planner_agent_task(),
                self.routing_decision_task(),
                self.video_download_task(),
                self.code_execution_task(),
                self.numerical_methods_task(),
                self.lab_report_generation_task(),
                self.notes_creation_task(output_file=output_file),
            ],
            process=Process.sequential,
            verbose=True,
            callbacks=callbacks or [],
        )
