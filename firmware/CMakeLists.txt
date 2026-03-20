# SPDX-License-Identifier: Apache-2.0
# Smart Insole Fall Prevention System Firmware
# Target: nrf52840dk_nrf52840

cmake_minimum_required(VERSION 3.20.0)

find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(smart_insole)

# Recursively collect all source files from src/
file(GLOB_RECURSE app_sources src/*.c)

target_sources(app PRIVATE ${app_sources})

target_include_directories(app PRIVATE
    src
    src/sensors
    src/ble
    src/processing
    src/power
)
