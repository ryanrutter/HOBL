// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

package com.microsoft.hobl.agent.inputinject

import com.microsoft.hobl.agent.ProcessRunner
import java.nio.ByteBuffer
import java.nio.ByteOrder

// Captures the display with the platform "screencap" tool, which the shell user may run on
// production builds.  Without a file argument screencap writes a raw RGBA frame to stdout.
class ScreencapSource : ScreenSource {
    override fun capture(screenIndex: Int): Frame {
        if (screenIndex != 0) throw UnsupportedOperationException("Only screen 0 is supported on Aluminium.")
        val process = ProcessBuilder("screencap").redirectErrorStream(false).start()
        val bytes = process.inputStream.readBytes()
        val exitCode = process.waitFor()
        if (exitCode != 0) throw IllegalStateException("screencap failed with exit code $exitCode")
        return parseRaw(bytes)
    }

    override fun density(): Int = parseDensity(ProcessRunner.runWithResultAndExitCode("wm", "density").second)

    companion object {
        private const val PIXEL_FORMAT_RGBA_8888 = 1
        private const val PIXEL_FORMAT_RGBX_8888 = 2

        // Raw screencap layout: width, height, and pixel format as little-endian 32-bit integers,
        // followed by the data space on newer Android versions, then the pixel rows.
        fun parseRaw(bytes: ByteArray): Frame {
            if (bytes.size < 12) throw IllegalStateException("screencap output is too short (${bytes.size} bytes)")
            val header = ByteBuffer.wrap(bytes).order(ByteOrder.LITTLE_ENDIAN)
            val width = header.getInt(0)
            val height = header.getInt(4)
            val format = header.getInt(8)
            if (format != PIXEL_FORMAT_RGBA_8888 && format != PIXEL_FORMAT_RGBX_8888) {
                throw IllegalStateException("Unsupported screencap pixel format: $format")
            }
            if (width <= 0 || height <= 0) throw IllegalStateException("Invalid screencap size: $width x $height")

            val rowBytes = height * 4
            val headerSize = if ((bytes.size - 16) % rowBytes == 0 && (bytes.size - 16) / rowBytes >= width) 16 else 12
            val stride = (bytes.size - headerSize) / rowBytes
            if (stride < width) throw IllegalStateException("screencap output is truncated")
            return Frame(width, height, stride, bytes, headerSize)
        }

        // "wm density" prints "Physical density: N" and, when changed in settings, "Override density: N".
        fun parseDensity(output: String): Int {
            val values = output.lines().mapNotNull { line ->
                val parts = line.split(":")
                if (parts.size == 2) parts[0].trim() to parts[1].trim().toIntOrNull() else null
            }.toMap()
            return values["Override density"] ?: values["Physical density"]
                ?: throw IllegalStateException("Unable to parse 'wm density' output: $output")
        }
    }
}
