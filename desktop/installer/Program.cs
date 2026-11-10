using System;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.IO.Compression;
using System.Reflection;
using System.Threading.Tasks;
using System.Windows.Forms;
using Microsoft.Win32;

namespace FinoraInstaller
{
    internal static class Program
    {
        [STAThread]
        private static int Main(string[] args)
        {
            bool silent = false;
            bool launchAfter = false;
            bool createDesktopShortcut = true;
            bool createStartMenuShortcut = true;
            string installDir = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                "Programs",
                "FINORA");

            foreach (string arg in args)
            {
                if (arg.Equals("/S", StringComparison.OrdinalIgnoreCase) ||
                    arg.Equals("/SILENT", StringComparison.OrdinalIgnoreCase) ||
                    arg.Equals("--silent", StringComparison.OrdinalIgnoreCase))
                {
                    silent = true;
                }
                else if (arg.Equals("/LAUNCH", StringComparison.OrdinalIgnoreCase) ||
                         arg.Equals("--launch", StringComparison.OrdinalIgnoreCase))
                {
                    launchAfter = true;
                }
                else if (arg.Equals("/NODESKTOP", StringComparison.OrdinalIgnoreCase))
                {
                    createDesktopShortcut = false;
                }
                else if (arg.StartsWith("/DIR=", StringComparison.OrdinalIgnoreCase))
                {
                    installDir = arg.Substring(5).Trim('"');
                }
            }

            if (silent)
            {
                try
                {
                    PerformInstallation(installDir, createStartMenuShortcut, createDesktopShortcut, null);
                    if (launchAfter)
                    {
                        string exePath = Path.Combine(installDir, "FINORA.exe");
                        if (File.Exists(exePath))
                        {
                            Process.Start(new ProcessStartInfo
                            {
                                FileName = exePath,
                                WorkingDirectory = installDir,
                                UseShellExecute = true
                            });
                        }
                    }
                    return 0;
                }
                catch (Exception ex)
                {
                    Console.Error.WriteLine("FINORA installation failed: " + ex.Message);
                    return 1;
                }
            }

            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new SetupForm(installDir));
            return 0;
        }

        public static void PerformInstallation(
            string installDir,
            bool startMenuShortcut,
            bool desktopShortcut,
            Action<int, string> progressCallback)
        {
            if (progressCallback != null) progressCallback(5, "Preparing installation directory...");

            foreach (Process proc in Process.GetProcessesByName("FINORA"))
            {
                try { proc.Kill(); proc.WaitForExit(3000); } catch { }
            }

            Directory.CreateDirectory(installDir);

            string appDataFinora = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
                "FINORA");
            Directory.CreateDirectory(appDataFinora);

            if (progressCallback != null) progressCallback(15, "Extracting FINORA desktop package...");

            Assembly asm = Assembly.GetExecutingAssembly();
            using (Stream payloadStream = asm.GetManifestResourceStream("FINORA.payload.zip"))
            {
                if (payloadStream == null)
                {
                    throw new InvalidOperationException("Embedded payload.zip resource not found.");
                }

                using (ZipArchive archive = new ZipArchive(payloadStream, ZipArchiveMode.Read))
                {
                    int totalEntries = Math.Max(1, archive.Entries.Count);
                    int processed = 0;

                    foreach (ZipArchiveEntry entry in archive.Entries)
                    {
                        processed++;
                        string destinationPath = Path.GetFullPath(Path.Combine(installDir, entry.FullName));
                        if (!destinationPath.StartsWith(Path.GetFullPath(installDir), StringComparison.OrdinalIgnoreCase))
                        {
                            continue;
                        }

                        if (string.IsNullOrEmpty(entry.Name))
                        {
                            Directory.CreateDirectory(destinationPath);
                            continue;
                        }

                        string parentDir = Path.GetDirectoryName(destinationPath);
                        if (!string.IsNullOrEmpty(parentDir))
                        {
                            Directory.CreateDirectory(parentDir);
                        }
                        entry.ExtractToFile(destinationPath, true);

                        if (processed % 15 == 0 || processed == totalEntries)
                        {
                            int pct = 15 + (int)(processed * 70.0 / totalEntries);
                            if (progressCallback != null)
                            {
                                progressCallback(pct, string.Format("Installing files ({0}/{1})...", processed, totalEntries));
                            }
                        }
                    }
                }
            }

            string targetExe = Path.Combine(installDir, "FINORA.exe");
            string iconPath = Path.Combine(installDir, "icon.ico");
            string uninstallExe = Path.Combine(installDir, "FINORA Uninstall.exe");

            if (progressCallback != null) progressCallback(90, "Creating Windows shortcuts...");

            if (startMenuShortcut)
            {
                string startMenuPath = Path.Combine(
                    Environment.GetFolderPath(Environment.SpecialFolder.Programs),
                    "FINORA.lnk");
                CreateWindowsShortcut(startMenuPath, targetExe, installDir, iconPath, "FINORA — AI Financial Intelligence Assistant");
            }

            if (desktopShortcut)
            {
                string desktopPath = Path.Combine(
                    Environment.GetFolderPath(Environment.SpecialFolder.DesktopDirectory),
                    "FINORA.lnk");
                CreateWindowsShortcut(desktopPath, targetExe, installDir, iconPath, "FINORA — AI Financial Intelligence Assistant");
            }

            if (progressCallback != null) progressCallback(95, "Registering application with Windows...");

            using (RegistryKey key = Registry.CurrentUser.CreateSubKey(
                @"Software\Microsoft\Windows\CurrentVersion\Uninstall\FINORA"))
            {
                if (key != null)
                {
                    key.SetValue("DisplayName", "FINORA — AI Financial Intelligence Assistant");
                    key.SetValue("DisplayVersion", "1.0.0");
                    key.SetValue("Publisher", "FINORA AI");
                    key.SetValue("InstallLocation", installDir);
                    key.SetValue("DisplayIcon", File.Exists(iconPath) ? iconPath : targetExe);
                    key.SetValue("UninstallString", "\"" + uninstallExe + "\" /DIR=\"" + installDir + "\"");
                    key.SetValue("NoModify", 1, RegistryValueKind.DWord);
                    key.SetValue("NoRepair", 1, RegistryValueKind.DWord);
                }
            }

            if (progressCallback != null) progressCallback(100, "Installation complete!");
        }

        private static void CreateWindowsShortcut(
            string shortcutPath,
            string targetExe,
            string workingDir,
            string iconPath,
            string description)
        {
            try
            {
                Type shellType = Type.GetTypeFromProgID("WScript.Shell");
                if (shellType == null) return;
                object shell = Activator.CreateInstance(shellType);
                object shortcut = shellType.InvokeMember("CreateShortcut", BindingFlags.InvokeMethod, null, shell, new object[] { shortcutPath });
                Type scType = shortcut.GetType();
                scType.InvokeMember("TargetPath", BindingFlags.SetProperty, null, shortcut, new object[] { targetExe });
                scType.InvokeMember("WorkingDirectory", BindingFlags.SetProperty, null, shortcut, new object[] { workingDir });
                if (File.Exists(iconPath))
                {
                    scType.InvokeMember("IconLocation", BindingFlags.SetProperty, null, shortcut, new object[] { iconPath });
                }
                scType.InvokeMember("Description", BindingFlags.SetProperty, null, shortcut, new object[] { description });
                scType.InvokeMember("Save", BindingFlags.InvokeMethod, null, shortcut, null);
            }
            catch { }
        }
    }

    internal sealed class SetupForm : Form
    {
        private readonly TextBox _dirBox;
        private readonly CheckBox _startMenuCheck;
        private readonly CheckBox _desktopCheck;
        private readonly CheckBox _launchCheck;
        private readonly ProgressBar _progressBar;
        private readonly Label _statusLabel;
        private readonly Button _installBtn;
        private readonly Button _browseBtn;

        public SetupForm(string defaultInstallDir)
        {
            Text = "FINORA v1.0.0 Setup";
            Size = new Size(580, 430);
            FormBorderStyle = FormBorderStyle.FixedDialog;
            MaximizeBox = false;
            StartPosition = FormStartPosition.CenterScreen;
            BackColor = Color.FromArgb(15, 23, 42);
            ForeColor = Color.FromArgb(248, 250, 252);
            Font = new Font("Segoe UI", 9.5F, FontStyle.Regular);

            Label titleLabel = new Label
            {
                Text = "FINORA — AI Financial Intelligence Assistant",
                Font = new Font("Segoe UI", 14F, FontStyle.Bold),
                ForeColor = Color.FromArgb(16, 185, 129),
                AutoSize = true,
                Location = new Point(24, 20)
            };

            Label subtitleLabel = new Label
            {
                Text = "Install the standalone FINORA Windows desktop application (Frontend + FastAPI + SQLite).",
                ForeColor = Color.FromArgb(148, 163, 184),
                AutoSize = true,
                Location = new Point(24, 52)
            };

            Label dirLabel = new Label
            {
                Text = "Installation Folder:",
                AutoSize = true,
                Location = new Point(24, 92)
            };

            _dirBox = new TextBox
            {
                Text = defaultInstallDir,
                Location = new Point(24, 116),
                Size = new Size(420, 28),
                BackColor = Color.FromArgb(2, 6, 23),
                ForeColor = Color.White,
                BorderStyle = BorderStyle.FixedSingle
            };

            _browseBtn = new Button
            {
                Text = "Browse...",
                Location = new Point(454, 114),
                Size = new Size(90, 28),
                FlatStyle = FlatStyle.Flat,
                BackColor = Color.FromArgb(30, 41, 59),
                ForeColor = Color.White
            };
            _browseBtn.Click += delegate
            {
                using (FolderBrowserDialog dlg = new FolderBrowserDialog { SelectedPath = _dirBox.Text })
                {
                    if (dlg.ShowDialog(this) == DialogResult.OK)
                    {
                        _dirBox.Text = dlg.SelectedPath;
                    }
                }
            };

            _startMenuCheck = new CheckBox
            {
                Text = "Create Start Menu shortcut",
                Checked = true,
                AutoSize = true,
                Location = new Point(24, 162)
            };

            _desktopCheck = new CheckBox
            {
                Text = "Create Desktop shortcut",
                Checked = true,
                AutoSize = true,
                Location = new Point(24, 192)
            };

            _launchCheck = new CheckBox
            {
                Text = "Launch FINORA after installation finishes",
                Checked = true,
                AutoSize = true,
                Location = new Point(24, 222)
            };

            _statusLabel = new Label
            {
                Text = "Ready to install. Existing user data in %APPDATA%\\FINORA will be preserved.",
                ForeColor = Color.FromArgb(148, 163, 184),
                AutoSize = true,
                Location = new Point(24, 265)
            };

            _progressBar = new ProgressBar
            {
                Location = new Point(24, 292),
                Size = new Size(520, 22),
                Minimum = 0,
                Maximum = 100,
                Value = 0
            };

            _installBtn = new Button
            {
                Text = "Install FINORA",
                Location = new Point(394, 334),
                Size = new Size(150, 36),
                FlatStyle = FlatStyle.Flat,
                BackColor = Color.FromArgb(16, 185, 129),
                ForeColor = Color.FromArgb(2, 6, 23),
                Font = new Font("Segoe UI", 10F, FontStyle.Bold)
            };
            _installBtn.Click += async delegate { await RunInstallAsync(); };

            Controls.AddRange(new Control[]
            {
                titleLabel, subtitleLabel, dirLabel, _dirBox, _browseBtn,
                _startMenuCheck, _desktopCheck, _launchCheck,
                _statusLabel, _progressBar, _installBtn
            });
        }

        private async Task RunInstallAsync()
        {
            _installBtn.Enabled = false;
            _browseBtn.Enabled = false;
            _dirBox.ReadOnly = true;

            string targetDir = _dirBox.Text.Trim();
            bool startMenu = _startMenuCheck.Checked;
            bool desktop = _desktopCheck.Checked;
            bool launch = _launchCheck.Checked;

            try
            {
                await Task.Run(delegate
                {
                    Program.PerformInstallation(targetDir, startMenu, desktop, delegate(int pct, string msg)
                    {
                        if (IsHandleCreated)
                        {
                            BeginInvoke(new Action(delegate
                            {
                                _progressBar.Value = Math.Max(0, Math.Min(100, pct));
                                _statusLabel.Text = msg;
                            }));
                        }
                    });
                });

                if (launch)
                {
                    string exePath = Path.Combine(targetDir, "FINORA.exe");
                    if (File.Exists(exePath))
                    {
                        Process.Start(new ProcessStartInfo
                        {
                            FileName = exePath,
                            WorkingDirectory = targetDir,
                            UseShellExecute = true
                        });
                    }
                }

                MessageBox.Show(
                    this,
                    "FINORA has been installed to:\n" + targetDir,
                    "FINORA Setup Complete",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Information);
                Close();
            }
            catch (Exception ex)
            {
                MessageBox.Show(
                    this,
                    "Installation failed:\n" + ex.Message,
                    "FINORA Setup Error",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error);
                _installBtn.Enabled = true;
                _browseBtn.Enabled = true;
                _dirBox.ReadOnly = false;
            }
        }
    }
}
