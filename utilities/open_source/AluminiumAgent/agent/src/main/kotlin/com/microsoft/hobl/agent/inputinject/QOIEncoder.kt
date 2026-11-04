// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

package com.microsoft.hobl.agent.inputinject

import java.io.ByteArrayOutputStream

// Encodes images in the "Quite OK Image" format (https://qoiformat.org), which HOBL decodes with
// the qoi Python package.  Mirrors InputInject/QOI.cs.  Source alpha is ignored (RGBX screen
// formats leave it undefined) and every pixel is encoded as opaque.  Screenshots are reported as
// 3-channel RGB, matching the Windows and macOS InputInject plugins; the ScreenServer stream uses
// 4 channels, which ScenarioMaker expects.
object QOIEncoder {
    private const val OP_INDEX = 0x00
    private const val OP_DIFF = 0x40
    private const val OP_LUMA = 0x80
    private const val OP_RUN = 0xc0
    private const val OP_RGB = 0xfe

    // rgba holds 4 bytes per pixel, rows are "stride" pixels apart.
    fun encode(rgba: ByteArray, offset: Int, width: Int, height: Int, stride: Int, channels: Int = 3): ByteArray {
        val out = ByteArrayOutputStream(width * height + 64)
        out.write('q'.code); out.write('o'.code); out.write('i'.code); out.write('f'.code)
        writeInt(out, width)
        writeInt(out, height)
        out.write(channels)
        out.write(0)

        val index = IntArray(64)
        var prevR = 0; var prevG = 0; var prevB = 0
        var run = 0
        val total = width * height
        var count = 0

        for (row in 0 until height) {
            var p = offset + row * stride * 4
            for (col in 0 until width) {
                val r = rgba[p].toInt() and 0xff
                val g = rgba[p + 1].toInt() and 0xff
                val b = rgba[p + 2].toInt() and 0xff
                p += 4
                count++

                if (r == prevR && g == prevG && b == prevB) {
                    run++
                    if (run == 62 || count == total) {
                        out.write(OP_RUN or (run - 1))
                        run = 0
                    }
                    continue
                }

                if (run > 0) {
                    out.write(OP_RUN or (run - 1))
                    run = 0
                }

                val pixel = (r shl 24) or (g shl 16) or (b shl 8) or 0xff
                val hash = (r * 3 + g * 5 + b * 7 + 255 * 11) % 64
                if (index[hash] == pixel) {
                    out.write(OP_INDEX or hash)
                } else {
                    index[hash] = pixel
                    val vr = (r - prevR).toByte().toInt()
                    val vg = (g - prevG).toByte().toInt()
                    val vb = (b - prevB).toByte().toInt()
                    val vgR = vr - vg
                    val vgB = vb - vg
                    if (vr in -2..1 && vg in -2..1 && vb in -2..1) {
                        out.write(OP_DIFF or ((vr + 2) shl 4) or ((vg + 2) shl 2) or (vb + 2))
                    } else if (vgR in -8..7 && vg in -32..31 && vgB in -8..7) {
                        out.write(OP_LUMA or (vg + 32))
                        out.write(((vgR + 8) shl 4) or (vgB + 8))
                    } else {
                        out.write(OP_RGB)
                        out.write(r); out.write(g); out.write(b)
                    }
                }
                prevR = r; prevG = g; prevB = b
            }
        }

        // End marker.
        repeat(7) { out.write(0) }
        out.write(1)
        return out.toByteArray()
    }

    private fun writeInt(out: ByteArrayOutputStream, value: Int) {
        out.write((value ushr 24) and 0xff)
        out.write((value ushr 16) and 0xff)
        out.write((value ushr 8) and 0xff)
        out.write(value and 0xff)
    }
}
