// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

package com.microsoft.hobl.agent.inputinject

import android.view.KeyEvent
import android.view.MotionEvent
import com.microsoft.hobl.agent.Logger
import java.util.Locale
import kotlin.math.max
import kotlin.math.min
import kotlin.math.roundToLong
import kotlin.math.sqrt

// Android implementation of InputInject, the counterpart of InteropWin.cs and InteropMac.cs.
// Input is injected as mouse and keyboard events to match the Windows plugin, which uses mouse
// SendInput for taps.
class Interop(private val injector: EventInjector, private val screen: ScreenSource) {
    private var x = 0f
    private var y = 0f
    private var buttons = 0
    private var screenWidth = 0
    private var screenHeight = 0

    fun screenshot(xFrac: Double, yFrac: Double, wFrac: Double, hFrac: Double, screenIndex: Long = 0): ByteArray {
        val frame = screen.capture(screenIndex.toInt())
        screenWidth = frame.width
        screenHeight = frame.height
        val x = clamp((frame.width * xFrac).toInt(), 0, frame.width - 1)
        val y = clamp((frame.height * yFrac).toInt(), 0, frame.height - 1)
        val w = clamp((frame.width * wFrac).toInt(), 1, frame.width - x)
        val h = clamp((frame.height * hFrac).toInt(), 1, frame.height - y)
        Logger.debug("Capturing rect: $x, $y, $w, $h")
        val offset = frame.offset + (y * frame.stride + x) * 4
        return QOIEncoder.encode(frame.rgba, offset, w, h, frame.stride)
    }

    fun getScreenWidth(): Long {
        ensureScreenSize()
        return screenWidth.toLong()
    }

    fun getScreenHeight(): Long {
        ensureScreenSize()
        return screenHeight.toLong()
    }

    fun getScreenInfo(): String {
        ensureScreenSize()
        // Android density is relative to 160 dpi, the equivalent of Windows' 100% (96 dpi) scale.
        val scale = screen.density() / 160.0
        return String.format(Locale.US, "%d,%d,%.3f;", screenWidth, screenHeight, scale)
    }

    fun moveTo(x: Long, y: Long, screenIndex: Long = 0, moveCursor: Boolean = false) {
        checkScreen(screenIndex)
        if (moveCursor) {
            // Glide the pointer to the target like a user would, in 8ms steps.
            val dx = x - this.x
            val dy = y - this.y
            val distance = sqrt(dx * dx + dy * dy)
            val steps = clamp((distance / 6).toInt() + 2, 10, 250)
            for (i in 1 until steps) {
                injector.mouseMove(this.x + dx * i / steps, this.y + dy * i / steps, buttons)
                Thread.sleep(8)
            }
        }
        this.x = x.toFloat()
        this.y = y.toFloat()
        injector.mouseMove(this.x, this.y, buttons)
    }

    fun moveBy(x: Long, y: Long, moveCursor: Boolean = false) {
        moveTo((this.x + x).toLong(), (this.y + y).toLong(), 0, moveCursor)
    }

    fun tap(x: Long, y: Long, delay: Long, primary: Boolean, screenIndex: Long = 0, moveCursor: Boolean = false) {
        moveTo(x, y, screenIndex, moveCursor)
        touchDown(primary)
        Thread.sleep(delay)
        touchUp(primary)
    }

    fun tapDown(x: Long, y: Long, primary: Boolean, screenIndex: Long = 0, moveCursor: Boolean = false) {
        moveTo(x, y, screenIndex, moveCursor)
        touchDown(primary)
    }

    fun tapUp(x: Long, y: Long, primary: Boolean, screenIndex: Long = 0, moveCursor: Boolean = false) {
        moveTo(x, y, screenIndex, moveCursor)
        touchUp(primary)
    }

    fun touchDown(primary: Boolean = true) {
        val button = if (primary) MotionEvent.BUTTON_PRIMARY else MotionEvent.BUTTON_SECONDARY
        buttons = buttons or button
        injector.mouseButton(x, y, button, true, buttons)
    }

    fun touchUp(primary: Boolean = true) {
        val button = if (primary) MotionEvent.BUTTON_PRIMARY else MotionEvent.BUTTON_SECONDARY
        buttons = buttons and button.inv()
        injector.mouseButton(x, y, button, false, buttons)
    }

    fun scroll(x: Long, y: Long, delay: Long, direction: String, screenIndex: Long = 0, moveCursor: Boolean = false) {
        moveTo(x, y, screenIndex, moveCursor)
        if (direction == "down") {
            mouseWheel(-delay.toInt())
        } else if (direction == "up") {
            mouseWheel(delay.toInt())
        }
    }

    // Same units as the Windows wheel delta: 120 per notch, so 720 scrolls about one screen.
    fun mouseWheel(amount: Int) {
        injector.mouseScroll(x, y, amount / WHEEL_DELTA)
    }

    fun type(s: String, delay: Long) {
        var control = false
        var alt = false
        var shift = false
        var command = false
        val halfDelay = delay / 2
        var accumDelay = 0L
        val startTime = System.nanoTime()

        fun metaState(): Int {
            var meta = 0
            if (shift) meta = meta or KeyEvent.META_SHIFT_ON or KeyEvent.META_SHIFT_LEFT_ON
            if (control) meta = meta or KeyEvent.META_CTRL_ON or KeyEvent.META_CTRL_LEFT_ON
            if (alt) meta = meta or KeyEvent.META_ALT_ON or KeyEvent.META_ALT_LEFT_ON
            if (command) meta = meta or KeyEvent.META_META_ON or KeyEvent.META_META_LEFT_ON
            return meta
        }

        fun pressModifier(keyCode: Int, down: Boolean) {
            injector.key(keyCode, down, metaState())
            accumDelay += halfDelay
            sleepTo(startTime, accumDelay)
        }

        for (c in s) {
            when (c) {
                KeyMap.CONTROL -> { control = !control; pressModifier(KeyEvent.KEYCODE_CTRL_LEFT, control); continue }
                KeyMap.ALT -> { alt = !alt; pressModifier(KeyEvent.KEYCODE_ALT_LEFT, alt); continue }
                KeyMap.SHIFT -> { shift = !shift; pressModifier(KeyEvent.KEYCODE_SHIFT_LEFT, shift); continue }
                KeyMap.COMMAND -> { command = !command; pressModifier(KeyEvent.KEYCODE_META_LEFT, command); continue }
                KeyMap.FUNCTION -> {
                    // There is no Fn key event on Android; the key is handled by keyboard firmware.
                    accumDelay += halfDelay
                    sleepTo(startTime, accumDelay)
                    continue
                }
            }

            val stroke = KeyMap.get(c)
            val addShift = stroke.shifted && !shift
            if (addShift) {
                shift = true
                injector.key(KeyEvent.KEYCODE_SHIFT_LEFT, true, metaState())
                // A delay is needed between Shift and the character, or the Shift doesn't take effect.
                accumDelay += 25
                sleepTo(startTime, accumDelay)
            }
            injector.key(stroke.keyCode, true, metaState())
            accumDelay += halfDelay
            sleepTo(startTime, accumDelay)
            injector.key(stroke.keyCode, false, metaState())
            if (addShift) {
                shift = false
                injector.key(KeyEvent.KEYCODE_SHIFT_LEFT, false, metaState())
            }
            accumDelay += halfDelay
            sleepTo(startTime, accumDelay)
        }

        // Release any modifier left held by the string.
        if (shift) { shift = false; pressModifier(KeyEvent.KEYCODE_SHIFT_LEFT, false) }
        if (alt) { alt = false; pressModifier(KeyEvent.KEYCODE_ALT_LEFT, false) }
        if (control) { control = false; pressModifier(KeyEvent.KEYCODE_CTRL_LEFT, false) }
        if (command) { command = false; pressModifier(KeyEvent.KEYCODE_META_LEFT, false) }
    }

    fun windowMove(delay: Long, screenIndex: Long = 0) {
        // Not supported on Aluminium.
    }

    fun windowMaximize() {
        // Not supported on Aluminium.
    }

    fun eventTag(tag: String) {
        // There is no ETW on Android; record the tag in the agent log for correlation.
        Logger.info("EventTag: $tag")
    }

    private fun ensureScreenSize() {
        if (screenWidth == 0 || screenHeight == 0) {
            val frame = screen.capture(0)
            screenWidth = frame.width
            screenHeight = frame.height
        }
    }

    private fun checkScreen(screenIndex: Long) {
        if (screenIndex != 0L) throw UnsupportedOperationException("Only screen 0 is supported on Aluminium.")
    }

    companion object {
        private const val WHEEL_DELTA = 120f

        private fun clamp(value: Int, low: Int, high: Int): Int = max(low, min(value, high))

        fun sleepTo(startNanos: Long, targetMs: Long) {
            val remaining = targetMs - (System.nanoTime() - startNanos) / 1_000_000.0
            if (remaining > 0) Thread.sleep(remaining.roundToLong())
        }
    }
}
