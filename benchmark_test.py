"""Standalone benchmark and smoke-test script for openmayahelper."""

import importlib
import statistics
import sys
import time

from maya import cmds
from maya.api import OpenMaya as om
from maya.api import OpenMayaAnim as oma

try:
    import numpy as np
except ImportError:
    np = None

if 'D:\\' not in sys.path:
    sys.path.insert(0, 'D:\\')


def reload_openmayahelper():
    """Reload openmayahelper modules so repeated Maya console runs pick up changes."""
    module_names = sorted(
        [name for name in sys.modules if name == 'openmayahelper' or name.startswith('openmayahelper.')],
        key=lambda value: value.count('.'),
        reverse=True,
    )
    for module_name in module_names:
        importlib.reload(sys.modules[module_name])

    if 'openmayahelper' not in sys.modules:
        importlib.import_module('openmayahelper')

    return sys.modules['openmayahelper']


openmayahelper = reload_openmayahelper()
my = openmayahelper.my
ops_module = importlib.import_module('openmayahelper.ops')
add_linear_keys = ops_module.add_linear_keys


SCENE_ROOT = 'openmayahelperBenchmark_grp'


def get_depend_node(name):
    """Return an MObject for a Maya node name."""
    selection = om.MSelectionList()
    selection.add(name)
    return selection.getDependNode(0)


def get_plug(plug_name):
    """Return an MPlug for a node attribute name."""
    node_name, attr_name = plug_name.split('.', 1)
    return om.MFnDependencyNode(get_depend_node(node_name)).findPlug(attr_name, True)


def create_connected_anim_curve(plug_name):
    """Create a connected animCurveTL for a destination plug."""
    anim_curve_obj = oma.MFnAnimCurve().create(get_plug(plug_name), oma.MFnAnimCurve.kAnimCurveTL)
    return om.MFnDependencyNode(anim_curve_obj).name()


def reset_scene():
    """Reset the Maya scene to a known state."""
    cmds.file(new=True, force=True)


def build_scene(pair_count=40):
    """Create a repeatable test scene with transforms and utility nodes."""
    if cmds.objExists(SCENE_ROOT):
        cmds.delete(SCENE_ROOT)

    root = cmds.group(empty=True, name=SCENE_ROOT)
    pairs = []
    utilities = []
    key_targets = []
    anim_curves = []

    for index in range(pair_count):
        source = cmds.createNode('transform', name=f'bench_src_{index:03d}', parent=root)
        target = cmds.createNode('transform', name=f'bench_dst_{index:03d}', parent=root)
        utility = cmds.createNode('multiplyDivide', name=f'bench_mul_{index:03d}')
        key_target = cmds.createNode('transform', name=f'bench_key_{index:03d}', parent=root)

        cmds.setAttr(f'{source}.translate', index + 1.0, index + 2.0, index + 3.0, type='double3')
        cmds.setAttr(f'{target}.translate', index + 10.0, index + 20.0, index + 30.0, type='double3')
        cmds.setAttr(f'{utility}.operation', 1)
        cmds.setAttr(f'{utility}.input2X', 1.0)

        key_target_attr = f'{key_target}.translateX'
        anim_curve = create_connected_anim_curve(key_target_attr)
        anim_curves.append(anim_curve)

        pairs.append((source, target))
        utilities.append(utility)
        key_targets.append(key_target_attr)

    return {
        'root': root,
        'pairs': pairs,
        'utilities': utilities,
        'key_targets': key_targets,
        'anim_curves': anim_curves,
    }


def get_sample_times(sample_count=120):
    """Build a deterministic sequence for derivative-style calculations."""
    return [index * 0.5 for index in range(sample_count)]


def get_sample_values(sample_count=120):
    """Build a simple ramp with oscillation for delta calculations."""
    values = []
    for index in range(sample_count):
        values.append((index * 1.25) + ((-1) ** index) * 0.5)
    return values


def reset_values(scene):
    """Restore deterministic translate values before each benchmark."""
    for index, (source, target) in enumerate(scene['pairs']):
        cmds.setAttr(f'{source}.translate', index + 1.0, index + 2.0, index + 3.0, type='double3')
        cmds.setAttr(f'{target}.translate', index + 10.0, index + 20.0, index + 30.0, type='double3')


def clear_connections(scene):
    """Disconnect benchmark utility nodes."""
    for utility in scene['utilities']:
        destination = f'{utility}.input1X'
        source = cmds.connectionInfo(destination, sourceFromDestination=True)
        if source:
            cmds.disconnectAttr(source, destination)


def clear_anim_curves(scene):
    """Remove all keys from benchmark animation curves."""
    for anim_curve in scene['anim_curves']:
        anim_curve_fn = oma.MFnAnimCurve(get_depend_node(anim_curve))
        for index in range(anim_curve_fn.numKeys - 1, -1, -1):
            anim_curve_fn.remove(index)


def cmds_filter_transforms(scene):
    """Find benchmark transforms by type and name pattern with cmds."""
    transforms = cmds.ls(f'{SCENE_ROOT}|bench_*', long=True, type='transform') or []
    return [node for node in transforms if 'bench_src_' in node or 'bench_dst_' in node]


def openmayahelper_filter_transforms(scene):
    """Find benchmark transforms by type and name pattern with openmayahelper."""
    nodes = my.ls(f'{SCENE_ROOT}|bench_*', type='transform')
    return [node for node in nodes if 'bench_src_' in node.name or 'bench_dst_' in node.name]


def calculate_derivatives(values, times):
    """Return first-order finite differences for evenly sampled values."""
    derivatives = []
    for index in range(1, len(values)):
        delta_value = values[index] - values[index - 1]
        delta_time = times[index] - times[index - 1]
        derivatives.append(delta_value / delta_time)
    return derivatives


def get_key_times(sample_count=120):
    """Build times for animation key insertion tests."""
    if np is not None:
        times = np.arange(sample_count, dtype=float)
        return times[(times % 3.0) != 1.0].tolist()
    return [float(index) for index in range(sample_count) if index % 3 != 1]


def get_key_values(sample_count=120):
    """Build values for animation key insertion tests."""
    if np is not None:
        times = np.arange(sample_count, dtype=float)
        values = times * 1.5 + ((times % 4.0) - 1.5) * 0.25
        return values[(times % 3.0) != 1.0].tolist()
    return [
        float(index) * 1.5 + ((index % 4) - 1.5) * 0.25
        for index in range(sample_count)
        if index % 3 != 1
    ]


def benchmark_cmds_attr_swaps(scene, loops=100):
    """Swap transform translations using maya.cmds."""
    reset_values(scene)
    start = time.perf_counter()
    for _ in range(loops):
        for source, target in scene['pairs']:
            source_value = cmds.getAttr(f'{source}.translate')[0]
            target_value = cmds.getAttr(f'{target}.translate')[0]
            cmds.setAttr(f'{source}.translate', *target_value, type='double3')
            cmds.setAttr(f'{target}.translate', *source_value, type='double3')
    return time.perf_counter() - start


def benchmark_openmayahelper_attr_swaps(scene, loops=100):
    """Swap transform translations using openmayahelper wrappers."""
    reset_values(scene)
    pairs = [(my.get(source), my.get(target)) for source, target in scene['pairs']]
    start = time.perf_counter()
    for _ in range(loops):
        for source, target in pairs:
            source_value = tuple(source.translate.get())
            target_value = tuple(target.translate.get())
            source.translate.set(target_value)
            target.translate.set(source_value)
    return time.perf_counter() - start


def benchmark_cmds_filtering(scene, loops=400):
    """Measure scene filtering with cmds and light Python post-filtering."""
    start = time.perf_counter()
    for _ in range(loops):
        nodes = cmds_filter_transforms(scene)
        if len(nodes) != len(scene['pairs']) * 2:
            raise AssertionError('cmds filtering returned an unexpected node count')
    return time.perf_counter() - start


def benchmark_openmayahelper_filtering(scene, loops=400):
    """Measure scene filtering with openmayahelper wrappers and Python post-filtering."""
    start = time.perf_counter()
    for _ in range(loops):
        nodes = openmayahelper_filter_transforms(scene)
        if len(nodes) != len(scene['pairs']) * 2:
            raise AssertionError('openmayahelper filtering returned an unexpected node count')
    return time.perf_counter() - start


def benchmark_cmds_add_keys(scene, loops=30):
    """Measure repeated key insertion with cmds.setKeyframe."""
    key_times = get_key_times()
    key_values = get_key_values()
    clear_anim_curves(scene)
    start = time.perf_counter()
    for _ in range(loops):
        clear_anim_curves(scene)
        for key_target in scene['key_targets']:
            for key_time, key_value in zip(key_times, key_values):
                cmds.setKeyframe(
                    key_target,
                    float=key_time,
                    value=key_value,
                    inTangentType='linear',
                    outTangentType='linear',
                )
    return time.perf_counter() - start


def benchmark_openmayahelper_add_keys(scene, loops=30):
    """Measure repeated bulk key insertion with OpenMayaAnim addKeys."""
    key_times = get_key_times()
    key_values = get_key_values()
    clear_anim_curves(scene)
    start = time.perf_counter()
    for _ in range(loops):
        clear_anim_curves(scene)
        for anim_curve in scene['anim_curves']:
            add_linear_keys(anim_curve, key_times, key_values)
    return time.perf_counter() - start


def benchmark_cmds_connections(scene, loops=80):
    """Connect and disconnect attributes with maya.cmds."""
    clear_connections(scene)
    start = time.perf_counter()
    for _ in range(loops):
        for index, (source, _) in enumerate(scene['pairs']):
            utility = scene['utilities'][index]
            src = f'{source}.translateX'
            dst = f'{utility}.input1X'
            cmds.connectAttr(src, dst, force=True)
            cmds.disconnectAttr(src, dst)
    return time.perf_counter() - start


def benchmark_openmayahelper_connections(scene, loops=80):
    """Connect and disconnect attributes with openmayahelper wrappers."""
    clear_connections(scene)
    pairs = [
        (my.get(source).translateX, my.get(scene['utilities'][index]).input1X)
        for index, (source, _) in enumerate(scene['pairs'])
    ]
    start = time.perf_counter()
    for _ in range(loops):
        for source_attr, destination_attr in pairs:
            source_attr.connect(destination_attr)
            source_attr.disconnect(destination_attr)
    return time.perf_counter() - start


def benchmark_openmayahelper_batch(scene, loops=80):
    """Queue sets and connection edits through my.batch()."""
    reset_values(scene)
    clear_connections(scene)
    start = time.perf_counter()
    for loop_index in range(loops):
        with my.batch() as batch:
            for index, (source, target) in enumerate(scene['pairs']):
                offset = float(loop_index + index)
                batch.set(f'{source}.translateX', offset)
                batch.set(f'{target}.translateY', offset + 1.0)

                src = f'{source}.translateX'
                dst = f"{scene['utilities'][index]}.input1X"
                batch.connect(src, dst)
                batch.disconnect(src, dst)
    return time.perf_counter() - start


def benchmark_cmds_derivatives(scene, loops=400):
    """Measure pure-Python finite differences driven from cmds-read samples."""
    source = scene['pairs'][0][0]
    times = get_sample_times()
    for index, value in enumerate(get_sample_values()):
        cmds.setAttr(f'{source}.translateX', value + index)

    start = time.perf_counter()
    for _ in range(loops):
        values = []
        base = cmds.getAttr(f'{source}.translateX')
        for index, sample_time in enumerate(times):
            values.append(base + sample_time + index * 0.01)
        derivatives = calculate_derivatives(values, times)
        if len(derivatives) != len(times) - 1:
            raise AssertionError('cmds derivative calculation returned an unexpected sample count')
    return time.perf_counter() - start


def benchmark_openmayahelper_derivatives(scene, loops=400):
    """Measure pure-Python finite differences driven from openmayahelper-read samples."""
    source = my.get(scene['pairs'][0][0])
    times = get_sample_times()

    start = time.perf_counter()
    for _ in range(loops):
        base = source.translateX.get()
        values = [base + sample_time + index * 0.01 for index, sample_time in enumerate(times)]
        derivatives = calculate_derivatives(values, times)
        if len(derivatives) != len(times) - 1:
            raise AssertionError('openmayahelper derivative calculation returned an unexpected sample count')
    return time.perf_counter() - start


def benchmark_cmds_mixed(scene, loops=80):
    """Immediate cmds equivalent of the mixed openmayahelper batch workload."""
    reset_values(scene)
    clear_connections(scene)
    start = time.perf_counter()
    for loop_index in range(loops):
        for index, (source, target) in enumerate(scene['pairs']):
            offset = float(loop_index + index)
            cmds.setAttr(f'{source}.translateX', offset)
            cmds.setAttr(f'{target}.translateY', offset + 1.0)

            src = f'{source}.translateX'
            dst = f"{scene['utilities'][index]}.input1X"
            cmds.connectAttr(src, dst, force=True)
            cmds.disconnectAttr(src, dst)
    return time.perf_counter() - start


def run_case(label, callback, repeats=3):
    """Run one benchmark callback several times and report the median."""
    samples = []
    for _ in range(repeats):
        duration = callback()
        if duration is None:
            return None
        samples.append(duration)

    return {
        'label': label,
        'samples': samples,
        'median': statistics.median(samples),
        'minimum': min(samples),
        'maximum': max(samples),
    }


def print_report(title, results):
    """Print a readable timing table."""
    print('\n' + title)
    print('-' * len(title))
    for result in results:
        if result is None:
            continue
        print(
            f"{result['label']:<16} "
            f"median={result['median']:.6f}s "
            f"min={result['minimum']:.6f}s "
            f"max={result['maximum']:.6f}s"
        )


def compare_to_baseline(results, baseline_label):
    """Print slowdown ratios against a chosen baseline."""
    baseline = next((result for result in results if result and result['label'] == baseline_label), None)
    if not baseline:
        return

    print(f'\nRelative to {baseline_label}:')
    for result in results:
        if result is None:
            continue
        ratio = result['median'] / baseline['median'] if baseline['median'] else 0.0
        print(f"  {result['label']:<16} {ratio:>7.2f}x")


def main(pair_count=40, swap_loops=100, connection_loops=80, repeats=3):
    """Build the scene and run all benchmark groups."""
    reset_scene()
    scene = build_scene(pair_count=pair_count)

    print('openmayahelper benchmark scene ready')
    print(f'pair count: {pair_count}')
    print(f'NumPy available: {np is not None}')

    # This section measures direct attribute read/write overhead while swapping
    # translation values between paired transforms.
    swap_results = [
        run_case('cmds', lambda: benchmark_cmds_attr_swaps(scene, loops=swap_loops), repeats=repeats),
        run_case('openmayahelper', lambda: benchmark_openmayahelper_attr_swaps(scene, loops=swap_loops), repeats=repeats),
    ]
    print_report('Attribute Swap Benchmark', swap_results)
    compare_to_baseline(swap_results, 'cmds')

    # This section measures repeated connect/disconnect churn on utility nodes.
    connection_results = [
        run_case('cmds', lambda: benchmark_cmds_connections(scene, loops=connection_loops), repeats=repeats),
        run_case('openmayahelper', lambda: benchmark_openmayahelper_connections(scene, loops=connection_loops), repeats=repeats),
    ]
    print_report('Connection Churn Benchmark', connection_results)
    compare_to_baseline(connection_results, 'cmds')

    # This section compares immediate edits against a batched MDGModifier flow.
    mixed_results = [
        run_case('cmds', lambda: benchmark_cmds_mixed(scene, loops=connection_loops), repeats=repeats),
        run_case('openmayahelper batch', lambda: benchmark_openmayahelper_batch(scene, loops=connection_loops), repeats=repeats),
    ]
    print_report('Mixed Batch Benchmark', mixed_results)
    compare_to_baseline(mixed_results, 'cmds')

    # This section measures list-and-filter overhead for benchmark transforms.
    filtering_results = [
        run_case('cmds', lambda: benchmark_cmds_filtering(scene), repeats=repeats),
        run_case('openmayahelper', lambda: benchmark_openmayahelper_filtering(scene), repeats=repeats),
    ]
    print_report('Filtering Benchmark', filtering_results)
    compare_to_baseline(filtering_results, 'cmds')

    # This section measures a simple first derivative calculation after reading
    # an initial driver value through each library.
    derivative_results = [
        run_case('cmds', lambda: benchmark_cmds_derivatives(scene), repeats=repeats),
        run_case('openmayahelper', lambda: benchmark_openmayahelper_derivatives(scene), repeats=repeats),
    ]
    print_report('Derivative Calculation Benchmark', derivative_results)
    compare_to_baseline(derivative_results, 'cmds')

    # This section pre-filters times and values with NumPy when available, then
    # measures bulk key insertion. The openmayahelper path uses one addKeys call per
    # curve instead of one command per key.
    animation_results = [
        run_case('cmds', lambda: benchmark_cmds_add_keys(scene), repeats=repeats),
        run_case('openmayahelper', lambda: benchmark_openmayahelper_add_keys(scene), repeats=repeats),
    ]
    print_report('Animation Key Benchmark', animation_results)
    compare_to_baseline(animation_results, 'cmds')

    print('\nExample smoke test:')
    example_node = my.get(scene['pairs'][0][0])
    print(f'  selected node wrapper type: {type(example_node).__name__}')
    print(f"  read translate: {tuple(example_node.translate.get())}")
    print(f"  destination count on translateX: {len(example_node.translateX.destinations())}")


if __name__ == '__main__':
    main()
