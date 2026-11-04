// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

package com.microsoft.hobl.agent.inputinject

import android.view.KeyEvent
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import java.nio.ByteBuffer
import java.nio.ByteOrder

class ScreencapSourceTest {
    private fun raw(width: Int, height: Int, stride: Int, headerSize: Int, format: Int = 1): ByteArray {
        val buffer = ByteBuffer.allocate(headerSize + stride * height * 4).order(ByteOrder.LITTLE_ENDIAN)
        buffer.putInt(width).putInt(height).putInt(format)
        if (headerSize == 16) buffer.putInt(142671872)
        for (i in 0 until stride * height) buffer.put(i.toByte()).put(0).put(0).put(0xff.toByte())
        return buffer.array()
    }

    @Test
    fun parsesSixteenByteHeader() {
        val frame = ScreencapSource.parseRaw(raw(8, 4, 8, 16))
        assertEquals(8, frame.width)
        assertEquals(4, frame.height)
        assertEquals(8, frame.stride)
        assertEquals(16, frame.offset)
    }

    @Test
    fun parsesTwelveByteHeader() {
        val frame = ScreencapSource.parseRaw(raw(8, 4, 8, 12))
        assertEquals(12, frame.offset)
        assertEquals(8, frame.stride)
    }

    @Test
    fun handlesRowPadding() {
        val frame = ScreencapSource.parseRaw(raw(6, 4, 8, 16))
        assertEquals(6, frame.width)
        assertEquals(8, frame.stride)
    }

    @Test(expected = IllegalStateException::class)
    fun rejectsUnsupportedFormat() {
        ScreencapSource.parseRaw(raw(8, 4, 8, 16, format = 4))
    }

    @Test(expected = IllegalStateException::class)
    fun rejectsTruncatedOutput() {
        ScreencapSource.parseRaw(raw(8, 4, 8, 16).copyOf(100))
    }

    @Test
    fun densityPrefersOverride() {
        assertEquals(240, ScreencapSource.parseDensity("Physical density: 240\n"))
        assertEquals(200, ScreencapSource.parseDensity("Physical density: 240\nOverride density: 200\n"))
    }

    @Test(expected = IllegalStateException::class)
    fun densityParseFailureIsReported() {
        ScreencapSource.parseDensity("cmd: Can't find service: window")
    }
}

class KeyMapTest {
    @Test
    fun lettersDigitsAndShiftedSymbols() {
        assertEquals(KeyEvent.KEYCODE_Z, KeyMap.get('z').keyCode)
        assertFalse(KeyMap.get('z').shifted)
        assertTrue(KeyMap.get('Z').shifted)
        assertEquals(KeyEvent.KEYCODE_0, KeyMap.get(')').keyCode)
        assertEquals(KeyEvent.KEYCODE_9, KeyMap.get('(').keyCode)
        assertEquals(KeyEvent.KEYCODE_SLASH, KeyMap.get('?').keyCode)
        assertTrue(KeyMap.get('?').shifted)
    }

    @Test
    fun webDriverSpecialKeys() {
        assertEquals(KeyEvent.KEYCODE_ENTER, KeyMap.get('\ue007').keyCode)
        assertEquals(KeyEvent.KEYCODE_ESCAPE, KeyMap.get('\ue00c').keyCode)
        assertEquals(KeyEvent.KEYCODE_DEL, KeyMap.get('\ue003').keyCode)
        assertEquals(KeyEvent.KEYCODE_F1, KeyMap.get('\ue031').keyCode)
        assertEquals(KeyEvent.KEYCODE_F12, KeyMap.get('\ue03c').keyCode)
        assertEquals(KeyEvent.KEYCODE_DPAD_DOWN, KeyMap.get('\ue015').keyCode)
    }

    @Test
    fun printableAsciiIsCovered() {
        for (c in ' '..'~') KeyMap.get(c)
    }
}
