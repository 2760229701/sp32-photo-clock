"""对仍然为空的子模块：完整 clone 镜像仓库 + 切到 IDF 指定的 commit"""
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


def g(args, cwd, check=False):
    return subprocess.run([GIT, "-c", "credential.helper="] + args, cwd=cwd,
                          capture_output=True, text=True, env=ENV, check=False)


def mirror(url):
    n = url.rstrip("/").split("/")[-1]
    if n.endswith(".git"):
        n = n[:-4]
    if "/espressif/" in url:
        return "https://jihulab.com/esp-mirror/espressif/%s" % n
    return "https://gitee.com/esp-submodules/%s" % CASEFIX.get(n.lower(), n)


cp = configparser.RawConfigParser()
cp.read(os.path.join(REPO, ".gitmodules"))

todo = []
for sec in cp.sections():
    d = dict(cp.items(sec))
    full = os.path.join(REPO, d["path"].replace("/", "\\"))
    items = os.listdir(full) if os.path.isdir(full) else []
    if len(items) <= 1:
        todo.append((d["path"], mirror(d["url"]), full))

print("待处理:", len(todo))
for path, url, full in todo:
    sha = g(["ls-tree", "HEAD", path], REPO).stdout.split()
    sha = sha[2] if len(sha) >= 3 else ""
    print("-> %s  sha=%s" % (path, sha[:10]))
    shutil.rmtree(full, ignore_errors=True)
    shutil.rmtree(os.path.join(REPO, ".git", "modules", path.replace("/", "\\")), ignore_errors=True)
    r = g(["clone", url, full], REPO)
    if r.returncode != 0:
        print("   clone FAIL", (r.stderr or "")[-160:])
        continue
    if sha:
        r2 = g(["checkout", "-f", sha], full)
        print("   checkout", "OK" if r2.returncode == 0 else "FAIL " + (r2.stderr or "")[-120:])

print("== 复查 ==")
for sec in cp.sections():
    d = dict(cp.items(sec))
    full = os.path.join(REPO, d["path"].replace("/", "\\"))
    n = len(os.listdir(full)) if os.path.isdir(full) else 0
    if n <= 1:
        print("  仍为空:", d["path"])
