# TWRP device tree — uws6152_1h10_go (M92K / W527)

适用于：**M92K / W527（CD20MAX 同平台）Android 9 手表**，代号 `uws6152_1h10_go`，SoC UWS6152（ums312 / sharkl5，arm64）。

本设备树已针对原机固件做过对齐：

| 项目 | 值 |
|---|---|
| 内核 | 直接取自原机 `boot.bin`（17,577,992 B，md5 `667b87df745d5a4f936ad860ee780be5`，2026-09-29 编译），**未修改** |
| recovery_dtbo | 直接取自原机 `recovery.bin` 尾部（135,168 B，md5 `5ebb4d120d12602931a8137de81b534e`） |
| cmdline | `console=ttyS1,115200n8 buildvariant=user`（与原机一致） |
| bootimg | header v1 / pagesize 2048 / ramdisk_offset 0x05400000 / tags 0x100（与原机一致） |
| AVB | 使用设备 `recovery` 分区 chain key（RSA-4096，公钥 SHA1 `d9093b9a181bdb5731b44d60a9f850dc724e2874`），`--rollback_index 0` |
| 分区 | 非 A/B；boot 35 MiB / recovery 40 MiB；system ext4（system-as-root）、data f2fs + FBE |

## 一键编译（GitHub Actions）

1. 把本目录全部文件上传/推送到你自己的 GitHub 仓库（根目录就是本目录）。
2. 仓库页面 → **Actions** → 左侧 **Build TWRP (uws6152_1h10_go / M92K-W527)** → **Run workflow**。
3. 约 40~90 分钟后：
   - 该次运行页面下方 **Artifacts → recovery-img**（需登录 GitHub 下载），或
   - 仓库右侧 **Releases** 里直接下载 `recovery.img`。
4. 产物 `recovery.img` 已经是 **40 MiB、已用设备 recovery key 做好 AVB 签名** 的完整分区镜像。

## 本地编译（Ubuntu 20.04 / 22.04）

```bash
mkdir twrp && cd twrp
repo init --depth=1 -u https://github.com/minimal-manifest-twrp/platform_manifest_twrp_omni -b twrp-9.0
repo sync -j$(nproc --all)

# 本目录放到 device/sprd/uws6152_1h10_go
source build/envsetup.sh
export ALLOW_MISSING_DEPENDENCIES=true
lunch omni_uws6152_1h10_go-eng
make -j$(nproc --all) recoveryimage
# 产物 out/target/product/uws6152_1h10_go/recovery.img
```

> AOSP 9 的 `mkbootimg` / `avbtool` 需要 python2；Ubuntu 22.04 上如无 python2，请先
> `sudo apt install python2` 并 `sudo ln -sf $(command -v python2) /usr/bin/python`。

## 刷入（只写 recovery 分区）

见上层目录 `README.md` 与 `flash/` 里的脚本：使用 spd_dump 的
`write_part recovery recovery.img`，**不碰 boot、misc、vbmeta**。

## 回滚

原厂 recovery 备份就在 `D:\1guodanpi\w527flashtool\Backup\recovery.bin`，用 `flash/restore_stock_recovery.bat` 写回即可。
