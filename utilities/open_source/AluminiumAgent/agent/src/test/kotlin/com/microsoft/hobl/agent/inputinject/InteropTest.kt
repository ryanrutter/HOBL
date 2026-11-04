// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

package com.microsoft.hobl.agent.inputinject

import android.view.KeyEvent
import android.view.MotionEvent
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class InteropTest {
    private val injector = RecordingInjector()
    private val screen = GradientScreen(width = 64, height = 48, densityDpi = 240)
    private val interop = Interop(injector, screen)

    private val shiftMeta = KeyEvent.META_SHIFT_ON or KeyEvent.META_SHIFT_LEFT_ON
    private val ctrlMeta = KeyEvent.META_CTRL_ON or KeyEvent.META_CTRL_LEFT_ON

    @Test
    fun tapMovesThenPressesAndReleasesPrimaryButton() {
        interop.tap(100, 200, 0, true)
        assertEquals(
            listOf(
                "move 100,200 buttons=0",
                "down 100,200 button=${MotionEvent.BUTTON_PRIMARY} buttons=${MotionEvent.BUTTON_PRIMARY}",
                "up 100,200 button=${MotionEvent.BUTTON_PRIMARY} buttons=0"
            ),
            injector.events
        )
    }

    @Test
    fun secondaryTapUsesSecondaryButton() {
        interop.tap(1, 2, 0, false)
        assertEquals("down 1,2 button=${MotionEvent.BUTTON_SECONDARY} buttons=${MotionEvent.BUTTON_SECONDARY}", injector.events[1])
    }

    @Test
    fun dragMovesWithButtonHeld() {
        interop.tapDown(10, 10, true)
        interop.moveTo(20, 30)
        interop.tapUp(20, 30, true)
        assertEquals("move 20,30 buttons=${MotionEvent.BUTTON_PRIMARY}", injector.events[2])
        assertEquals("up 20,30 button=${MotionEvent.BUTTON_PRIMARY} buttons=0", injector.events.last())
    }

    @Test
    fun moveCursorGlidesToTarget() {
        interop.moveTo(0, 0)
        injector.events.clear()
        interop.moveTo(300, 0, 0, moveCursor = true)
        assertTrue("Intermediate points are injected", injector.events.size >= 10)
        assertEquals("move 300,0 buttons=0", injector.events.last())
    }

    @Test
    fun moveByIsRelative() {
        interop.moveTo(50, 60)
        interop.moveBy(5, -10)
        assertEquals("move 55,50 buttons=0", injector.events.last())
    }

    @Test
    fun scrollUsesWindowsWheelUnits() {
        interop.scroll(10, 20, 720, "down")
        assertEquals("scroll 10,20 notches=-6.0", injector.events.last())
        interop.scroll(10, 20, 240, "up")
        assertEquals("scroll 10,20 notches=2.0", injector.events.last())
    }

    @Test
    fun typePressesShiftForUppercaseAndSymbols() {
        interop.type("aB!", 0)
        assertEquals(
            listOf(
                "key down ${KeyEvent.KEYCODE_A} meta=0",
                "key up ${KeyEvent.KEYCODE_A} meta=0",
                "key down ${KeyEvent.KEYCODE_SHIFT_LEFT} meta=$shiftMeta",
                "key down ${KeyEvent.KEYCODE_B} meta=$shiftMeta",
                "key up ${KeyEvent.KEYCODE_B} meta=$shiftMeta",
                "key up ${KeyEvent.KEYCODE_SHIFT_LEFT} meta=0",
                "key down ${KeyEvent.KEYCODE_SHIFT_LEFT} meta=$shiftMeta",
                "key down ${KeyEvent.KEYCODE_1} meta=$shiftMeta",
                "key up ${KeyEvent.KEYCODE_1} meta=$shiftMeta",
                "key up ${KeyEvent.KEYCODE_SHIFT_LEFT} meta=0"
            ),
            injector.events
        )
    }

    @Test
    fun controlKeyTogglesLikeWebDriver() {
        // Ctrl+T then release, as HOBL scenarios send "\ue009t\ue009".
        interop.type("\ue009t\ue009", 0)
        assertEquals(
            listOf(
                "key down ${KeyEvent.KEYCODE_CTRL_LEFT} meta=$ctrlMeta",
                "key down ${KeyEvent.KEYCODE_T} meta=$ctrlMeta",
                "key up ${KeyEvent.KEYCODE_T} meta=$ctrlMeta",
                "key up ${KeyEvent.KEYCODE_CTRL_LEFT} meta=0"
            ),
            injector.events
        )
    }

    @Test
    fun heldModifiersAreReleasedAtEnd() {
        interop.type("\ue009", 0)
        assertEquals("key up ${KeyEvent.KEYCODE_CTRL_LEFT} meta=0", injector.events.last())
    }

    @Test
    fun typeHonorsDelayBetweenKeys() {
        val start = System.nanoTime()
        interop.type("abcd", 50)
        val elapsedMs = (System.nanoTime() - start) / 1_000_000
        assertTrue("Typing 4 keys at 50ms took $elapsedMs ms", elapsedMs >= 190)
    }

    @Test(expected = IllegalArgumentException::class)
    fun unsupportedCharacterFails() {
        interop.type("\u00e9", 0)
    }

    @Test
    fun screenInfoReportsSizeAndScale() {
        assertEquals("64,48,1.500;", interop.getScreenInfo())
        assertEquals(64L, interop.getScreenWidth())
        assertEquals(48L, interop.getScreenHeight())
        assertEquals("Screen size is cached", 1, screen.captures)
    }

    @Test
    fun screenshotCropsFractionalRegion() {
        val image = QoiTestDecoder.decode(interop.screenshot(0.25, 0.5, 0.5, 0.25))
        assertEquals(32, image.width)
        assertEquals(12, image.height)
        val expectedFirst = (GradientScreen.pixelR(16) shl 16) or (GradientScreen.pixelG(24) shl 8) or GradientScreen.PIXEL_B
        assertEquals(expectedFirst, image.rgb[0])
    }

    @Test
    fun fullScreenshot() {
        val image = QoiTestDecoder.decode(interop.screenshot(0.0, 0.0, 1.0, 1.0))
        assertEquals(64, image.width)
        assertEquals(48, image.height)
    }

    @Test(expected = UnsupportedOperationException::class)
    fun onlyPrimaryScreenIsSupported() {
        interop.moveTo(1, 1, screenIndex = 1)
    }
}
