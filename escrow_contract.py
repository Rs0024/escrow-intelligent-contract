# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *


class TaskEscrow(gl.Contract):
    """
    Intelligent Contract that automates task/reward escrow settlement.
    The client deposits a reward for a task; the worker submits evidence
    of completion; an LLM-based Equivalence Principle judges whether the
    evidence satisfies the task description, and the contract releases
    or withholds payment accordingly.
    """

    client: Address
    worker: Address
    task_description: str
    reward_amount: u256
    evidence_url: str
    status: str  # "pending" -> "submitted" -> "released" / "rejected"

    def __init__(self, worker: Address, task_description: str, reward_amount: u256):
        self.client = gl.message.sender_address
        self.worker = worker
        self.task_description = task_description
        self.reward_amount = reward_amount
        self.evidence_url = ""
        self.status = "pending"

    @gl.public.write
    def submit_work(self, evidence_url: str) -> None:
        if gl.message.sender_address != self.worker:
            raise Exception("Only the assigned worker can submit work")
        if self.status != "pending":
            raise Exception("Task already submitted or settled")
        self.evidence_url = evidence_url
        self.status = "submitted"

    @gl.public.write
    def verify_and_settle(self) -> None:
        if self.status != "submitted":
            raise Exception("No submission awaiting verification")

        task_description = self.task_description
        evidence_url = self.evidence_url

        def judge_completion() -> bool:
            page_content = gl.nondet.web.render(evidence_url, mode="text")
            prompt = f"""
            Task description: {task_description}

            Evidence submitted by worker (webpage content):
            {page_content}

            Question: Does this evidence reasonably demonstrate that the
            task was completed as described? Answer strictly "True" or "False".
            """
            result = gl.nondet.exec_prompt(prompt)
            return "true" in result.lower()

        approved = gl.eq_principle.prompt_comparative(
            judge_completion,
            "The validators must agree on whether the evidence satisfies the task description.",
        )

        if approved:
            self.status = "released"
        else:
            self.status = "rejected"

    @gl.public.view
    def get_status(self) -> str:
        return self.status

    @gl.public.view
    def get_details(self) -> dict:
        return {
            "client": str(self.client),
            "worker": str(self.worker),
            "task_description": self.task_description,
            "reward_amount": self.reward_amount,
            "evidence_url": self.evidence_url,
            "status": self.status,
        }
