import pytest
from multi_agent_system.agents.breakdown.breakdown_tools import prepare_prompt
from multi_agent_system.agents.breakdown.breakdown_tools import extract_json_block
from unittest.mock import patch, MagicMock

@pytest.mark.asyncio
async def test_prepare_prompt_real_template():
    hpo_ids = ["HP:0004322", "HP:0001250"]
    sex = "female"
    result = await prepare_prompt(hpo_ids, sex)
    assert "HP:0004322, HP:0001250" in result
    assert "Sex: female" in result
    # Test for some key words that should be present from the template
    assert "candidate diseases" in result
    assert "Phenotype label" in result
    assert result.strip().startswith("The patient presents")


@pytest.mark.asyncio
async def test_extract_json_block_valid():
    text = """```json
    [
      {"foo": "bar"},
      {"baz": 123}
    ]
    ```"""
    result = await extract_json_block(text)
    assert isinstance(result, list)
    assert result == [{"foo": "bar"}, {"baz": 123}]

@pytest.mark.asyncio
async def test_extract_json_block_invalid_json():
    text = """```json
    not a valid json
    ```"""
    result = await extract_json_block(text)
    assert isinstance(result, list)
    assert result[0].get("error") == "Could not parse JSON"
    assert "not a valid json" in result[1].get("raw", "")

@pytest.mark.asyncio
async def test_extract_json_block_no_json_block():
    text = "This response contains no json block."
    result = await extract_json_block(text)
    assert isinstance(result, list)
    assert result[0].get("error") == "Could not parse JSON"
    assert "no json block" in result[1].get("raw", "")



@pytest.mark.asyncio
async def test_prepare_prompt_mocked():
    mock_template = MagicMock()
    mock_template.render.return_value = "Mocked template with HP:0001250 and female"

    with patch("your_module._template", mock_template):  # Replace your_module
        from multi_agent_system.agents.breakdown.breakdown_tools import prepare_prompt
        result = await prepare_prompt(["HP:0001250"], "female")
        assert "HP:0001250" in result
        assert "female" in result