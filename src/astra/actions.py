"""Jev selects an allowlisted investigation; the host executes it with Astra."""
from pathlib import Path
from pydantic import BaseModel, ConfigDict
from astra.jev import CONFIDENCE_FLOOR, answers_from, parse_choice
from astra.models import Assessment
from astra.prompts import judge_prompt

ACTIONS = {
    'check_math': 'Independently calculate the disputed formulas, domains, critical values or topology. Report actual tool results and specific corrections.',
    'clarify_definitions': 'Trace first use of every term against its definition. Recommend exact wording and shot ordering for the identified gaps.',
    'inspect_scene': 'Inspect Manim source and installed APIs for the identified implementation defect. Recommend exact source locations and changes; do not edit or render.',
    'inspect_frames': 'Inspect supplied actual frames for the identified uncertainty. Cite frame filenames and exact visible geometry or notation problems.',
    'replan_camera': 'Inspect shot layout and available frames. Recommend concrete camera targets, zoom values, label positions, colors and holds supported by evidence.',
    'no_action': 'No further investigation is warranted by this evidence.',
}
# Investigations available at each checkpoint, in the order offered to Jev.
STAGE_ACTIONS = {
    'brief': ['clarify_definitions','no_action'],
    'mathematics': ['check_math','clarify_definitions','no_action'],
    'storyboard': ['clarify_definitions','check_math','replan_camera','no_action'],
    'scene': ['inspect_scene','check_math','clarify_definitions','replan_camera','no_action'],
    'render': ['inspect_frames','inspect_scene','check_math','clarify_definitions','replan_camera','no_action'],
}
# Investigations whose Astra session gets live web search (primary references).
SEARCHING_ACTIONS = frozenset({'check_math'})

class ActionDecision(BaseModel):
    model_config = ConfigDict(extra='forbid')
    action: str
    confidence: float
    execute: bool
    model: str
    probabilities: dict[str,float]


def action_question(stage):
    return {'next_action':{'type':'choice',
        'instructions':'Which ONE available investigation would most directly resolve the specific uncertainty or defect in this state? Choose no_action if evidence supports proceeding without further investigation. You select an action; the host executes it.',
        'criteria':{k:ACTIONS[k] for k in STAGE_ACTIONS[stage]}}}


def parse_action(raw, stage):
    answers=answers_from(raw,action_question(stage))
    choice,confidence,probabilities=parse_choice(answers['next_action'],STAGE_ACTIONS[stage])
    return ActionDecision(action=choice,confidence=confidence,
        execute=confidence>=CONFIDENCE_FLOOR and choice!='no_action',model=raw['model'],probabilities=probabilities)


def select_action(jev, state, stage, output):
    output=Path(output)
    raw=jev.ask(state=state,questions=action_question(stage),output=output)
    decision=parse_action(raw,stage)
    output.write_text(decision.model_dump_json(indent=2),encoding='utf-8')
    return decision


def execute_action(client, decision, *, stage, request, folder, paths, images, output):
    if not decision.execute:return None
    if decision.action not in STAGE_ACTIONS[stage]:raise ValueError('Action unavailable at checkpoint')
    if decision.action=='inspect_frames' and not images:raise ValueError('Frame inspection requires actual images')
    names=[Path(p).relative_to(folder).as_posix() for p in paths]
    prompt=judge_prompt(stage,request,'\n'.join(names),names)
    prompt+='\nJev selected this investigation: '+decision.action+'\n'+ACTIONS[decision.action]
    prompt+='\nReturn concrete recommendations in feedback, supported by exact evidence. Do not claim Jev authored your prose.'
    report=client.call(prompt,cwd=folder,output=output,schema=Assessment,images=images,
                       effort=request.effort,search=decision.action in SEARCHING_ACTIONS,evidence_paths=names)
    if not set(report.evidence).issubset(names):raise ValueError('Action cited unavailable evidence')
    if decision.action=='inspect_frames' and not set(report.evidence).intersection(
            Path(p).relative_to(folder).as_posix() for p in images):
        raise ValueError('Frame investigation must cite an actual frame')
    Path(output).write_text(report.model_dump_json(indent=2),encoding='utf-8')
    return report
