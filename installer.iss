#define MyAppName "Hotel Venecia"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Hotel Venecia"
#define MyAppExeName "Hotel Venecia.exe"

[Setup]
AppId={{B8B4B9B3-3F8B-4D88-9C12-8D1D0A0AA001}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\Hotel Venecia
DefaultGroupName={#MyAppName}
OutputDir=installer_output
OutputBaseFilename=HotelVeneciaSetup
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=lowest
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Dirs]
Name: "{localappdata}\HotelSistema"

[Icons]
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Parameters: "--migrate"; StatusMsg: "Preparando la base de datos local..."; Flags: runhidden waituntilterminated
Filename: "{app}\{#MyAppExeName}"; Description: "Abrir {#MyAppName}"; Flags: nowait postinstall skipifsilent