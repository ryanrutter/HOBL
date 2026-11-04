// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

package com.microsoft.hobl.agent.inputinject

import java.nio.ByteBuffer

// Records injected events as readable strings, for asserting on input sequences.
class RecordingInjector : EventInjector {
    val events = mutableListOf<String>()

    override fun mouseMove(x: Float, y: Float, buttons: Int) {
        events += "move ${x.toInt()},${y.toInt()} buttons=$buttons"
    }

    override fun mouseButton(x: Float, y: Float, button: Int, down: Boolean, buttons: Int) {
        events += "${if (down) "down" else "up"} ${x.toInt()},${y.toInt()} button=$button buttons=$buttons"
    }

    override fun mouseScroll(x: Float, y: Float, notches: Float) {
        events += "scroll ${x.toInt()},${y.toInt()} notches=$notches"
    }

    override fun key(keyCode: Int, down: Boolean, metaState: Int) {
        events += "key ${if (down) "down" else "up"} $keyCode meta=$metaState"
    }
}

// Deterministic test image: red increases with x, green with y, blue is constant.
class GradientScreen(private val width: Int = 64, private val height: Int = 48, private val densityDpi: Int = 240) : ScreenSource {
    var captures = 0

    override fun capture(screenIndex: Int): Frame {
        captures++
        val rgba = ByteArray(width * height * 4)
        for (y in 0 until height) {
            for (x in 0 until width) {
                val p = (y * width + x) * 4
                rgba[p] = pixelR(x).toByte()
                rgba[p + 1] = pixelG(y).toByte()
                rgba[p + 2] = PIXEL_B.toByte()
                rgba[p + 3] = 0xff.toByte()
            }
        }
        return Frame(width, height, width, rgba, 0)
    }

    override fun density(): Int = densityDpi

    companion object {
        const val PIXEL_B = 0x40
        fun pixelR(x: Int) = (x * 4) and 0xff
        fun pixelG(y: Int) = (y * 5) and 0xff
    }
}

// Reference decoder from the QOI specification, used to verify QOIEncoder.
object QoiTestDecoder {
    class Image(val width: Int, val height: Int, val channels: Int, val rgb: IntArray)

    fun decode(data: ByteArray): Image {
        val header = ByteBuffer.wrap(data)
        require(String(data, 0, 4) == "qoif")
        val width = header.getInt(4)
        val height = header.getInt(8)
        val channels = data[12].toInt()
        val pixels = IntArray(width * height)
        val index = IntArray(64)
        var r = 0; var g = 0; var b = 0; var a = 255
        var p = 14
        var run = 0
        for (i in pixels.indices) {
            if (run > 0) {
                run--
            } else {
                val b1 = data[p++].toInt() and 0xff
                when {
                    b1 == 0xfe -> { r = data[p++].toInt() and 0xff; g = data[p++].toInt() and 0xff; b = data[p++].toInt() and 0xff }
                    b1 == 0xff -> { r = data[p++].toInt() and 0xff; g = data[p++].toInt() and 0xff; b = data[p++].toInt() and 0xff; a = data[p++].toInt() and 0xff }
                    b1 and 0xc0 == 0x00 -> { val px = index[b1]; r = px ushr 24 and 0xff; g = px ushr 16 and 0xff; b = px ushr 8 and 0xff; a = px and 0xff }
                    b1 and 0xc0 == 0x40 -> { r = (r + ((b1 shr 4) and 3) - 2) and 0xff; g = (g + ((b1 shr 2) and 3) - 2) and 0xff; b = (b + (b1 and 3) - 2) and 0xff }
                    b1 and 0xc0 == 0x80 -> {
                        val b2 = data[p++].toInt() and 0xff
                        val vg = (b1 and 0x3f) - 32
                        r = (r + vg - 8 + ((b2 shr 4) and 0x0f)) and 0xff
                        g = (g + vg) and 0xff
                        b = (b + vg - 8 + (b2 and 0x0f)) and 0xff
                    }
                    else -> run = b1 and 0x3f
                }
                index[(r * 3 + g * 5 + b * 7 + a * 11) % 64] = (r shl 24) or (g shl 16) or (b shl 8) or a
            }
            pixels[i] = (r shl 16) or (g shl 8) or b
        }
        val end = data.copyOfRange(data.size - 8, data.size)
        require(end.contentEquals(byteArrayOf(0, 0, 0, 0, 0, 0, 0, 1))) { "Missing QOI end marker" }
        return Image(width, height, channels, pixels)
    }
}
