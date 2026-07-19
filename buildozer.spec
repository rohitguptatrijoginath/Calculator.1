[app]

title = Calculator

package.name = calculator
package.domain = com.calculatorapp

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0

requirements = python3,kivy,numpy,matplotlib,speechrecognition,pyjnius

orientation = portrait
fullscreen = 0

icon.filename = icon.png
presplash.filename =

android.permissions = INTERNET,RECORD_AUDIO,USE_FINGERPRINT

android.api = 31
android.minapi = 21
android.sdk = 31
android.ndk = 25b
android.ndk_api = 21

android.archs = arm64-v8a

android.accept_sdk_license = True
android.skip_update = False

log_level = 2


[buildozer]
log_level = 2
warn_on_root = 1


[p4a]
p4a.branch = master
