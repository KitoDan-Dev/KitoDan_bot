#define MyAppName "KitoDan"
#define MyAppVersion "0.3.0"
#define MyAppPublisher "KitoDan"
#define MyAppExeName "kitodan-tray.exe"

[Setup]
AppId={{41B1C050-4D93-49C6-8DB2-8587D7C5273D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\KitoDan
DefaultGroupName=KitoDan
DisableProgramGroupPage=yes
OutputDir=release
OutputBaseFilename=KitoDanSetup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "autostart"; Description: "Start with Windows"; GroupDescription: "Additional options:"; Flags: unchecked

[Files]
Source: "dist\kitodan-server.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\kitodan-tray.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "README_INSTALL.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\KitoDan"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\KitoDan"; Filename: "{app}\{#MyAppExeName}"

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "KitoDan"; ValueData: """{app}\{#MyAppExeName}"""; Tasks: autostart; Flags: uninsdeletevalue

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Run KitoDan after install"; Flags: nowait postinstall skipifsilent

[Code]
function OllamaInstalled(): Boolean;
var
  ResultCode: Integer;
begin
  Result := Exec(ExpandConstant('{cmd}'), '/C where ollama', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) and (ResultCode = 0);
end;

function OllamaPortOnline(): Boolean;
var
  ResultCode: Integer;
begin
  Result := Exec(ExpandConstant('{cmd}'), '/C powershell -NoProfile -Command "try { $r=Invoke-WebRequest -Uri http://localhost:11434/api/version -UseBasicParsing -TimeoutSec 2; if($r.StatusCode -eq 200){exit 0}else{exit 1}} catch {exit 1}"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) and (ResultCode = 0);
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep=ssPostInstall then
  begin
    if not OllamaInstalled() then
      MsgBox('Ollama was not detected. Install it from https://ollama.com/download and run: ollama pull llama3.1:8b', mbInformation, MB_OK)
    else if not OllamaPortOnline() then
      MsgBox('Ollama is installed but appears offline. Start it with: ollama serve. Also ensure model exists: ollama pull llama3.1:8b', mbInformation, MB_OK);
  end;
end;
