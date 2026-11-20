#
# Copyright (C) 2025 The Android Open Source Project
# Copyright (C) 2025 SebaUbuntu's TWRP device tree generator
#
# SPDX-License-Identifier: Apache-2.0
#

# Inherit from those products. Most specific first.
$(call inherit-product, $(SRC_TARGET_DIR)/product/core_64_bit.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/full_base_telephony.mk)

# Inherit some common Omni stuff.
$(call inherit-product, vendor/omni/config/common.mk)

# Inherit from uws6152_1h10_go device
$(call inherit-product, device/sprd/uws6152_1h10_go/device.mk)

PRODUCT_DEVICE := uws6152_1h10_go
PRODUCT_NAME := omni_uws6152_1h10_go
PRODUCT_BRAND := hesc
PRODUCT_MODEL := M92K
PRODUCT_MANUFACTURER := hesc

PRODUCT_GMS_CLIENTID_BASE := android-sprd

PRODUCT_BUILD_PROP_OVERRIDES += \
    PRIVATE_BUILD_DESC="uws6152_1h10_gofu-user 9 PPR1.180610.011 39220 release-keys"

BUILD_FINGERPRINT := SPRD/uws6152_1h10_gofu/uws6152_1h10_go:9/PPR1.180610.011/39220:user/release-keys
