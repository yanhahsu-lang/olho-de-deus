[app]

title = Olho de Deus
package.name = olhodedeus
package.domain = com.olhodedeus

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0.0

requirements = python3,kivy,requests,g4f,pyttsx3

orientation = portrait

fullscreen = 0

android.permissions = INTERNET, RECORD_AUDIO, MODIFY_AUDIO_SETTINGS

[buildozer]
log_level = 2
warn_on_root = 1
