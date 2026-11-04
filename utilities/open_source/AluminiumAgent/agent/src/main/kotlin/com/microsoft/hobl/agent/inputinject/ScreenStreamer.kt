// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

package com.microsoft.hobl.agent.inputinject

import java.io.OutputStream
import java.nio.ByteBuffer
import java.nio.ByteOrder

// Streams the screen using the protocol of utilities/open_source/ScreenServer, which
// ScenarioMaker/remote.py reads:
//   header:    height, width                       (little-endian int32)
//   per frame: dirty rect count                    (int32, always 1 here)
//              left, top, right, bottom            (int32)
//              encoded size, then 4-channel QOI data
class ScreenStreamer(private val screen: ScreenSource, private val minFrameIntervalMs: Long = 100) {

    fun serve(out: OutputStream, isOpen: () -> Boolean) {
        var frame: Frame? = screen.capture(0)
        out.write(ints(frame!!.height, frame.width))
        out.flush()

        while (isOpen()) {
            val start = System.nanoTime()
            writeFrame(out, frame ?: screen.capture(0))
            frame = null
            val elapsedMs = (System.nanoTime() - start) / 1_000_000
            if (elapsedMs < minFrameIntervalMs) Thread.sleep(minFrameIntervalMs - elapsedMs)
        }
    }

    fun writeFrame(out: OutputStream, frame: Frame) {
        val qoi = QOIEncoder.encode(frame.rgba, frame.offset, frame.width, frame.height, frame.stride, channels = 4)
        out.write(ints(1, 0, 0, frame.width, frame.height, qoi.size))
        out.write(qoi)
        out.flush()
    }

    private fun ints(vararg values: Int): ByteArray {
        val buffer = ByteBuffer.allocate(values.size * 4).order(ByteOrder.LITTLE_ENDIAN)
        values.forEach { buffer.putInt(it) }
        return buffer.array()
    }
}
