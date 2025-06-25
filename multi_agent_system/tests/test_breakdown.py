from multi_agent_system.agents.breakdown.breakdown_config import get_config

def test_get_config():
    cfg = get_config()
    assert hasattr(cfg, 'template_dir')
    assert hasattr(cfg, 'template_file')
    print(cfg.template_dir, cfg.template_file)

# PASSED - returns /home/jessica/masters_project/src/multi_agent_system/prompts
# PASSED returns diagnosis_prompt.jinja2

from jinja2 import Environment, FileSystemLoader

def test_template_loading():
    cfg = get_config()
    env = Environment(loader=FileSystemLoader(str(cfg.template_dir)))
    template = env.get_template(cfg.template_file)
    assert template is not None
    print(template.render(hpo_terms="HP:0003150, HP:0004322", sex="female"))
# PASSED = inserts hpo_id and sex into prompt as expcted

if __name__ == "__main__":
    test_get_config()
    test_template_loading()