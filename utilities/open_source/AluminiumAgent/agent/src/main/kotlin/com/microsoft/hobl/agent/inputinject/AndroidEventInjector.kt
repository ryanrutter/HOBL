// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

package com.microsoft.hobl.agent.inputinject

import android.os.SystemClock
import android.view.InputDevice
import android.view.InputEvent
import android.view.KeyCharacterMap
import android.view.KeyEvent
import android.view.MotionEvent
import com.microsoft.hobl.agent.Logger
import java.lang.reflect.Method

// Injects events through the hidden InputManager API.  The agent runs as the shell user through
// app_process, which holds the INJECT_EVENTS permission.  This is the same approach used by
// scrcpy and UI Automator.
class AndroidEventInjector : EventInjector {
    private val manager: Any
    private val injectInputEvent: Method
    private val setActionButton: Method?
    private var downTime = 0L

    init {
        // InputManagerGlobal holds the injection API from Android 14 onwards.
        val managerClass = try {
            Class.forName("android.hardware.input.InputManagerGlobal")
        } catch (e: ClassNotFoundException) {
            Class.forName("android.hardware.input.InputManager")
        }
        manager = managerClass.getDeclaredMethod("getInstance").invoke(null)
            ?: throw IllegalStateException("Unable to get ${managerClass.name} instance.")
        injectInputEvent = managerClass.getMethod("injectInputEvent", InputEvent::class.java, Int::class.javaPrimitiveType)
        setActionButton = try {
            MotionEvent::class.java.getMethod("setActionButton", Int::class.javaPrimitiveType)
        } catch (e: NoSuchMethodException) {
            Logger.warn("MotionEvent.setActionButton() not found; mouse button press events will be skipped.")
            null
        }
    }

    override fun mouseMove(x: Float, y: Float, buttons: Int) {
        val action = if (buttons == 0) MotionEvent.ACTION_HOVER_MOVE else MotionEvent.ACTION_MOVE
        inject(motionEvent(action, x, y, buttons))
    }

    override fun mouseButton(x: Float, y: Float, button: Int, down: Boolean, buttons: Int) {
        if (down) {
            // The first button pressed starts the gesture.
            if (buttons == button) {
                downTime = SystemClock.uptimeMillis()
                inject(motionEvent(MotionEvent.ACTION_DOWN, x, y, buttons))
            }
            injectButtonEvent(MotionEvent.ACTION_BUTTON_PRESS, x, y, button, buttons)
        } else {
            injectButtonEvent(MotionEvent.ACTION_BUTTON_RELEASE, x, y, button, buttons)
            if (buttons == 0) {
                inject(motionEvent(MotionEvent.ACTION_UP, x, y, buttons))
                downTime = 0
            }
        }
    }

    override fun mouseScroll(x: Float, y: Float, notches: Float) {
        inject(motionEvent(MotionEvent.ACTION_SCROLL, x, y, 0, notches))
    }

    override fun key(keyCode: Int, down: Boolean, metaState: Int) {
        val now = SystemClock.uptimeMillis()
        val action = if (down) KeyEvent.ACTION_DOWN else KeyEvent.ACTION_UP
        inject(KeyEvent(now, now, action, keyCode, 0, metaState, KeyCharacterMap.VIRTUAL_KEYBOARD, 0, 0, InputDevice.SOURCE_KEYBOARD))
    }

    private fun injectButtonEvent(action: Int, x: Float, y: Float, button: Int, buttons: Int) {
        val method = setActionButton ?: return
        val event = motionEvent(action, x, y, buttons)
        method.invoke(event, button)
        inject(event)
    }

    private fun motionEvent(action: Int, x: Float, y: Float, buttons: Int, vscroll: Float = 0f): MotionEvent {
        val now = SystemClock.uptimeMillis()
        val properties = MotionEvent.PointerProperties().apply {
            id = 0
            toolType = MotionEvent.TOOL_TYPE_MOUSE
        }
        val coords = MotionEvent.PointerCoords().apply {
            this.x = x
            this.y = y
            pressure = if (buttons != 0) 1f else 0f
            size = 1f
            if (vscroll != 0f) setAxisValue(MotionEvent.AXIS_VSCROLL, vscroll)
        }
        val eventDownTime = if (downTime != 0L) downTime else now
        return MotionEvent.obtain(
            eventDownTime, now, action, 1, arrayOf(properties), arrayOf(coords),
            0, buttons, 1f, 1f, 0, 0, InputDevice.SOURCE_MOUSE, 0
        )
    }

    private fun inject(event: InputEvent) {
        val injected = injectInputEvent.invoke(manager, event, INJECT_INPUT_EVENT_MODE_ASYNC) as Boolean
        if (!injected) Logger.warn("Input event was not injected: $event")
    }

    companion object {
        // InputManager.INJECT_INPUT_EVENT_MODE_ASYNC (hidden).
        private const val INJECT_INPUT_EVENT_MODE_ASYNC = 0
    }
}
