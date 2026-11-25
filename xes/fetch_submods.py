"""拉取 ESP-IDF 子模块（国内镜像版）
规则：
  - 乐鑫自家仓库 -> https://jihulab.com/esp-mirror/espressif/<name>
  - 第三方仓库   -> https://gitee.com/esp-submodules/<name>
"""
import configparser
import os
import subprocess
import sys

GIT = r"C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\tools\mingit\cmd\git.exe"
REPO = r"C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\esp-idf"
CFG = r"C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\gitconfig"

CASEFIX = {"unity": "Unity", "cmock": "CMock", "cexception": "CException"}

ENV = dict(os.environ)
ENV.update({
    "GIT_CONFIG_GLOBAL": CFG,
    "GIT_TERMINAL_PROMPT": "0",
    "GIT_ASKPASS": "",
})


def git(args, cwd=REPO, check=True):
    r = subprocess.run([GIT, "-c", "credential.helper="] + args, cwd=cwd,
                       capture_output=True, text=True, env=ENV)
    if check and r.returncode != 0:
        print("FAIL:", " ".join(args))
        print((r.stdout or "")[-800:], (r.stderr or "")[-800:])
        sys.exit(1)
    return r


def name_from_url(url):
    n = url.rstrip("/").split("/")[-1]
    return n[:-4] if n.endswith(".git") else n


def mirror_url(url):
    name = name_from_url(url)
    if "/espressif/" in url:
        return "https://jihulab.com/esp-mirror/espressif/%s" % name
    return "https://gitee.com/esp-submodules/%s" % CASEFIX.get(name.lower(), name)


def main():
    cp = configparser.RawConfigParser()
    cp.read(os.path.join(REPO, ".gitmodules"))
    pairs = []
    for sec in cp.sections():
        path = cp.get(sec, "path")
        url = dict(cp.items(sec))["url"]
        pairs.append((path, mirror_url(url)))

    print("== 清理上次残留 ==")
    git(["submodule", "deinit", "--all", "-f"], check=False)

    print("== 写入镜像映射 ==")
    for p, u in pairs:
        print("  %-52s %s" % (p, u))
        git(["config", "-f", os.path.join(REPO, ".gitmodules"), "submodule.%s.url" % p, u])
        git(["config", "submodule.%s.url" % p, u])

    print("== 拉取 ==")
    r = subprocess.run([GIT, "-c", "credential.helper=", "submodule", "update",
                        "--init", "--depth", "1", "-j", "4"],
                       cwd=REPO, text=True, env=ENV)
    print("exit=", r.returncode)
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
