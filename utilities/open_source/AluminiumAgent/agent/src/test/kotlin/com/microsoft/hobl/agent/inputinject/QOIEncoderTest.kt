// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

package com.microsoft.hobl.agent.inputinject

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import kotlin.random.Random

class QOIEncoderTest {
    private fun rgba(width: Int, height: Int, pixel: (Int, Int) -> Int): ByteArray {
        val bytes = ByteArray(width * height * 4)
        for (y in 0 until height) for (x in 0 until width) {
            val p = (y * width + x) * 4
            val rgb = pixel(x, y)
            bytes[p] = (rgb shr 16).toByte()
            bytes[p + 1] = (rgb shr 8).toByte()
            bytes[p + 2] = rgb.toByte()
            bytes[p + 3] = 0xff.toByte()
        }
        return bytes
    }

    private fun assertRoundTrip(width: Int, height: Int, pixel: (Int, Int) -> Int) {
        val encoded = QOIEncoder.encode(rgba(width, height, pixel), 0, width, height, width)
        val image = QoiTestDecoder.decode(encoded)
        assertEquals(width, image.width)
        assertEquals(height, image.height)
        assertEquals("Encoded as RGB, like the Windows and macOS plugins", 3, image.channels)
        for (y in 0 until height) for (x in 0 until width) {
            assertEquals("pixel $x,$y", pixel(x, y) and 0xffffff, image.rgb[y * width + x])
        }
    }

    @Test
    fun solidImageUsesRunsAcrossTheRunLimit() {
        // 200 identical pixels exercise run lengths beyond the 62 pixel maximum.
        assertRoundTrip(20, 10) { _, _ -> 0x336699 }
        val encoded = QOIEncoder.encode(rgba(20, 10) { _, _ -> 0x336699 }, 0, 20, 10, 20)
        assertTrue("Runs compress a solid image", encoded.size < 40)
    }

    @Test
    fun gradientsUseDiffAndLumaOps() {
        assertRoundTrip(50, 30) { x, y -> ((x * 3) shl 16) or ((y * 2) shl 8) or (x + y) }
    }

    @Test
    fun repeatedColorsUseIndexOp() {
        assertRoundTrip(16, 16) { x, y -> if ((x + y) % 2 == 0) 0xff0000 else 0x00ff00 }
    }

    @Test
    fun randomPixelsUseRgbOp() {
        val random = Random(42)
        val pixels = IntArray(31 * 17) { random.nextInt(0x1000000) }
        assertRoundTrip(31, 17) { x, y -> pixels[y * 31 + x] }
    }

    @Test
    fun encodesSubRegionUsingStride() {
        val full = rgba(10, 10) { x, y -> (x shl 16) or (y shl 8) }
        // Region starting at (3, 4), 5 x 2 pixels.
        val encoded = QOIEncoder.encode(full, (4 * 10 + 3) * 4, 5, 2, 10)
        val image = QoiTestDecoder.decode(encoded)
        assertEquals(5, image.width)
        assertEquals(2, image.height)
        assertEquals((3 shl 16) or (4 shl 8), image.rgb[0])
        assertEquals((7 shl 16) or (5 shl 8), image.rgb[9])
    }
}
