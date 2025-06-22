
"""
Evaluation of Breakdown Agent using pydantic-evals framework
"""


from pydantic_evals import Case, Dataset
from multi_agent_system.evaluators.substring_eval import SubstringEvaluator
from multi_agent_system.evaluators.metadata import MetadataDict, metadata



# Define test cases

case1 = Case(
    name='glutaric_acidemia_type_1',
    inputs="""The patient presents with phenotypes: HP:0000256, HP:0002059, HP:0100309, HP:0003150, HP:0001332.
    The patient is female. What is the diagnosis?""",
    expected_output='Glutaric aciduria type 1', # glutaric acidemia type 1
    metadata=metadata("medium", "breakdown")
)


case2 = Case(
    name="bardet-biedl syndrome 1 (BSS1)",
    inputs=(
        "A 26-year-old male presents with: attenuation of retinal blood vessels (HP:0007843), "
        "obesity (HP:0001513), macular degeneration (HP:0000608), strabismus (HP:0000486), "
        "specific learning disability (HP:0001328), rod-cone dystrophy (HP:0000510), "
        "and global developmental delay (HP:0001263). "
        "Return the a list of 1-3 candidate diseases."
    ),
    expected_output="Bardet", # should be in the list
    metadata=metadata("hard", "breakdown")
)


def create_eval_dataset() -> Dataset[str, str, MetadataDict]:
    """
    Create dataset for Breakdown Agent evaluation.

    Returns:
        Dataset for evaluation.
    """
    cases = [case1, case2]
    evaluators = [SubstringEvaluator()]
    return Dataset(cases=cases, evaluators=evaluators)
