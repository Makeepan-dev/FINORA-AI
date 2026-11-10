using System;
using System.Diagnostics;
using System.IO;
using System.Windows.Forms;
using Microsoft.Win32;

namespace FinoraUninstaller
{
    internal static class UninstallProgram
    {
        [STAThread]
        private static int Main(string[] args)
        {
            bool silent = false;
            bool purgeUserData = false;
            string targetDir = AppDomain.CurrentDomain.BaseDirectory.TrimEnd('\\', '/');

            for (int i = 0; i < args.Length; i++)
            {
                string a = args[i];
                if (a.Equals("/S", StringComparison.OrdinalIgnoreCase) ||
                    a.Equals("/SILENT", StringComparison.OrdinalIgnoreCase) ||
                    a.Equals("--silent", StringComparison.OrdinalIgnoreCase))
                {
                    silent = true;
                }
                else if (a.Equals("--purge-user-data", StringComparison.OrdinalIgnoreCase))
                {
                    purgeUserData = true;
                }
                else if (a.StartsWith("/DIR=", StringComparison.OrdinalIgnoreCase))
                {
                    targetDir = a.Substring(5).Trim('"');
                }
            }

            if (!silent)
            {
                DialogResult confirm = MessageBox.Show(
                    "Are you sure you want to uninstall FINORA from your computer?\n\n" +
                    "Your personal financial database in %APPDATA%\\FINORA will be preserved unless you choose to remove it.",
                    "FINORA Uninstaller",
                    MessageBoxButtons.YesNo,
                    MessageBoxIcon.Question);
                if (confirm != DialogResult.Yes)
                {
                    return 0;
                }

                DialogResult removeData = MessageBox.Show(
                    "Do you want to KEEP your personal financial database and settings in %APPDATA%\\FINORA?\n\n" +
                    "Click YES to keep your data (Recommended).\nClick NO to permanently delete %APPDATA%\\FINORA.",
                    "FINORA — Preserve User Financial Data?",
                    MessageBoxButtons.YesNo,
                    MessageBoxIcon.Warning);
                if (removeData == DialogResult.No)
                {
                    purgeUserData = true;
                }
            }

            try
            {
                foreach (Process proc in Process.GetProcessesByName("FINORA"))
                {
                    try { proc.Kill(); proc.WaitForExit(3000); } catch { }
                }
                foreach (Process proc in Process.GetProcessesByName("FINORA Portable"))
                {
                    try { proc.Kill(); proc.WaitForExit(3000); } catch { }
                }
            }
            catch { }

            try
            {
                string startMenuLnk = Path.Combine(
                    Environment.GetFolderPath(Environment.SpecialFolder.Programs),
                    "FINORA.lnk");
                if (File.Exists(startMenuLnk)) File.Delete(startMenuLnk);

                string desktopLnk = Path.Combine(
                    Environment.GetFolderPath(Environment.SpecialFolder.DesktopDirectory),
                    "FINORA.lnk");
                if (File.Exists(desktopLnk)) File.Delete(desktopLnk);

                Registry.CurrentUser.DeleteSubKeyTree(
                    @"Software\Microsoft\Windows\CurrentVersion\Uninstall\FINORA",
                    false);
            }
            catch { }

            if (purgeUserData)
            {
                try
                {
                    string appDataDir = Path.Combine(
                        Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
                        "FINORA");
                    if (Directory.Exists(appDataDir))
                    {
                        Directory.Delete(appDataDir, true);
                    }
                }
                catch { }
            }

            if (Directory.Exists(targetDir))
            {
                try
                {
                    string currentExe = Process.GetCurrentProcess().MainModule != null
                        ? Process.GetCurrentProcess().MainModule.FileName
                        : "";
                    bool runningInsideTarget = currentExe.StartsWith(targetDir, StringComparison.OrdinalIgnoreCase);

                    if (!runningInsideTarget)
                    {
                        Directory.Delete(targetDir, true);
                    }
                    else
                    {
                        foreach (string file in Directory.GetFiles(targetDir, "*", SearchOption.AllDirectories))
                        {
                            if (!file.Equals(currentExe, StringComparison.OrdinalIgnoreCase))
                            {
                                try { File.Delete(file); } catch { }
                            }
                        }
                        Process.Start(new ProcessStartInfo
                        {
                            FileName = "cmd.exe",
                            Arguments = "/C ping 127.0.0.1 -n 2 > nul & rmdir /S /Q \"" + targetDir + "\"",
                            CreateNoWindow = true,
                            UseShellExecute = false,
                            WindowStyle = ProcessWindowStyle.Hidden
                        });
                    }
                }
                catch { }
            }

            if (!silent)
            {
                MessageBox.Show(
                    "FINORA has been uninstalled successfully.",
                    "FINORA Uninstaller",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Information);
            }

            return 0;
        }
    }
}
