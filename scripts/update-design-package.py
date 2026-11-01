"""Update verified UI assets without recompressing unchanged, independently tested runtimes."""
import copy,datetime,hashlib,json,os,shutil,sys,traceback,zipfile
from pathlib import Path

def sha(path):
    with Path(path).open('rb') as file:return hashlib.file_digest(file,'sha256').hexdigest()

def patch_zip(source_path,target_path,replacements):
    with zipfile.ZipFile(source_path) as source,zipfile.ZipFile(target_path,'w',zipfile.ZIP_DEFLATED,compresslevel=1) as target:
        infos=source.infolist();assert len(infos)==len({x.filename for x in infos})
        assert set(replacements)<=set(source.namelist())
        with Path(source_path).open('rb') as raw:
            for index,info in enumerate(infos):
                if info.filename in replacements:continue
                end=infos[index+1].header_offset if index+1<len(infos) else source.start_dir
                clone=copy.copy(info);clone.header_offset=target.fp.tell();raw.seek(info.header_offset)
                remaining=end-info.header_offset
                while remaining:
                    block=raw.read(min(4*1024**2,remaining))
                    if not block:raise ValueError('Truncated source archive')
                    target.fp.write(block);remaining-=len(block)
                target.filelist.append(clone);target.NameToInfo[clone.filename]=clone
        target.start_dir=target.fp.tell();target._didModify=True;target.comment=source.comment
        for name,file in replacements.items():target.write(file,name)
    with zipfile.ZipFile(target_path) as archive:
        assert len(archive.namelist())==len(infos)
        assert len(set(archive.namelist()))==len(infos)
        assert archive.testzip() is None
        for name,file in replacements.items():assert archive.read(name)==Path(file).read_bytes(),name
        assert not any('/state/' in n or '/logs/' in n or 'cookies.json' in n for n in archive.namelist())

def main():
    root=Path(sys.argv[1]).resolve();release=root/'release';logdir=release/'logs';status=logdir/'package-status.json'
    def phase(name,**extra):
        data={'phase':name,'pid':os.getpid(),'updated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),**extra}
        tmp=status.with_suffix('.tmp');tmp.write_text(json.dumps(data),encoding='utf-8');os.replace(tmp,status)
    try:
        base=release/'OmniDispatch-Desktop-Windows-x64.zip';expected='c33e10354d9fd3aa474a9e5df48e45418540a2a5f4ff028675d4a19e50c0ec85'
        phase('updating_verified_ui');assert sha(base)==expected,'Base differs from independently verified runtime package'
        previous=(logdir/'package-check.log').read_text(encoding='utf-8')
        assert all(x in previous for x in ['"portable_import": true','"portable_community_engine": true','"portable_xhs_browser": true'])
        ui=json.loads((logdir/'design-workspace-check.json').read_text(encoding='utf-8'))
        assert not ui['page_errors'] and ui['draft_preserved'] and ui['channel_drilldown'] and len(ui['design_workspace'])==3
        names=['omnidispatch/static/index.html','omnidispatch/static/app.js','omnidispatch/static/app.css','BUILD-DESKTOP.json','DESIGN.md','THIRD-PARTY.md','HANDOVER.md','HANDOFF.md']
        replacements={'OmniDispatch/'+name:release/name for name in names}
        staged=base.with_name(base.stem+'.ui-update.zip');patch_zip(base,staged,replacements)
        digest=sha(staged);backup=root/'backups'/('OmniDispatch_runtime_verified_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.zip')
        os.replace(base,backup)
        try:os.replace(staged,base)
        except BaseException:os.replace(backup,base);raise
        checksum=base.with_suffix('.sha256');temp=checksum.with_suffix('.tmp');temp.write_text(digest+'  '+base.name+'\n');os.replace(temp,checksum)
        result={'archive':str(base),'bytes':base.stat().st_size,'sha256':digest,'runtime_base_sha256':expected,'unchanged_runtimes_previously_extracted_and_tested':True,'ui_assets_matched_deployed_files':True,'design_workspace_reviewed':True,'state_included':False}
        (logdir/'package-ui-update.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        phase('complete',**result);print(json.dumps(result,ensure_ascii=False))
    except BaseException as error:
        phase('failed',error=type(error).__name__,message=str(error));raise
if __name__=='__main__':main()
