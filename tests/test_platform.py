import base64,hashlib,importlib,json,os,sys,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock,patch
HOST=Path(__file__).resolve().parents[1]/'host'
sys.path.insert(0,str(HOST))
import platform_config as config
import process_utils
import keyfinder_backend
import install

class PlatformTests(unittest.TestCase):
    def test_windows_current_user_layout(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(sys,'platform','win32'),patch.dict(os.environ,{'LOCALAPPDATA':tmp}):
            base=config.install_base()
            self.assertEqual(base,Path(tmp)/'YouTube Audio')
            self.assertEqual(config.manifest_path(base),base/'com.local.youtube_audio.json')
            self.assertEqual(keyfinder_backend.helper_path().name,'keyfinder-audio.exe')
            self.assertEqual(process_utils.spawn_options()['creationflags'],0x08000000)
    def test_mac_layout_and_executable(self):
        with patch.object(sys,'platform','darwin'):
            self.assertEqual(config.install_base(),Path.home()/'Library/Application Support/YouTube Audio')
            self.assertEqual(keyfinder_backend.helper_path().name,'keyfinder-audio')
            self.assertEqual(process_utils.spawn_options(),{})
    def test_registry_current_user_only(self):
        key=MagicMock();context=MagicMock();context.__enter__.return_value=key
        registry=SimpleNamespace(HKEY_CURRENT_USER='HKCU',KEY_SET_VALUE=2,REG_SZ=1,CreateKeyEx=MagicMock(return_value=context),SetValueEx=MagicMock())
        with patch.dict(sys.modules,{'winreg':registry}):config.register_windows(Path('native-host.json'))
        registry.CreateKeyEx.assert_called_once_with('HKCU',r'Software\Google\Chrome\NativeMessagingHosts\com.local.youtube_audio',0,2)
        registry.SetValueEx.assert_called_once_with(key,'',0,1,str(Path('native-host.json').resolve()))
    def test_binary_integrity_detects_damage(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory=Path(tmp);data={name:b'MZ-test-'+name.encode() for name in ('native-host.exe','keyfinder-audio.exe')}
            for name,content in data.items():(directory/name).write_bytes(content)
            (directory/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(content).hexdigest()+'  '+name+'\n' for name,content in data.items()))
            install.verify_windows_binaries(directory)
            (directory/'keyfinder-audio.exe').write_bytes(b'damaged')
            with self.assertRaises(RuntimeError):install.verify_windows_binaries(directory)
    def test_extension_id_is_portable(self):
        manifest=json.loads((HOST.parent/'extension/manifest.json').read_text())
        fingerprint=hashlib.sha256(base64.b64decode(manifest['key'])).hexdigest()[:32]
        expected=''.join(chr(ord('a')+int(c,16)) for c in fingerprint)
        self.assertEqual(install.extension_id(),expected)
        self.assertEqual(install.extension_id('a'*32),'a'*32)
    def test_windows_folder_reveal(self):
        with patch.object(sys,'platform','win32'),patch.object(os,'startfile',create=True) as reveal:
            config.reveal_audio(Path('/audio/track.mp3'));reveal.assert_called_once_with('/audio')

if __name__=='__main__':unittest.main()
