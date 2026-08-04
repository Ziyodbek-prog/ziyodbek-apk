[app]
title = ZiyodbekMultiTool
package.name = multitool
package.domain = com.ziyodbek
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0
requirements = python3,kivy==2.3.0,kivymd==1.2.0,requests,urllib3,chardet,idna,certifi


orientation = portrait
fullscreen = 0

android.api = 33
android.minapi = 21
android.ndk_api = 21
android.accept_sdk_license = True
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
