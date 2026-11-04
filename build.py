#!/usr/bin/env python3
"""Build and sign the IONIQ 5 CarPlay Mute Pause USB package."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile


def execute(*argv):
    subprocess.run([str(x) for x in argv],check=True)


def java_sources(root):
    return sorted(root.rglob('*.java'))


def zip_tree(root, output):
    with zipfile.ZipFile(output,'w') as z:
        for p in sorted(root.rglob('*')):
            if p.is_file():
                attr=zipfile.ZipInfo(p.relative_to(root).as_posix(),(2026,11,4,0,0,0))
                attr.create_system=3
                attr.external_attr=(0o100755 if p.suffix=='.sh' else 0o100644)<<16
                z.writestr(attr,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED)


def digest(path):
    return hashlib.md5(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    root = Path(__file__).resolve().parent
    parser.add_argument('--java-home',type=Path,required=True)
    parser.add_argument('--hmg-source',type=Path,required=True,help='HMG-API v1.0.1 source tree')
    parser.add_argument('--android-jar',type=Path,required=True)
    parser.add_argument('--d8',type=Path,required=True,help='R8/D8 jar')
    parser.add_argument('--sign-key',type=Path,required=True,help='HMG author PKCS#8 .key; use a local private file')
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--generate-key',action='store_true',help='Create a new author key outside this repository')
    a=parser.parse_args()
    hmg=a.hmg_source.resolve()
    java=a.java_home/'bin/java'
    javac=a.java_home/'bin/javac'
    out=a.out.resolve()
    key=a.sign_key.resolve()
    if root == key or root in key.parents or out==key or out in key.parents:
        raise SystemExit('Keep the author key outside the repository and output directory')
    out.mkdir(parents=True,exist_ok=True)
    if any(out.iterdir()): raise SystemExit('Use an empty output directory')
    with tempfile.TemporaryDirectory() as temp:
        work=Path(temp)
        def javac_to(name, cp, sources):
            dest=work/name
            dest.mkdir()
            execute(javac,'--release','8','-encoding','UTF-8','-cp',os.pathsep.join(map(str,cp)),'-d',dest,*sources)
            return dest
        def dex(classes, target, cp=()):
            args=[opt for p in cp for opt in ('--classpath',p)]
            execute(java,'-cp',a.d8,'com.android.tools.r8.D8','--release','--min-api','19','--lib',a.android_jar,*args,'--output',target,*sorted(classes.rglob('*.class')))
            with zipfile.ZipFile(target) as jar:
                if jar.read('classes.dex')[:8]!=b'dex\n035\0':
                    raise ValueError('not a KitKat DEX')
        def sign(*args):
            return subprocess.check_output([str(x) for x in (java,'-cp',api,'hmgapi.engine.Signing',*args)],text=True).strip()
        stubs=javac_to('stubs',[a.android_jar],java_sources(hmg/'core/runtime/stubs'))
        api=javac_to('api',[a.android_jar,stubs],java_sources(hmg/'core/runtime/java'))
        if a.generate_key:
            if key.exists() or Path(str(key)+'.pub').exists(): raise SystemExit('Choose an unused key path')
            key.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
            previous_mask=os.umask(0o077)
            try: sign('keygen',key)
            finally: os.umask(previous_mask)
        if not key.is_file(): raise SystemExit('No signer key found; use --generate-key for a new local key')
        src=root/'mute'
        mod=work/'mod';mod.mkdir()
        cls=javac_to('mute',[a.android_jar,api],java_sources(src/'java'))
        dex(cls,mod/'hooks.jar',[api])
        shutil.copyfile(src/'mod.json',mod/'mod.json')
        shutil.copyfile(hmg/'LICENSE',mod/'LICENSE')
        manifest=json.loads((mod/'mod.json').read_text())
        if manifest['id']!='neev-carplay-mute-pause': raise ValueError('unexpected mute package ID')
        sign('sign',mod,key)
        owner=json.loads((mod/'META-HMGAPI/manifest.json').read_text())['uuid']
        sign('verify',mod,owner)
        app=work/'nemesis';shutil.copytree(src/'usb/package',app)
        payload=app/'mod/package.zip';zip_tree(mod,payload)
        common=app/'scripts/common.sh'
        template=common.read_text()
        for k,v in {'@AUTHOR_UUID@':owner,'@MOD_MANIFEST_MD5@':digest(mod/'META-HMGAPI/manifest.json'),'@PACKAGE_ZIP_MD5@':digest(payload)}.items():
            if k not in template: raise ValueError(f'missing {k}')
            template=template.replace(k,v)
        common.write_text(template)
        stick=work/'stick';shutil.copytree(src/'usb/stick',stick)
        (stick/'packages').mkdir()
        zip_tree(app,stick/'packages/hmgapi.neev-carplay-mute-pause.zip')
        archive=out/'IONIQ5_CarPlay_Mute_Pause_1.0.0_USB.zip'
        zip_tree(stick,archive)
        print(f'{archive.name}  {hashlib.sha256(archive.read_bytes()).hexdigest()}')


if __name__=='__main__': main()
