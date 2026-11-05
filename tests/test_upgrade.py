"""Run the signed Mute Pause USB hooks with the real HMG 1.0.1 host engine.

Android IPC and firmware map readiness are bounded stubs. Tests never access the
vehicle, mounted USB, or private author key; --archive is the finished signed kit.
"""
import argparse
from hashlib import sha256
from io import BytesIO
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from zipfile import ZipFile

SOURCE=Path(__file__).resolve().parents[1]
JDK=None
HMG=None
FIRMWARE=None
ID='neev-carplay-mute-pause'
OWNER='bd5f651c-38f9-8ef4-827c-34ad706c2b5c'
APP='hmgapi.'+ID
OLD_USB=None
OLD_UNBRANDED=None
ARCHIVE=None
CLASSES=None


def command(argv, **kw):
    return subprocess.run(list(map(str,argv)),capture_output=True,text=True,check=True,**kw)


def contents(path):
    with ZipFile(path) as z:
        if 'mod/package.zip' in z.namelist():
            return {n:z.read(n) for n in z.namelist() if not n.endswith('/')}
        with ZipFile(BytesIO(z.read('packages/'+APP+'.zip'))) as app:
            return {n:app.read(n) for n in app.namelist() if not n.endswith('/')}


def unpack(files, dest):
    for n,b in files.items():
        p=dest/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)


class Upgrade(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory(prefix='mute-upgrade-')
        self.addCleanup(temp.cleanup)
        self.root=Path(temp.name)
        self.car=self.root/'car';self.sysbin=self.car/'system/bin';self.sysbin.mkdir(parents=True)
        self.hmg=self.car/'data/hmgapi';(self.hmg/'state').mkdir(parents=True)
        (self.hmg/'settings').mkdir();self.settings=self.hmg/'settings'/f'{ID}.json'
        self.settings.write_text('{"keep":true}\n')
        self.other=self.hmg/'mods/neev-usb-carplay';self.other.mkdir(parents=True)
        (self.other/'mod.json').write_text('{"id":"neev-usb-carplay","version":"1.0.1"}')
        self.other_before=(self.other/'mod.json').read_bytes()
        self.installed=self.hmg/'mods'/ID
        self.pkg=self.root/'package';self.package=contents(ARCHIVE);unpack(self.package,self.pkg)
        with ZipFile(BytesIO(self.package['mod/package.zip'])) as z:
            self.expected={n:z.read(n) for n in z.namelist() if not n.endswith('/')}
        self.assertEqual(json.loads(self.expected['mod.json'])['version'],'1.1.0')
        self.versions=self.root/'mutations'
        self.env=dict(os.environ,HMGAPI_ROOT=str(self.car),HMGAPI_HOST='1',
            MP_JAVA=str(JDK/'java'),MP_CLASSES=str(CLASSES),MP_MUTATIONS=str(self.versions))
        odex=self.car/'system/app/HKMC_DiPO.odex';odex.parent.mkdir(parents=True)
        shutil.copyfile(FIRMWARE,odex)
        (self.car/'props.txt').write_text('ro.build.product=NEEV.KOR.0000.V039.001.260902\nro.board.platform=tcc803x\n')
        self.route(self.pkg)
        self.tool('md5','if [ -x /sbin/md5 ]; then exec /sbin/md5 -r "$1"; else exec md5sum "$1"; fi')
        self.tool('getprop','''case "$1" in
ro.build.product) echo "${PRODUCT:-NEEV.KOR.0000.V039.001.260902}";;
ro.board.platform) echo tcc803x;; sys.boot_completed) echo 1;; esac''')
        self.tool('app_process','shift\nexec "$MP_JAVA" -cp "$MP_CLASSES" "$@"')
        self.tool('hmgapid','''case "$1" in
version) echo "hmgapid ${ENGINE_VERSION:-1.0.1}";; ping) exit 0;;
engine) shift
    case "$1" in
    map) echo "hook map: probed, hooks ${MAP_STATE:-on}";;
    install|remove) echo "$*" >> "$MP_MUTATIONS"; exec "$MP_JAVA" -cp "$MP_CLASSES" hmgapi.engine.Engine "$@";;
    *) exit 69;; esac;;
*) exit 69;; esac''')
        (self.root/'caller').write_text('nemesis install --update')

    def route(self, package):
        for p in (package/'scripts').glob('*.sh'):
            text=p.read_text().replace('/system/',str(self.car)+'/system/').replace('/data/',str(self.car)+'/data/')
            text=text.replace(str(self.car)+'/data/nemesis/bin\n',str(self.car)+'/data/nemesis/bin:/usr/bin:/bin\n')
            text=text.replace('/proc/$PPID/cmdline',str(self.root/'caller'))
            p.write_text(text);command(['/bin/sh','-n',p])

    def tool(self,name,body):
        p=self.sysbin/name;p.write_text('#!/bin/sh\n'+body+'\n');p.chmod(0o755)

    def hook(self,name,okay=True,package=None,**flags):
        package=package or self.pkg
        p=subprocess.run(['/bin/sh',str(package/'scripts'/f'{name}.sh')],cwd=package,
                         env=dict(self.env,**flags),capture_output=True,text=True)
        self.assertEqual(p.returncode==0,okay,p.stdout+p.stderr)
        return p

    def engine(self,*args):
        return command([JDK/'java','-cp',CLASSES,'hmgapi.engine.Engine',*args],env=self.env)

    def old(self,unbranded=False,disabled=False):
        package=self.root/'old-package';unpack(contents(OLD_UNBRANDED if unbranded else OLD_USB),package)
        self.engine('install',package/'mod/package.zip','--uuid',OWNER,'--from-nemesis')
        if disabled:(self.installed/'.disabled').touch()
        return package

    def count(self):
        return len(self.versions.read_text().splitlines()) if self.versions.exists() else 0

    def assert_current(self,disabled=False):
        for n,b in self.expected.items():self.assertEqual((self.installed/n).read_bytes(),b,n)
        self.assertEqual((self.installed/'.disabled').exists(),disabled)
        self.assertEqual(self.settings.read_text(),'{"keep":true}\n')
        self.assertEqual((self.other/'mod.json').read_bytes(),self.other_before)

    def test_fresh_then_idempotent_install(self):
        self.hook('preinstall');self.hook('postinstall');self.assert_current()
        self.hook('postinstall');self.assert_current();self.assertEqual(self.count(),1)

    def test_public_100_upgrade_preserves_disabled_and_settings(self):
        old=self.old(disabled=True)
        # NEMESIS uses --update and invokes the old preuninstall before replacement.
        stage=self.car/'data/local/tmp/nemesis/stage'/APP;stage.mkdir(parents=True)
        shutil.copyfile(self.pkg/'NEMESIS.data',stage/'NEMESIS.data')
        self.route(old);self.hook('preuninstall',package=old)
        self.assertEqual(json.loads((self.installed/'mod.json').read_text())['version'],'1.0.0')
        self.hook('preinstall');self.hook('postinstall');self.assert_current(True)
        self.assertEqual(self.count(),1)
        self.hook('postinstall');self.assertEqual(self.count(),1)

    def test_unbranded_100_upgrade(self):
        if OLD_UNBRANDED is None:self.skipTest("optional private unbranded fixture not supplied")
        self.old(unbranded=True)
        self.hook('preinstall');self.hook('postinstall');self.assert_current()

    def test_tampered_old_mod_rejected_before_mutation(self):
        self.old();p=self.installed/'hooks.jar';before=p.read_bytes();p.write_bytes(before+b'x')
        self.hook('preinstall',False);self.hook('postinstall',False)
        self.assertEqual(self.count(),0);self.assertEqual(p.read_bytes(),before+b'x')

    def test_unknown_manifest_and_unsigned_file_rejected(self):
        self.old();p=self.installed/'META-HMGAPI/manifest.json';raw=p.read_bytes();p.write_bytes(raw+b' ')
        self.hook('preinstall',False);p.write_bytes(raw)
        (self.installed/'._LICENSE').touch();self.hook('preinstall',False)
        self.assertEqual(self.count(),0)

    def test_prerequisites_and_damaged_input_do_not_mutate(self):
        for flags in ({'PRODUCT':'CN7.X'},{'ENGINE_VERSION':'1.0.0'},{'MAP_STATE':'off'}):self.hook('preinstall',False,**flags)
        journal=self.hmg/'state/journal.json';journal.touch();self.hook('preinstall',False);journal.unlink()
        p=self.pkg/'mod/package.zip';p.write_bytes(p.read_bytes()+b'x');self.hook('preinstall',False)
        self.assertFalse(self.installed.exists());self.assertEqual(self.count(),0)

    def test_uninstall_only_our_mod(self):
        self.hook('postinstall');self.assert_current()
        (self.root/'caller').write_text('nemesis uninstall '+APP)
        self.hook('preuninstall');self.hook('preuninstall')
        self.assertFalse(self.installed.exists());self.assertEqual(self.count(),2)
        self.assertEqual((self.other/'mod.json').read_bytes(),self.other_before)
        self.assertEqual(self.settings.read_text(),'{"keep":true}\n')


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    for name in ('archive','java-home','hmg-source','old-archive','firmware-odex'):
        ap.add_argument('--'+name,type=Path,required=True)
    ap.add_argument('--old-unbranded',type=Path,help='Optional unpublished1.0.0 NEMESIS capsule')
    a=ap.parse_args()
    ARCHIVE=a.archive.resolve();JDK=a.java_home.resolve()/'bin';HMG=a.hmg_source.resolve()
    OLD_USB=a.old_archive.resolve();FIRMWARE=a.firmware_odex.resolve()
    OLD_UNBRANDED=a.old_unbranded.resolve() if a.old_unbranded else None
    with tempfile.TemporaryDirectory(prefix='mute-upgrade-engine-') as t:
        CLASSES=Path(t)/'classes';CLASSES.mkdir()
        command([JDK/'javac','--release','8','-d',CLASSES,*sorted((HMG/'core/runtime/java/hmgapi/engine').glob('*.java'))])
        result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Upgrade))
        raise SystemExit(0 if result.wasSuccessful() else 1)
