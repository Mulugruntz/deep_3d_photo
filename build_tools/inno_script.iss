; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "Deep3DPhoto"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Samuel Giffard"
#define MyAppURL "https://github.com/Mulugruntz/deep_3d_photo"
#define MyAppExeName "START.bat"

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{FDD739FE-2EBE-4F3A-88A7-7172BE3689A7}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=D:\Deep3DPhoto\deep_3d_photo\winbuild\deep_3d_photo\LICENSE
; Remove the following line to run in administrative install mode (install for all users.)
PrivilegesRequired=lowest
OutputDir=D:\Deep3DPhoto\deep_3d_photo\windist
OutputBaseFilename=Install Deep3DPhoto
SetupIconFile=D:\Deep3DPhoto\deep_3d_photo\winbuild\deep_3d_photo\res\deep3dphoto.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "D:\Deep3DPhoto\deep_3d_photo\winbuild\START.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\Deep3DPhoto\deep_3d_photo\winbuild\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\deep_3d_photo\res\deep3dphoto.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\deep_3d_photo\res\deep3dphoto.ico"

[Run]
Filename: "{cmd}"; Parameters: "/C set PIPENV_INSTALL_TIMEOUT=7200 & SET PIPENV_VENV_IN_PROJECT=1 & ""{app}\deep_3d_photo\bootstrap\Scripts\python.exe"" -m pipenv install"; WorkingDir: "{app}\deep_3d_photo"; StatusMsg: "Installing Python dependencies... (may take several minutes)"   ; Flags: runminimized
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: shellexec postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"