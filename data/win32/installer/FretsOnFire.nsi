;Frets on Fire NSIS script
;Written by Joonas Kerttula

!ifndef VERSION
  !define VERSION '1.2.512-win32'
!endif

;--------------------------------
;General

  SetCompressor /SOLID lzma

  InstType "Full"
  InstType "Lite"

  ;Name and file
  Name "Frets on Fire"
  Caption "Frets on Fire ${VERSION} Setup"
  OutFile FretsOnFire-${VERSION}.exe
  InstallButtonText Install

  XPStyle on

  ;Default installation folder
  InstallDir "$PROGRAMFILES\Frets on Fire"

  ;Get installation folder from registry if available
  InstallDirRegKey HKLM "Software\Frets on Fire" ""

;--------------------------------
;Include Modern UI

  !include "MUI.nsh"

;--------------------------------
;Interface Settings

  !define MUI_HEADERIMAGE
  !define MUI_HEADERIMAGE_BITMAP "InstallerHeader.bmp" ; optional
  !define MUI_ABORTWARNING

;--------------------------------
;Pages

  !insertmacro MUI_PAGE_COMPONENTS
  !insertmacro MUI_PAGE_DIRECTORY
  Page custom SetSettings
  !insertmacro MUI_PAGE_INSTFILES

  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES


;--------------------------------
;Reserve Files
  
  ;These files should be inserted before other files in the data block
  ;Keep these lines before any File command
  ;Only for solid compression (by default, solid compression is enabled for BZIP2 and LZMA)
  
  ReserveFile "SettingsDialog.ini"
  !insertmacro MUI_RESERVEFILE_INSTALLOPTIONS

;--------------------------------
;Installer Functions

Function .onInit

  ;Extract InstallOptions INI files
  !insertmacro MUI_INSTALLOPTIONS_EXTRACT "SettingsDialog.ini"

FunctionEnd

LangString TEXT_IO_TITLE ${LANG_ENGLISH} "Settings"
LangString TEXT_IO_SUBTITLE ${LANG_ENGLISH} "Choose the settings you want to use with Frets on Fire."

Function SetSettings ;FunctionName defined with Page command

  !insertmacro MUI_HEADER_TEXT "$(TEXT_IO_TITLE)" "$(TEXT_IO_SUBTITLE)"
  !insertmacro MUI_INSTALLOPTIONS_DISPLAY "SettingsDialog.ini"

FunctionEnd

;--------------------------------
;Languages

  !insertmacro MUI_LANGUAGE "English"

;--------------------------------
;Installer Sections

Section "Frets on Fire core files (required)" SecCore

  SetOverwrite on
  SetDetailsPrint textonly
  DetailPrint "Installing Frets On Fire Core Files..."
  SetDetailsPrint listonly

  SectionIn 1 2 RO
  SetOutPath "$INSTDIR"
  RMDir /r "$SMPROGRAMS\Frets on Fire"

  File ..\*.*

  SetOutPath "$INSTDIR\data"
  File /r ..\data\PyOpenGL-3.0.0a5-py2.5.egg

  SetOutPath "$INSTDIR\data"
  
  File ..\data\*.*

  SetOutPath $INSTDIR\data\songs\tutorial

  File ..\data\songs\tutorial\*.*

SectionEnd

!ifndef NO_STARTMENUSHORTCUTS
Section "Start Menu and Desktop Shortcuts" SecShortcuts

  SetDetailsPrint textonly
  DetailPrint "Installing Start Menu and Desktop Shortcuts..."
  SetDetailsPrint listonly

!else
Section "Desktop Shortcut" SecShortcuts

  SetOverwrite on
  SetDetailsPrint textonly
  DetailPrint "Installing Desktop Shortcut..."
  SetDetailsPrint listonly

!endif
  SectionIn 1 2
  SetOutPath $INSTDIR
!ifndef NO_STARTMENUSHORTCUTS
  CreateDirectory "$SMPROGRAMS\Frets on Fire"
  CreateShortCut "$SMPROGRAMS\Frets on Fire\Frets on Fire.lnk" "$INSTDIR\FretsOnFire.exe" "" "$INSTDIR\icon.ico" 0
  CreateShortCut "$SMPROGRAMS\Frets on Fire\Readme.lnk" "$INSTDIR\readme.txt"
  CreateShortCut "$SMPROGRAMS\Frets on Fire\Uninstall Frets on Fire.lnk" "$INSTDIR\Uninstall.exe"
  WriteINIStr "$SMPROGRAMS\Frets on Fire\Frets on Fire Webpage.url" "InternetShortcut" "URL" "http://fretsonfire.sourceforge.net"

!endif

  CreateShortCut "$DESKTOP\Frets on Fire.lnk" "$INSTDIR\FretsOnFire.exe"

SectionEnd

SectionGroup "Mods" SecMods

Section "Chilly" SecModsChilly

  SetOverwrite on
  SetDetailsPrint textonly
  DetailPrint "Installing mod | Chilly..."
  SetDetailsPrint listonly

  SectionIn 1
  SetOutPath $INSTDIR\data\mods\Chilly

  File ..\data\mods\Chilly\*.*

SectionEnd

Section "LightGraphics" SecModsLightGraphics

  SetOverwrite on
  SetDetailsPrint textonly
  DetailPrint "Installing mod | Light Graphics..."
  SetDetailsPrint listonly

  SectionIn 1
  SetOutPath $INSTDIR\data\mods\LightGraphics

  File ..\data\mods\LightGraphics\*.*

SectionEnd

SectionGroupEnd

SectionGroup "Songs" SecSongs

Section "Bang Bang, Mystery Man" SecBangBang

  SetOverwrite on
  SetDetailsPrint textonly
  DetailPrint "Installing song | Bang Bang, Mystery Man..."
  SetDetailsPrint listonly

  SectionIn 1
  SetOutPath $INSTDIR\data\songs\bangbang

  File ..\data\songs\bangbang\*.*

SectionEnd

Section "Defy The Machine" SecDefy

  SetOverwrite on
  SetDetailsPrint textonly
  DetailPrint "Installing song | Defy The Machine..."
  SetDetailsPrint listonly

  SectionIn 1
  SetOutPath $INSTDIR\data\songs\defy

  File ..\data\songs\defy\*.*

SectionEnd

Section "This Week I've Been Mostly Playing Guitar" SecTwibmpg

  SetOverwrite on
  SetDetailsPrint textonly
  DetailPrint "Installing song | This Week I've Been Mostly Playing Guitar..."
  SetDetailsPrint listonly

  SectionIn 1
  SetOutPath $INSTDIR\data\songs\twibmpg

  File ..\data\songs\twibmpg\*.*

SectionEnd

SectionGroupEnd

SectionGroup "Translations" SecTrans

Section "French" SecTransFrench

  SetOverwrite on
  SetDetailsPrint textonly
  DetailPrint "Installing translation | French..."
  SetDetailsPrint listonly

  SectionIn 1
  SetOutPath $INSTDIR\data\translations

  File ..\data\translations\french.mo

SectionEnd

Section "Hebrew" SecTransHebrew

  SetOverwrite on
  SetDetailsPrint textonly
  DetailPrint "Installing translation | Hebrew..."
  SetDetailsPrint listonly

  SectionIn 1
  SetOutPath $INSTDIR\data\translations

  File ..\data\translations\hebrew.mo

SectionEnd

Section "Italian" SecTransItalian

  SetOverwrite on
  SetDetailsPrint textonly
  DetailPrint "Installing translation | Italian..."
  SetDetailsPrint listonly

  SectionIn 1
  SetOutPath $INSTDIR\data\translations

  File ..\data\translations\italian.mo

SectionEnd

Section "German" SecTransGerman

  SetOverwrite on
  SetDetailsPrint textonly
  DetailPrint "Installing translation | German..."
  SetDetailsPrint listonly

  SectionIn 1
  SetOutPath $INSTDIR\data\translations

  File ..\data\translations\german.mo

SectionEnd

Section "Polish" SecTransPolish

  SetOverwrite on
  SetDetailsPrint textonly
  DetailPrint "Installing translation | Polish..."
  SetDetailsPrint listonly

  SectionIn 1
  SetOutPath $INSTDIR\data\translations

  File ..\data\translations\polish.mo

SectionEnd

Section "Russian" SecTransRussian

  SetOverwrite on
  SetDetailsPrint textonly
  DetailPrint "Installing translation | Russian..."
  SetDetailsPrint listonly

  SectionIn 1
  SetOutPath $INSTDIR\data\translations

  File ..\data\translations\russian.mo

SectionEnd

Section "Spanish" SecTransSpanish

  SetOverwrite on
  SetDetailsPrint textonly
  DetailPrint "Installing translation | Spanish..."
  SetDetailsPrint listonly

  SectionIn 1
  SetOutPath $INSTDIR\data\translations

  File ..\data\translations\spanish.mo

SectionEnd

Section "Swedish" SecTransSwedish

  SetOverwrite on
  SetDetailsPrint textonly
  DetailPrint "Installing translation | Swedish..."
  SetDetailsPrint listonly

  SectionIn 1
  SetOutPath $INSTDIR\data\translations

  File ..\data\translations\swedish.mo

SectionEnd

Section "Brazilian Portuguese" SecTransBrazilianPortuguese
  
  SetOverwrite on
  SetDetailsPrint textonly
  DetailPrint "Installing translation | Brazilian Portuguese..."
  SetDetailsPrint listonly

  SectionIn 1
  SetOutPath $INSTDIR\data\translations

  File ..\data\translations\brazilian_portuguese.mo

SectionEnd

Section "Dutch" SecTransDutch
  
  SetOverwrite on
  SetDetailsPrint textonly
  DetailPrint "Installing translation | Dutch..."
  SetDetailsPrint listonly

  SectionIn 1
  SetOutPath $INSTDIR\data\translations

  File ..\data\translations\dutch.mo

SectionEnd

Section "Finnish" SecTransFinnish
  
  SetOverwrite on
  SetDetailsPrint textonly
  DetailPrint "Installing translation | Finnish..."
  SetDetailsPrint listonly

  SectionIn 1
  SetOutPath $INSTDIR\data\translations

  File ..\data\translations\finnish.mo

SectionEnd

Section "Turkish" SecTransTurkish
  
  SetOverwrite on
  SetDetailsPrint textonly
  DetailPrint "Installing translation | Turkish..."
  SetDetailsPrint listonly

  SectionIn 1
  SetOutPath $INSTDIR\data\translations

  File ..\data\translations\turkish.mo

SectionEnd

Section "Galician" SecTransGalician
  
  SetOverwrite on
  SetDetailsPrint textonly
  DetailPrint "Installing translation | Galician..."
  SetDetailsPrint listonly

  SectionIn 1
  SetOutPath $INSTDIR\data\translations

  File ..\data\translations\galician.mo

SectionEnd

Section "Hungarian" SecTransHungarian
  
  SetOverwrite on
  SetDetailsPrint textonly
  DetailPrint "Installing translation | Hungarian..."
  SetDetailsPrint listonly

  SectionIn 1
  SetOutPath $INSTDIR\data\translations

  File ..\data\translations\hungarian.mo

SectionEnd

SectionGroupEnd

Section -post

  SetOverwrite on
  SetDetailsPrint textonly
  DetailPrint "Creating Registry Keys..."
  SetDetailsPrint listonly

  ;Store installation folder
  WriteRegStr HKLM "Software\Frets on Fire" "" $INSTDIR

  ;Create uninstall information
  WriteRegExpandStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Frets on Fire" "UninstallString" '"$INSTDIR\Uninstall.exe"'
  WriteRegExpandStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Frets on Fire" "InstallLocation" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Frets on Fire" "DisplayName" "Frets On Fire"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Frets on Fire" "DisplayIcon" "$INSTDIR\icon.ico,0"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Frets on Fire" "DisplayVersion" "${VERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Frets on Fire" "URLInfoAbout" "http://louhi.kempele.fi/~skyostil/uv/fretsonfire/"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Frets on Fire" "NoModify" "1"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Frets on Fire" "NoRepair" "1"

  ;Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"

  SetDetailsPrint both

  !insertmacro MUI_INSTALLOPTIONS_READ $R1 "SettingsDialog.ini" "Field 6" "State"  #overwrite
  IfFileExists "$APPDATA/fretsonfire/fretsonfire.ini" 0 +2
  StrCmp $R1 "1" "" dontinstallsettings
  
  DetailPrint "Creating settings for Frets on Fire..."
  !insertmacro MUI_INSTALLOPTIONS_READ $R2 "SettingsDialog.ini" "Field 1" "State"  #resolution
  !insertmacro MUI_INSTALLOPTIONS_READ $R3 "SettingsDialog.ini" "Field 2" "State"  #multisamples
  !insertmacro MUI_INSTALLOPTIONS_READ $R4 "SettingsDialog.ini" "Field 5" "State"  #fullscreen
  ClearErrors
  SetOutPath $APPDATA\fretsonfire
  FileOpen $0 $APPDATA\fretsonfire\fretsonfire.ini a #open file
  IfErrors errors
  FileSeek $0 0 END #go to end
  FileWrite $0 "[video]$\r$\nfullscreen = " #write to file
  StrCmp $R4 "1" "" +3
  FileWrite $0 "True$\r$\n"
  goto +2
  FileWrite $0 "False$\r$\n"
  FileWrite $0 "resolution = $R2$\r$\nmultisamples = $R3$\r$\n$\r$\n"
  FileClose $0

  goto +3
  errors:
  DetailPrint "Can't write to file $APPDATA\fretsonfire\fretsonfire.ini"
  dontinstallsettings:

SectionEnd

;--------------------------------
;Descriptions

  ;Assign language strings to sections
  !insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecCore} "Frets On Fire core files including tutorial."
    !insertmacro MUI_DESCRIPTION_TEXT ${SecShortcuts} "Adds icons to your start menu and your desktop for easy access"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecSongs} "Install songs"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecTrans} "Install translations"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecTransBrazilianPortuguese} "Install translation: brazilian portuguese"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecTransFrench} "Install translation: french"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecTransGerman} "Install translation: german"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecTransHebrew} "Install translation: hebrew"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecTransItalian} "Install translation: italian"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecTransPolish} "Install translation: polish"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecTransRussian} "Install translation: russian"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecTransSpanish} "Install translation: spanish"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecTransSwedish} "Install translation: swedish"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecTransFinnish} "Install translation: finnish"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecTransDutch} "Install translation: dutch"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecTransGalician} "Install translation: galician"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecTransHungarian} "Install translation: hungarian"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecTransTurkish} "Install translation: turkish"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecMods} "Install mods"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecModsLightGraphics} "Install mod: Light Graphics"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecModsChilly} "Install mod: Chilly"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecBangBang} "Install song: Bang Bang, Mystery Man by Mary Jo feat. Tommi Inkilä"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecDefy} "Install song: Defy The Machine by Tommi Inkilä"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecTwibmpg} "Install song: This Week I've Been Mostly Playing Guitar by Tommi Inkilä"
  !insertmacro MUI_FUNCTION_DESCRIPTION_END

;--------------------------------
;Uninstaller Section

Section "Uninstall"

  SetDetailsPrint textonly
  DetailPrint "Uninstalling Frets on Fire..."
  SetDetailsPrint listonly

  IfFileExists $INSTDIR\FretsOnFire.exe fof_installed
    MessageBox MB_YESNO "It does not appear that Frets on Fire is installed in the directory '$INSTDIR'.$\r$\nContinue anyway (not recommended)?" IDYES fof_installed
    Abort "Uninstall aborted by user"
  fof_installed:

  SetDetailsPrint textonly
  DetailPrint "Deleting Registry Keys..."
  SetDetailsPrint listonly

  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Frets on Fire"
  DeleteRegKey HKLM "Software\Frets on Fire"

  SetDetailsPrint textonly
  DetailPrint "Deleting Files..."
  SetDetailsPrint listonly

  RMDir /r "$SMPROGRAMS\Frets on Fire"
  Delete "$DESKTOP\Frets on Fire.lnk"
  Delete $INSTDIR\FretsOnFire.exe
  Delete $INSTDIR\msvcr71.dll
  Delete $INSTDIR\python25.dll
  Delete $INSTDIR\msvcp71.dll
  Delete $INSTDIR\readme.txt
  Delete $INSTDIR\copying.txt
  Delete $INSTDIR\Uninstall.exe
  RMDir /r $INSTDIR\data\songs
  RMDir /r $INSTDIR\data
  RMDir $INSTDIR

  MessageBox MB_YESNO "Do you want to delete Frets on Fire settings?" IDYES 0 IDNO +3
  RMDir /r $APPDATA\fretsonfire\songs
  RMDir /r $APPDATA\fretsonfire

  SetDetailsPrint both

SectionEnd
