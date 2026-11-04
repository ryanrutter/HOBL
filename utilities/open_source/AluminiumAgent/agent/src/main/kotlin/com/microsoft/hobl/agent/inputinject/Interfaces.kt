// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

package com.microsoft.hobl.agent.inputinject

// Abstractions over the Android specific parts of input injection and screen capture, so the
// InputInject logic in Interop can be unit tested on the host JVM.

interface EventInjector {
    // Moves the mouse pointer.  "buttons" is the MotionEvent button state; 0 means hovering.
    fun mouseMove(x: Float, y: Float, buttons: Int)

    fun mouseButton(x: Float, y: Float, button: Int, down: Boolean, buttons: Int)

    // Positive values scroll up, in mouse wheel notches.
    fun mouseScroll(x: Float, y: Float, notches: Float)

    fun key(keyCode: Int, down: Boolean, metaState: Int)
}

// A captured frame with 4 bytes (RGBA) per pixel, rows "stride" pixels apart.
class Frame(val width: Int, val height: Int, val stride: Int, val rgba: ByteArray, val offset: Int)

interface ScreenSource {
    fun capture(screenIndex: Int): Frame

    fun density(): Int
}
