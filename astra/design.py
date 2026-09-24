"""Verbose, inspectable design decisions for Jev; evidence-scoped artistic advice."""
import json
from pathlib import Path
from astra.jev import JEV_MODEL, _unit

# Each rubric asks one question. Artistic advice never overrides correctness gates.
RUBRICS = [
 dict(id='dramatic_question',domain='art',stages=['brief','storyboard','render'],action='clarify_definitions',question='Does the opening establish a specific visual question whose answer the film reveals?',evidence='Opening shot plan or timestamped observations',repair='Replace a generic title-first opening with a visible puzzle; preserve a short orientation beat.',verify='A viewer can state the question after the opening.'),
 dict(id='geometric_reveal',domain='art',stages=['storyboard','scene','render'],action='replan_camera',question='Does a geometric transformation reveal the central mathematical relationship rather than merely decorate narration?',evidence='Transformation specification, source, or before/after frame observations',repair='Stage the actual mathematical transformation before its symbolic conclusion.',verify='The relevant relation is visibly identifiable before the summary formula.'),
 dict(id='visual_hierarchy',domain='clarity',stages=['storyboard','scene','render'],action='replan_camera',question='Is one primary mathematical object or event visually dominant in each shot?',evidence='Shot composition or per-frame descriptions',repair='Dim scaffolding, remove competing labels, and isolate the object that carries the argument.',verify='The focal object remains distinguishable at delivery resolution.'),
 dict(id='definition_order',domain='clarity',stages=['brief','mathematics','storyboard','render'],action='clarify_definitions',question='Are prerequisite terms and symbols introduced before their first consequential use?',evidence='First-use timeline and captions',repair='Move or add a concise definition immediately before first use.',verify='Every new symbol has an earlier or simultaneous explicit meaning.'),
 dict(id='reading_time',domain='clarity',stages=['storyboard','scene','render'],action='inspect_scene',question='Does each new formula have a stable reading interval without competing camera or topology changes?',evidence='Timed storyboard and source schedule; isolated stills cannot verify duration',repair='Separate reveal, explanation, and motion; add a hold sized to formula complexity.',verify='Source and sampled timestamps support a readable interval; flag unobserved motion.'),
 dict(id='latex_hierarchy',domain='latex',stages=['storyboard','scene','render'],action='replan_camera',question='Is the principal equation clearly distinguished from definitions and secondary annotations?',evidence='Exact MathTex strings, font sizes, overlay bounds, actual frame observations',repair='Keep one principal formula, subordinate captions, and clear screen-space bands.',verify='Main equation remains readable without competing text.'),
 dict(id='latex_integrity',domain='latex',stages=['mathematics','storyboard','scene','render'],action='check_math',question='Do visible LaTeX expressions preserve grouping, domains, signs, indices and mathematical meaning?',evidence='Approved equations versus exact source strings and rendered observations',repair='Correct the exact expression; color whole semantic terms without splitting radicands or indices.',verify='Source and rendered expression agree with the mathematical dossier.'),
 dict(id='symbol_geometry_binding',domain='latex',stages=['storyboard','scene','render'],action='clarify_definitions',question='Can each important symbol be connected unambiguously to the geometric object it describes?',evidence='Symbol legend, object colors and shot transitions',repair='Highlight the corresponding object as its symbol appears; maintain consistent colors.',verify='Symbol-to-object associations remain consistent across shots.'),
 dict(id='camera_purpose',domain='camera',stages=['storyboard','scene','render'],action='replan_camera',question='Does each camera move reveal depth, an invariant, a hidden relationship or a local event?',evidence='Camera targets and per-shot teaching purpose',repair='Replace arbitrary orbiting with a move that exposes the mathematical relation.',verify='Each movement has a named explanatory purpose.'),
 dict(id='local_global_bridge',domain='camera',stages=['storyboard','scene','render'],action='replan_camera',question='Does the sequence restore global orientation after a local close-up?',evidence='Wide/detail/return sequence and camera centers',repair='Establish the whole object, push into the critical region, then pull back to reconnect the result.',verify='Local events remain locatable on the full object.'),
 dict(id='camera_clearance',domain='camera',stages=['scene','render'],action='inspect_frames',question='Do the inspected views keep the critical geometry visible and clear of fixed overlays?',evidence='Projected bounds or actual frame observations; source intent alone is insufficient',repair='Change target, zoom or angle; relocate labels into reserved screen space.',verify='Re-render the affected views and inspect their actual bounds.'),
 dict(id='spatial_depth',domain='space',stages=['storyboard','scene','render'],action='replan_camera',question='Do occlusion, mesh, lighting and perspective make the relevant three-dimensional structure legible?',evidence='Surface/material plan, source and frame observations',repair='Use restrained mesh, directional shading, depth-aware opacity and a revealing oblique view.',verify='Near/far surfaces and the relevant opening can be distinguished.'),
 dict(id='surface_volume_boundary',domain='space',stages=['mathematics','storyboard','scene','render'],action='check_math',question='Does the explanation distinguish surfaces, enclosed volumes and boundary curves wherever their distinction matters?',evidence='Definitions, geometric construction, captions and frame observations',repair='Render and label the correct dimensional object; remove misleading filled-volume metaphors.',verify='The displayed object has the intended dimension and boundary.'),
 dict(id='topology_transition',domain='space',stages=['mathematics','storyboard','scene','render'],action='check_math',question='Are claimed topology changes supported by the actual construction and shown only at the appropriate critical events?',evidence='Critical values, connectivity checks, source and observations on both sides of events',repair='Correct connectivity or clipping; distinguish regular states from singular crossings.',verify='Pre-event and post-event states match the verified topology.'),
 dict(id='color_semantics',domain='art',stages=['storyboard','scene','render'],action='replan_camera',question='Do colors encode stable mathematical roles rather than change meaning between shots?',evidence='Color-role map and observed usage',repair='Assign consistent colors to included sets, boundaries, extrema and saddles; reinforce with shape or labels.',verify='Color-role assignments stay consistent in all inspected shots.'),
 dict(id='earned_finale',domain='art',stages=['storyboard','scene','render'],action='replan_camera',question='Does the final tableau visibly account for the terms of the concluding equation?',evidence='Final objects, formula and preceding argument',repair='Bring the relevant objects into one clean composition and reveal the relation term by term.',verify='Every important term has a visible or explicitly recalled geometric meaning.'),
]

LEVELS=['Absent or contradicted by supplied evidence','Major design failure supported by evidence',
        'Partly effective with a specific unresolved weakness','Effective with minor limitations',
        'Exceptionally clear and purposeful, supported by concrete evidence']


def mapping(stage=None):
    result=[dict(r) for r in RUBRICS if stage is None or stage in r['stages']]
    for r in result:
        if stage=='storyboard' and r['action']=='inspect_scene':r['action']='replan_camera'
        if stage=='scene' and r['action']=='inspect_frames':r['action']='inspect_scene'
    return result


def questions(stage):
    return {r['id']:{'type':'score','instructions':{'question':r['question'],
        'required_evidence':r['evidence'],'scope':'Evaluate only this checkpoint. At planning stages assess the plan, not nonexistent pixels. At render, Jev sees Astra text observations only. Do not infer unobserved motion.'},
        'criteria':LEVELS} for r in mapping(stage)}


def interpret(raw,stage):
    if raw.get('model')!=JEV_MODEL or set(raw.get('answers',{}))!=set(questions(stage)):
        raise ValueError('Invalid design response')
    findings=[]
    for r in mapping(stage):
        a=raw['answers'][r['id']]
        if a.get('type')!='score':raise ValueError('Expected design Score')
        score=a['score'];confidence=_unit(a['confidence'])
        if isinstance(score,bool) or not isinstance(score,(int,float)) or not 0<=score<=4:
            raise ValueError('Invalid design score')
        probabilities=a['probabilities']
        if set(probabilities)!={'0','1','2','3','4'}:raise ValueError('Invalid design distribution')
        values=[_unit(probabilities[str(i)]) for i in range(5)]
        if abs(sum(values)-1)>.02 or abs(sum(i*p for i,p in enumerate(values))-score)>.06:
            raise ValueError('Invalid design expected score')
        status='investigate' if confidence<.65 else ('improve' if score<3.2 else 'supported')
        # These are provisional design signals, never permission to weaken correctness.
        findings.append(dict(r,score=score,confidence=confidence,status=status))
    return {'model':raw['model'],'policy':'design-advice-v1','advisory_only':True,
            'findings':findings,'priority':[f['id'] for f in sorted(findings,key=lambda f:f['score']) if f['status']=='improve'],
            'note':'Low confidence requests evidence, not speculative visual changes. Scores are not calibrated quality measures.'}


def review_design(jev,state,stage,output):
    output=Path(output)
    if len(json.dumps(state,ensure_ascii=False).encode('utf-8'))>90000:
        raise ValueError('Jev design state exceeds local evidence budget')
    q=questions(stage)
    output.with_suffix('.request.json').write_text(json.dumps({'model':JEV_MODEL,'state':state,'questions':q},indent=2),encoding='utf-8')
    raw=jev.ask(state=state,questions=q,output=output)
    result=interpret(raw,stage)
    output.write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result
