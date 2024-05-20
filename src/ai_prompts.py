class AIPrompts:

    @staticmethod
    def summarize_day_recap(recap_logs: str) -> list[dict[str, str]]:
        """Summarize the day's recap logs.

        Args:
            recap_logs: List of logs to summarize.

        Returns:
            str: Summarized logs.
        """
        return [{"role": "system",
                 "content": "Generate a short summary in prose form, based on the list of log entries provided. "
                            "This summary should adhere to the following criteria:\n\n- Character Limit: The "
                            "summary must strictly have less than 1000 characters.\n\n- Language Use: The summary "
                            "must be in first person and must use a simple language.\n\n- Always include the exact "
                            "dates, times and names mentioned.\n\n- Content Focus: Concentrate mostly on "
                            "non-routine activities, particularly emphasizing those entries marked with a '!'. "
                            "These are the important events/activities of the day and should be featured "
                            "prominently in the summary.\n\n- Flow and Coherence: The summary should read as a "
                            "coherent narrative, smoothly transitioning from one log to the next to create a full "
                            "picture of the day.\n\n- Start the summary with \"I...\" and without adding an "
                            "introduction sentence.\n\n- Do not exaggerate or sugarcoat the emotions or activities "
                            "described in the logs, keep them closely tight to the original text."
                 },
                {"role": "user",
                 "content": f"Here are the log entries:\n\n{recap_logs}"}]
