// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

package com.microsoft.hobl.agent.inputinject

import android.view.KeyEvent
import com.microsoft.hobl.agent.RpcArgs
import org.json.JSONArray
import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder

class ApplicationTest {
    @get:Rule
    val temp = TemporaryFolder()

    private val injector = RecordingInjector()
    private val app = Application(Interop(injector, GradientScreen()))

    private fun call(method: String, vararg args: Any?): Any? = app.call(method, RpcArgs(args.toList()))

    @Test
    fun tapUsesHoblParameterOrder() {
        // Same arguments as core/app_scenario.py _click_by_template(): x, y, delay, primary, screen,
        // moveCursor, and trace parameters that are ignored on Aluminium.
        assertNull(call("Tap", 10, 20, 0, true, 0, false, null, null, null, null, null, null, null))
        assertEquals(3, injector.events.size)
        assertEquals("move 10,20 buttons=0", injector.events[0])
    }

    @Test
    fun typeAndScrollDispatch() {
        call("Type", "a", 0, null, null, null, null, null, null, null)
        call("Scroll", 5, 6, 720, "up", 0, false)
        assertEquals("key down ${KeyEvent.KEYCODE_A} meta=0", injector.events[0])
        assertEquals("scroll 5,6 notches=6.0", injector.events.last())
    }

    @Test
    fun screenshotReturnsQoiBytes() {
        val bytes = call("Screenshot", 0, 0, 1, 1, 0) as ByteArray
        assertEquals("qoif", String(bytes, 0, 4))
    }

    @Test
    fun screenQueries() {
        assertEquals("64,48,1.500;", call("GetScreenInfo"))
        assertEquals(64L, call("GetScreenWidth"))
        assertEquals(48L, call("GetScreenHeight"))
    }

    @Test
    fun pathPressesMovesAndReleases() {
        call("Path", JSONArray(listOf(1, 2, 3)), JSONArray(listOf(4, 5, 6)), JSONArray(listOf(0, 0, 0)), true, 0)
        assertEquals("move 1,4 buttons=0", injector.events.first())
        assertTrue(injector.events[1].startsWith("down 1,4"))
        assertTrue(injector.events.last().startsWith("up 3,6"))
    }

    @Test(expected = IllegalStateException::class)
    fun pathRejectsMismatchedLists() {
        call("Path", JSONArray(listOf(1, 2)), JSONArray(listOf(4)), JSONArray(listOf(0, 0)), true, 0)
    }

    @Test
    fun unsupportedCapabilitiesAreNoOps() {
        assertEquals(0, call("ContinuousScreenshot", 0, 0, 10, 10, "out"))
        assertNull(call("WriteCapturesToDisk", "out"))
        assertNull(call("WindowMaximize"))
        assertNull(call("WindowMove", 100, 0))
        assertNull(call("EventTag", "phase_begin"))
        assertTrue(injector.events.isEmpty())
    }

    @Test
    fun processRunsJsonCommandsFromStringOrFile() {
        val commands = JSONArray()
            .put(JSONObject().put("cmd", "moveto").put("x", JSONArray(listOf("7"))).put("y", JSONArray(listOf("8"))).put("delay", JSONArray(listOf("0"))))
            .put(JSONObject().put("cmd", "tap").put("x", JSONArray(listOf("7"))).put("y", JSONArray(listOf("8"))).put("delay", JSONArray(listOf("0"))).put("primary", true))
            .put(JSONObject().put("cmd", "type").put("keys", "b").put("delay", JSONArray(listOf("0"))))
        call("Process", commands.toString())
        assertEquals("move 7,8 buttons=0", injector.events[0])
        assertEquals("key up ${KeyEvent.KEYCODE_B} meta=0", injector.events.last())

        injector.events.clear()
        val file = temp.newFile("input.json").apply { writeText(commands.toString()) }
        call("Process", file.path)
        assertEquals("move 7,8 buttons=0", injector.events[0])
    }

    @Test(expected = IllegalArgumentException::class)
    fun unknownMethodFails() {
        call("NoSuchMethod")
    }
}
