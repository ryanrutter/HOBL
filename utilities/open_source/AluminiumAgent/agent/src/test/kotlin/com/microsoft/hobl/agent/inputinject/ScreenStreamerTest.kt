// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

package com.microsoft.hobl.agent.inputinject

import org.junit.Assert.assertEquals
import org.junit.Test
import java.io.ByteArrayOutputStream
import java.nio.ByteBuffer
import java.nio.ByteOrder

class ScreenStreamerTest {
    @Test
    fun streamsHeaderThenFullScreenFrames() {
        val screen = GradientScreen(width = 20, height = 10)
        val out = ByteArrayOutputStream()
        var frames = 0
        ScreenStreamer(screen, minFrameIntervalMs = 0).serve(out) { frames++ < 2 }

        val data = ByteBuffer.wrap(out.toByteArray()).order(ByteOrder.LITTLE_ENDIAN)
        // ScenarioMaker/remote.py reads height first, then width.
        assertEquals(10, data.int)
        assertEquals(20, data.int)

        repeat(2) {
            assertEquals("One dirty rect per frame", 1, data.int)
            assertEquals(listOf(0, 0, 20, 10), listOf(data.int, data.int, data.int, data.int))
            val size = data.int
            val qoi = ByteArray(size).also { data.get(it) }
            val image = QoiTestDecoder.decode(qoi)
            assertEquals("ScenarioMaker expects 4-channel frames", 4, image.channels)
            assertEquals(20, image.width)
            assertEquals(10, image.height)
        }
        assertEquals(0, data.remaining())
        assertEquals("The first capture is reused for the first frame", 2, screen.captures)
    }
}
