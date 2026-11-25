"""补齐所有只拉了 .git 的空子模块"""
import configparser
import os
import shutil
import subprocess

GIT = r"C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\tools\mingit\cmd\git.exe"
REPO = r"C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\esp-idf"
CFG = r"C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\gitconfig"
CASEFIX = {"unity": "Unity", "cmock": "CMock", "cexception": "CException"}

ENV = dict(os.environ)
ENV.update({"GIT_CONFIG_GLOBAL": CFG, "GIT_TERMINAL_PROMPT": "0", "GIT_ASKPASS": ""})

cp = configparser.RawConfigParser()
cp.read(os.path.join(REPO, ".gitmodules"))

def mirror(url):
    n = url.rstrip("/").split("/")[-1]
    if n.endswith(".git"):
        n = n[:-4]
    if "/espressif/" in url:
        return "https://jihulab.com/esp-mirror/espressif/%s" % n
    return "https://gitee.com/esp-submodules/%s" % CASEFIX.get(n.lower(), n)

todo = []
for sec in cp.sections():
    d = dict(cp.items(sec))
    path, url = d["path"], d["url"]
    full = os.path.join(REPO, path.replace("/", "\\"))
    items = os.listdir(full) if os.path.isdir(full) else []
    if len(items) <= 1:
        todo.append((path, mirror(url), full))

print("需要补齐:", len(todo))
for path, url, full in todo:
    print("  ->", path, url)
    module_dir = os.path.join(REPO, ".git", "modules", path.replace("/", "\\"))
    if os.path.isdir(module_dir):
        shutil.rmtree(module_dir, ignore_errors=True)
    if os.path.isdir(full):
        shutil.rmtree(full, ignore_errors=True)
    subprocess.run([GIT, "-c", "credential.helper=", "config",
                    "submodule.%s.url" % path, url], cwd=REPO, env=ENV, check=True)
    r = subprocess.run([GIT, "-c", "credential.helper=", "submodule", "update",
                        "--init", "--depth", "1", path], cwd=REPO, env=ENV,
                       capture_output=True, text=True)
    ok = r.returncode == 0
    n = len(os.listdir(full)) if os.path.isdir(full) else 0
    print("     %s  内容项数=%d" % ("OK" if ok else "FAIL", n))
    if not ok:
        print("     ", (r.stderr or "")[-300:])

print("== 复查 ==")
bad = 0
for sec in cp.sections():
    d = dict(cp.items(sec))
    full = os.path.join(REPO, d["path"].replace("/", "\\"))
    n = len(os.listdir(full)) if os.path.isdir(full) else 0
    if n <= 1:
        bad += 1
        print("  仍为空:", d["path"])
print("空子模块数:", bad)
