"""Run with: uv run --no-project --with tomlkit==0.15.1 python -m unittest -v"""
import argparse
import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import tomlkit
import install


class InstallerTests(unittest.TestCase):
    def args(self, home, dry=False):
        return argparse.Namespace(codex_home=home, dry_run=dry, skip_agent_browser=True)

    def test_merge_backup_and_repeat(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            original = '# local comment\nmodel = "old"\n[features]\nmulti_agent_v2 = true\n[mcp_servers.local]\ncommand = "local-tool"\n[mcp_servers.local.env]\nTOKEN = "fixture-only"\n'
            (home / 'config.toml').write_text(original)
            (home / 'AGENTS.md').write_text('Keep my local guidance.\n')
            with contextlib.redirect_stdout(io.StringIO()):
                install.install(self.args(home))
                first = {name: (home / name).read_text() for name in ['AGENTS.md', 'config.toml']}
                install.install(self.args(home))
            self.assertEqual(first, {name: (home / name).read_text() for name in first})
            config = tomlkit.parse(first['config.toml'])
            self.assertTrue(config['features']['multi_agent_v2']['enabled'])
            self.assertEqual(config['features']['multi_agent_v2']['min_wait_timeout_ms'], 120000)
            self.assertEqual(config['mcp_servers']['local']['env']['TOKEN'], 'fixture-only')
            self.assertIn('# local comment', first['config.toml'])
            self.assertIn('Keep my local guidance.', first['AGENTS.md'])
            self.assertEqual(first['AGENTS.md'].count(install.BEGIN_MARKER), 1)
            self.assertEqual(config['model_instructions_file'], str(home.resolve() / 'model-instructions-long-waits.md'))
            self.assertEqual((home / 'config.toml').stat().st_mode & 0o777, 0o600)
            backups = list((home / install.BACKUP_DIR_NAME).glob('*/config.toml'))
            self.assertEqual(len(backups), 2)
            self.assertIn(original, [p.read_text() for p in backups])

    def test_fresh_dry_run_does_not_create_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / 'absent'
            with patch.object(install, 'run_agent_browser_install') as run, contextlib.redirect_stdout(io.StringIO()):
                install.install(self.args(home, dry=True))
                run.assert_not_called()
            self.assertFalse(home.exists())

    def test_reversed_markers_rejected_without_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            original = install.END_MARKER + '\n' + install.BEGIN_MARKER
            (home / 'AGENTS.md').write_text(original)
            with self.assertRaises(install.InstallerError):
                install.install(self.args(home, dry=True))
            self.assertEqual((home / 'AGENTS.md').read_text(), original)
            self.assertFalse((home / 'config.toml').exists())

    def test_inline_table_preserves_unrelated_settings(self):
        source = tomlkit.parse('[features.multi_agent_v2]\nmin_wait_timeout_ms = 120000\n')
        local = tomlkit.parse('features = { multi_agent_v2 = { enabled = true, max_wait_timeout_ms = 3600000 } }\n')
        result = install.merged_config(source, local)
        self.assertTrue(result['features']['multi_agent_v2']['enabled'])
        self.assertEqual(result['features']['multi_agent_v2']['max_wait_timeout_ms'], 3600000)
        tomlkit.parse(tomlkit.dumps(result))

    def test_browser_uses_resolved_command(self):
        with patch.object(install.shutil, 'which', side_effect=lambda name: '/bin/bun' if name == 'bun' else '/bin/agent-browser'), patch.object(install.subprocess, 'run') as run:
            self.assertEqual(install.run_agent_browser_install(), '/bin/agent-browser')
            self.assertEqual(run.call_args_list[1].args[0], ['/bin/agent-browser', 'install'])


if __name__ == '__main__':
    unittest.main()
