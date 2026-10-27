"""Resolve locally installed version slots; no task is allowed to provide executable paths."""
import json
from pathlib import Path

def slot_config(base,root,engine,version):
    slot=(Path(root)/engine/version).resolve();root=Path(root).resolve()
    if not slot.is_relative_to(root):raise ValueError('Version slot escaped root')
    manifest=json.loads((slot/'omni-engine.json').read_text())
    if manifest.get('engine')!=engine or manifest.get('version')!=version or manifest.get('adapter_protocol')!=1:raise ValueError('Invalid installed manifest')
    if manifest.get('adapter',base['adapter'])!=base['adapter']:raise ValueError('Adapter changes require explicit configuration')
    binary=manifest.get('executable')
    if not isinstance(binary,str):raise ValueError('Native executable missing from manifest')
    executable=(slot/binary).resolve()
    if not executable.is_relative_to(slot) or not executable.is_file():raise ValueError('Executable is not inside signed version slot')
    arguments=manifest.get('arguments',[])
    if not isinstance(arguments,list) or not all(isinstance(a,str) for a in arguments):raise ValueError('Invalid signed arguments')
    return {**base,'version':version,'argv':[str(executable),*arguments]}

def runtime_channels(config,path):
    root=Path(config.get('versions_dir',Path(path).parent/'engine-versions'))
    channels={}
    for channel_id,base in config.get('channels',{}).items():
        if '--canary' in channel_id:continue
        engine=base.get('managed_engine');active=base
        if engine:
            pointer=root/engine/'active.json'
            if pointer.exists():
                version=json.loads(pointer.read_text())['version']
                if version!=base.get('version'):active=slot_config(base,root,engine,version)
            pointer=root/engine/'canary.json'
            if pointer.exists():
                version=json.loads(pointer.read_text())['version']
                if version:channels[channel_id+'--canary']=slot_config(base,root,engine,version)
        channels[channel_id]=active
    return channels
