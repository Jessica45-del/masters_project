"""
Evaluation module for Multi-agent system consisting of Breakdown, Grounding, Similarity Scoring and Aggregator Agents

"""
from typing import Any

from pydantic_evals.evaluators import Evaluator, EvaluatorContext

class SubstringEvaluator(Evaluator[str, Any]):
    """
    Custom evaluator for breakdown, Grounding, Similarity Scoring and Aggregator Agents responses.

    The evaluator checks if the expected substring is present in the response.
    If the substring is not present, it will assume that the test has past.
    This is only for cases where we want to check the agent does not produce an error.
    """

    def evaluate(self, ctx: EvaluatorContext[str, Any]) -> float:
        """
        Evaluate agent by checking for expected substring present in response.

        Args:
            ctx: The evaluator context. This contains the input, output and substring.

        Returns:
             A score between 0.0 and 1.0, where 0.0 is fail and 1.0 is pass.
        """

        # if no expected output is specific, return 1.0 which mean success
        if ctx.expected_output is None:
            return 1.0

        # check if agent has not generated an output
        if ctx.output is None:
            return 0.0

        output_str = ctx.output.output

        # checks if expected output is a substring of the output
        return float(ctx.expected_output.lower() in ctx.output.output.lower())
