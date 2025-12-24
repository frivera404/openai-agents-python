class WorkerBase:
    role = "base"

    def run(self, step: dict, task_payload: dict) -> dict:
        raise NotImplementedError
