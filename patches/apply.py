#!/usr/bin/env python3
"""Add an input force-feedback vibrator backend to TWRP's vibrate().

The SPRD sc27xx vibrator (compatible "sprd,sc27xx-vibrator") registers an
input device named "sc27xx:vibrator" with FF_RUMBLE support.  Stock TWRP only
knows /sys/class/leds/vibrator/* and /sys/class/timed_output/vibrator/enable,
so on this watch haptics silently does nothing.  This patch adds a fallback
that finds the FF_RUMBLE input device and plays a rumble effect.

Run from the AOSP/TWRP tree root:  python3 <this file>
"""
import os
import sys

TARGET = os.path.join('bootable', 'recovery', 'minuitwrp', 'events.cpp')

HELPER = r'''
/* ---- input force-feedback vibrator fallback (SPRD sc27xx etc.) ---- */
#include <dirent.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/input.h>

static int g_ff_fd = -1;
static int g_ff_id = -1;

static int ff_vibrator_open(void)
{
    DIR* dir = opendir("/dev/input");
    if (dir == NULL)
        return -1;
    struct dirent* de;
    int ret = -1;
    while ((de = readdir(dir)) != NULL) {
        if (strncmp(de->d_name, "event", 5) != 0)
            continue;
        char path[96];
        snprintf(path, sizeof(path), "/dev/input/%s", de->d_name);
        int fd = open(path, O_RDWR | O_CLOEXEC);
        if (fd < 0)
            continue;
        struct ff_effect effect;
        memset(&effect, 0, sizeof(effect));
        effect.type = FF_RUMBLE;
        effect.id = -1;
        effect.u.rumble.strong_magnitude = 0xFFFF;
        effect.u.rumble.weak_magnitude = 0xFFFF;
        effect.replay.length = 100;
        effect.replay.delay = 0;
        if (ioctl(fd, EVIOCSFF, &effect) == 0) {
            g_ff_id = effect.id;
            ret = fd;
            break;
        }
        close(fd);
    }
    closedir(dir);
    return ret;
}

static void ff_vibrator_play(int timeout_ms)
{
    if (g_ff_fd < 0) {
        g_ff_fd = ff_vibrator_open();
        if (g_ff_fd < 0) {
            LOGI("No FF vibrator found, haptics disabled\n");
            return;
        }
    }
    struct ff_effect effect;
    memset(&effect, 0, sizeof(effect));
    effect.type = FF_RUMBLE;
    effect.id = g_ff_id;
    effect.u.rumble.strong_magnitude = 0xFFFF;
    effect.u.rumble.weak_magnitude = 0xFFFF;
    effect.replay.length = (uint16_t)timeout_ms;
    effect.replay.delay = 0;
    if (ioctl(g_ff_fd, EVIOCSFF, &effect) < 0)
        return;
    struct input_event play;
    memset(&play, 0, sizeof(play));
    play.type = EV_FF;
    play.code = effect.id;
    play.value = 1;
    if (write(g_ff_fd, &play, sizeof(play)) != (ssize_t)sizeof(play))
        LOGI("Failed to play FF effect\n");
}
/* ------------------------------------------------------------------ */
'''

MARK = '#ifndef TW_NO_HAPTICS\n#ifndef TW_HAPTICS_TSPDRV\nint vibrate(int timeout_ms)'

OLD = '''    } else
        write_to_file(VIBRATOR_TIMEOUT_FILE, tout);
#endif
    return 0;
}'''

NEW = '''    } else if (std::ifstream(VIBRATOR_TIMEOUT_FILE).good()) {
        write_to_file(VIBRATOR_TIMEOUT_FILE, tout);
    } else {
        ff_vibrator_play(timeout_ms);
    }
#endif
    return 0;
}'''


def main():
    if not os.path.exists(TARGET):
        print('ERROR: %s not found (run from the AOSP root)' % TARGET)
        return 1
    src = open(TARGET, encoding='utf-8').read()
    if 'ff_vibrator_play' in src:
        print('already patched')
        return 0
    if MARK not in src:
        print('ERROR: vibrate() block not found, TWRP source changed?')
        return 1
    src = src.replace(MARK, HELPER + MARK, 1)
    if OLD not in src:
        print('ERROR: vibrate() body not found')
        return 1
    src = src.replace(OLD, NEW, 1)
    open(TARGET, 'w', encoding='utf-8', newline='\n').write(src)
    print('patched %s: input FF vibrator fallback added' % TARGET)
    return 0


if __name__ == '__main__':
    sys.exit(main())
